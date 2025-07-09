"""Preview image management for fast display in the main window preview area.

This module handles image processing specifically optimized for preview display,
focusing on speed and responsiveness rather than print quality.
"""

import cv2
import numpy as np
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt


class PreviewImageManager:
    """Manages image processing and display for the main window preview area.
    
    This class is optimized for fast preview display with good-enough quality,
    prioritizing speed and responsiveness over print-quality processing.
    """
    
    def __init__(self, cv2_resize=None):
        """Initialize the PreviewImageManager.
        
        Args:
            cv2_resize: Optional cv2.resize function for dependency injection (testing)
        """
        self.cv2_resize = cv2_resize or cv2.resize
        
    def prepare_preview_image(self, image_data, container_size=(400, 300)):
        """Prepare an image for fast preview display.
        
        Optimizes the image for preview display with fast scaling and good-enough quality.
        Preserves aspect ratio within the container dimensions.
        
        Args:
            image_data (numpy.ndarray): Input image data (16-bit grayscale)
            container_size (tuple): Target container size as (width, height)
            
        Returns:
            numpy.ndarray: Preview-optimized image data (8-bit grayscale)
        """
        if image_data is None:
            raise ValueError("Cannot prepare preview for None image")
            
        if image_data.ndim != 2:
            raise ValueError(f"Expected 2D grayscale image, got {image_data.ndim}D")
            
        # Convert to 8-bit for preview (faster processing)
        if image_data.dtype == np.uint16:
            preview_image = (image_data >> 8).astype(np.uint8)
        else:
            preview_image = image_data.astype(np.uint8)
            
        # Calculate optimal preview size maintaining aspect ratio
        preview_size = self.calculate_preview_size(preview_image.shape, container_size)
        
        # Fast resize using INTER_LINEAR for speed (good enough for preview)
        if preview_size != preview_image.shape[::-1]:  # (width, height) vs (height, width)
            preview_image = self.cv2_resize(
                preview_image, 
                preview_size, 
                interpolation=cv2.INTER_LINEAR
            )
            
        return preview_image
        
    def calculate_preview_size(self, image_shape, container_size):
        """Calculate optimal preview size maintaining aspect ratio.
        
        Args:
            image_shape (tuple): Image shape as (height, width)
            container_size (tuple): Container size as (width, height)
            
        Returns:
            tuple: Optimal size as (width, height)
        """
        img_height, img_width = image_shape
        container_width, container_height = container_size
        
        # Calculate scaling factors for both dimensions
        width_scale = container_width / img_width
        height_scale = container_height / img_height
        
        # Use the smaller scale to ensure image fits within container
        scale = min(width_scale, height_scale)
        
        # Calculate new dimensions
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        return (new_width, new_height)
        
    def create_preview_pixmap(self, image_data, container_size=(400, 300)):
        """Create a QPixmap optimized for preview display.
        
        Args:
            image_data (numpy.ndarray): Input image data
            container_size (tuple): Target container size as (width, height)
            
        Returns:
            QPixmap: Preview-ready pixmap
        """
        # Prepare preview image
        preview_image = self.prepare_preview_image(image_data, container_size)
        
        # Convert to QPixmap
        return self.numpy_to_pixmap(preview_image)
        
    def numpy_to_pixmap(self, image_data):
        """Convert numpy array to QPixmap for Qt display.
        
        Args:
            image_data (numpy.ndarray): 8-bit grayscale image data
            
        Returns:
            QPixmap: Qt pixmap for display
        """
        if image_data.dtype != np.uint8:
            raise ValueError("Expected 8-bit image data for pixmap conversion")
            
        height, width = image_data.shape
        
        # Create QImage from numpy array
        q_image = QImage(
            image_data.data, 
            width, 
            height, 
            QImage.Format.Format_Grayscale8
        )
        
        # Convert to QPixmap
        return QPixmap.fromImage(q_image)
        
    def get_preview_info(self, original_image, preview_image):
        """Get information about preview processing.
        
        Args:
            original_image (numpy.ndarray): Original image data
            preview_image (numpy.ndarray): Preview-processed image data
            
        Returns:
            dict: Preview processing information
        """
        if original_image is None or preview_image is None:
            return {
                'original_size': None,
                'preview_size': None,
                'scale_factor': None,
                'data_type_conversion': None,
                'processing_applied': False
            }
            
        orig_height, orig_width = original_image.shape
        prev_height, prev_width = preview_image.shape
        
        scale_factor = min(prev_width / orig_width, prev_height / orig_height)
        
        return {
            'original_size': (orig_width, orig_height),
            'preview_size': (prev_width, prev_height),
            'scale_factor': scale_factor,
            'data_type_conversion': f"{original_image.dtype} → {preview_image.dtype}",
            'processing_applied': True,
            'optimization': 'speed-optimized',
            'interpolation': 'INTER_LINEAR'
        }
        
    def validate_preview_readiness(self, image_data, container_size=(400, 300)):
        """Validate if image is ready for preview processing.
        
        Args:
            image_data (numpy.ndarray): Input image data
            container_size (tuple): Target container size
            
        Returns:
            dict: Validation results with warnings and recommendations
        """
        validation = {
            'ready': True,
            'warnings': [],
            'recommendations': [],
            'estimated_processing_time': 'fast'
        }
        
        if image_data is None:
            validation['ready'] = False
            validation['warnings'].append("Image data is None")
            return validation
            
        if image_data.ndim != 2:
            validation['ready'] = False
            validation['warnings'].append(f"Expected 2D image, got {image_data.ndim}D")
            return validation
            
        height, width = image_data.shape
        
        # Check image size for preview optimization
        if width > 4000 or height > 4000:
            validation['recommendations'].append(
                f"Large image ({width}×{height}) - preview will be significantly downscaled"
            )
            
        if width < 100 or height < 100:
            validation['warnings'].append(
                f"Very small image ({width}×{height}) - preview quality may be poor"
            )
            
        # Check data type
        if image_data.dtype not in [np.uint8, np.uint16]:
            validation['warnings'].append(
                f"Unusual data type {image_data.dtype} - may affect preview quality"
            )
            
        return validation

