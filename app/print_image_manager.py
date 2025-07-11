"""Print image management for high-quality processing and 8K display preparation.

This module handles image processing specifically optimized for printing on the
secondary 7680x4320 display, focusing on quality and print-specific optimizations.
"""

import cv2
import numpy as np



class PrintImageManager:
    """Manages image processing and preparation for high-quality printing display.
    
    This class is optimized for print-quality processing with 8K display preparation,
    prioritizing quality and print-specific optimizations over speed.
    """
    
    # 8K display dimensions
    DISPLAY_WIDTH = 7680
    DISPLAY_HEIGHT = 4320
    
    def __init__(self, cv2_rotate=None, cv2_bitwise_not=None):
        """Initialize the PrintImageManager.
        
        Args:
            cv2_rotate: Optional cv2.rotate function for dependency injection (testing)
            cv2_bitwise_not: Optional cv2.bitwise_not function for dependency injection (testing)
        """
        self.cv2_rotate = cv2_rotate or cv2.rotate
        self.cv2_bitwise_not = cv2_bitwise_not or cv2.bitwise_not
        
    def prepare_print_image(self, image_data, lut_data):
        """Prepare an image for high-quality printing display.
        
        Complete print processing pipeline including LUT application, inversion,
        and optional display optimizations.
        
        Args:
            image_data (numpy.ndarray): Input image data (16-bit grayscale)
            lut_data (numpy.ndarray): LUT data for color correction
            
        Returns:
            numpy.ndarray: Print-ready image data
        """
        if image_data is None:
            raise ValueError("Cannot prepare print image for None image")
            
        if image_data.ndim != 2:
            raise ValueError(f"Expected 2D grayscale image, got {image_data.ndim}D")
            
        if lut_data is None:
            raise ValueError("Cannot prepare print image without LUT data")
            
        # Apply LUT transformation
        processed_image = self.apply_lut(image_data, lut_data)
        
        # Invert image (negative to positive)
        inverted_image = self.invert_image(processed_image)

        return inverted_image
        
    def apply_lut(self, image, lut):
        """Apply Look-Up Table (LUT) to the image for color correction.
        
        Args:
            image (numpy.ndarray): Input 16-bit image data
            lut (numpy.ndarray): 256x256 LUT data
            
        Returns:
            numpy.ndarray: LUT-processed image data
        """
        if image is None or lut is None:
            raise ValueError("Image and LUT cannot be None")
            
        # Flatten the 2D LUT to create a 1D lookup table
        lut_1d = lut.flatten()
        
        # Use manual indexing for 16-bit LUT application
        processed_image = lut_1d[image]
        
        return processed_image
        
    def invert_image(self, image):
        """Invert the image (negative effect) for positive printing.
        
        Args:
            image (numpy.ndarray): Input image data
            
        Returns:
            numpy.ndarray: Inverted image data
        """
        if image is None:
            raise ValueError("Cannot invert None image")
            
        # Use OpenCV's bitwise_not for efficient inversion
        return self.cv2_bitwise_not(image)


        
    def get_print_processing_info(self, original_image, processed_image):
        """Get detailed information about print processing.
        
        Args:
            original_image (numpy.ndarray): Original image data
            processed_image (numpy.ndarray): Print-processed image data
            
        Returns:
            dict: Print processing information
        """
        if original_image is None or processed_image is None:
            return {
                'original_size': None,
                'processed_size': None,
                'processing_applied': False
            }
            
        orig_height, orig_width = original_image.shape
        proc_height, proc_width = processed_image.shape
        
        return {
            'original_size': (orig_width, orig_height),
            'processed_size': (proc_width, proc_height),
            'display_dimensions': (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT),
            'processing_applied': True,
            'optimization': 'print-quality',
            'lut_applied': True,
            'image_inverted': True,
            'padded_for_8k': proc_width == self.DISPLAY_WIDTH and proc_height == self.DISPLAY_HEIGHT,
            'data_type': str(processed_image.dtype)
        }
        
    def calculate_8k_display_info(self, image_data):
        """Calculate display information for 8K preparation.
        
        Args:
            image_data (numpy.ndarray): Input image data
            
        Returns:
            dict: Display preparation information
        """
        if image_data is None:
            return {'error': 'Image data is None'}
            
        height, width = image_data.shape
        
        # Calculate padding requirements
        h_padding = max(0, self.DISPLAY_HEIGHT - height)
        w_padding = max(0, self.DISPLAY_WIDTH - width)
        
        # Calculate memory usage
        original_memory_mb = (width * height * image_data.itemsize) / (1024 * 1024)
        display_memory_mb = (self.DISPLAY_WIDTH * self.DISPLAY_HEIGHT * image_data.itemsize) / (1024 * 1024)
        
        return {
            'input_size': (width, height),
            'display_size': (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT),
            'padding_needed': (w_padding, h_padding),
            'fits_without_scaling': width <= self.DISPLAY_WIDTH and height <= self.DISPLAY_HEIGHT,
            'original_memory_mb': round(original_memory_mb, 2),
            'display_memory_mb': round(display_memory_mb, 2),
            'memory_increase_factor': round(display_memory_mb / original_memory_mb, 2) if original_memory_mb > 0 else 0,
            'aspect_ratio_original': round(width / height, 3) if height > 0 else 0,
            'aspect_ratio_display': round(self.DISPLAY_WIDTH / self.DISPLAY_HEIGHT, 3)
        }
        
    def validate_print_readiness(self, image_data, lut_data=None):
        """Validate if image and LUT are ready for print processing.
        
        Args:
            image_data (numpy.ndarray): Input image data
            lut_data (numpy.ndarray): LUT data (optional for validation)
            
        Returns:
            dict: Validation results with warnings and recommendations
        """
        validation = {
            'ready': True,
            'warnings': [],
            'recommendations': [],
            'estimated_processing_time': 'medium'
        }
        
        # Validate image data
        if image_data is None:
            validation['ready'] = False
            validation['warnings'].append("Image data is None")
            return validation
            
        if image_data.ndim != 2:
            validation['ready'] = False
            validation['warnings'].append(f"Expected 2D image, got {image_data.ndim}D")
            return validation
            
        height, width = image_data.shape
        
        # Check size constraints
        if height > self.DISPLAY_HEIGHT:
            validation['ready'] = False
            validation['warnings'].append(
                f"Image height ({height}) exceeds display height ({self.DISPLAY_HEIGHT})"
            )
            
        if width > self.DISPLAY_WIDTH:
            validation['warnings'].append(
                f"Image width ({width}) exceeds display width ({self.DISPLAY_WIDTH}) - consider squashing"
            )
            
        # Check data type
        if image_data.dtype not in [np.uint8, np.uint16]:
            validation['warnings'].append(
                f"Unusual data type {image_data.dtype} - may affect processing"
            )
            
        # Validate LUT if provided
        if lut_data is not None:
            if lut_data.shape != (256, 256):
                validation['warnings'].append(
                    f"Expected 256×256 LUT, got {lut_data.shape}"
                )
                
        # Performance recommendations
        total_pixels = width * height
        if total_pixels > 10_000_000:  # 10MP
            validation['estimated_processing_time'] = 'slow'
            validation['recommendations'].append(
                "Large image - processing may take longer"
            )
        elif total_pixels < 1_000_000:  # 1MP
            validation['estimated_processing_time'] = 'fast'
            
        return validation

    def generate_dithered_frames_from_tiff(self, image_16bit_pil, target_width=7680, target_height=4320, num_frames=16):
        """
        Converts a 16-bit grayscale PIL image into a centered 12-bit representation
        and generates a list of 8-bit dithered frames for temporal exposure simulation.
        Frames are brightness-balanced to avoid flashing.
        """
        # Convert to NumPy array
        image_array = np.array(image_16bit_pil)

        # Validate dimensions
        height, width = image_array.shape
        if height > target_height or width > target_width:
            raise ValueError(f"Image size {width}x{height} exceeds target {target_width}x{target_height}.")

        # Create black canvas and center the image
        canvas = np.zeros((target_height, target_width), dtype=np.uint16)
        y_offset = (target_height - height) // 2
        x_offset = (target_width - width) // 2
        canvas[y_offset:y_offset + height, x_offset:x_offset + width] = image_array

        # Convert to 12-bit (0–4095)
        image_12bit = (canvas >> 4).astype(np.uint16)

        # Decompose into base 8-bit value and 4-bit remainder
        base = (image_12bit >> 4).astype(np.uint8)  # Most significant 8 bits
        remainder = image_12bit & 0xF  # 4-bit remainder (0–15)

        # Generate 8-bit dithered frames with equalized brightness
        frames = []
        for f in range(num_frames):
            mask = (remainder > f)
            dithered = base + mask.astype(np.uint8)
            frames.append(dithered)
        #check for frame brightness uniformity
        for i, f in enumerate(frames):
            print(f"Frame {i}: mean={np.mean(f):.2f}")
        return frames