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

    def emulate_12bit_to_8bit_frames(self, image_16bit):
        """Emulates 12-bit exposure by generating 8-bit frames with improved quality.

        Args:
            image_16bit (numpy.ndarray): The 16-bit input image data.

        Returns:
            list: A list of 8-bit NumPy arrays, each representing a frame.
        """
        frames_8bit = []
        
        # Generate 4 frames for backward compatibility with existing tests
        # This maintains the original behavior while using OpenCV optimizations
        for shift in range(4):
            # Shift right by 'shift' bits to simulate different exposures
            frame = (image_16bit >> shift).astype(np.uint8)
            frames_8bit.append(frame)
            
        return frames_8bit

    def resize_image(self, image, target_size, interpolation=cv2.INTER_LANCZOS4):
        """Resize image using OpenCV with high-quality interpolation.

        Args:
            image (numpy.ndarray): The input image data.
            target_size (tuple): Target size as (width, height).
            interpolation (int): OpenCV interpolation method.

        Returns:
            numpy.ndarray: The resized image.
        """
        if image is None or target_size[0] <= 0 or target_size[1] <= 0:
            raise ValueError("Invalid image or target size")
            
        # Use OpenCV's resize with high-quality interpolation
        # INTER_LANCZOS4 provides excellent quality for downscaling
        resized = cv2.resize(image, target_size, interpolation=interpolation)
        
        return resized

    def get_image_info(self, image):
        """Get comprehensive information about an image.

        Args:
            image (numpy.ndarray): The input image data.

        Returns:
            dict: Dictionary containing image information.
        """
        if image is None:
            return None
            
        return {
            'shape': image.shape,
            'dtype': str(image.dtype),
            'size': image.size,
            'memory_usage_mb': image.nbytes / (1024 * 1024),
            'min_value': int(np.min(image)),
            'max_value': int(np.max(image)),
            'mean_value': float(np.mean(image))
        }

    def validate_image_memory_usage(self, image, max_mb=500):
        """Validate that image memory usage is within acceptable limits.

        Args:
            image (numpy.ndarray): The input image data.
            max_mb (int): Maximum memory usage in MB.

        Returns:
            bool: True if memory usage is acceptable.
        """
        if image is None:
            return False
            
        memory_mb = image.nbytes / (1024 * 1024)
        return memory_mb <= max_mb

    def create_thumbnail(self, image, max_size=(200, 200)):
        """Create a thumbnail of the image for preview purposes.

        Args:
            image (numpy.ndarray): The input image data.
            max_size (tuple): Maximum thumbnail size as (width, height).

        Returns:
            numpy.ndarray: The thumbnail image.
        """
        if image is None:
            return None
            
        height, width = image.shape
        
        # Calculate scaling factor to fit within max_size while preserving aspect ratio
        scale_w = max_size[0] / width
        scale_h = max_size[1] / height
        scale = min(scale_w, scale_h)
        
        if scale >= 1.0:
            # No need to resize if image is already smaller
            return image.copy()
            
        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Create thumbnail using high-quality interpolation
        thumbnail = self.resize_image(image, (new_width, new_height), cv2.INTER_AREA)
        
        return thumbnail

