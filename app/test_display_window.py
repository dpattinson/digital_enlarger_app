"""Test mode display window for the Darkroom Enlarger Application."""
import numpy as np
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer


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
        container_height = self.image_label.height()
        container_width = self.image_label.width()

        # --------- Step 1: Normalize 16-bit -> 8-bit ----------
        # Ensure image_data is numpy.uint16
        image_8bit = (image_data / 256).astype(np.uint8)

        # --------- Step 2: Create QImage (8-bit) ----------
        q_image = QImage(
            image_8bit.data,
            img_width,
            img_height,
            img_width,  # bytes per line for 8-bit
            QImage.Format.Format_Grayscale8
        )

        # --------- Step 3: Scale image by height ----------
        # resized_image = q_image.scaledToHeight(700, Qt.TransformationMode.SmoothTransformation)

        # --------- Step 4: Pad image to label dimensions ----------
        image_padded = self.scale_and_pad_qimage(q_image, container_width, container_height)

        # --------- Step 5: Display ----------
        pixmap = QPixmap.fromImage(image_padded)
        self.image_label.setPixmap(pixmap)

    def scale_and_pad_qimage(self, image: QImage, target_width: int, target_height: int) -> QImage:
        # Scale image preserving aspect ratio, but not bigger than target size
        print("original image format", image.format())
        print("original image size", image.size())
        scaled = image.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
        print("scaled image format", scaled.format())
        print("scaled image size", scaled.size())
        # Create padded image with black background
        padded = QImage(target_width, target_height, QImage.Format.Format_Grayscale8)
        padded.fill(0)  # black for Grayscale8
        print("padded format:", padded.format())
        print("padded size:", padded.size())

        assert not padded.isNull(), "Padded QImage is null"
        pixmap = QPixmap.fromImage(padded)
        assert not pixmap.isNull(), "Generated QPixmap is null"

        # Center scaled image
        x_offset = (target_width - scaled.width()) // 2
        y_offset = (target_height - scaled.height()) // 2

        painter = QPainter(padded)
        painter.drawImage(x_offset, y_offset, scaled)

        from PyQt6.QtGui import QPen

        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawRect(0, 0, padded.width() - 1, padded.height() - 1)
        painter.end()

        return padded