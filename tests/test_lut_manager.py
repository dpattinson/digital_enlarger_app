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

    def test_init_sets_lut_directory_correctly_when_given_valid_path(self):
        """Test that LUTManager initialization sets the LUT directory correctly."""
        # GIVEN: A valid directory path and mocked dependencies
        from unittest.mock import Mock
        mock_file_checker = Mock(return_value=True)
        mock_dir_lister = Mock(return_value=['test.tif'])
        lut_directory = "luts"
        
        # WHEN: We initialize a LUTManager with the directory
        lut_manager = LUTManager(lut_directory, file_checker=mock_file_checker, dir_lister=mock_dir_lister)
        
        # THEN: The LUT directory should be set correctly
        self.assertEqual(lut_manager.lut_dir, lut_directory)
        
        # AND THEN: Custom directory paths should also work correctly
        custom_dir = "/custom/lut/dir"
        lut_manager_custom = LUTManager(custom_dir, file_checker=mock_file_checker, dir_lister=mock_dir_lister)
        self.assertEqual(lut_manager_custom.lut_dir, custom_dir)

    def test_load_lut_returns_correct_array_when_given_valid_lut_file(self):
        """Test that loading a valid LUT file returns the correct 256x256 array."""
        # GIVEN: A valid 256x256 16-bit LUT file exists
        lut_manager = self.lut_manager
        valid_lut_path = self.valid_lut_path
        expected_lut_data = self.valid_lut_data
        
        # WHEN: We load the LUT file
        loaded_lut = lut_manager.load_lut(valid_lut_path)
        
        # THEN: The loaded LUT should match the original data exactly
        np.testing.assert_array_equal(loaded_lut, expected_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)
        self.assertEqual(loaded_lut.shape, (256, 256))

    def test_load_lut_resolves_relative_path_correctly_when_given_filename_only(self):
        """Test that loading a LUT with relative path resolves correctly to lut_dir."""
        # GIVEN: A LUT file exists in the lut_dir and we have just the filename
        relative_lut_path = os.path.join(self.temp_dir, "relative_lut.tif")
        tifffile.imwrite(relative_lut_path, self.valid_lut_data)
        lut_manager = self.lut_manager
        filename_only = "relative_lut.tif"
        
        # WHEN: We load the LUT using just the filename
        loaded_lut = lut_manager.load_lut(filename_only)
        
        # THEN: The LUT should be loaded correctly from the lut_dir
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)

    def test_load_lut_raises_file_not_found_when_given_nonexistent_path(self):
        """Test that loading a non-existent LUT file raises FileNotFoundError."""
        # GIVEN: A path to a non-existent LUT file
        lut_manager = self.lut_manager
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tif")
        
        # WHEN: We attempt to load the non-existent LUT
        # THEN: A FileNotFoundError should be raised with descriptive message
        with self.assertRaises(FileNotFoundError) as context:
            lut_manager.load_lut(non_existent_path)
        
        self.assertIn("LUT file not found", str(context.exception))

    def test_load_lut_raises_value_error_when_given_invalid_file_extension(self):
        """Test that loading a file with invalid extension raises ValueError."""
        # GIVEN: A file path with invalid extension and mocked file checker
        from unittest.mock import Mock
        mock_file_checker = Mock(return_value=True)
        lut_manager = LUTManager(self.temp_dir, file_checker=mock_file_checker)
        invalid_path = "/fake/path/invalid.jpg"
        
        # WHEN: We attempt to load the file with invalid extension
        # THEN: A ValueError should be raised with descriptive message
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(invalid_path)
        
        self.assertIn("LUT file must be a TIFF file", str(context.exception))

    def test_load_lut_raises_value_error_when_given_wrong_data_type(self):
        """Test that loading a LUT with wrong data type raises ValueError."""
        # GIVEN: An 8-bit LUT file (invalid data type)
        invalid_lut_data = np.zeros((256, 256), dtype=np.uint8)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_dtype.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We attempt to load the 8-bit LUT
        # THEN: A ValueError should be raised indicating wrong data type
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 16-bit (uint16)", str(context.exception))

    def test_load_lut_raises_value_error_when_given_wrong_dimensions(self):
        """Test that loading a LUT with wrong dimensions raises ValueError."""
        # GIVEN: A 128x128 LUT file (invalid dimensions)
        invalid_lut_data = np.zeros((128, 128), dtype=np.uint16)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_size.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We attempt to load the incorrectly sized LUT
        # THEN: A ValueError should be raised indicating wrong dimensions
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 256x256 pixels", str(context.exception))

    def test_load_lut_raises_value_error_when_given_3d_array(self):
        """Test that loading a 3D LUT array (RGB) raises ValueError."""
        # GIVEN: A 3D RGB LUT file (invalid format)
        invalid_lut_data = np.zeros((256, 256, 3), dtype=np.uint16)
        invalid_lut_path = os.path.join(self.temp_dir, "invalid_3d.tif")
        tifffile.imwrite(invalid_lut_path, invalid_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We attempt to load the 3D RGB LUT
        # THEN: A ValueError should be raised indicating wrong dimensions
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(invalid_lut_path)
        
        self.assertIn("LUT must be 256x256 pixels", str(context.exception))

    def test_load_lut_raises_value_error_when_tiff_reader_fails(self):
        """Test that TIFF read errors are properly handled and converted to ValueError."""
        # GIVEN: A LUTManager with mocked TIFF reader that raises an exception
        from unittest.mock import Mock
        mock_tiff_reader = Mock(side_effect=Exception("TIFF read error"))
        lut_manager = LUTManager(self.temp_dir, tiff_reader=mock_tiff_reader)
        
        # WHEN: We attempt to load a LUT and the TIFF reader fails
        # THEN: A ValueError should be raised with descriptive message
        with self.assertRaises(ValueError) as context:
            lut_manager.load_lut(self.valid_lut_path)
        
        self.assertIn("Failed to read TIFF LUT file", str(context.exception))

    def test_load_lut_handles_edge_case_values_correctly(self):
        """Test that LUT loading works correctly with edge case values (min/max)."""
        # GIVEN: A LUT with edge case values (0, 32767, 65535)
        edge_lut_data = np.zeros((256, 256), dtype=np.uint16)
        edge_lut_data[0, :] = 0  # Minimum values
        edge_lut_data[255, :] = 65535  # Maximum values
        edge_lut_data[128, :] = 32767  # Middle values
        edge_lut_path = os.path.join(self.temp_dir, "edge_case.tif")
        tifffile.imwrite(edge_lut_path, edge_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We load the edge case LUT
        loaded_lut = lut_manager.load_lut(edge_lut_path)
        
        # THEN: The LUT should be loaded correctly with all edge values preserved
        np.testing.assert_array_equal(loaded_lut, edge_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)
        self.assertEqual(loaded_lut.shape, (256, 256))

    def test_load_lut_accepts_both_tif_and_tiff_extensions(self):
        """Test that both .tif and .tiff extensions are accepted as valid."""
        # GIVEN: A valid LUT file with .tiff extension
        tiff_path = os.path.join(self.temp_dir, "test.tiff")
        tifffile.imwrite(tiff_path, self.valid_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We load the LUT with .tiff extension
        loaded_lut = lut_manager.load_lut(tiff_path)
        
        # THEN: The LUT should load successfully and match the original data
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)

    def test_load_lut_handles_case_insensitive_extensions(self):
        """Test that LUT loading works with case variations in file extensions."""
        # GIVEN: A valid LUT file with uppercase .TIF extension
        tif_upper_path = os.path.join(self.temp_dir, "test.TIF")
        tifffile.imwrite(tif_upper_path, self.valid_lut_data)
        lut_manager = self.lut_manager
        
        # WHEN: We load the LUT with uppercase extension
        loaded_lut = lut_manager.load_lut(tif_upper_path)
        
        # THEN: The LUT should load successfully regardless of case
        np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
        self.assertEqual(loaded_lut.dtype, np.uint16)

    def test_load_lut_produces_same_result_for_absolute_and_relative_paths(self):
        """Test that absolute and relative paths produce identical results."""
        # GIVEN: A valid LUT file accessible via both absolute and relative paths
        lut_manager = self.lut_manager
        absolute_path = self.valid_lut_path
        relative_path = "valid_lut.tif"
        
        # WHEN: We load the LUT using both path types
        abs_loaded = lut_manager.load_lut(absolute_path)
        rel_loaded = lut_manager.load_lut(relative_path)
        
        # THEN: Both should load identical data
        np.testing.assert_array_equal(abs_loaded, rel_loaded)
        self.assertEqual(abs_loaded.dtype, rel_loaded.dtype)
        self.assertEqual(abs_loaded.shape, rel_loaded.shape)

    def test_lut_manager_works_correctly_with_different_directories(self):
        """Test that LUTManager functions correctly when configured with different directories."""
        # GIVEN: A second temporary directory with a LUT file
        temp_dir2 = tempfile.mkdtemp()
        lut_path2 = os.path.join(temp_dir2, "test_lut.tif")
        tifffile.imwrite(lut_path2, self.valid_lut_data)
        
        try:
            # AND GIVEN: A LUTManager configured for the second directory
            lut_manager2 = LUTManager(temp_dir2)
            
            # WHEN: We load a LUT from the second directory
            loaded_lut = lut_manager2.load_lut("test_lut.tif")
            
            # THEN: The LUT should be loaded correctly from the configured directory
            np.testing.assert_array_equal(loaded_lut, self.valid_lut_data)
            self.assertEqual(loaded_lut.dtype, np.uint16)
            self.assertEqual(loaded_lut.shape, (256, 256))
            
        finally:
            # Clean up the second directory
            if os.path.exists(lut_path2):
                os.remove(lut_path2)
            os.rmdir(temp_dir2)


if __name__ == '__main__':
    unittest.main()

