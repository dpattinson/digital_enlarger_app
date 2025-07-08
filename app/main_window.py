"""Main application window for the Darkroom Enlarger Application."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QLineEdit, QHBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    """The main window of the application, handling UI elements and user interactions."""
    def __init__(self):
        """Initializes the MainWindow and sets up the UI."""
        super().__init__()
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

        # Preview Area (Optional - Placeholder)
        self.preview_label = QLabel("Preview Area (Optional)")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray; min-height: 150px;")
        self.layout.addWidget(self.preview_label)

        # Processing Summary
        self.processing_summary_label = QLabel("Processing Summary: Ready")
        self.layout.addWidget(self.processing_summary_label)

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
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select 16-bit TIFF Image", "", "TIFF Images (*.tif *.tiff)"
        )
        if file_path:
            self.image_path_display.setText(file_path)
            return file_path
        return None

    def update_processing_summary(self, text):
        """Updates the processing summary label with the given text.

        Args:
            text (str): The text to display in the processing summary.
        """
        self.processing_summary_label.setText(f"Processing Summary: {text}")

    #def populate_lut_combo(self, lut_files):
    #    """Populates the LUT combo box with available LUT files.
    #
    #    Args:
    #        lut_files (list): A list of LUT filenames.
    #    """
    #    self.lut_combo.clear()
    #    if not lut_files:
    #        self.lut_combo.addItem("No LUTs Found")
    #    else:
    #        self.lut_combo.addItems(lut_files)


