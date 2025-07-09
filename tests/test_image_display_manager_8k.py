"""Tests for 8K Display Optimization features in ImageDisplayManager class."""
import unittest
import numpy as np
from app.image_display_manager import ImageDisplayManager


class TestImageDisplayManager8K(unittest.TestCase):
    """Test cases for 8K Display Optimization features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ImageDisplayManager()
        
        # Create test image data
        self.valid_image = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.invalid_image_8bit = np.array([[100, 200], [150, 250]], dtype=np.uint8)
    
    def test_squash_image_for_display_compresses_width_by_specified_ratio(self):
        """Test that image squashing compresses width by the specified ratio."""
        # GIVEN: A valid image and compression ratio of 3
        manager = self.manager
        test_image = np.random.randint(1000, 5000, (100, 300), dtype=np.uint16)
        compression_ratio = 3
        
        # WHEN: We squash the image
        result = manager.squash_image_for_display(test_image, compression_ratio)
        
        # THEN: Width should be compressed by the ratio
        expected_width = 300 // 3
        self.assertEqual(result.shape[1], expected_width)
        self.assertEqual(result.shape[0], 100)  # Height unchanged
        self.assertEqual(result.dtype, np.uint16)
    
    def test_squash_image_for_display_raises_error_when_given_invalid_image(self):
        """Test that image squashing raises ValueError for invalid image data."""
        # GIVEN: Invalid image data (8-bit instead of 16-bit)
        manager = self.manager
        invalid_image = self.invalid_image_8bit
        
        # WHEN: We attempt to squash the invalid image
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            manager.squash_image_for_display(invalid_image)
        
        self.assertIn("Invalid image data", str(context.exception))
    
    def test_squash_image_for_display_handles_small_images_gracefully(self):
        """Test that image squashing handles very small images without errors."""
        # GIVEN: A very small image (width smaller than compression ratio)
        manager = self.manager
        small_image = np.array([[1000, 2000]], dtype=np.uint16)  # 1x2 image
        compression_ratio = 3
        
        # WHEN: We squash the small image
        result = manager.squash_image_for_display(small_image, compression_ratio)
        
        # THEN: Result should have minimum width of 1
        self.assertEqual(result.shape[1], 1)
        self.assertEqual(result.shape[0], 1)
    
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
            test_image, 
            apply_squashing=True, 
            compression_ratio=3
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
            test_image, 
            apply_squashing=False
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
            test_image, 
            apply_squashing=True, 
            compression_ratio=3
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

