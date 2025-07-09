"""Tests for ImageDisplayManager class."""
import unittest
import numpy as np
from app.image_display_manager import ImageDisplayManager


class TestImageDisplayManager(unittest.TestCase):
    """Test cases for ImageDisplayManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ImageDisplayManager()
        
        # Create test image data
        self.valid_image = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.invalid_image_8bit = np.array([[100, 200], [150, 250]], dtype=np.uint8)
        self.invalid_image_3d = np.random.randint(0, 65535, (10, 10, 3), dtype=np.uint16)
    
    def test_validate_image_data_returns_true_when_given_valid_16bit_grayscale_image(self):
        """Test that image validation returns True for valid 16-bit grayscale images."""
        # GIVEN: A valid 16-bit grayscale numpy array
        manager = self.manager
        valid_image_data = self.valid_image
        
        # WHEN: We validate the image data
        result = manager.validate_image_data(valid_image_data)
        
        # THEN: Validation should return True
        self.assertTrue(result)
    
    def test_validate_image_data_returns_false_when_given_none_image(self):
        """Test that image validation returns False when given None."""
        # GIVEN: A None value instead of image data
        manager = self.manager
        none_image = None
        
        # WHEN: We validate the None value
        result = manager.validate_image_data(none_image)
        
        # THEN: Validation should return False
        self.assertFalse(result)
    
    def test_validate_image_data_returns_false_when_given_non_numpy_array(self):
        """Test that image validation returns False for non-numpy array types."""
        # GIVEN: A non-numpy array object (string)
        manager = self.manager
        invalid_type = "not an array"
        
        # WHEN: We validate the non-array object
        result = manager.validate_image_data(invalid_type)
        
        # THEN: Validation should return False
        self.assertFalse(result)
    
    def test_validate_image_data_returns_false_when_given_3d_image_array(self):
        """Test that image validation returns False for 3D (RGB) images."""
        # GIVEN: A 3D numpy array (RGB image)
        manager = self.manager
        three_dimensional_image = self.invalid_image_3d
        
        # WHEN: We validate the 3D image
        result = manager.validate_image_data(three_dimensional_image)
        
        # THEN: Validation should return False
        self.assertFalse(result)
    
    def test_validate_image_data_returns_false_when_given_8bit_image(self):
        """Test that image validation returns False for 8-bit images."""
        # GIVEN: An 8-bit numpy array (wrong data type)
        manager = self.manager
        eight_bit_image = self.invalid_image_8bit
        
        # WHEN: We validate the 8-bit image
        result = manager.validate_image_data(eight_bit_image)
        
        # THEN: Validation should return False
        self.assertFalse(result)
    
    def test_calculate_scaled_size_maintains_aspect_ratio_when_scaling_landscape_image(self):
        """Test that landscape image scaling maintains aspect ratio and fits container."""
        # GIVEN: A landscape image (16:9) and a container (4:3)
        manager = self.manager
        landscape_image_size = (1920, 1080)  # 16:9 landscape
        container_size = (800, 600)  # 4:3 container
        
        # WHEN: We calculate the scaled size
        result = manager.calculate_scaled_size(landscape_image_size, container_size)
        
        # THEN: Image should scale to fit width and maintain aspect ratio
        expected_height = int(1080 * (800 / 1920))
        self.assertEqual(result, (800, expected_height))
        
        # AND THEN: Aspect ratio should be preserved
        original_ratio = 1920 / 1080
        scaled_ratio = result[0] / result[1]
        self.assertAlmostEqual(original_ratio, scaled_ratio, places=2)
    
    def test_calculate_scaled_size_maintains_aspect_ratio_when_scaling_portrait_image(self):
        """Test that portrait image scaling maintains aspect ratio and fits container."""
        # GIVEN: A portrait image (9:16) and a container (4:3)
        manager = self.manager
        portrait_image_size = (1080, 1920)  # 9:16 portrait
        container_size = (800, 600)  # 4:3 container
        
        # WHEN: We calculate the scaled size
        result = manager.calculate_scaled_size(portrait_image_size, container_size)
        
        # THEN: Image should scale to fit height and maintain aspect ratio
        expected_width = int(1080 * (600 / 1920))
        self.assertEqual(result, (expected_width, 600))
        
        # AND THEN: Aspect ratio should be preserved
        original_ratio = 1080 / 1920
        scaled_ratio = result[0] / result[1]
        self.assertAlmostEqual(original_ratio, scaled_ratio, places=2)
    
    def test_calculate_scaled_size_returns_zero_when_given_zero_dimensions(self):
        """Test that scaling calculation handles zero dimensions gracefully."""
        # GIVEN: Image sizes with zero dimensions
        manager = self.manager
        container_size = (800, 600)
        
        # WHEN: We calculate scaled size for zero width image
        result_zero_width = manager.calculate_scaled_size((0, 100), container_size)
        
        # THEN: Result should be (0, 0)
        self.assertEqual(result_zero_width, (0, 0))
        
        # AND WHEN: We calculate scaled size for zero height image
        result_zero_height = manager.calculate_scaled_size((100, 0), container_size)
        
        # AND THEN: Result should be (0, 0)
        self.assertEqual(result_zero_height, (0, 0))
    
    def test_calculate_scaled_size_returns_same_size_when_image_exactly_fits_container(self):
        """Test that scaling returns original size when image exactly fits container."""
        # GIVEN: An image that exactly matches the container size
        manager = self.manager
        image_size = (800, 600)
        container_size = (800, 600)
        
        # WHEN: We calculate the scaled size
        result = manager.calculate_scaled_size(image_size, container_size)
        
        # THEN: Result should be the same as the original size
        self.assertEqual(result, (800, 600))
    
    def test_prepare_image_for_qt_display_returns_correct_parameters_when_given_valid_image(self):
        """Test that Qt display preparation returns correct parameters for valid images."""
        # GIVEN: A valid 16-bit grayscale image
        manager = self.manager
        valid_image = self.valid_image
        
        # WHEN: We prepare the image for Qt display
        display_array, width, height, bytes_per_line = manager.prepare_image_for_qt_display(valid_image)
        
        # THEN: All parameters should be correct
        self.assertEqual(width, 2)
        self.assertEqual(height, 2)
        self.assertEqual(bytes_per_line, 4)  # width * 2 for 16-bit
        self.assertTrue(display_array.flags['C_CONTIGUOUS'])
        
        # AND THEN: Display array should match the original image
        np.testing.assert_array_equal(display_array, valid_image)
    
    def test_prepare_image_for_qt_display_raises_value_error_when_given_invalid_image(self):
        """Test that Qt display preparation raises ValueError for invalid images."""
        # GIVEN: Invalid image data (None and 8-bit image)
        manager = self.manager
        none_image = None
        eight_bit_image = self.invalid_image_8bit
        
        # WHEN: We attempt to prepare None for Qt display
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError):
            manager.prepare_image_for_qt_display(none_image)
        
        # AND WHEN: We attempt to prepare 8-bit image for Qt display
        # AND THEN: A ValueError should be raised
        with self.assertRaises(ValueError):
            manager.prepare_image_for_qt_display(eight_bit_image)
    
    def test_calculate_display_info_returns_valid_info_when_given_valid_image(self):
        """Test that display info calculation returns valid information for valid images."""
        # GIVEN: A valid image and container size
        manager = self.manager
        valid_image = self.valid_image
        container_size = (800, 600)
        
        # WHEN: We calculate display information
        result = manager.calculate_display_info(valid_image, container_size)
        
        # THEN: Result should indicate valid image with correct properties
        self.assertTrue(result['is_valid'])
        self.assertFalse(result['show_placeholder'])
        self.assertEqual(result['placeholder_text'], "")
        self.assertEqual(result['image_size'], (2, 2))
        self.assertIsNotNone(result['display_data'])
        self.assertIsNotNone(result['qt_params'])
    
    def test_calculate_display_info_returns_placeholder_info_when_given_invalid_image(self):
        """Test that display info calculation returns placeholder information for invalid images."""
        # GIVEN: An invalid image (None) and container size
        manager = self.manager
        invalid_image = None
        container_size = (800, 600)
        
        # WHEN: We calculate display information
        result = manager.calculate_display_info(invalid_image, container_size)
        
        # THEN: Result should indicate invalid image with placeholder information
        self.assertFalse(result['is_valid'])
        self.assertTrue(result['show_placeholder'])
        self.assertEqual(result['placeholder_text'], "No Image Loaded")
        self.assertEqual(result['image_size'], (0, 0))
        self.assertIsNone(result['display_data'])
    
    def test_get_aspect_ratio_calculates_correctly_for_various_dimensions(self):
        """Test that aspect ratio calculation works correctly for various image dimensions."""
        # GIVEN: An ImageDisplayManager and various image dimensions
        manager = self.manager
        
        # WHEN: We calculate aspect ratios for different dimensions
        landscape_ratio = manager.get_aspect_ratio((1920, 1080))
        portrait_ratio = manager.get_aspect_ratio((1080, 1920))
        zero_height_ratio = manager.get_aspect_ratio((100, 0))
        
        # THEN: Aspect ratios should be calculated correctly
        self.assertAlmostEqual(landscape_ratio, 16/9, places=2)
        self.assertAlmostEqual(portrait_ratio, 9/16, places=2)
        self.assertEqual(zero_height_ratio, 0.0)
    
    def test_is_landscape_detects_orientation_correctly_for_various_dimensions(self):
        """Test that landscape orientation detection works correctly."""
        # GIVEN: An ImageDisplayManager and various image dimensions
        manager = self.manager
        
        # WHEN: We check orientation for different dimensions
        landscape_result = manager.is_landscape((1920, 1080))
        portrait_result = manager.is_landscape((1080, 1920))
        square_result = manager.is_landscape((1000, 1000))
        
        # THEN: Orientation should be detected correctly
        self.assertTrue(landscape_result)
        self.assertFalse(portrait_result)
        self.assertFalse(square_result)  # Square is not landscape
    
    def test_calculate_letterbox_padding_returns_correct_padding_when_image_smaller_than_container(self):
        """Test that letterbox padding calculation works correctly when image is smaller."""
        # GIVEN: An image smaller than the container
        manager = self.manager
        image_size = (400, 300)
        container_size = (800, 600)
        
        # WHEN: We calculate letterbox padding
        h_padding, v_padding = manager.calculate_letterbox_padding(image_size, container_size)
        
        # THEN: Padding should be calculated correctly
        self.assertEqual(h_padding, 200)  # (800 - 400) / 2
        self.assertEqual(v_padding, 150)  # (600 - 300) / 2
    
    def test_calculate_letterbox_padding_returns_zero_when_image_matches_container_size(self):
        """Test that letterbox padding returns zero when image matches container size."""
        # GIVEN: An image that exactly matches the container size
        manager = self.manager
        image_size = (800, 600)
        container_size = (800, 600)
        
        # WHEN: We calculate letterbox padding
        h_padding, v_padding = manager.calculate_letterbox_padding(image_size, container_size)
        
        # THEN: No padding should be needed
        self.assertEqual(h_padding, 0)
        self.assertEqual(v_padding, 0)
    
    def test_calculate_letterbox_padding_returns_zero_when_image_larger_than_container(self):
        """Test that letterbox padding handles edge case when image is larger than container."""
        # GIVEN: An image larger than the container (edge case)
        manager = self.manager
        image_size = (1000, 800)
        container_size = (800, 600)
        
        # WHEN: We calculate letterbox padding
        h_padding, v_padding = manager.calculate_letterbox_padding(image_size, container_size)
        
        # THEN: Should return zero padding (no negative padding)
        self.assertEqual(h_padding, 0)
        self.assertEqual(v_padding, 0)


if __name__ == '__main__':
    unittest.main()


    # Tests for 8K Display Optimization Methods
    
    def test_pad_image_for_8k_display_creates_correct_dimensions(self):
        """Test that padding creates image with exact 8K dimensions."""
        # GIVEN: A small test image
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (1000, 1500), dtype=np.uint16)
        
        # WHEN: We pad the image for 8K display
        result = manager.pad_image_for_8k_display(test_image)
        
        # THEN: Result should have exact 8K dimensions
        self.assertEqual(result.shape, (4320, 7680))
        self.assertEqual(result.dtype, np.uint16)
    
    def test_pad_image_for_8k_display_centers_image_correctly(self):
        """Test that padding centers the image correctly."""
        # GIVEN: A small test image with known values
        manager = self.manager
        test_image = np.full((100, 200), 30000, dtype=np.uint16)
        
        # WHEN: We pad the image with centering
        result = manager.pad_image_for_8k_display(test_image, center_image=True)
        
        # THEN: Image should be centered with white borders
        # Calculate expected center position
        expected_y_start = (4320 - 100) // 2
        expected_x_start = (7680 - 200) // 2
        
        # Check that the original image is in the center
        center_region = result[expected_y_start:expected_y_start+100, 
                             expected_x_start:expected_x_start+200]
        np.testing.assert_array_equal(center_region, test_image)
        
        # Check that borders are white (65535 for 16-bit)
        self.assertEqual(result[0, 0], 65535)  # Top-left corner
        self.assertEqual(result[-1, -1], 65535)  # Bottom-right corner
    
    def test_pad_image_for_8k_display_scales_down_oversized_images(self):
        """Test that padding scales down images larger than 8K display."""
        # GIVEN: An image larger than 8K display
        manager = self.manager
        large_image = np.random.randint(1000, 5000, (5000, 8000), dtype=np.uint16)
        
        # WHEN: We pad the oversized image
        result = manager.pad_image_for_8k_display(large_image)
        
        # THEN: Result should still be 8K dimensions
        self.assertEqual(result.shape, (4320, 7680))
        # And should contain scaled-down version of original
        self.assertNotEqual(np.sum(result == 65535), result.size)  # Not all white
    
    def test_pad_image_for_8k_display_rejects_non_white_borders(self):
        """Test that padding rejects non-white border colors."""
        # GIVEN: A test image and invalid border color
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (100, 200), dtype=np.uint16)
        
        # WHEN: We attempt to use non-white border
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            manager.pad_image_for_8k_display(test_image, border_color="black")
        
        self.assertIn("Only white borders are supported", str(context.exception))
    
    def test_prepare_image_for_8k_display_combines_operations_correctly(self):
        """Test that the complete preparation pipeline works correctly."""
        # GIVEN: A test image and processing options
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (1000, 3000), dtype=np.uint16)
        
        # WHEN: We prepare the image with squashing enabled
        result = manager.prepare_image_for_8k_display(
            test_image
        )
        
        # THEN: Result should be 8K dimensions and properly processed
        self.assertEqual(result.shape, (4320, 7680))
        self.assertEqual(result.dtype, np.uint16)
        # Should contain both original data and white borders
        unique_values = np.unique(result)
        self.assertIn(65535, unique_values)  # White borders present
        self.assertTrue(len(unique_values) > 1)  # Not all white
    
    def test_prepare_image_for_8k_display_without_squashing(self):
        """Test that preparation works correctly without squashing."""
        # GIVEN: A test image with squashing disabled
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (500, 800), dtype=np.uint16)
        
        # WHEN: We prepare the image without squashing
        result = manager.prepare_image_for_8k_display(
            test_image
        )
        
        # THEN: Result should be 8K dimensions with original image preserved
        self.assertEqual(result.shape, (4320, 7680))
        # Original image should be findable in the result (centered)
        y_start = (4320 - 500) // 2
        x_start = (7680 - 800) // 2
        extracted_region = result[y_start:y_start+500, x_start:x_start+800]
        np.testing.assert_array_equal(extracted_region, test_image)
    
    def test_calculate_8k_display_info_provides_accurate_information(self):
        """Test that 8K display info calculation provides accurate details."""
        # GIVEN: A test image with known dimensions
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (1000, 2000), dtype=np.uint16)
        
        # WHEN: We calculate 8K display info with squashing
        result = manager.calculate_8k_display_info(
            test_image
        )
        
        # THEN: Information should be accurate
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['original_size'], (2000, 1000))
        self.assertEqual(result['squashed_size'], (2000 // 3, 1000))
        self.assertEqual(result['final_size'], (7680, 4320))
        self.assertTrue(result['compression_applied'])
        self.assertEqual(result['compression_ratio'], 3)
        self.assertGreater(result['memory_usage_mb'], 0)
    
    def test_calculate_8k_display_info_handles_invalid_image(self):
        """Test that 8K display info calculation handles invalid images."""
        # GIVEN: Invalid image data
        manager = self.manager
        invalid_image = None
        
        # WHEN: We calculate display info for invalid image
        result = manager.calculate_8k_display_info(invalid_image)
        
        # THEN: Result should indicate invalid state
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['original_size'], (0, 0))
        self.assertEqual(result['final_size'], (7680, 4320))
    
    def test_validate_8k_display_readiness_identifies_issues_and_recommendations(self):
        """Test that display readiness validation provides useful feedback."""
        # GIVEN: A test image that might have issues
        manager = self.manager
        large_image = np.random.randint(1000, 5000, (10000, 20000), dtype=np.uint16)
        
        # WHEN: We validate display readiness
        result = manager.validate_8k_display_readiness(large_image)
        
        # THEN: Should provide warnings and recommendations
        self.assertTrue(result['is_ready'])
        self.assertGreater(len(result['warnings']), 0)
        self.assertIn('info', result)
        self.assertEqual(result['info']['dimensions'], (20000, 10000))
    
    def test_validate_8k_display_readiness_handles_small_images(self):
        """Test that validation provides appropriate feedback for small images."""
        # GIVEN: A very small test image
        manager = self.manager
        small_image = np.random.randint(1000, 5000, (100, 200), dtype=np.uint16)
        
        # WHEN: We validate display readiness
        result = manager.validate_8k_display_readiness(small_image)
        
        # THEN: Should warn about small size
        self.assertTrue(result['is_ready'])
        warning_text = ' '.join(result['warnings'])
        self.assertIn('small', warning_text.lower())
    
    def test_8k_display_constants_are_correct(self):
        """Test that 8K display constants are set correctly."""
        # GIVEN: The ImageDisplayManager class
        manager = self.manager
        
        # WHEN: We check the 8K display constants
        # THEN: They should match 8K UHD specifications
        self.assertEqual(manager.DISPLAY_8K_WIDTH, 7680)
        self.assertEqual(manager.DISPLAY_8K_HEIGHT, 4320)
        self.assertEqual(manager.DISPLAY_8K_SIZE, (7680, 4320))



if __name__ == '__main__':
    unittest.main()

