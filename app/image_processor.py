"""Image processing functionalities for the Darkroom Enlarger Application."""
import os
import numpy as np
import tifffile

class ImageProcessor:
    """Handles loading, processing, and converting images for display."""
    def __init__(self, file_checker=None, tiff_reader=None):
        """Initializes the ImageProcessor.
        
        Args:
            file_checker (callable, optional): Function to check if file exists. 
                                             Defaults to os.path.exists.
            tiff_reader (callable, optional): Function to read TIFF files.
                                            Defaults to tifffile.imread.
        """
        self.file_checker = file_checker or os.path.exists
        self.tiff_reader = tiff_reader or tifffile.imread

    def load_image(self, image_path):
        """Loads a 16-bit grayscale TIFF image and validates its format.

        Args:
            image_path (str): The path to the 16-bit TIFF image file.

        Returns:
            numpy.ndarray: The loaded image data as a NumPy array.

        Raises:
            ValueError: If the image is not a 16-bit grayscale TIFF.
            FileNotFoundError: If the image file does not exist.
        """
        # Check if file exists
        if not self.file_checker(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Check if file is a TIFF file
        if not image_path.lower().endswith(('.tif', '.tiff')):
            raise ValueError("Input file must be a TIFF file (.tif or .tiff)")
        
        try:
            image = self.tiff_reader(image_path)
        except Exception as e:
            raise ValueError(f"Failed to read TIFF file: {e}")

        # Validate image format
        if image.dtype != np.uint16:
            raise ValueError(f"Input image must be 16-bit (uint16). Found: {image.dtype}")
        
        if image.ndim != 2:  # Grayscale images have 2 dimensions (height, width)
            raise ValueError(f"Input image must be grayscale (2D). Found {image.ndim} dimensions with shape {image.shape}")

        return image

    def apply_lut(self, image, lut):
        """Applies a Look-Up Table (LUT) to the image.

        Args:
            image (numpy.ndarray): The input image data.
            lut (numpy.ndarray): The LUT to apply (256x256 2D array).

        Returns:
            numpy.ndarray: The image with the LUT applied.
        """
        # Ensure image is 16-bit for proper LUT application
        if image.dtype != np.uint16:
            image = image.astype(np.uint16)

        # Flatten the 2D LUT to create a 1D lookup table
        # The 256x256 LUT contains 65536 values for the full 16-bit range
        lut_1d = lut.flatten()
        
        # Apply the LUT directly using the image values as indices
        # Since we have a 16-bit image (0-65535) and a 65536-entry LUT, we can index directly
        processed_image = lut_1d[image]

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
            # Shift right by \'shift\' bits to simulate different exposures
            frame = (image_16bit >> shift).astype(np.uint8)
            frames_8bit.append(frame)
        return frames_8bit


