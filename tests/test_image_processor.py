import unittest
import numpy as np
import tifffile
import os
from app.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = ImageProcessor()
        self.test_image_path = "test_image.tif"
        self.test_lut_path = "test_lut.tif"

        # Create a dummy 16-bit grayscale image for testing
        self.dummy_image_data = np.array([[1000, 2000, 3000], [4000, 5000, 6000]], dtype=np.uint16)
        tifffile.imwrite(self.test_image_path, self.dummy_image_data)

        # Create a dummy 256x256 16-bit LUT for testing
        self.dummy_lut_data = np.zeros((256, 256), dtype=np.uint16)
        for i in range(256):
            self.dummy_lut_data[i, :] = np.linspace(0, 65535, 256, dtype=np.uint16)
        tifffile.imwrite(self.test_lut_path, self.dummy_lut_data)

    def tearDown(self):
        os.remove(self.test_image_path)
        os.remove(self.test_lut_path)

    def test_load_image(self):
        loaded_image = self.processor.load_image(self.test_image_path)
        np.testing.assert_array_equal(loaded_image, self.dummy_image_data)

    def test_apply_lut(self):
        # Test with a simple LUT that maps input_8bit to output_16bit
        # Create a 2D LUT where lut[i, j] maps to a simple value
        test_lut_simple = np.zeros((65536, 256), dtype=np.uint16)
        for i in range(65536):
            test_lut_simple[i, :] = np.full(256, min(65535, i // 256), dtype=np.uint16)
        
        # Save this simple LUT for testing
        tifffile.imwrite("test_lut_simple.tif", test_lut_simple)
        loaded_simple_lut = tifffile.imread("test_lut_simple.tif")

        # Calculate expected output based on the logic in apply_lut
        # 1. Scale dummy_image_data to 0-65535 range (uint16)
        lut_max_index = loaded_simple_lut.shape[0] - 1
        scaled_image = (self.dummy_image_data / np.iinfo(self.dummy_image_data.dtype).max * lut_max_index).astype(int)
        scaled_image = np.clip(scaled_image, 0, lut_max_index)
        
        # 2. Apply the 2D LUT to the scaled_image
        expected_image = loaded_simple_lut[scaled_image]

        processed_image = self.processor.apply_lut(self.dummy_image_data, loaded_simple_lut)
        np.testing.assert_array_equal(processed_image, expected_image)
        os.remove("test_lut_simple.tif")

    def test_invert_image(self):
        inverted_image = self.processor.invert_image(self.dummy_image_data)
        expected_inverted_image = 65535 - self.dummy_image_data
        np.testing.assert_array_equal(inverted_image, expected_inverted_image)

    def test_emulate_12bit_to_8bit_frames(self):
        frames = self.processor.emulate_12bit_to_8bit_frames(self.dummy_image_data)
        self.assertEqual(len(frames), 4)
        for frame in frames:
            self.assertEqual(frame.dtype, np.uint8)
            self.assertEqual(frame.shape, self.dummy_image_data.shape)

if __name__ == '__main__':
    unittest.main()


