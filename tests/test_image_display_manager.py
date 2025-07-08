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
    
    def test_validate_image_data_valid(self):
        """Test validation with valid 16-bit grayscale image."""
        result = self.manager.validate_image_data(self.valid_image)
        self.assertTrue(result)
    
    def test_validate_image_data_none(self):
        """Test validation with None image."""
        result = self.manager.validate_image_data(None)
        self.assertFalse(result)
    
    def test_validate_image_data_wrong_type(self):
        """Test validation with non-numpy array."""
        result = self.manager.validate_image_data("not an array")
        self.assertFalse(result)
    
    def test_validate_image_data_wrong_dimensions(self):
        """Test validation with 3D image."""
        result = self.manager.validate_image_data(self.invalid_image_3d)
        self.assertFalse(result)
    
    def test_validate_image_data_wrong_dtype(self):
        """Test validation with 8-bit image."""
        result = self.manager.validate_image_data(self.invalid_image_8bit)
        self.assertFalse(result)
    
    def test_calculate_scaled_size_landscape_image(self):
        """Test scaling calculation for landscape image."""
        image_size = (1920, 1080)  # 16:9 landscape
        container_size = (800, 600)  # 4:3 container
        
        result = self.manager.calculate_scaled_size(image_size, container_size)
        
        # Should scale to fit width (800) and maintain aspect ratio
        expected_height = int(1080 * (800 / 1920))
        self.assertEqual(result, (800, expected_height))
    
    def test_calculate_scaled_size_portrait_image(self):
        """Test scaling calculation for portrait image."""
        image_size = (1080, 1920)  # 9:16 portrait
        container_size = (800, 600)  # 4:3 container
        
        result = self.manager.calculate_scaled_size(image_size, container_size)
        
        # Should scale to fit height (600) and maintain aspect ratio
        expected_width = int(1080 * (600 / 1920))
        self.assertEqual(result, (expected_width, 600))
    
    def test_calculate_scaled_size_zero_dimensions(self):
        """Test scaling calculation with zero dimensions."""
        result = self.manager.calculate_scaled_size((0, 100), (800, 600))
        self.assertEqual(result, (0, 0))
        
        result = self.manager.calculate_scaled_size((100, 0), (800, 600))
        self.assertEqual(result, (0, 0))
    
    def test_calculate_scaled_size_exact_fit(self):
        """Test scaling when image exactly fits container."""
        image_size = (800, 600)
        container_size = (800, 600)
        
        result = self.manager.calculate_scaled_size(image_size, container_size)
        self.assertEqual(result, (800, 600))
    
    def test_prepare_image_for_qt_display_valid(self):
        """Test Qt display preparation with valid image."""
        display_array, width, height, bytes_per_line = self.manager.prepare_image_for_qt_display(self.valid_image)
        
        self.assertEqual(width, 2)
        self.assertEqual(height, 2)
        self.assertEqual(bytes_per_line, 4)  # width * 2 for 16-bit
        self.assertTrue(display_array.flags['C_CONTIGUOUS'])
        np.testing.assert_array_equal(display_array, self.valid_image)
    
    def test_prepare_image_for_qt_display_invalid(self):
        """Test Qt display preparation with invalid image."""
        with self.assertRaises(ValueError):
            self.manager.prepare_image_for_qt_display(None)
        
        with self.assertRaises(ValueError):
            self.manager.prepare_image_for_qt_display(self.invalid_image_8bit)
    
    def test_calculate_display_info_valid_image(self):
        """Test display info calculation with valid image."""
        container_size = (800, 600)
        result = self.manager.calculate_display_info(self.valid_image, container_size)
        
        self.assertTrue(result['is_valid'])
        self.assertFalse(result['show_placeholder'])
        self.assertEqual(result['placeholder_text'], "")
        self.assertEqual(result['image_size'], (2, 2))
        self.assertIsNotNone(result['display_data'])
        self.assertIsNotNone(result['qt_params'])
    
    def test_calculate_display_info_invalid_image(self):
        """Test display info calculation with invalid image."""
        container_size = (800, 600)
        result = self.manager.calculate_display_info(None, container_size)
        
        self.assertFalse(result['is_valid'])
        self.assertTrue(result['show_placeholder'])
        self.assertEqual(result['placeholder_text'], "No Image Loaded")
        self.assertEqual(result['image_size'], (0, 0))
        self.assertIsNone(result['display_data'])
    
    def test_get_aspect_ratio(self):
        """Test aspect ratio calculation."""
        self.assertAlmostEqual(self.manager.get_aspect_ratio((1920, 1080)), 16/9, places=2)
        self.assertAlmostEqual(self.manager.get_aspect_ratio((1080, 1920)), 9/16, places=2)
        self.assertEqual(self.manager.get_aspect_ratio((100, 0)), 0.0)
    
    def test_is_landscape(self):
        """Test landscape orientation detection."""
        self.assertTrue(self.manager.is_landscape((1920, 1080)))
        self.assertFalse(self.manager.is_landscape((1080, 1920)))
        self.assertFalse(self.manager.is_landscape((1000, 1000)))  # Square
    
    def test_calculate_letterbox_padding(self):
        """Test letterbox padding calculation."""
        # Image smaller than container
        image_size = (400, 300)
        container_size = (800, 600)
        
        h_padding, v_padding = self.manager.calculate_letterbox_padding(image_size, container_size)
        
        self.assertEqual(h_padding, 200)  # (800 - 400) / 2
        self.assertEqual(v_padding, 150)  # (600 - 300) / 2
    
    def test_calculate_letterbox_padding_no_padding_needed(self):
        """Test letterbox padding when no padding is needed."""
        # Image same size as container
        image_size = (800, 600)
        container_size = (800, 600)
        
        h_padding, v_padding = self.manager.calculate_letterbox_padding(image_size, container_size)
        
        self.assertEqual(h_padding, 0)
        self.assertEqual(v_padding, 0)
    
    def test_calculate_letterbox_padding_image_larger(self):
        """Test letterbox padding when image is larger than container."""
        # This shouldn't happen in normal usage, but test edge case
        image_size = (1000, 800)
        container_size = (800, 600)
        
        h_padding, v_padding = self.manager.calculate_letterbox_padding(image_size, container_size)
        
        # Should return 0 when image is larger
        self.assertEqual(h_padding, 0)
        self.assertEqual(v_padding, 0)


if __name__ == '__main__':
    unittest.main()

