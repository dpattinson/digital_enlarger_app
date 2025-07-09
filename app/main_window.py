"""Main application window for the Darkroom Enlarger Application."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QHBoxLayout, QFileDialog, QTextEdit
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import numpy as np
from datetime import datetime
from app.image_display_manager import ImageDisplayManager

class MainWindow(QMainWindow):
    """The main window of the application, handling UI elements and user interactions."""
    def __init__(self, display_manager=None, file_dialog=None):
        """Initializes the MainWindow and sets up the UI.
        
        Args:
            display_manager: ImageDisplayManager instance for testable image display logic.
                           Defaults to ImageDisplayManager() if not provided.
            file_dialog: File dialog interface for file selection.
                        Defaults to QtFileDialog() if not provided.
        """
        super().__init__()
        self.display_manager = display_manager or ImageDisplayManager()
        
        # Import here to avoid circular imports
        from app.view_interfaces import QtFileDialog
        self.file_dialog = file_dialog or QtFileDialog()
        self.setWindowTitle("Darkroom Enlarger App")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface elements and their layout."""
        # Tone Map Selector
        lut_layout = QHBoxLayout()
        self.lut_label = QLabel("Tone Map LUT:")
        self.lut_path_display = QLineEdit()
        self.lut_path_display.setReadOnly(True)
        self.browse_lut_button = QPushButton("Browse LUT")
        lut_layout.addWidget(self.lut_label)
        lut_layout.addWidget(self.lut_path_display)
        lut_layout.addWidget(self.browse_lut_button)
        self.layout.addLayout(lut_layout)

        # Image Loader
        image_layout = QHBoxLayout()
        self.image_label = QLabel("Input Image:")
        self.image_path_display = QLineEdit()
        self.image_path_display.setReadOnly(True)
        self.browse_image_button = QPushButton("Browse")
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.image_path_display)
        image_layout.addWidget(self.browse_image_button)
        self.layout.addLayout(image_layout)

        # Preview Area
        self.preview_label = QLabel("No Image Loaded")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set fixed size with 16:9 aspect ratio (7680:4320 scaled down)
        self.preview_label.setFixedSize(768, 432)  # 16:9 aspect ratio
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        self.layout.addWidget(self.preview_label)

        # Process Image Control
        process_layout = QHBoxLayout()
        self.process_image_button = QPushButton("Process Image")
        process_layout.addWidget(self.process_image_button)
        process_layout.addStretch()  # Add stretch to left-align the button
        self.layout.addLayout(process_layout)

        # Processing Summary - Scrollable Log
        processing_log_label = QLabel("Processing Log:")
        self.layout.addWidget(processing_log_label)
        
        self.processing_log = QTextEdit()
        self.processing_log.setReadOnly(True)
        self.processing_log.setMaximumHeight(120)  # Limit height to keep it compact
        self.processing_log.setStyleSheet("""
            QTextEdit { 
                background-color: #2a2a2a; 
                color: #f0f0f0; 
                border: 1px solid #555555; 
                padding: 5px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        self.layout.addWidget(self.processing_log)
        
        # Initialize with ready message
        self.add_log_entry("Application ready")

        # Print Control
        print_control_layout = QHBoxLayout()
        self.print_button = QPushButton("Start Print")
        self.stop_button = QPushButton("Stop Print")
        self.exposure_label = QLabel("Exposure Duration (s):")
        self.exposure_input = QLineEdit("30") # Default to 30 seconds
        self.exposure_input.setFixedWidth(50)

        print_control_layout.addWidget(self.print_button)
        print_control_layout.addWidget(self.stop_button)
        print_control_layout.addStretch()
        print_control_layout.addWidget(self.exposure_label)
        print_control_layout.addWidget(self.exposure_input)
        self.layout.addLayout(print_control_layout)

        # Darkroom-friendly styling (basic)
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: #f0f0f0; }
            QLabel { color: #f0f0f0; }
            QPushButton { background-color: #333333; color: #f0f0f0; \
                          border: 1px solid #555555; padding: 10px; }
            QPushButton:hover { background-color: #555555; }
            QComboBox { background-color: #333333; color: #f0f0f0; \
                        border: 1px solid #555555; padding: 5px; }
            QLineEdit { background-color: #333333; color: #f0f0f0; \
                        border: 1px solid #555555; padding: 5px; }
        """)

        # Example of red-on-black for critical elements (adjust as needed)
        self.stop_button.setStyleSheet("""
            QPushButton { background-color: #800000; color: #ffcccc; \
                          border: 1px solid #ff0000; padding: 10px; }
            QPushButton:hover { background-color: #a00000; }
        """)

    def get_image_file(self):
        """Opens a file dialog to select a 16-bit TIFF image.

        Returns:
            str: The path to the selected image file, or None if no file is selected.
        """
        file_path, _ = self.file_dialog.get_open_filename(
            self, "Select 16-bit TIFF Image", "", "TIFF Images (*.tif *.tiff)"
        )
        if file_path:
            self.image_path_display.setText(file_path)
            return file_path
        return None

    def get_lut_file(self):
        """Opens a file dialog to select a LUT file.

        Returns:
            str: The path to the selected LUT file, or None if no file is selected.
        """
        file_path, _ = self.file_dialog.get_open_filename(
            self, "Select LUT File", "", "LUT Files (*.tif *.tiff)"
        )
        if file_path:
            self.lut_path_display.setText(file_path)
            return file_path
        return None

    def add_log_entry(self, text):
        """Adds a new entry to the processing log with timestamp.

        Args:
            text (str): The text to add to the processing log.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {text}"
        self.processing_log.append(log_entry)
        
        # Auto-scroll to bottom to show latest entry
        scrollbar = self.processing_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_processing_summary(self, text):
        """Updates the processing log with the given text (maintains backward compatibility).

        Args:
            text (str): The text to add to the processing log.
        """
        self.add_log_entry(text)

    def clear_processing_log(self):
        """Clears all entries from the processing log."""
        self.processing_log.clear()
        self.add_log_entry("Log cleared")

    def display_image_in_preview(self, image_data):
        """Displays the given image data in the preview_label.

        Args:
            image_data (numpy.ndarray): The image data (16-bit grayscale) to display.
        """
        # Use ImageDisplayManager for all display logic
        container_size = (self.preview_label.width(), self.preview_label.height())
        display_info = self.display_manager.calculate_display_info(image_data, container_size)
        
        if display_info['show_placeholder']:
            self.preview_label.setText(display_info['placeholder_text'])
            self.preview_label.clear()
            return

        
        # Create QImage from processed data
        display_data = display_info['display_data']
        qt_params = display_info['qt_params']
        
        q_image = QImage(
            display_data.data,
            qt_params['width'],
            qt_params['height'],
            qt_params['bytes_per_line'],
            QImage.Format.Format_Grayscale16
        )

        pixmap = QPixmap.fromImage(q_image)

        # Scale pixmap to fit within the 16:9 container while preserving aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.setText("")  # Clear text once image is displayed


