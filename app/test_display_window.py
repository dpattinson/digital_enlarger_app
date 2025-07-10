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

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._next_frame)
        self.frames = []
        self.current_frame_index = 0
        self.loop_duration_ms = 0

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
        resized_image = q_image.scaledToHeight(container_height, Qt.TransformationMode.SmoothTransformation)

        # --------- Step 4: Pad image to label dimensions ----------
        image_padded = self.pad_qimage_to_size(resized_image, container_width, container_height)

        # --------- Step 5: Display ----------
        pixmap = QPixmap.fromImage(image_padded)
        self.image_label.setPixmap(pixmap)

    def set_frames(self, frames, loop_duration_ms):
        """Sets the frames to be displayed and the total loop duration.

        Args:
            frames (list): A list of 8-bit numpy arrays representing image frames.
            loop_duration_ms (int): The total duration of the display loop in milliseconds.
        """
        self.frames = frames
        self.loop_duration_ms = loop_duration_ms
        self.current_frame_index = 0

    def start_display_loop(self):
        """Starts the continuous display loop of image frames."""
        if not self.frames:
            print("No frames to display.")
            return

        # Calculate interval per frame to achieve desired loop duration
        interval_per_frame = int(self.loop_duration_ms / len(self.frames))
        if interval_per_frame <= 500:
            interval_per_frame = 500  # Ensure at least 500ms interval

        self.frame_timer.start(interval_per_frame)
        self._next_frame()

    def stop_display_loop(self):
        """Stops the display loop and clears the displayed image."""
        self.frame_timer.stop()
        self.image_label.clear()

    def _next_frame(self):
        """Displays the next frame in the sequence."""
        if not self.frames:
            self.stop_display_loop()
            return

        frame_data = self.frames[self.current_frame_index]
        h, w = frame_data.shape

        # Create QImage from 8-bit grayscale frame
        q_image = QImage(frame_data.data, w, h, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)

        # Scale to fit the test window while maintaining aspect ratio
        # This simulates how the image would appear on the secondary display
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

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

    # Compress image for feeding to monochrome LCD screen

    def pad_qimage_to_size(self, image: QImage, target_width: int, target_height: int) -> QImage:
        # Ensure target size is at least as large as the original image
        if target_width < image.width() or target_height < image.height():
            raise ValueError("Target dimensions must be greater than or equal to the original image size.")

        # Create a new image with the target dimensions and fill it with black
        padded_image = QImage(target_width, target_height, image.format())
        padded_image.fill(QColor(0, 0, 250))  # Black background

        # Compute top-left corner to center the original image
        x_offset = (target_width - image.width()) // 2
        y_offset = (target_height - image.height()) // 2

        # Draw original image into the center of the padded canvas
        painter = QPainter(padded_image)
        painter.drawImage(x_offset, y_offset, image)
        painter.end()

        return padded_image