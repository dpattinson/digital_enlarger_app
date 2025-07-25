"""Image display management for the Darkroom Enlarger Application using OpenCV.

This module contains testable logic for image display operations,
separated from PyQt6 UI dependencies, enhanced with OpenCV capabilities.
"""
import numpy as np
import cv2
from typing import Tuple, Optional


class ImageDisplayManager:
    """Handles image display logic without UI dependencies using OpenCV.
    
    This class contains pure logic for image processing and display calculations
    that can be easily tested without requiring PyQt6 or UI components.
    Enhanced with OpenCV for better performance and quality.
    """
    
    def __init__(self):
        """Initialize the ImageDisplayManager with OpenCV backend."""
        pass
    
    def validate_image_data(self, image_data: Optional[np.ndarray]) -> bool:
        """Validate that image data is suitable for display.
        
        Args:
            image_data: The image data to validate.
            
        Returns:
            bool: True if image data is valid, False otherwise.
        """
        if image_data is None:
            return False
        
        if not isinstance(image_data, np.ndarray):
            return False
        
        if image_data.ndim != 2:  # Must be 2D grayscale
            return False
        
        if image_data.dtype != np.uint16:  # Must be 16-bit
            return False
        
        return True
    
    def calculate_scaled_size(self, image_size: Tuple[int, int], 
                            container_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate scaled image size that fits within container while preserving aspect ratio.
        
        Args:
            image_size: (width, height) of the original image.
            container_size: (width, height) of the container.
            
        Returns:
            Tuple[int, int]: (width, height) of the scaled image.
        """
        img_width, img_height = image_size
        container_width, container_height = container_size
        
        if img_width == 0 or img_height == 0:
            return (0, 0)
        
        # Calculate scaling factors for both dimensions
        width_scale = container_width / img_width
        height_scale = container_height / img_height
        
        # Use the smaller scale to ensure image fits within container
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        return (new_width, new_height)
    
    def scale_image_for_display(self, image_data: np.ndarray, 
                               target_size: Tuple[int, int],
                               interpolation: int = cv2.INTER_LANCZOS4) -> np.ndarray:
        """Scale image using OpenCV with high-quality interpolation.
        
        Args:
            image_data: The input image data.
            target_size: Target size as (width, height).
            interpolation: OpenCV interpolation method.
            
        Returns:
            np.ndarray: The scaled image.
            
        Raises:
            ValueError: If image data is invalid or target size is invalid.
        """
        if not self.validate_image_data(image_data):
            raise ValueError("Invalid image data for scaling")
            
        if target_size[0] <= 0 or target_size[1] <= 0:
            raise ValueError("Target size must be positive")
        
        # Use OpenCV's resize with high-quality interpolation
        # INTER_LANCZOS4 provides excellent quality for both upscaling and downscaling
        scaled_image = cv2.resize(image_data, target_size, interpolation=interpolation)
        
        return scaled_image
    
    def prepare_image_for_qt_display(self, image_data: np.ndarray, 
                                   target_size: Optional[Tuple[int, int]] = None) -> Tuple[np.ndarray, int, int, int]:
        """Prepare 16-bit grayscale image data for Qt display with optional scaling.
        
        Args:
            image_data: 16-bit grayscale image data.
            target_size: Optional target size for scaling (width, height).
            
        Returns:
            Tuple containing:
            - Contiguous array suitable for QImage
            - Width
            - Height  
            - Bytes per line
            
        Raises:
            ValueError: If image data is invalid.
        """
        if not self.validate_image_data(image_data):
            raise ValueError("Invalid image data for display")
        
        # Scale image if target size is specified
        if target_size is not None:
            display_image = self.scale_image_for_display(image_data, target_size)
        else:
            display_image = image_data
        
        height, width = display_image.shape
        
        # Ensure data is contiguous for QImage
        display_image = np.ascontiguousarray(display_image)
        
        # For 16-bit grayscale, bytes per line = width * 2
        bytes_per_line = width * 2
        
        return display_image, width, height, bytes_per_line
    
    def calculate_display_info(self, image_data: Optional[np.ndarray], 
                             container_size: Tuple[int, int]) -> dict:
        """Calculate all information needed for image display with OpenCV enhancements.
        
        Args:
            image_data: The image data to display.
            container_size: Size of the display container.
            
        Returns:
            dict: Display information including validity, dimensions, scaling info.
        """
        result = {
            'is_valid': False,
            'show_placeholder': True,
            'placeholder_text': "No Image Loaded",
            'image_size': (0, 0),
            'scaled_size': (0, 0),
            'display_data': None,
            'qt_params': None,
            'memory_usage_mb': 0.0,
            'scaling_factor': 0.0
        }
        
        if not self.validate_image_data(image_data):
            return result
        
        try:
            height, width = image_data.shape
            image_size = (width, height)
            scaled_size = self.calculate_scaled_size(image_size, container_size)
            
            # Calculate scaling factor
            scaling_factor = min(container_size[0] / width, container_size[1] / height)
            
            # Prepare Qt display parameters with scaling
            display_array, disp_width, disp_height, bytes_per_line = self.prepare_image_for_qt_display(
                image_data, scaled_size
            )
            
            # Calculate memory usage
            memory_usage_mb = image_data.nbytes / (1024 * 1024)
            
            result.update({
                'is_valid': True,
                'show_placeholder': False,
                'placeholder_text': "",
                'image_size': image_size,
                'scaled_size': scaled_size,
                'display_data': display_array,
                'qt_params': {
                    'width': disp_width,
                    'height': disp_height,
                    'bytes_per_line': bytes_per_line
                },
                'memory_usage_mb': memory_usage_mb,
                'scaling_factor': scaling_factor
            })
            
        except Exception as e:
            result['placeholder_text'] = f"Error preparing image: {str(e)}"
        
        return result