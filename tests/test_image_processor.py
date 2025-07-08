import unittest
import numpy as np
import tifffile
import os
import tempfile
from unittest.mock import patch
from app.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ImageProcessor()
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.tif")
        self.test_lut_path = os.path.join(self.temp_dir, "test_lut.tif")

        # Create a dummy 16-bit grayscale image for testing
        self.dummy_image_data = np.array([[1000, 2000, 3000], [4000, 5000, 6000]], dtype=np.uint16)
        tifffile.imwrite(self.test_image_path, self.dummy_image_data)

        # Create a dummy 256x256 16-bit LUT for testing
        self.dummy_lut_data = np.zeros((256, 256), dtype=np.uint16)
        for i in range(256):
            self.dummy_lut_data[i, :] = np.linspace(0, 65535, 256, dtype=np.uint16)
        tifffile.imwrite(self.test_lut_path, self.dummy_lut_data)

    def tearDown(self):
        # Clean up all test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def test_load_image_valid(self):
        """Test loading a valid 16-bit grayscale TIFF image."""
        loaded_image = self.processor.load_image(self.test_image_path)
        np.testing.assert_array_equal(loaded_image, self.dummy_image_data)

    def test_load_image_file_not_found(self):
        """Test loading non-existent image file."""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tif")
        
        with self.assertRaises(FileNotFoundError) as context:
            self.processor.load_image(non_existent_path)
        
        self.assertIn("Image file not found", str(context.exception))

    def test_load_image_invalid_extension(self):
        """Test loading file with invalid extension."""
        invalid_path = os.path.join(self.temp_dir, "invalid.jpg")
        
        with self.assertRaises(ValueError) as context:
            self.processor.load_image(invalid_path)
        
        self.assertIn("Input file must be a TIFF file", str(context.exception))

    @patch('tifffile.imread')
    def test_load_image_read_error(self, mock_imread):
        """Test handling of TIFF read errors."""
        mock_imread.side_effect = Exception("TIFF read error")
        
        with self.assertRaises(ValueError) as context:
            self.processor.load_image(self.test_image_path)
        
        self.assertIn("Failed to read TIFF file", str(context.exception))

    def test_load_image_wrong_dtype(self):
        """Test loading image with wrong data type."""
        # Create 8-bit image (invalid)
        invalid_image_data = np.array([[100, 150, 200]], dtype=np.uint8)
        invalid_image_path = os.path.join(self.temp_dir, "invalid_dtype.tif")
        tifffile.imwrite(invalid_image_path, invalid_image_data)
        
        with self.assertRaises(ValueError) as context:
            self.processor.load_image(invalid_image_path)
        
        self.assertIn("Input image must be 16-bit (uint16)", str(context.exception))

    def test_load_image_wrong_dimensions(self):
        """Test loading image with wrong dimensions (3D instead of 2D)."""
        # Create 3D image (RGB instead of grayscale)
        invalid_image_data = np.zeros((10, 10, 3), dtype=np.uint16)
        invalid_image_path = os.path.join(self.temp_dir, "invalid_3d.tif")
        tifffile.imwrite(invalid_image_path, invalid_image_data)
        
        with self.assertRaises(ValueError) as context:
            self.processor.load_image(invalid_image_path)
        
        self.assertIn("Input image must be grayscale (2D)", str(context.exception))

    def test_load_image_different_extensions(self):
        """Test loading images with different valid extensions."""
        # Test .tiff extension
        tiff_path = os.path.join(self.temp_dir, "test.tiff")
        tifffile.imwrite(tiff_path, self.dummy_image_data)
        
        loaded_image = self.processor.load_image(tiff_path)
        np.testing.assert_array_equal(loaded_image, self.dummy_image_data)

    def test_apply_lut_valid(self):
        """Test applying LUT to valid image."""
        # Test with the 256x256 LUT created in setUp
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # Flatten the 2D LUT to create a 1D lookup table (as done in apply_lut)
        lut_1d = loaded_lut.flatten()
        
        # Calculate expected output: apply LUT directly using image values as indices
        expected_image = lut_1d[self.dummy_image_data]
        processed_image = self.processor.apply_lut(self.dummy_image_data, loaded_lut)
        np.testing.assert_array_equal(processed_image, expected_image)

    def test_apply_lut_non_uint16_image(self):
        """Test applying LUT to non-uint16 image (should convert automatically)."""
        # Create 8-bit image
        image_8bit = np.array([[100, 150, 200]], dtype=np.uint8)
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # Should convert to uint16 automatically
        processed_image = self.processor.apply_lut(image_8bit, loaded_lut)
        
        # Verify conversion happened and LUT was applied
        self.assertEqual(processed_image.dtype, np.uint16)
        
        # Expected: image converted to uint16, then LUT applied
        converted_image = image_8bit.astype(np.uint16)
        lut_1d = loaded_lut.flatten()
        expected_image = lut_1d[converted_image]
        np.testing.assert_array_equal(processed_image, expected_image)

    def test_apply_lut_edge_values(self):
        """Test applying LUT with edge case values (0 and 65535)."""
        # Create image with edge values
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        processed_image = self.processor.apply_lut(edge_image, loaded_lut)
        
        # Verify processing worked
        self.assertEqual(processed_image.dtype, np.uint16)
        self.assertEqual(processed_image.shape, edge_image.shape)

    def test_invert_image_uint16(self):
        """Test inverting 16-bit image."""
        inverted_image = self.processor.invert_image(self.dummy_image_data)
        expected_inverted_image = 65535 - self.dummy_image_data
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)

    def test_invert_image_uint8(self):
        """Test inverting 8-bit image."""
        image_8bit = np.array([[100, 150, 200]], dtype=np.uint8)
        inverted_image = self.processor.invert_image(image_8bit)
        expected_inverted_image = 255 - image_8bit
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)

    def test_invert_image_edge_values(self):
        """Test inverting image with edge values."""
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        inverted_image = self.processor.invert_image(edge_image)
        expected_inverted_image = np.array([[65535, 32768, 0]], dtype=np.uint16)
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)

    def test_emulate_12bit_to_8bit_frames(self):
        """Test 12-bit to 8-bit frame emulation."""
        frames = self.processor.emulate_12bit_to_8bit_frames(self.dummy_image_data)
        
        # Should return 4 frames
        self.assertEqual(len(frames), 4)
        
        # Each frame should be 8-bit and same shape as input
        for i, frame in enumerate(frames):
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, self.dummy_image_data.shape)
            
            # Verify the bit shifting logic
            expected_frame = (self.dummy_image_data >> i).astype(np.uint8)
            np.testing.assert_array_equal(frame, expected_frame)

    def test_emulate_12bit_to_8bit_frames_edge_values(self):
        """Test frame emulation with edge case values."""
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        frames = self.processor.emulate_12bit_to_8bit_frames(edge_image)
        
        self.assertEqual(len(frames), 4)
        
        # Check specific values for edge cases
        # Frame 0: no shift
        expected_frame_0 = (edge_image >> 0).astype(np.uint8)
        np.testing.assert_array_equal(frames[0], expected_frame_0)
        
        # Frame 3: shift by 3 bits
        expected_frame_3 = (edge_image >> 3).astype(np.uint8)
        np.testing.assert_array_equal(frames[3], expected_frame_3)

    def test_emulate_12bit_to_8bit_frames_large_image(self):
        """Test frame emulation with larger image."""
        large_image = np.random.randint(0, 65536, size=(100, 100), dtype=np.uint16)
        frames = self.processor.emulate_12bit_to_8bit_frames(large_image)
        
        self.assertEqual(len(frames), 4)
        for frame in frames:
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, large_image.shape)


if __name__ == '__main__':
    unittest.main()

