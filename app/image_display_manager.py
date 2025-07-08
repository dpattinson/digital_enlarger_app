"""Image display management for the Darkroom Enlarger Application.

This module contains testable logic for image display operations,
separated from PyQt6 UI dependencies.
"""
import numpy as np
from typing import Tuple, Optional


class ImageDisplayManager:
    """Handles image display logic without UI dependencies.
    
    This class contains pure logic for image processing and display calculations
    that can be easily tested without requiring PyQt6 or UI components.
    """
    
    def __init__(self):
        """Initialize the ImageDisplayManager."""
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
    
    def prepare_image_for_qt_display(self, image_data: np.ndarray) -> Tuple[np.ndarray, int, int, int]:
        """Prepare 16-bit grayscale image data for Qt display.
        
        Args:
            image_data: 16-bit grayscale image data.
            
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
        
        height, width = image_data.shape
        
        # Ensure data is contiguous for QImage
        display_image = np.ascontiguousarray(image_data)
        
        # For 16-bit grayscale, bytes per line = width * 2
        bytes_per_line = width * 2
        
        return display_image, width, height, bytes_per_line
    
    def calculate_display_info(self, image_data: Optional[np.ndarray], 
                             container_size: Tuple[int, int]) -> dict:
        """Calculate all information needed for image display.
        
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
            'qt_params': None
        }
        
        if not self.validate_image_data(image_data):
            return result
        
        try:
            # Prepare Qt display parameters
            display_array, width, height, bytes_per_line = self.prepare_image_for_qt_display(image_data)
            
            # Calculate scaling
            image_size = (width, height)
            scaled_size = self.calculate_scaled_size(image_size, container_size)
            
            result.update({
                'is_valid': True,
                'show_placeholder': False,
                'placeholder_text': "",
                'image_size': image_size,
                'scaled_size': scaled_size,
                'display_data': display_array,
                'qt_params': {
                    'width': width,
                    'height': height,
                    'bytes_per_line': bytes_per_line
                }
            })
            
        except Exception as e:
            result['placeholder_text'] = f"Error preparing image: {str(e)}"
        
        return result
    
    def get_aspect_ratio(self, size: Tuple[int, int]) -> float:
        """Calculate aspect ratio from size tuple.
        
        Args:
            size: (width, height) tuple.
            
        Returns:
            float: Aspect ratio (width/height), or 0 if height is 0.
        """
        width, height = size
        return width / height if height > 0 else 0.0
    
    def is_landscape(self, size: Tuple[int, int]) -> bool:
        """Check if image is landscape orientation.
        
        Args:
            size: (width, height) tuple.
            
        Returns:
            bool: True if landscape (width > height), False otherwise.
        """
        width, height = size
        return width > height
    
    def calculate_letterbox_padding(self, image_size: Tuple[int, int], 
                                  container_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate padding needed for letterboxing/pillarboxing.
        
        Args:
            image_size: Size of the scaled image.
            container_size: Size of the container.
            
        Returns:
            Tuple[int, int]: (horizontal_padding, vertical_padding) in pixels.
        """
        img_width, img_height = image_size
        container_width, container_height = container_size
        
        horizontal_padding = max(0, (container_width - img_width) // 2)
        vertical_padding = max(0, (container_height - img_height) // 2)
        
        return (horizontal_padding, vertical_padding)

