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
        # Test with the 256x256 LUT created in setUp
        loaded_lut = tifffile.imread(self.test_lut_path)
        
        # Flatten the 2D LUT to create a 1D lookup table (as done in apply_lut)
        lut_1d = loaded_lut.flatten()

        
        # Calculate expected output: apply LUT directly using image values as indices
        expected_image = lut_1d[self.dummy_image_data]
        processed_image = self.processor.apply_lut(self.dummy_image_data, loaded_lut)
        np.testing.assert_array_equal(processed_image, expected_image)

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


