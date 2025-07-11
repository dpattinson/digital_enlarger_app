"""Image processing functionalities for the Darkroom Enlarger Application using OpenCV."""
import os
import numpy as np
import cv2


class ImageProcessor:
    """Handles loading, processing, and converting images for display using OpenCV."""
    
    def __init__(self, file_checker=None, tiff_reader=None, cv2_reader=None):
        """Initializes the ImageProcessor with OpenCV backend.
        
        Args:
            file_checker (callable, optional): Function to check if file exists. 
                                             Defaults to os.path.exists.
            cv2_reader (callable, optional): Function to read image files.
                                           Defaults to cv2.imread.
        """
        self.file_checker = file_checker or os.path.exists
        # Support both old and new parameter names for backward compatibility
        self.cv2_reader = cv2_reader or tiff_reader or cv2.imread

    def load_image(self, image_path):
        """Loads a 16-bit grayscale TIFF image using OpenCV and validates its format.

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
            # Load image with OpenCV - use IMREAD_UNCHANGED to preserve bit depth
            image = self.cv2_reader(image_path, cv2.IMREAD_UNCHANGED)
            
            if image is None:
                raise ValueError("Failed to read image file - file may be corrupted or unsupported")
                
        except Exception as e:
            raise ValueError(f"Failed to read TIFF file: {e}")

        # Validate image format
        if image.dtype != np.uint16:
            raise ValueError(f"Input image must be 16-bit (uint16). Found: {image.dtype}")
        
        if image.ndim != 2:  # Grayscale images have 2 dimensions (height, width)
            raise ValueError(f"Input image must be grayscale (2D). Found {image.ndim} dimensions with shape {image.shape}")

        # Auto-rotate portrait images to landscape orientation
        if self.is_portrait_orientation(image):
            image = self.rotate_image_clockwise_90(image)

        return image

    def apply_lut(self, image, lut):
        """Applies a Look-Up Table (LUT) to the image using OpenCV for optimal performance.

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
        
        # Use manual indexing for 16-bit LUT application (more reliable than cv2.LUT for 16-bit)
        processed_image = lut_1d[image]

        return processed_image

    def invert_image(self, image):
        """Inverts the image (negative effect) using OpenCV.

        Args:
            image (numpy.ndarray): The input image data.

        Returns:
            numpy.ndarray: The inverted image data.
        """
        # Use OpenCV's bitwise_not for efficient inversion
        # This is faster than manual arithmetic for large images
        return cv2.bitwise_not(image)


    def is_portrait_orientation(self, image):
        """Determines if an image is in portrait orientation (height > width).

        Args:
            image (numpy.ndarray): The input image data.

        Returns:
            bool: True if the image is in portrait orientation, False otherwise.
        """
        if image is None or image.ndim != 2:
            return False
            
        height, width = image.shape
        return height > width

    def rotate_image_clockwise_90(self, image):
        """Rotates an image 90 degrees clockwise using OpenCV.

        Args:
            image (numpy.ndarray): The input image data.

        Returns:
            numpy.ndarray: The rotated image.
            
        Raises:
            ValueError: If image data is invalid.
        """
        if image is None:
            raise ValueError("Cannot rotate None image")
            
        if image.ndim != 2:
            raise ValueError(f"Can only rotate 2D grayscale images. Found {image.ndim} dimensions")
            
        # Use OpenCV's rotate function for 90-degree clockwise rotation
        # cv2.ROTATE_90_CLOCKWISE is equivalent to rotating 90 degrees clockwise
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        
        return rotated_image

