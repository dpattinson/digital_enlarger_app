"""Secondary display window for the Darkroom Enlarger Application."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer

class DisplayWindow(QWidget):
    """A window to display the processed image frames for 12-bit emulation."""
    def __init__(self):
        """Initializes the DisplayWindow."""
        super().__init__()
        self.setWindowTitle("Secondary Display - Darkroom Enlarger")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")

        self.layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._next_frame)
        self.frames = []
        self.current_frame_index = 0
        self.loop_duration_ms = 0
        self.start_time = 0

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
            interval_per_frame = 500 # Ensure at least 500ms interval

        self.start_time = self.frame_timer.remainingTime() # Not accurate, but for simulation
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
        # QImage.Format_Grayscale8 is for 8-bit grayscale images
        q_image = QImage(frame_data.data, w, h, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

    def show_on_secondary_monitor(self):
        """Shows the display window, ideally on a secondary monitor if available.

        Note: This is a simplified approach. Proper multi-monitor handling requires
        QApplication.screens() and moving the window to the geometry of the target screen.
        For now, it just shows the window maximized.
        """
        self.showMaximized()


