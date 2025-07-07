from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer
import numpy as np

class DisplayWindow(QWidget):
    def __init__(self):
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
        self.frames = frames
        self.loop_duration_ms = loop_duration_ms
        self.current_frame_index = 0

    def start_display_loop(self):
        if not self.frames:
            print("No frames to display.")
            return

        self.start_time = self.frame_timer.remainingTime() # Not accurate, but for simulation
        self.frame_timer.start(int(self.loop_duration_ms / len(self.frames)))
        self._next_frame()

    def stop_display_loop(self):
        self.frame_timer.stop()
        self.image_label.clear()

    def _next_frame(self):
        if not self.frames:
            self.stop_display_loop()
            return

        frame_data = self.frames[self.current_frame_index]
        h, w = frame_data.shape
        q_image = QImage(frame_data.data, w, h, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)

        # Simple loop duration check (needs more robust implementation for precise timing)
        # if (QTimer.remainingTime() - self.start_time) >= self.loop_duration_ms:
        #     self.stop_display_loop()

    def show_on_secondary_monitor(self, screen_index=1):
        # This is a simplified approach. Proper multi-monitor handling requires QApplication.screens()
        # and moving the window to the geometry of the target screen.
        # For now, it just shows the window.
        self.showMaximized()



