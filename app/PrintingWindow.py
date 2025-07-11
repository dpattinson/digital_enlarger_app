from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
import numpy as np
import cv2

class PrintingWindow(QWidget):
    finished = pyqtSignal()

    def __init__(self, screen_index=1, fps=25):
        super().__init__()
        self.screen_index = screen_index
        self.setWindowTitle("Secondary Display - Darkroom Enlarger")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: white;")

        self.layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Get screen geometry
        screens = self.screen().virtualSiblings()
        if screen_index >= len(screens):
            raise IndexError(f"No screen {screen_index}; only {len(screens)} available.")
        self.screen_geometry = screens[screen_index].geometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        self.setGeometry(self.screen_geometry)
        self.move(self.screen_geometry.left(), self.screen_geometry.top())

        self.fps = fps
        self.frames = []
        self.current_frame = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.stop_timer = QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_printing)

    def show_black_frame(self):
        white = np.full((self.screen_height, self.screen_width), 255, dtype=np.uint8)
        qimage = QImage(white.data, self.screen_width, self.screen_height, self.screen_width, QImage.Format.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

    def _begin_printing_frame_loop(self):
        self.timer.start(1000 // self.fps)

    def start_printing(self, frames: list[np.ndarray], duration: float):
        """Starts the printing sequence on screen[1] with validated 8-bit grayscale frames."""

        # 🔍 Validate input frames
        if not isinstance(frames, list) or not frames:
            raise ValueError("frames must be a non-empty list of 2D np.uint8 arrays.")

        for i, frame in enumerate(frames):
            if not isinstance(frame, np.ndarray):
                raise ValueError(f"Frame {i} is not a NumPy array.")
            if frame.ndim != 2:
                raise ValueError(f"Frame {i} is not 2D (grayscale).")
            if frame.dtype != np.uint8:
                raise ValueError(f"Frame {i} must have dtype np.uint8, but got {frame.dtype}.")

        self.frames = self._scale_frames_to_screen(frames)
        self.current_frame = 0

        screen = QApplication.screens()[self.screen_index]
        self.windowHandle().setScreen(screen)
        self.setGeometry(screen.geometry())
        self.move(screen.geometry().topLeft())

        self.showFullScreen()
        self.show_black_frame()

        QTimer.singleShot(100, self._begin_printing_frame_loop)
        self.stop_timer.start(int(duration * 1000))

    def stop_printing(self):
        self.timer.stop()
        self.show_black_frame()
        self.finished.emit()

    def update_frame(self):
        frame = self.frames[self.current_frame]
        h, w = frame.shape
        qimage = QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(qimage))
        self.current_frame = (self.current_frame + 1) % len(self.frames)

    def _scale_frames_to_screen(self, frames):
        """Resize and letterbox frames using OpenCV."""
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