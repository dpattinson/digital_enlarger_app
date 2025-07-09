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

