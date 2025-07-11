from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
import numpy as np
from PIL import Image

class NewDisplayWindow(QWidget):
    finished = pyqtSignal()

    def __init__(self, screen_index=1, fps=25):
        super().__init__()
        self.screen_index = screen_index  # 🔑 Store for later use
        self.setWindowTitle("Secondary Display - Darkroom Enlarger")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")

        self.layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Determine target screen geometry
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
        black = np.zeros((self.screen_height, self.screen_width), dtype=np.uint8)
        qimage = QImage(black.data, self.screen_width, self.screen_height, self.screen_width, QImage.Format.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(qimage))

    def start_printing(self, frames: list[np.ndarray], duration: float):
        """Starts the printing sequence on screen[1] (MacBook display) without blanking external display."""
        self.frames = self._scale_frames_to_screen(frames)
        self.current_frame = 0

        # 🔧 Explicitly assign the window to screen[1] (MacBook)
        screen = QApplication.screens()[1]  # MacBook internal screen
        self.windowHandle().setScreen(screen)  # ✅ Prevents fullscreen from hijacking other screen
        self.setGeometry(screen.geometry())
        self.move(screen.geometry().topLeft())

        self.showFullScreen()  # ✅ Now this will *only* go fullscreen on the MacBook
        self.show_black_frame()

        QTimer.singleShot(100, self._begin_loop)
        self.stop_timer.start(int(duration * 1000))

    def stop_printing(self):
        """Stops playback and resets the screen to black."""
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
        """Resize and letterbox frames to screen resolution."""
        h, w = frames[0].shape
        scale = min(self.screen_height / h, self.screen_width / w, 1.0)
        target_h = int(h * scale)
        target_w = int(w * scale)

        scaled_frames = []
        for frame in frames:
            img = Image.fromarray(frame, mode='L')
            img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas = Image.new('L', (self.screen_width, self.screen_height), color=0)
            x_offset = (self.screen_width - target_w) // 2
            y_offset = (self.screen_height - target_h) // 2
            canvas.paste(img_resized, (x_offset, y_offset))
            scaled_frames.append(np.array(canvas))
        return scaled_frames