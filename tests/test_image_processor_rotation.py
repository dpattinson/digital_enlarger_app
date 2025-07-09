"""Tests for portrait rotation functionality in ImageProcessor."""
import unittest
import numpy as np
import cv2
from unittest.mock import patch, MagicMock
from app.image_processor import ImageProcessor


class TestImageProcessorRotation(unittest.TestCase):
    """Test cases for portrait rotation functionality using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.processor = ImageProcessor()

    # Portrait Detection Tests

    def test_is_portrait_orientation_returns_true_when_given_portrait_image(self):
        """
        GIVEN: A portrait image (height > width)
        WHEN: is_portrait_orientation is called
        THEN: Returns True
        """
        # GIVEN: Portrait image (800x1200)
        portrait_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
        
        # WHEN: Checking orientation
        result = self.processor.is_portrait_orientation(portrait_image)
        
        # THEN: Should return True
        self.assertTrue(result)

    def test_is_portrait_orientation_returns_false_when_given_landscape_image(self):
        """
        GIVEN: A landscape image (width > height)
        WHEN: is_portrait_orientation is called
        THEN: Returns False
        """
        # GIVEN: Landscape image (1200x800)
        landscape_image = np.random.randint(0, 65535, (800, 1200), dtype=np.uint16)
        
        # WHEN: Checking orientation
        result = self.processor.is_portrait_orientation(landscape_image)
        
        # THEN: Should return False
        self.assertFalse(result)

    def test_is_portrait_orientation_returns_false_when_given_square_image(self):
        """
        GIVEN: A square image (height == width)
        WHEN: is_portrait_orientation is called
        THEN: Returns False
        """
        # GIVEN: Square image (1000x1000)
        square_image = np.random.randint(0, 65535, (1000, 1000), dtype=np.uint16)
        
        # WHEN: Checking orientation
        result = self.processor.is_portrait_orientation(square_image)
        
        # THEN: Should return False
        self.assertFalse(result)

    def test_is_portrait_orientation_returns_false_when_given_none_image(self):
        """
        GIVEN: None image data
        WHEN: is_portrait_orientation is called
        THEN: Returns False
        """
        # GIVEN: None image
        none_image = None
        
        # WHEN: Checking orientation
        result = self.processor.is_portrait_orientation(none_image)
        
        # THEN: Should return False
        self.assertFalse(result)

    def test_is_portrait_orientation_returns_false_when_given_3d_image(self):
        """
        GIVEN: A 3D image array
        WHEN: is_portrait_orientation is called
        THEN: Returns False
        """
        # GIVEN: 3D image (color image)
        color_image = np.random.randint(0, 255, (800, 1200, 3), dtype=np.uint8)
        
        # WHEN: Checking orientation
        result = self.processor.is_portrait_orientation(color_image)
        
        # THEN: Should return False
        self.assertFalse(result)

    # Rotation Tests

    def test_rotate_image_clockwise_90_transforms_portrait_to_landscape(self):
        """
        GIVEN: A portrait image
        WHEN: rotate_image_clockwise_90 is called
        THEN: Returns landscape image with swapped dimensions
        """
        # GIVEN: Portrait image (800x1200)
        portrait_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
        original_height, original_width = portrait_image.shape
        
        # WHEN: Rotating 90 degrees clockwise
        rotated_image = self.processor.rotate_image_clockwise_90(portrait_image)
        
        # THEN: Dimensions should be swapped (landscape)
        rotated_height, rotated_width = rotated_image.shape
        self.assertEqual(rotated_height, original_width)
        self.assertEqual(rotated_width, original_height)
        self.assertFalse(self.processor.is_portrait_orientation(rotated_image))

    def test_rotate_image_clockwise_90_preserves_data_type(self):
        """
        GIVEN: A 16-bit portrait image
        WHEN: rotate_image_clockwise_90 is called
        THEN: Returns image with same data type
        """
        # GIVEN: 16-bit portrait image
        portrait_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
        
        # WHEN: Rotating image
        rotated_image = self.processor.rotate_image_clockwise_90(portrait_image)
        
        # THEN: Data type should be preserved
        self.assertEqual(rotated_image.dtype, np.uint16)

    def test_rotate_image_clockwise_90_raises_error_when_given_none_image(self):
        """
        GIVEN: None image data
        WHEN: rotate_image_clockwise_90 is called
        THEN: Raises ValueError
        """
        # GIVEN: None image
        none_image = None
        
        # WHEN & THEN: Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.processor.rotate_image_clockwise_90(none_image)
        
        self.assertIn("Cannot rotate None image", str(context.exception))

    def test_rotate_image_clockwise_90_raises_error_when_given_3d_image(self):
        """
        GIVEN: A 3D image array
        WHEN: rotate_image_clockwise_90 is called
        THEN: Raises ValueError
        """
        # GIVEN: 3D image
        color_image = np.random.randint(0, 255, (800, 1200, 3), dtype=np.uint8)
        
        # WHEN & THEN: Should raise ValueError
        with self.assertRaises(ValueError) as context:
            self.processor.rotate_image_clockwise_90(color_image)
        
        self.assertIn("Can only rotate 2D grayscale images", str(context.exception))

    # Rotation Info Tests

    def test_get_rotation_info_provides_accurate_information(self):
        """
        GIVEN: Original and rotated images
        WHEN: get_rotation_info is called
        THEN: Returns accurate rotation information
        """
        # GIVEN: Original portrait image and its rotation
        original_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
        rotated_image = self.processor.rotate_image_clockwise_90(original_image)
        
        # WHEN: Getting rotation info
        info = self.processor.get_rotation_info(original_image, rotated_image)
        
        # THEN: Should provide accurate information
        self.assertTrue(info['rotation_applied'])
        self.assertEqual(info['rotation_angle'], 90)
        self.assertEqual(info['original_size'], (800, 1200))  # (width, height)
        self.assertEqual(info['rotated_size'], (1200, 800))   # (width, height)
        self.assertEqual(info['original_orientation'], 'portrait')
        self.assertEqual(info['final_orientation'], 'landscape')

    def test_get_rotation_info_returns_none_when_given_none_images(self):
        """
        GIVEN: None images
        WHEN: get_rotation_info is called
        THEN: Returns None
        """
        # GIVEN: None images
        original_image = None
        rotated_image = None
        
        # WHEN: Getting rotation info
        info = self.processor.get_rotation_info(original_image, rotated_image)
        
        # THEN: Should return None
        self.assertIsNone(info)

    # Integration Tests

    @patch('os.path.exists')
    @patch('cv2.imread')
    def test_load_image_automatically_rotates_portrait_images(self, mock_imread, mock_exists):
        """
        GIVEN: A portrait TIFF image file
        WHEN: load_image is called
        THEN: Returns landscape-oriented image
        """
        # GIVEN: Mock file system and portrait image
        mock_exists.return_value = True
        portrait_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
        mock_imread.return_value = portrait_image
        
        processor = ImageProcessor(file_checker=mock_exists, cv2_reader=mock_imread)
        
        # WHEN: Loading image
        result = processor.load_image("test_portrait.tif")
        
        # THEN: Should return landscape image
        self.assertFalse(processor.is_portrait_orientation(result))
        self.assertEqual(result.shape, (800, 1200))  # Rotated dimensions

    @patch('os.path.exists')
    @patch('cv2.imread')
    def test_load_image_does_not_rotate_landscape_images(self, mock_imread, mock_exists):
        """
        GIVEN: A landscape TIFF image file
        WHEN: load_image is called
        THEN: Returns image unchanged
        """
        # GIVEN: Mock file system and landscape image
        mock_exists.return_value = True
        landscape_image = np.random.randint(0, 65535, (800, 1200), dtype=np.uint16)
        mock_imread.return_value = landscape_image
        
        processor = ImageProcessor(file_checker=mock_exists, cv2_reader=mock_imread)
        
        # WHEN: Loading image
        result = processor.load_image("test_landscape.tif")
        
        # THEN: Should return unchanged image
        self.assertEqual(result.shape, (800, 1200))  # Original dimensions
        np.testing.assert_array_equal(result, landscape_image)

    @patch('os.path.exists')
    @patch('cv2.imread')
    def test_load_image_does_not_rotate_square_images(self, mock_imread, mock_exists):
        """
        GIVEN: A square TIFF image file
        WHEN: load_image is called
        THEN: Returns image unchanged
        """
        # GIVEN: Mock file system and square image
        mock_exists.return_value = True
        square_image = np.random.randint(0, 65535, (1000, 1000), dtype=np.uint16)
        mock_imread.return_value = square_image
        
        processor = ImageProcessor(file_checker=mock_exists, cv2_reader=mock_imread)
        
        # WHEN: Loading image
        result = processor.load_image("test_square.tif")
        
        # THEN: Should return unchanged image
        self.assertEqual(result.shape, (1000, 1000))  # Original dimensions
        np.testing.assert_array_equal(result, square_image)

    def test_rotation_preserves_pixel_values_correctly(self):
        """
        GIVEN: A portrait image with known pixel pattern
        WHEN: rotate_image_clockwise_90 is called
        THEN: Pixel values are correctly repositioned
        """
        # GIVEN: Small portrait image with known pattern
        # Create a 3x2 image (height=3, width=2) with specific values
        portrait_image = np.array([
            [100, 200],
            [300, 400], 
            [500, 600]
        ], dtype=np.uint16)
        
        # WHEN: Rotating 90 degrees clockwise
        rotated_image = self.processor.rotate_image_clockwise_90(portrait_image)
        
        # THEN: Should be 2x3 with correctly rotated values
        expected_rotated = np.array([
            [500, 300, 100],
            [600, 400, 200]
        ], dtype=np.uint16)
        
        np.testing.assert_array_equal(rotated_image, expected_rotated)


if __name__ == '__main__':
    unittest.main()

