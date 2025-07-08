"""Image processing functionalities for the Darkroom Enlarger Application."""
import numpy as np
import tifffile

class ImageProcessor:
    """Handles loading, processing, and converting images for display."""
    def __init__(self):
        """Initializes the ImageProcessor."""
        pass

    def load_image(self, image_path):
        """Loads a 16-bit TIFF image.

        Args:
            image_path (str): The path to the 16-bit TIFF image file.

        Returns:
            numpy.ndarray: The loaded image data as a NumPy array.
        """
        return tifffile.imread(image_path)

    def apply_lut(self, image, lut):
        """Applies a Look-Up Table (LUT) to the image.

        Args:
            image (numpy.ndarray): The input image data.
            lut (numpy.ndarray): The LUT to apply.

        Returns:
            numpy.ndarray: The image with the LUT applied.
        """
        # Ensure image is 16-bit for proper LUT application
        if image.dtype != np.uint16:
            image = image.astype(np.uint16)

        # Normalize image to 0-lut_max_index for LUT lookup
        lut_max_index = lut.shape[0] - 1
        # Scale image values to fit the LUT index range
        scaled_image = (image / np.iinfo(image.dtype).max * lut_max_index).astype(int)
        # Clip values to ensure they are within the valid LUT index range
        scaled_image = np.clip(scaled_image, 0, lut_max_index)

        # Apply the LUT
        processed_image = lut[scaled_image]

        return processed_image

    def invert_image(self, image):
        """Inverts the image (negative effect).

        Args:
            image (numpy.ndarray): The input image data.

        Returns:
            numpy.ndarray: The inverted image data.
        """
        return np.iinfo(image.dtype).max - image

    def emulate_12bit_to_8bit_frames(self, image_16bit):
        """Emulates 12-bit exposure by generating 8-bit frames.

        Args:
            image_16bit (numpy.ndarray): The 16-bit input image data.

        Returns:
            list: A list of 8-bit NumPy arrays, each representing a frame.
        """
        frames_8bit = []
        # Assuming 12-bit emulation means shifting bits to get different exposures
        # This is a simplified emulation. For true 12-bit emulation, more complex
        # algorithms involving exposure times and light intensity would be needed.
        for shift in range(4):
            # Shift right by 'shift' bits to simulate different exposures
            frame = (image_16bit >> shift).astype(np.uint8)
            frames_8bit.append(frame)
        return frames_8bit


