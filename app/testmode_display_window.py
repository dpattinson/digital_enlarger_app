"""Test mode display window for the Darkroom Enlarger Application."""
import numpy as np
import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class TestDisplayWindow(QWidget):
    """A windowed display for testing print output with the same aspect ratio as the secondary display."""

    def __init__(self):
        """Initializes the TestDisplayWindow with 16:9 aspect ratio matching the secondary display."""
        super().__init__()
        self.setWindowTitle("Test Mode - Print Output Preview")

        self.window_width = 1280
        self.window_height = 720  # 16:9 aspect ratio

        self.setFixedSize(self.window_width, self.window_height)
        self.setStyleSheet("background-color: black;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.image_label = QLabel()
        self.image_label.setFixedSize(self.window_width, self.window_height)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)

    def stop_display(self):
        """Stops the display loop and clears the displayed image."""
        self.image_label.clear()

    def show_test_window(self):
        """Shows the test display window in windowed mode."""
        self.move(100, 100)
        self.show()
        self.raise_()
        self.activateWindow()

    def get_display_info(self):
        """Get information about the test display window."""
        return {
            'window_size': (self.window_width, self.window_height),
            'aspect_ratio': self.window_width / self.window_height,
            'simulates_secondary_display': '7680x4320 (16:9)',
            'mode': 'windowed_test'
        }

    def display_simple_print_image(self, image_data: np.ndarray):
        """Display a scaled and padded 8-bit version of a 16-bit grayscale image."""
        if image_data.dtype != np.uint16 or image_data.ndim != 2:
            raise ValueError("Input image must be a 2D NumPy array with dtype=np.uint16")

        resized_image = self.resize_by_height(image_data, self.window_height)

        height, width = resized_image.shape
        if height > self.window_height or width > self.window_width:
            raise ValueError(f"Resized image {width}x{height} exceeds target {self.window_width}x{self.window_height}")

        # Create black canvas
        canvas = np.zeros((self.window_height, self.window_width), dtype=np.uint16)
        y_offset = (self.window_height - height) // 2
        x_offset = (self.window_width - width) // 2
        canvas[y_offset:y_offset + height, x_offset:x_offset + width] = resized_image

        # Convert to 8-bit
        image_8bit = (canvas / 256).astype(np.uint8)

        qimage = QImage(image_8bit.data, self.window_width, self.window_height, self.window_width, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

    def resize_by_height(self, image_array: np.ndarray, target_height: int) -> np.ndarray:
        """Resizes a 16-bit grayscale NumPy array based on height, preserving aspect ratio."""
        original_height, original_width = image_array.shape
        scale = target_height / original_height
        target_width = int(original_width * scale)

        resized = cv2.resize(image_array, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized