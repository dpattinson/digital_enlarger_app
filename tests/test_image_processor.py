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

    def test_load_image_returns_correct_array_when_given_valid_tiff_file(self):
        """Test that loading a valid 16-bit grayscale TIFF image returns the correct array."""
        # GIVEN: A valid 16-bit grayscale TIFF image file exists
        processor = ImageProcessor()
        valid_image_path = self.test_image_path
        expected_image_data = self.dummy_image_data
        
        # WHEN: We load the image
        loaded_image = processor.load_image(valid_image_path)
        
        # THEN: The loaded image should match the original data exactly
        np.testing.assert_array_equal(loaded_image, expected_image_data)
        self.assertEqual(loaded_image.dtype, np.uint16)
        self.assertEqual(loaded_image.shape, expected_image_data.shape)

    def test_load_image_raises_file_not_found_when_given_nonexistent_path(self):
        """Test that loading a non-existent image file raises FileNotFoundError."""
        # GIVEN: A path to a non-existent image file
        processor = ImageProcessor()
        non_existent_path = os.path.join(self.temp_dir, "non_existent.tif")
        
        # WHEN: We attempt to load the non-existent image
        # THEN: A FileNotFoundError should be raised with descriptive message
        with self.assertRaises(FileNotFoundError) as context:
            processor.load_image(non_existent_path)
        
        self.assertIn("Image file not found", str(context.exception))

    def test_load_image_raises_value_error_when_given_invalid_file_extension(self):
        """Test that loading a file with invalid extension raises ValueError."""
        # GIVEN: A file path with invalid extension and mocked file checker
        from unittest.mock import Mock
        mock_file_checker = Mock(return_value=True)
        processor = ImageProcessor(file_checker=mock_file_checker)
        invalid_path = "/fake/path/invalid.jpg"
        
        # WHEN: We attempt to load the file with invalid extension
        # THEN: A ValueError should be raised with descriptive message
        with self.assertRaises(ValueError) as context:
            processor.load_image(invalid_path)
        
        self.assertIn("Input file must be a TIFF file", str(context.exception))

    def test_load_image_raises_value_error_when_tiff_reader_fails(self):
        """Test that TIFF read errors are properly handled and converted to ValueError."""
        # GIVEN: A processor with mocked TIFF reader that raises an exception
        from unittest.mock import Mock
        mock_tiff_reader = Mock(side_effect=Exception("TIFF read error"))
        processor = ImageProcessor(tiff_reader=mock_tiff_reader)
        
        # WHEN: We attempt to load an image and the TIFF reader fails
        # THEN: A ValueError should be raised with descriptive message
        with self.assertRaises(ValueError) as context:
            processor.load_image(self.test_image_path)
        
        self.assertIn("Failed to read TIFF file", str(context.exception))

    def test_load_image_raises_value_error_when_given_wrong_data_type(self):
        """Test that loading an image with wrong data type raises ValueError."""
        # GIVEN: An 8-bit TIFF image file (invalid data type)
        invalid_image_data = np.array([[100, 150, 200]], dtype=np.uint8)
        invalid_image_path = os.path.join(self.temp_dir, "invalid_dtype.tif")
        tifffile.imwrite(invalid_image_path, invalid_image_data)
        processor = ImageProcessor()
        
        # WHEN: We attempt to load the 8-bit image
        # THEN: A ValueError should be raised indicating wrong data type
        with self.assertRaises(ValueError) as context:
            processor.load_image(invalid_image_path)
        
        self.assertIn("Input image must be 16-bit (uint16)", str(context.exception))

    def test_load_image_raises_value_error_when_given_3d_image(self):
        """Test that loading a 3D image (RGB) raises ValueError for non-grayscale format."""
        # GIVEN: A 3D RGB TIFF image file (invalid dimensions)
        invalid_image_data = np.zeros((10, 10, 3), dtype=np.uint16)
        invalid_image_path = os.path.join(self.temp_dir, "invalid_3d.tif")
        tifffile.imwrite(invalid_image_path, invalid_image_data)
        processor = ImageProcessor()
        
        # WHEN: We attempt to load the 3D RGB image
        # THEN: A ValueError should be raised indicating wrong dimensions
        with self.assertRaises(ValueError) as context:
            processor.load_image(invalid_image_path)
        
        self.assertIn("Input image must be grayscale (2D)", str(context.exception))

    def test_load_image_accepts_both_tif_and_tiff_extensions(self):
        """Test that both .tif and .tiff extensions are accepted as valid."""
        # GIVEN: A valid image file with .tiff extension
        processor = ImageProcessor()
        tiff_path = os.path.join(self.temp_dir, "test.tiff")
        tifffile.imwrite(tiff_path, self.dummy_image_data)
        
        # WHEN: We load the image with .tiff extension
        loaded_image = processor.load_image(tiff_path)
        
        # THEN: The image should load successfully and match the original data
        np.testing.assert_array_equal(loaded_image, self.dummy_image_data)
        self.assertEqual(loaded_image.dtype, np.uint16)

    def test_apply_lut_transforms_image_correctly_when_given_valid_lut(self):
        """Test that applying a LUT to an image produces the expected transformation."""
        # GIVEN: A valid image and a 256x256 LUT
        processor = ImageProcessor()
        input_image = self.dummy_image_data
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # AND GIVEN: The expected transformation (LUT applied as 1D lookup)
        lut_1d = loaded_lut.flatten()
        expected_image = lut_1d[input_image]
        
        # WHEN: We apply the LUT to the image
        processed_image = processor.apply_lut(input_image, loaded_lut)
        
        # THEN: The processed image should match the expected transformation
        np.testing.assert_array_equal(processed_image, expected_image)
        self.assertEqual(processed_image.dtype, np.uint16)

    def test_apply_lut_converts_8bit_image_to_16bit_before_processing(self):
        """Test that 8-bit images are automatically converted to 16-bit before LUT application."""
        # GIVEN: An 8-bit image and a valid LUT
        processor = ImageProcessor()
        image_8bit = np.array([[100, 150, 200]], dtype=np.uint8)
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # WHEN: We apply the LUT to the 8-bit image
        processed_image = processor.apply_lut(image_8bit, loaded_lut)
        
        # THEN: The image should be converted to 16-bit and LUT applied correctly
        self.assertEqual(processed_image.dtype, np.uint16)
        
        # AND THEN: The result should match manual conversion and LUT application
        converted_image = image_8bit.astype(np.uint16)
        lut_1d = loaded_lut.flatten()
        expected_image = lut_1d[converted_image]
        np.testing.assert_array_equal(processed_image, expected_image)

    def test_apply_lut_handles_edge_values_correctly(self):
        """Test that LUT application works correctly with edge case values (0 and 65535)."""
        # GIVEN: An image with edge case values and a valid LUT
        processor = ImageProcessor()
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # WHEN: We apply the LUT to the edge case image
        processed_image = processor.apply_lut(edge_image, loaded_lut)
        
        # THEN: The processing should complete without errors
        self.assertEqual(processed_image.dtype, np.uint16)
        self.assertEqual(processed_image.shape, edge_image.shape)
        
        # AND THEN: All values should be within valid 16-bit range
        self.assertGreaterEqual(processed_image.min(), 0)
        self.assertLessEqual(processed_image.max(), 65535)

    def test_invert_image_produces_correct_inversion_for_16bit_image(self):
        """Test that 16-bit image inversion produces mathematically correct results."""
        # GIVEN: A 16-bit grayscale image
        processor = ImageProcessor()
        input_image = self.dummy_image_data
        expected_inverted_image = 65535 - input_image
        
        # WHEN: We invert the image
        inverted_image = processor.invert_image(input_image)
        
        # THEN: The inverted image should be mathematically correct (65535 - original)
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)
        self.assertEqual(inverted_image.dtype, np.uint16)

    def test_invert_image_produces_correct_inversion_for_8bit_image(self):
        """Test that 8-bit image inversion produces mathematically correct results."""
        # GIVEN: An 8-bit grayscale image
        processor = ImageProcessor()
        image_8bit = np.array([[100, 150, 200]], dtype=np.uint8)
        expected_inverted_image = 255 - image_8bit
        
        # WHEN: We invert the 8-bit image
        inverted_image = processor.invert_image(image_8bit)
        
        # THEN: The inverted image should be mathematically correct (255 - original)
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)
        self.assertEqual(inverted_image.dtype, np.uint8)

    def test_invert_image_handles_edge_values_correctly(self):
        """Test that image inversion works correctly with edge case values."""
        # GIVEN: An image with edge case values (0, middle, max)
        processor = ImageProcessor()
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        expected_inverted_image = np.array([[65535, 32768, 0]], dtype=np.uint16)
        
        # WHEN: We invert the edge case image
        inverted_image = processor.invert_image(edge_image)
        
        # THEN: The inversion should be mathematically correct for all edge values
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)
        self.assertEqual(inverted_image.dtype, np.uint16)

    def test_emulate_12bit_to_8bit_frames_produces_four_frames_with_correct_bit_shifts(self):
        """Test that 12-bit to 8-bit frame emulation produces 4 frames with correct bit shifting."""
        # GIVEN: A 16-bit input image
        processor = ImageProcessor()
        input_image = self.dummy_image_data
        
        # WHEN: We emulate 12-bit to 8-bit frames
        frames = processor.emulate_12bit_to_8bit_frames(input_image)
        
        # THEN: We should get exactly 4 frames
        self.assertEqual(len(frames), 4)
        
        # AND THEN: Each frame should be 8-bit with correct shape and bit shifting
        for i, frame in enumerate(frames):
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, input_image.shape)
            
            # Verify the bit shifting logic is correct
            expected_frame = (input_image >> i).astype(np.uint8)
            np.testing.assert_array_equal(frame, expected_frame)

    def test_emulate_12bit_to_8bit_frames_handles_edge_values_correctly(self):
        """Test that frame emulation works correctly with edge case values."""
        # GIVEN: An image with edge case values
        processor = ImageProcessor()
        edge_image = np.array([[0, 32767, 65535]], dtype=np.uint16)
        
        # WHEN: We emulate frames from the edge case image
        frames = processor.emulate_12bit_to_8bit_frames(edge_image)
        
        # THEN: We should get 4 frames with correct bit shifting
        self.assertEqual(len(frames), 4)
        
        # AND THEN: Frame 0 should have no bit shift
        expected_frame_0 = (edge_image >> 0).astype(np.uint8)
        np.testing.assert_array_equal(frames[0], expected_frame_0)
        
        # AND THEN: Frame 3 should have 3-bit shift
        expected_frame_3 = (edge_image >> 3).astype(np.uint8)
        np.testing.assert_array_equal(frames[3], expected_frame_3)

    def test_emulate_12bit_to_8bit_frames_works_with_large_images(self):
        """Test that frame emulation performs correctly with larger image sizes."""
        # GIVEN: A large random 16-bit image
        processor = ImageProcessor()
        large_image = np.random.randint(0, 65536, size=(100, 100), dtype=np.uint16)
        
        # WHEN: We emulate frames from the large image
        frames = processor.emulate_12bit_to_8bit_frames(large_image)
        
        # THEN: We should get 4 frames with correct properties
        self.assertEqual(len(frames), 4)
        
        # AND THEN: Each frame should maintain the original shape and be 8-bit
        for frame in frames:
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, large_image.shape)


if __name__ == '__main__':
    unittest.main()

