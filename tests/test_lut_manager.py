import unittest
import numpy as np
import tifffile
import os
import tempfile
from unittest.mock import patch, mock_open
from app.lut_manager import LUTManager


class TestLUTManager(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.lut_manager = LUTManager(self.temp_dir)
        
        # Create a valid 256x256 16-bit LUT for testing
        self.valid_lut_data = np.zeros((256, 256), dtype=np.uint16)
        for i in range(256):
            self.valid_lut_data[i, :] = np.linspace(0, 65535, 256, dtype=np.uint16)
        
        self.valid_lut_path = os.path.join(self.temp_dir, "valid_lut.tif")
        tifffile.imwrite(self.valid_lut_path, self.valid_lut_data)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove all test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_init(self):
        """Test LUTManager initialization."""
        from unittest.mock import Mock
        
        # Mock dependencies for testing
        mock_file_checker = Mock(return_value=True)
        mock_dir_lister = Mock(return_value=['test.tif'])
        
        lut_manager = LUTManager("luts", file_checker=mock_file_checker, dir_lister=mock_dir_lister)
        self.assertEqual(lut_manager.lut_dir, "luts")
        
        # Test with custom directory
        custom_dir = "/custom/lut/dir"
        lut_manager = LUTManager(custom_dir, file_checker=mock_file_checker, dir_lister=mock_dir_lister)
        self.assertEqual(lut_manager.lut_dir, custom_dir)

    def test_load_lut_valid_file(self):
        """Test loading a valid LUT file."""
        loaded_lut = self.lut_manager.load_lut(self.valid_lut_path)
        
        # Check that LUT was loaded correctly
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)
        self.assertEqual(loaded_lut.shape, (256, 256))

    def test_load_lut_relative_path(self):
        """Test loading LUT with relative path."""
        # Create LUT in the lut_dir
        relative_lut_path = os.path.join(self.temp_dir, "relative_lut.tif")
        tifffile.imwrite(relative_lut_path, self.valid_lut_data)
        
        # Test with just filename (relative to lut_dir)
        loaded_lut = self.lut_manager.load_lut("relative_lut.tif")
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)

    def test_load_lut_file_not_found(self):
        """Test loading non-existent LUT file."""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tif")
        
        with self.assertRaises(FileNotFoundError) as context:
            self.lut_manager.load_lut(non_existent_path)
        
        self.assertIn("LUT file not found", str(context.exception))

    def test_load_lut_invalid_extension(self):
        """Test loading file with invalid extension."""
        from unittest.mock import Mock
        
        # Mock file_checker to return True (file exists)
        mock_file_checker = Mock(return_value=True)
        lut_manager = LUTManager(self.temp_dir, file_checker=mock_file_checker)
        
        invalid_path = "/fake/path/invalid.jpg"
        
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(invalid_path)
        
        self.assertIn("LUT file must be a TIFF file", str(context.exception))

    def test_load_lut_wrong_dtype(self):
        """Test loading LUT with wrong data type."""
        # Create 8-bit LUT (invalid)
        invalid_lut_data = np.zeros((256, 256), dtype=np.uint8)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_dtype.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        
        with self.assertRaises(ValueError) as context:
            self.lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 16-bit (uint16)", str(context.exception))

    def test_load_lut_wrong_dimensions(self):
        """Test loading LUT with wrong dimensions."""
        # Create 128x128 LUT (invalid size)
        invalid_lut_data = np.zeros((128, 128), dtype=np.uint16)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_size.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        
        with self.assertRaises(ValueError) as context:
            self.lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 256x256 pixels", str(context.exception))

    def test_load_lut_3d_array(self):
        """Test loading LUT with 3D array (RGB instead of grayscale)."""
        # Create 3D array (invalid)
        invalid_lut_data = np.zeros((256, 256, 3), dtype=np.uint16)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_3d.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        
        with self.assertRaises(ValueError) as context:
            self.lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 256x256 pixels", str(context.exception))

    @patch('tifffile.imread')
    def test_load_lut_read_error(self, mock_imread):
        """Test handling of TIFF read errors."""
        mock_imread.side_effect = Exception("TIFF read error")
        
        with self.assertRaises(ValueError) as context:
            self.lut_manager.load_lut(self.valid_lut_path)
        
        self.assertIn("Failed to read TIFF LUT file", str(context.exception))

    def test_load_lut_edge_case_values(self):
        """Test LUT with edge case values (min/max)."""
        # Create LUT with extreme values
        edge_lut_data = np.zeros((256, 256), dtype=np.uint16)
        edge_lut_data[0, :] = 0  # Minimum values
        edge_lut_data[255, :] = 65535  # Maximum values
        edge_lut_data[128, :] = 32767  # Middle values
        
        edge_lut_path = os.path.join(self.temp_dir, "edge_case.tif")
        tifffile.imwrite(edge_lut_path, edge_lut_data)
        
        loaded_lut = self.lut_manager.load_lut(edge_lut_path)
        np.testing.assert_array_equal(loaded_lut, edge_lut_data)

    def test_load_lut_different_extensions(self):
        """Test loading LUT files with different valid extensions."""
        # Test .tiff extension
        tiff_path = os.path.join(self.temp_dir, "test.tiff")
        tifffile.imwrite(tiff_path, self.valid_lut_data)
        
        loaded_lut = self.lut_manager.load_lut(tiff_path)
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)

    def test_load_lut_case_insensitive_extension(self):
        """Test loading LUT files with case variations in extension."""
        # Test .TIF extension (uppercase)
        tif_upper_path = os.path.join(self.temp_dir, "test.TIF")
        tifffile.imwrite(tif_upper_path, self.valid_lut_data)
        
        loaded_lut = self.lut_manager.load_lut(tif_upper_path)
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)

    def test_load_lut_absolute_vs_relative_paths(self):
        """Test that absolute and relative paths work correctly."""
        # Test absolute path
        abs_loaded = self.lut_manager.load_lut(self.valid_lut_path)
        
        # Test relative path
        rel_loaded = self.lut_manager.load_lut("valid_lut.tif")
        
        # Both should load the same data
        np.testing.assert_array_equal(abs_loaded, rel_loaded)

    def test_lut_manager_with_different_directories(self):
        """Test LUTManager with different lut_dir settings."""
        # Create another temp directory
        temp_dir2 = tempfile.mkdtemp()
        
        try:
            # Create LUT in second directory
            lut_path2 = os.path.join(temp_dir2, "test_lut.tif")
            tifffile.imwrite(lut_path2, self.valid_lut_data)
            
            # Create LUTManager with second directory
            lut_manager2 = LUTManager(temp_dir2)
            loaded_lut = lut_manager2.load_lut("test_lut.tif")
            
            np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
            
        finally:
            # Clean up
            if os.path.exists(lut_path2):
                os.remove(lut_path2)
            os.rmdir(temp_dir2)


if __name__ == '__main__':
    unittest.main()

