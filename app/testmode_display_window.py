"""Test mode display window for the Darkroom Enlarger Application."""
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

class TestDisplayWindow(QWidget):
    """A windowed display for testing print output with the same aspect ratio as the secondary display."""

    def __init__(self):
        """Initializes the TestDisplayWindow with 16:9 aspect ratio matching the secondary display."""
        super().__init__()
        self.setWindowTitle("Test Mode - Print Output Preview")

        # Calculate window size maintaining 16:9 aspect ratio (7680:4320)
        # Use a reasonable size for desktop testing (e.g., 960x540 or 1280x720)
        self.window_width = 1280
        self.window_height = 720  # 16:9 aspect ratio

        self.setFixedSize(self.window_width, self.window_height)
        self.setStyleSheet("background-color: black;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full window usage

        self.image_label = QLabel()
        # try explicitly setting image_label size to match window size
        self.image_label.setFixedSize(self.window_width, self.window_height)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)



    def stop_display(self):
        """Stops the display loop and clears the displayed image."""
        self.image_label.clear()


    def show_test_window(self):
        """Shows the test display window in windowed mode."""
        # Position the window away from the main window for better visibility
        self.move(100, 100)
        self.show()
        self.raise_()  # Bring to front
        self.activateWindow()  # Give focus

    def get_display_info(self):
        """Get information about the test display window.
        
        Returns:
            dict: Display information including size and aspect ratio
        """
        return {
            'window_size': (self.window_width, self.window_height),
            'aspect_ratio': self.window_width / self.window_height,
            'simulates_secondary_display': '7680x4320 (16:9)',
            'mode': 'windowed_test'
        }

    def display_simple_print_image(self, image_data):
        """Display a scaled and padded 8-bit version of a 16-bit grayscale image."""

        img_height, img_width = image_data.shape
        target_height = self.image_label.height()
        target_width = self.image_label.width()

        # Convert to NumPy array
        image_array = np.array(image_data)

        # Validate dimensions
        height, width = image_array.shape
        if height > target_height or width > target_width:
            raise ValueError(f"Image size {width}x{height} exceeds target {target_width}x{target_height}.")

        # Create black canvas and center the image
        canvas = np.zeros((target_height, target_width), dtype=np.uint16)
        y_offset = (target_height - height) // 2
        x_offset = (target_width - width) // 2
        canvas[y_offset:y_offset + height, x_offset:x_offset + width] = image_array

        # Normalize 16-bit image to 8-bit
        image_8bit = (canvas / 256).astype(np.uint8)  # Scale 0–65535 → 0–255

        # Convert to QImage (grayscale format)
        height, width = image_8bit.shape
        qimage = QImage(image_8bit.data, width, height, width, QImage.Format.Format_Grayscale8)

        # --------- Step 5: Display ----------
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)

