"""Test mode display window for the Darkroom Enlarger Application."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
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
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.image_label)

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._next_frame)
        self.frames = []
        self.current_frame_index = 0
        self.loop_duration_ms = 0

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


    def set_image(self, image_data):
        """Sets and displays a 16-bit grayscale image directly.

        Args:
            image_data (numpy.ndarray): 16-bit grayscale image data to display.
        """
        if image_data is None:
            self.clear_image()
            return

        h, w = image_data.shape
        
        # Create QImage from 16-bit grayscale data
        q_image = QImage(image_data.data, w, h, w * 2, QImage.Format.Format_Grayscale16)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit the test window while maintaining aspect ratio
        # This simulates how the image would appear on the secondary display
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)

    def clear_image(self):
        """Clears the displayed image."""
        self.image_label.clear()

