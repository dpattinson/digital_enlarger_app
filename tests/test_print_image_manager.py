"""Tests for PrintImageManager class.

This module contains unit tests for the PrintImageManager class,
focusing on high-quality print processing and 8K display preparation.
"""

import unittest
from unittest.mock import Mock, patch
import numpy as np

from app.print_image_manager import PrintImageManager


class TestPrintImageManager(unittest.TestCase):
    """Test cases for PrintImageManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.manager = PrintImageManager()

    # Tests for Print Image Preparation

    def test_prepare_print_image_complete_pipeline(self):
        """
        GIVEN: Valid image and LUT data
        WHEN: prepare_print_image is called
        THEN: Complete print processing pipeline is executed
        """
        # GIVEN: Test image and LUT
        test_image = np.ones((1000, 1500), dtype=np.uint16) * 1000
        test_lut = np.arange(65536, dtype=np.uint16).reshape(256, 256)
        
        # WHEN: Preparing print image
        result = self.manager.prepare_print_image(test_image, test_lut)
        
        # THEN: Result is 8K display ready
        self.assertEqual(result.shape, (4320, 7680))
        self.assertEqual(result.dtype, test_image.dtype)

    def test_prepare_print_image_with_squashing(self):
        """
        GIVEN: Valid image and LUT data with squashing enabled
        WHEN: prepare_print_image is called
        THEN: Image squashing is applied in the pipeline
        """
        # GIVEN: Test image and LUT
        test_image = np.ones((1000, 1500), dtype=np.uint16) * 1000
        test_lut = np.arange(65536, dtype=np.uint16).reshape(256, 256)
        
        # WHEN: Preparing print image with squashing
        result = self.manager.prepare_print_image(
            test_image, test_lut, apply_squashing=True, compression_ratio=3
        )
        
        # THEN: Result is 8K display ready with squashing applied
        self.assertEqual(result.shape, (4320, 7680))

    def test_prepare_print_image_raises_error_for_none_image(self):
        """
        GIVEN: None image data
        WHEN: prepare_print_image is called
        THEN: ValueError is raised
        """
        # GIVEN: None image and valid LUT
        test_lut = np.ones((256, 256), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.prepare_print_image(None, test_lut)
        self.assertIn("Cannot prepare print image for None image", str(context.exception))

    def test_prepare_print_image_raises_error_for_none_lut(self):
        """
        GIVEN: Valid image but None LUT
        WHEN: prepare_print_image is called
        THEN: ValueError is raised
        """
        # GIVEN: Valid image and None LUT
        test_image = np.ones((1000, 1500), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.prepare_print_image(test_image, None)
        self.assertIn("Cannot prepare print image without LUT data", str(context.exception))

    # Tests for LUT Application

    def test_apply_lut_processes_correctly(self):
        """
        GIVEN: Valid image and LUT data
        WHEN: apply_lut is called
        THEN: LUT is applied correctly using flattened lookup
        """
        # GIVEN: Simple test image and LUT
        test_image = np.array([[0, 255], [1000, 2000]], dtype=np.uint16)
        test_lut = np.arange(65536, dtype=np.uint16).reshape(256, 256)
        
        # WHEN: Applying LUT
        result = self.manager.apply_lut(test_image, test_lut)
        
        # THEN: LUT values are applied correctly
        self.assertEqual(result[0, 0], 0)      # LUT[0] = 0
        self.assertEqual(result[0, 1], 255)    # LUT[255] = 255
        self.assertEqual(result[1, 0], 1000)   # LUT[1000] = 1000
        self.assertEqual(result[1, 1], 2000)   # LUT[2000] = 2000

    def test_apply_lut_raises_error_for_none_inputs(self):
        """
        GIVEN: None image or LUT
        WHEN: apply_lut is called
        THEN: ValueError is raised
        """
        # GIVEN: Valid image and None LUT
        test_image = np.ones((100, 100), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.apply_lut(test_image, None)
        self.assertIn("Image and LUT cannot be None", str(context.exception))

    # Tests for Image Inversion

    @patch('cv2.bitwise_not')
    def test_invert_image_uses_opencv(self, mock_bitwise_not):
        """
        GIVEN: Valid image data
        WHEN: invert_image is called
        THEN: cv2.bitwise_not is used for inversion
        """
        # GIVEN: Test image and mock
        test_image = np.ones((100, 100), dtype=np.uint16) * 1000
        inverted_result = np.ones((100, 100), dtype=np.uint16) * 64535
        mock_bitwise_not.return_value = inverted_result
        
        manager = PrintImageManager(cv2_bitwise_not=mock_bitwise_not)
        
        # WHEN: Inverting image
        result = manager.invert_image(test_image)
        
        # THEN: cv2.bitwise_not was called
        mock_bitwise_not.assert_called_once_with(test_image)
        np.testing.assert_array_equal(result, inverted_result)

    def test_invert_image_raises_error_for_none(self):
        """
        GIVEN: None image data
        WHEN: invert_image is called
        THEN: ValueError is raised
        """
        # GIVEN: None image
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.invert_image(None)
        self.assertIn("Cannot invert None image", str(context.exception))

    # Tests for Image Squashing

    def test_squash_image_for_display_compresses_width(self):
        """
        GIVEN: Image with width divisible by compression ratio
        WHEN: squash_image_for_display is called
        THEN: Width is compressed while height remains unchanged
        """
        # GIVEN: Test image 100x300 (height x width)
        test_image = np.arange(30000, dtype=np.uint16).reshape(100, 300)
        
        # WHEN: Squashing with ratio 3
        result = self.manager.squash_image_for_display(test_image, compression_ratio=3)
        
        # THEN: Width is compressed, height unchanged
        self.assertEqual(result.shape, (100, 100))  # 300/3 = 100
        self.assertEqual(result.dtype, test_image.dtype)

    def test_squash_image_averages_pixels_correctly(self):
        """
        GIVEN: Image with known pixel values
        WHEN: squash_image_for_display is called
        THEN: Pixels are averaged correctly in compression windows
        """
        # GIVEN: Simple test pattern
        test_image = np.array([[100, 200, 300, 400, 500, 600]], dtype=np.uint16)
        
        # WHEN: Squashing with ratio 3
        result = self.manager.squash_image_for_display(test_image, compression_ratio=3)
        
        # THEN: Pixels are averaged correctly
        # First window: (100+200+300)/3 = 200
        # Second window: (400+500+600)/3 = 500
        expected = np.array([[200, 500]], dtype=np.uint16)
        np.testing.assert_array_equal(result, expected)

    def test_squash_image_raises_error_for_invalid_ratio(self):
        """
        GIVEN: Valid image but invalid compression ratio
        WHEN: squash_image_for_display is called
        THEN: ValueError is raised
        """
        # GIVEN: Valid image and invalid ratio
        test_image = np.ones((100, 100), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.squash_image_for_display(test_image, compression_ratio=0)
        self.assertIn("Compression ratio must be >= 1", str(context.exception))

    def test_squash_image_raises_error_for_too_narrow_image(self):
        """
        GIVEN: Image too narrow for compression ratio
        WHEN: squash_image_for_display is called
        THEN: ValueError is raised
        """
        # GIVEN: Very narrow image
        test_image = np.ones((100, 2), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.squash_image_for_display(test_image, compression_ratio=5)
        self.assertIn("Image too narrow", str(context.exception))

    # Tests for 8K Display Padding

    def test_pad_image_for_8k_display_centers_image(self):
        """
        GIVEN: Image smaller than 8K display
        WHEN: pad_image_for_8k_display is called
        THEN: Image is centered with white padding
        """
        # GIVEN: Small test image
        test_image = np.ones((1000, 1500), dtype=np.uint16) * 1000
        
        # WHEN: Padding for 8K display
        result = self.manager.pad_image_for_8k_display(test_image)
        
        # THEN: Result is 8K size with centered image
        self.assertEqual(result.shape, (4320, 7680))
        
        # Check that image is centered
        y_offset = (4320 - 1000) // 2
        x_offset = (7680 - 1500) // 2
        
        # Original image should be in the center
        np.testing.assert_array_equal(
            result[y_offset:y_offset + 1000, x_offset:x_offset + 1500],
            test_image
        )
        
        # Borders should be white (max value)
        self.assertEqual(result[0, 0], 65535)  # Top-left corner should be white

    def test_pad_image_for_8k_display_handles_different_dtypes(self):
        """
        GIVEN: Images with different data types
        WHEN: pad_image_for_8k_display is called
        THEN: Appropriate white value is used for each data type
        """
        # GIVEN: 8-bit test image
        test_image_8bit = np.ones((1000, 1500), dtype=np.uint8) * 100
        
        # WHEN: Padding 8-bit image
        result_8bit = self.manager.pad_image_for_8k_display(test_image_8bit)
        
        # THEN: White padding uses 8-bit max value
        self.assertEqual(result_8bit[0, 0], 255)  # 8-bit white
        
        # GIVEN: 16-bit test image
        test_image_16bit = np.ones((1000, 1500), dtype=np.uint16) * 1000
        
        # WHEN: Padding 16-bit image
        result_16bit = self.manager.pad_image_for_8k_display(test_image_16bit)
        
        # THEN: White padding uses 16-bit max value
        self.assertEqual(result_16bit[0, 0], 65535)  # 16-bit white

    def test_pad_image_raises_error_for_oversized_image(self):
        """
        GIVEN: Image larger than 8K display
        WHEN: pad_image_for_8k_display is called
        THEN: ValueError is raised
        """
        # GIVEN: Oversized image
        oversized_image = np.ones((5000, 8000), dtype=np.uint16)
        
        # WHEN & THEN: ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.manager.pad_image_for_8k_display(oversized_image)
        self.assertIn("exceeds 8K display dimensions", str(context.exception))

    # Tests for Frame Generation

    def test_emulate_12bit_to_8bit_frames_generates_correct_count(self):
        """
        GIVEN: 16-bit image data
        WHEN: emulate_12bit_to_8bit_frames is called
        THEN: Correct number of 8-bit frames is generated
        """
        # GIVEN: 16-bit test image
        test_image = np.ones((100, 100), dtype=np.uint16) * 1000
        
        # WHEN: Generating frames
        result = self.manager.emulate_12bit_to_8bit_frames(test_image)
        
        # THEN: 4 frames are generated
        self.assertEqual(len(result), 4)
        for frame in result:
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, (100, 100))

    def test_emulate_12bit_to_8bit_frames_bit_shifting(self):
        """
        GIVEN: 16-bit image with known values
        WHEN: emulate_12bit_to_8bit_frames is called
        THEN: Frames use correct bit shifting
        """
        # GIVEN: Test image with specific value
        test_image = np.full((2, 2), 1024, dtype=np.uint16)  # 1024 = 0x0400
        
        # WHEN: Generating frames
        result = self.manager.emulate_12bit_to_8bit_frames(test_image)
        
        # THEN: Frames have correct bit-shifted values
        # Frame 0: 1024 >> 0 = 1024 -> 8-bit = 255 (clamped)
        # Frame 1: 1024 >> 1 = 512 -> 8-bit = 255 (clamped)
        # Frame 2: 1024 >> 2 = 256 -> 8-bit = 255 (clamped)
        # Frame 3: 1024 >> 3 = 128 -> 8-bit = 128
        self.assertEqual(result[3][0, 0], 128)

    # Tests for Information and Validation

    def test_get_print_processing_info_returns_complete_information(self):
        """
        GIVEN: Original and processed images
        WHEN: get_print_processing_info is called
        THEN: Complete processing information is returned
        """
        # GIVEN: Original and processed images
        original = np.ones((1000, 1500), dtype=np.uint16)
        processed = np.ones((4320, 7680), dtype=np.uint16)
        
        # WHEN: Getting processing info
        result = self.manager.get_print_processing_info(original, processed)
        
        # THEN: Complete information is returned
        self.assertEqual(result['original_size'], (1500, 1000))
        self.assertEqual(result['processed_size'], (7680, 4320))
        self.assertEqual(result['display_dimensions'], (7680, 4320))
        self.assertTrue(result['processing_applied'])
        self.assertTrue(result['padded_for_8k'])

    def test_calculate_8k_display_info_provides_detailed_analysis(self):
        """
        GIVEN: Image data
        WHEN: calculate_8k_display_info is called
        THEN: Detailed display analysis is provided
        """
        # GIVEN: Test image
        test_image = np.ones((2000, 3000), dtype=np.uint16)
        
        # WHEN: Calculating display info
        result = self.manager.calculate_8k_display_info(test_image)
        
        # THEN: Detailed analysis is provided
        self.assertEqual(result['input_size'], (3000, 2000))
        self.assertEqual(result['display_size'], (7680, 4320))
        self.assertTrue(result['fits_without_scaling'])
        self.assertGreater(result['memory_increase_factor'], 1)

    def test_validate_print_readiness_accepts_valid_setup(self):
        """
        GIVEN: Valid image and LUT data
        WHEN: validate_print_readiness is called
        THEN: Validation passes
        """
        # GIVEN: Valid image and LUT
        valid_image = np.ones((2000, 3000), dtype=np.uint16)
        valid_lut = np.ones((256, 256), dtype=np.uint16)
        
        # WHEN: Validating print readiness
        result = self.manager.validate_print_readiness(valid_image, valid_lut)
        
        # THEN: Validation passes
        self.assertTrue(result['ready'])
        self.assertEqual(len(result['warnings']), 0)

    def test_validate_print_readiness_rejects_oversized_height(self):
        """
        GIVEN: Image with height exceeding display
        WHEN: validate_print_readiness is called
        THEN: Validation fails with height warning
        """
        # GIVEN: Image too tall for display
        oversized_image = np.ones((5000, 3000), dtype=np.uint16)
        
        # WHEN: Validating print readiness
        result = self.manager.validate_print_readiness(oversized_image)
        
        # THEN: Validation fails
        self.assertFalse(result['ready'])
        self.assertTrue(any("exceeds display height" in w for w in result['warnings']))

    def test_validate_print_readiness_warns_about_wide_images(self):
        """
        GIVEN: Image wider than display
        WHEN: validate_print_readiness is called
        THEN: Validation passes but warns about width
        """
        # GIVEN: Very wide image
        wide_image = np.ones((2000, 8000), dtype=np.uint16)
        
        # WHEN: Validating print readiness
        result = self.manager.validate_print_readiness(wide_image)
        
        # THEN: Validation passes with width warning
        self.assertTrue(result['ready'])
        self.assertTrue(any("consider squashing" in w for w in result['warnings']))


if __name__ == '__main__':
    unittest.main()

