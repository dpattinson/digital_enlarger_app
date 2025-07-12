from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
import numpy as np
import cv2


# noinspection PyUnresolvedReferences
class PrintingWindow(QWidget):
    """
    A full-screen window used to display a sequence of 8-bit grayscale frames
    on a secondary screen for darkroom printing via a transparent LCD (e.g., Sumopai).
    """
    finished = pyqtSignal()  # Signal emitted when printing sequence finishes

    def __init__(self, screen_index=1, fps=16):
        """
        Initialize the printing window.

        Args:
            screen_index (int): Index of the display screen to use.
            fps (int): Frames per second to display the frames.
        """
        super().__init__()
        self.screen_index = screen_index
        self.fps = fps

        self.setWindowTitle("Secondary Display - Darkroom Enlarger")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")  # Ensure background light-blocking

        # Set up layout and QLabel for image rendering
        self.layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Retrieve target screen's geometry
        screens = self.screen().virtualSiblings()
        if screen_index >= len(screens):
            raise IndexError(f"No screen {screen_index}; only {len(screens)} available.")
        self.screen_geometry = screens[screen_index].geometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.setGeometry(self.screen_geometry)
        self.move(self.screen_geometry.left(), self.screen_geometry.top())

        self.frames = []  # List of 8-bit grayscale frames to display
        self.current_frame = 0  # Index of the current frame being shown
        self.total_frames_to_show = 0  # How many frames to show in total for given duration
        self.frames_displayed = 0  # Counter for how many frames have been displayed

        # Timer that triggers frame updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

    def _begin_printing_frame_loop(self):
        """Start the timer that cycles through the image frames at the specified FPS."""
        self.timer.start(1000 // self.fps)

    def start_printing(self, frames: list[np.ndarray], duration: int):
        """
        Start printing the provided frames for a specified duration.

        Args:
            frames (list[np.ndarray]): List of 2D np.uint8 frames to be displayed.
            duration (int): Total display duration in milliseconds.
        """
        # Validate input frames
        if not isinstance(frames, list) or not frames:
            raise ValueError("frames must be a non-empty list of 2D np.uint8 arrays.")

        for i, frame in enumerate(frames):
            if not isinstance(frame, np.ndarray):
                raise ValueError(f"Frame {i} is not a NumPy array.")
            if frame.ndim != 2:
                raise ValueError(f"Frame {i} is not 2D (grayscale).")
            if frame.dtype != np.uint8:
                raise ValueError(f"Frame {i} must have dtype np.uint8, but got {frame.dtype}.")

        # Select appropriate screen and apply geometry
        screen = QApplication.screens()[self.screen_index]
        self.windowHandle().setScreen(screen)
        self.setGeometry(screen.geometry())
        self.move(screen.geometry().topLeft())

        self.screen_width = screen.geometry().width()
        self.screen_height = screen.geometry().height()

        # Decide whether to scale frames (only scale if not Sumopai screen)
        if (self.screen_width, self.screen_height) == (7680, 4320):
            self.frames = frames
        else:
            self.frames = self._scale_frames_to_screen(frames)

        # Compute number of frames to display for the given duration
        self.total_frames_to_show = int((duration / 1000) * self.fps)
        self.frames_displayed = 0
        self.current_frame = 0

        self.showFullScreen()
        QTimer.singleShot(100, self._begin_printing_frame_loop)

    def _scale_frames_to_screen(self, frames):
        """
        Scale and letterbox each frame to fit the screen resolution.

        Args:
            frames (list[np.ndarray]): Original frames.

        Returns:
            list[np.ndarray]: Scaled and padded frames.
        """
        h, w = frames[0].shape
        scale = min(self.screen_height / h, self.screen_width / w, 1.0)
        target_h = int(h * scale)
        target_w = int(w * scale)

        scaled_frames = []
        for frame in frames:
            resized = cv2.resize(frame, (target_w, target_h), interpolation=cv2.INTER_AREA)
            top = (self.screen_height - target_h) // 2
            bottom = self.screen_height - target_h - top
            left = (self.screen_width - target_w) // 2
            right = self.screen_width - target_w - left
            letterboxed = cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=0)
            scaled_frames.append(letterboxed)

        return scaled_frames

    def stop_printing(self):
        """
        Stop the timer and emit the finished signal.
        Called either manually or automatically after the last frame.
        """
        self.timer.stop()
        self.finished.emit()

    def update_frame(self):
        """
        Display the current frame, then schedule the next one.
        Stops automatically when all expected frames have been shown.
        """
        frame = self.frames[self.current_frame]
        h, w = frame.shape
        stride = frame.strides[0]

        # Convert to QImage and show in QLabel
        qimage = QImage(frame.data, w, h, stride, QImage.Format.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.frames_displayed += 1

        # Stop after total desired frames have been displayed
        if self.frames_displayed >= self.total_frames_to_show:
            self.stop_printing()

