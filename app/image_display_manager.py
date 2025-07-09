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
    
    def create_preview_image(self, image_data: np.ndarray, 
                           container_size: Tuple[int, int],
                           preserve_aspect_ratio: bool = True) -> np.ndarray:
        """Create a preview image optimized for display container.
        
        Args:
            image_data: The source image data.
            container_size: Size of the display container (width, height).
            preserve_aspect_ratio: Whether to preserve aspect ratio.
            
        Returns:
            np.ndarray: Preview image ready for display.
            
        Raises:
            ValueError: If image data is invalid.
        """
        if not self.validate_image_data(image_data):
            raise ValueError("Invalid image data for preview")
        
        if preserve_aspect_ratio:
            # Calculate size that fits within container while preserving aspect ratio
            height, width = image_data.shape
            target_size = self.calculate_scaled_size((width, height), container_size)
        else:
            # Use container size directly
            target_size = container_size
        
        # Create preview using high-quality scaling
        preview = self.scale_image_for_display(image_data, target_size, cv2.INTER_AREA)
        
        return preview
    
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
    
    def optimize_for_memory(self, image_data: np.ndarray, 
                          max_memory_mb: float = 100.0) -> np.ndarray:
        """Optimize image for memory usage by scaling down if necessary.
        
        Args:
            image_data: The input image data.
            max_memory_mb: Maximum allowed memory usage in MB.
            
        Returns:
            np.ndarray: Optimized image data.
        """
        if not self.validate_image_data(image_data):
            return image_data
        
        current_memory_mb = image_data.nbytes / (1024 * 1024)
        
        if current_memory_mb <= max_memory_mb:
            return image_data
        
        # Calculate scaling factor to reduce memory usage
        scale_factor = np.sqrt(max_memory_mb / current_memory_mb)
        
        height, width = image_data.shape
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Scale down using high-quality interpolation
        optimized = cv2.resize(image_data, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return optimized
    
    def get_image_statistics(self, image_data: np.ndarray) -> dict:
        """Get statistical information about the image.
        
        Args:
            image_data: The input image data.
            
        Returns:
            dict: Statistical information about the image.
        """
        if not self.validate_image_data(image_data):
            return {}
        
        return {
            'min_value': int(np.min(image_data)),
            'max_value': int(np.max(image_data)),
            'mean_value': float(np.mean(image_data)),
            'std_value': float(np.std(image_data)),
            'median_value': float(np.median(image_data)),
            'dynamic_range': int(np.max(image_data) - np.min(image_data))
        }


    # Display Optimization Methods for 7680x4320 Secondary Display
    
    DISPLAY_8K_WIDTH = 7680
    DISPLAY_8K_HEIGHT = 4320
    DISPLAY_8K_SIZE = (DISPLAY_8K_WIDTH, DISPLAY_8K_HEIGHT)
    
    
    def pad_image_for_8k_display(self, image_data: np.ndarray, 
                                center_image: bool = True,
                                border_color: str = "white") -> np.ndarray:
        """Pad image to fit 7680x4320 display with white borders.
        
        Adapted from LCD-Alt-Print-Tools for 8K display dimensions.
        Centers image and adds white padding to fill display area.
        
        Args:
            image_data: Input image data to pad.
            center_image: Whether to center the image (default: True).
            border_color: Border color - only "white" supported (default: "white").
            
        Returns:
            np.ndarray: Padded image sized for 8K display.
            
        Raises:
            ValueError: If image data is invalid or border_color is not "white".
        """
        if not self.validate_image_data(image_data):
            raise ValueError("Invalid image data for padding")
        
        if border_color != "white":
            raise ValueError("Only white borders are supported")
        
        height, width = image_data.shape
        
        # Determine border fill value based on image bit depth
        if image_data.dtype == np.uint16:
            border_value = 65535  # White for 16-bit
        else:
            border_value = 255    # White for 8-bit
        
        # If image is already larger than display, scale it down first
        if width > self.DISPLAY_8K_WIDTH or height > self.DISPLAY_8K_HEIGHT:
            # Calculate scaling to fit within display
            scale_factor = min(self.DISPLAY_8K_WIDTH / width, self.DISPLAY_8K_HEIGHT / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Scale down the image
            image_data = cv2.resize(image_data, (new_width, new_height), 
                                  interpolation=cv2.INTER_AREA)
            height, width = image_data.shape
        
        # Calculate padding needed
        if center_image:
            # Center the image
            pad_x = (self.DISPLAY_8K_WIDTH - width) // 2
            pad_y = (self.DISPLAY_8K_HEIGHT - height) // 2
            
            # Handle odd padding
            pad_x_remainder = (self.DISPLAY_8K_WIDTH - width) % 2
            pad_y_remainder = (self.DISPLAY_8K_HEIGHT - height) % 2
        else:
            # Align to top-left
            pad_x = 0
            pad_y = 0
            pad_x_remainder = 0
            pad_y_remainder = 0
        
        # Create padded image filled with white
        padded_image = np.full((self.DISPLAY_8K_HEIGHT, self.DISPLAY_8K_WIDTH), 
                              border_value, dtype=image_data.dtype)
        
        # Place the original image in the padded area
        start_y = pad_y
        end_y = start_y + height
        start_x = pad_x
        end_x = start_x + width
        
        padded_image[start_y:end_y, start_x:end_x] = image_data
        
        return padded_image
    
    def prepare_image_for_8k_display(self, image_data: np.ndarray,
                                   center_image: bool = True) -> np.ndarray:
        """Complete preparation pipeline for 8K display output.
        
        Pads image for optimal 8K display without squashing.
        
        Args:
            image_data: Input image data.
            center_image: Whether to center the image (default: True).
            
        Returns:
            np.ndarray: Image ready for 8K display.
            
        Raises:
            ValueError: If image data is invalid.
        """
        if not self.validate_image_data(image_data):
            raise ValueError("Invalid image data for 8K display preparation")
        
        # Pad to 8K display dimensions with white borders
        display_ready_image = self.pad_image_for_8k_display(image_data, center_image)
        
        return display_ready_image
    
    def calculate_8k_display_info(self, image_data: Optional[np.ndarray]) -> dict:
        """Calculate display information specifically for 8K display output.
        
        Args:
            image_data: The image data to analyze.
            
        Returns:
            dict: 8K display-specific information.
        """
        result = {
            'is_valid': False,
            'original_size': (0, 0),
            'final_size': self.DISPLAY_8K_SIZE,
            'padding_info': {'x': 0, 'y': 0},
            'memory_usage_mb': 0.0,
            'scaling_applied': False,
            'scaling_factor': 1.0
        }
        
        if not self.validate_image_data(image_data):
            return result
        
        try:
            height, width = image_data.shape
            original_size = (width, height)
            
            # Check if scaling will be needed
            final_width, final_height = original_size
            scaling_applied = (final_width > self.DISPLAY_8K_WIDTH or 
                             final_height > self.DISPLAY_8K_HEIGHT)
            
            if scaling_applied:
                scale_factor = min(self.DISPLAY_8K_WIDTH / final_width, 
                                 self.DISPLAY_8K_HEIGHT / final_height)
                final_width = int(final_width * scale_factor)
                final_height = int(final_height * scale_factor)
            else:
                scale_factor = 1.0
            
            # Calculate padding
            pad_x = (self.DISPLAY_8K_WIDTH - final_width) // 2
            pad_y = (self.DISPLAY_8K_HEIGHT - final_height) // 2
            
            # Calculate memory usage for final 8K image
            memory_usage_mb = (self.DISPLAY_8K_WIDTH * self.DISPLAY_8K_HEIGHT * 2) / (1024 * 1024)
            
            result.update({
                'is_valid': True,
                'original_size': original_size,
                'final_size': self.DISPLAY_8K_SIZE,
                'padding_info': {'x': pad_x, 'y': pad_y},
                'memory_usage_mb': memory_usage_mb,
                'scaling_applied': scaling_applied,
                'scaling_factor': scale_factor
            })
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def validate_8k_display_readiness(self, image_data: np.ndarray) -> dict:
        """Validate if image is ready for 8K display and provide recommendations.
        
        Args:
            image_data: Image data to validate.
            
        Returns:
            dict: Validation results and recommendations.
        """
        result = {
            'is_ready': False,
            'recommendations': [],
            'warnings': [],
            'info': {}
        }
        
        if not self.validate_image_data(image_data):
            result['recommendations'].append("Provide valid 16-bit grayscale image data")
            return result
        
        height, width = image_data.shape
        
        # Check image dimensions
        if width > self.DISPLAY_8K_WIDTH * 2 or height > self.DISPLAY_8K_HEIGHT * 2:
            result['warnings'].append(f"Image is very large ({width}x{height}). Consider pre-scaling for better performance.")
        
        if width < self.DISPLAY_8K_WIDTH // 4 or height < self.DISPLAY_8K_HEIGHT // 4:
            result['warnings'].append(f"Image is quite small ({width}x{height}). Quality may be reduced when scaled to 8K.")
        
        # Check aspect ratio compatibility
        image_aspect = width / height
        display_aspect = self.DISPLAY_8K_WIDTH / self.DISPLAY_8K_HEIGHT
        
        if abs(image_aspect - display_aspect) > 0.5:
            result['recommendations'].append("Consider cropping or adjusting aspect ratio for better 8K display utilization")
        
        # Memory usage check
        memory_mb = image_data.nbytes / (1024 * 1024)
        if memory_mb > 200:
            result['warnings'].append(f"High memory usage ({memory_mb:.1f}MB). Consider optimization.")
        
        # Check if squashing might be beneficial
        if width > self.DISPLAY_8K_WIDTH:
            result['recommendations'].append("Consider applying image squashing for better display optimization")
        
        result['is_ready'] = True
        result['info'] = {
            'dimensions': (width, height),
            'aspect_ratio': image_aspect,
            'memory_mb': memory_mb,
            'display_compatibility': abs(image_aspect - display_aspect) < 0.2
        }
        
        return result

