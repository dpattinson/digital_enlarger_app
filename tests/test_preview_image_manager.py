"""Tests for PreviewImageManager class.

This module contains unit tests for the PreviewImageManager class,
focusing on fast preview display optimization functionality.
"""

import unittest
from unittest.mock import Mock, patch
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

from app.preview_image_manager import PreviewImageManager


class TestPreviewImageManager(unittest.TestCase):
    """Test cases for PreviewImageManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = PreviewImageManager()

    # Tests for Preview Image Preparation

    def test_prepare_preview_image_converts_16bit_to_8bit(self):
        """
        GIVEN: A 16-bit grayscale image
        WHEN: prepare_preview_image is called
        THEN: Image is converted to 8-bit for fast preview processing
        """
        # GIVEN: 16-bit test image
        image_16bit = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        
        # WHEN: Preparing preview image
        result = self.manager.prepare_preview_image(image_16bit)
        
        # THEN: Result is 8-bit
        self.assertEqual(result.dtype, np.uint8)
        # Values should be right-shifted by 8 bits
        expected = np.array([[3, 7], [11, 15]], dtype=np.uint8)
        np.testing.assert_array_equal(result, expected)

    def test_prepare_preview_image_handles_8bit_input(self):
        """
        GIVEN: An 8-bit grayscale image
        WHEN: prepare_preview_image is called
        THEN: Image is processed as 8-bit without conversion
        """
        # GIVEN: 8-bit test image
        image_8bit = np.array([[100, 150], [200, 250]], dtype=np.uint8)
        
        # WHEN: Preparing preview image
        result = self.manager.prepare_preview_image(image_8bit)
        
        # THEN: Result remains 8-bit with same values
        self.assertEqual(result.dtype, np.uint8)
        np.testing.assert_array_equal(result, image_8bit)

    @patch('cv2.resize')
    def test_prepare_preview_image_resizes_when_needed(self, mock_resize):
        """
        GIVEN: An image larger than container size
        WHEN: prepare_preview_image is called
        THEN: Image is resized using cv2.resize with INTER_LINEAR
        """
        # GIVEN: Large test image and mock resize
        large_image = np.ones((1000, 1500), dtype=np.uint16)
        resized_image = np.ones((200, 300), dtype=np.uint8)
        mock_resize.return_value = resized_image
        
        manager = PreviewImageManager(cv2_resize=mock_resize)
        
        # WHEN: Preparing preview image
        result = manager.prepare_preview_image(large_image, container_size=(400, 300))
        
        # THEN: cv2.resize was called with correct parameters
        mock_resize.assert_called_once()
        args, kwargs = mock_resize.call_args
        self.assertEqual(kwargs.get('interpolation'), 2)  # cv2.INTER_LINEAR = 2

    def test_prepare_preview_image_raises_error_for_none_image(self):
        """
        GIVEN: None image data
        WHEN: prepare_preview_image is called
        THEN: ValueError is raised with appropriate message
        """
        # GIVEN: None image
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.prepare_preview_image(None)
        self.assertIn("Cannot prepare preview for None image", str(context.exception))

    def test_prepare_preview_image_raises_error_for_3d_image(self):
        """
        GIVEN: A 3D image array
        WHEN: prepare_preview_image is called
        THEN: ValueError is raised with appropriate message
        """
        # GIVEN: 3D image
        image_3d = np.ones((100, 100, 3), dtype=np.uint8)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.prepare_preview_image(image_3d)
        self.assertIn("Expected 2D grayscale image, got 3D", str(context.exception))

    # Tests for Preview Size Calculation

    def test_calculate_preview_size_maintains_aspect_ratio(self):
        """
        GIVEN: An image shape and container size
        WHEN: calculate_preview_size is called
        THEN: Calculated size maintains aspect ratio and fits in container
        """
        # GIVEN: Portrait image (taller than wide)
        image_shape = (1200, 800)  # height, width
        container_size = (400, 300)  # width, height
        
        # WHEN: Calculating preview size
        result = self.manager.calculate_preview_size(image_shape, container_size)
        
        # THEN: Size maintains aspect ratio and fits in container
        width, height = result
        self.assertEqual(width, 200)  # Limited by height: 300 * (800/1200) = 200
        self.assertEqual(height, 300)  # Uses full container height
        
        # Verify aspect ratio is maintained
        original_ratio = 800 / 1200
        result_ratio = width / height
        self.assertAlmostEqual(original_ratio, result_ratio, places=3)

    def test_calculate_preview_size_landscape_image(self):
        """
        GIVEN: A landscape image shape and container size
        WHEN: calculate_preview_size is called
        THEN: Calculated size maintains aspect ratio and fits in container
        """
        # GIVEN: Landscape image (wider than tall)
        image_shape = (600, 1200)  # height, width
        container_size = (400, 300)  # width, height
        
        # WHEN: Calculating preview size
        result = self.manager.calculate_preview_size(image_shape, container_size)
        
        # THEN: Size maintains aspect ratio and fits in container
        width, height = result
        self.assertEqual(width, 400)  # Uses full container width
        self.assertEqual(height, 200)  # Limited by width: 400 * (600/1200) = 200

    # Tests for Pixmap Creation

    def test_create_preview_pixmap_returns_valid_pixmap(self):
        """
        GIVEN: Valid image data
        WHEN: create_preview_pixmap is called
        THEN: Valid QPixmap is returned
        """
        # GIVEN: Test image
        test_image = np.array([[100, 150], [200, 250]], dtype=np.uint8)
        
        # WHEN: Creating preview pixmap
        result = self.manager.create_preview_pixmap(test_image)
        
        # THEN: Valid QPixmap is returned
        self.assertIsInstance(result, QPixmap)
        self.assertFalse(result.isNull())

    def test_numpy_to_pixmap_converts_correctly(self):
        """
        GIVEN: 8-bit numpy array
        WHEN: numpy_to_pixmap is called
        THEN: QPixmap is created with correct dimensions
        """
        # GIVEN: 8-bit test image
        test_image = np.ones((100, 150), dtype=np.uint8) * 128
        
        # WHEN: Converting to pixmap
        result = self.manager.numpy_to_pixmap(test_image)
        
        # THEN: QPixmap has correct dimensions
        self.assertEqual(result.width(), 150)
        self.assertEqual(result.height(), 100)

    def test_numpy_to_pixmap_raises_error_for_wrong_dtype(self):
        """
        GIVEN: Non-8-bit numpy array
        WHEN: numpy_to_pixmap is called
        THEN: ValueError is raised
        """
        # GIVEN: 16-bit image
        image_16bit = np.ones((100, 100), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.numpy_to_pixmap(image_16bit)
        self.assertIn("Expected 8-bit image data", str(context.exception))

    # Tests for Information and Validation

    def test_get_preview_info_returns_complete_information(self):
        """
        GIVEN: Original and preview images
        WHEN: get_preview_info is called
        THEN: Complete processing information is returned
        """
        # GIVEN: Original and preview images
        original = np.ones((1000, 1500), dtype=np.uint16)
        preview = np.ones((200, 300), dtype=np.uint8)
        
        # WHEN: Getting preview info
        result = self.manager.get_preview_info(original, preview)
        
        # THEN: Complete information is returned
        self.assertEqual(result['original_size'], (1500, 1000))
        self.assertEqual(result['preview_size'], (300, 200))
        self.assertEqual(result['scale_factor'], 0.2)
        self.assertEqual(result['data_type_conversion'], "uint16 → uint8")
        self.assertTrue(result['processing_applied'])
        self.assertEqual(result['optimization'], 'speed-optimized')

    def test_get_preview_info_handles_none_images(self):
        """
        GIVEN: None images
        WHEN: get_preview_info is called
        THEN: Information indicates no processing
        """
        # GIVEN: None images
        # WHEN: Getting preview info
        result = self.manager.get_preview_info(None, None)
        
        # THEN: Information indicates no processing
        self.assertIsNone(result['original_size'])
        self.assertIsNone(result['preview_size'])
        self.assertFalse(result['processing_applied'])

    def test_validate_preview_readiness_accepts_valid_image(self):
        """
        GIVEN: Valid image data
        WHEN: validate_preview_readiness is called
        THEN: Validation passes with no warnings
        """
        # GIVEN: Valid test image
        valid_image = np.ones((1000, 1500), dtype=np.uint16)
        
        # WHEN: Validating preview readiness
        result = self.manager.validate_preview_readiness(valid_image)
        
        # THEN: Validation passes
        self.assertTrue(result['ready'])
        self.assertEqual(len(result['warnings']), 0)

    def test_validate_preview_readiness_warns_about_large_images(self):
        """
        GIVEN: Very large image
        WHEN: validate_preview_readiness is called
        THEN: Validation passes but includes size warning
        """
        # GIVEN: Large test image
        large_image = np.ones((5000, 6000), dtype=np.uint16)
        
        # WHEN: Validating preview readiness
        result = self.manager.validate_preview_readiness(large_image)
        
        # THEN: Validation passes with recommendation
        self.assertTrue(result['ready'])
        self.assertTrue(len(result['recommendations']) > 0)
        self.assertIn("significantly downscaled", result['recommendations'][0])

    def test_validate_preview_readiness_warns_about_small_images(self):
        """
        GIVEN: Very small image
        WHEN: validate_preview_readiness is called
        THEN: Validation passes but includes quality warning
        """
        # GIVEN: Small test image
        small_image = np.ones((50, 80), dtype=np.uint16)
        
        # WHEN: Validating preview readiness
        result = self.manager.validate_preview_readiness(small_image)
        
        # THEN: Validation passes with warning
        self.assertTrue(result['ready'])
        self.assertTrue(len(result['warnings']) > 0)
        self.assertIn("preview quality may be poor", result['warnings'][0])

    def test_validate_preview_readiness_rejects_none_image(self):
        """
        GIVEN: None image data
        WHEN: validate_preview_readiness is called
        THEN: Validation fails with appropriate warning
        """
        # GIVEN: None image
        # WHEN: Validating preview readiness
        result = self.manager.validate_preview_readiness(None)
        
        # THEN: Validation fails
        self.assertFalse(result['ready'])
        self.assertIn("Image data is None", result['warnings'])

    def test_validate_preview_readiness_rejects_3d_image(self):
        """
        GIVEN: 3D image data
        WHEN: validate_preview_readiness is called
        THEN: Validation fails with appropriate warning
        """
        # GIVEN: 3D image
        image_3d = np.ones((100, 100, 3), dtype=np.uint8)
        
        # WHEN: Validating preview readiness
        result = self.manager.validate_preview_readiness(image_3d)
        
        # THEN: Validation fails
        self.assertFalse(result['ready'])
        self.assertIn("Expected 2D image, got 3D", result['warnings'])


if __name__ == '__main__':
    unittest.main()

