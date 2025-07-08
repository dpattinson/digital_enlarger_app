"""Controller for the Darkroom Enlarger Application."""
import os
from app.lut_manager import LUTManager
from app.image_processor import ImageProcessor
from app.display_window import DisplayWindow
import tifffile

class Controller:
    """Handles the logic and interactions between the main window, image processor, and LUT manager."""
    def __init__(self, main_window):
        """Initializes the Controller with the main application window.

        Args:
            main_window: The main application window (MainWindow instance).
        """
        self.main_window = main_window
        self.lut_manager = LUTManager(os.path.join(os.path.dirname(__file__), "..", "luts"))
        self.image_processor = ImageProcessor()
        self.display_window = DisplayWindow()

        self.connect_signals()
        #self.populate_luts()

        self.current_image_path = None
        self.loaded_image = None
        self.loaded_lut = None

    def connect_signals(self):
        """Connects UI signals to controller slots."""
        self.main_window.browse_image_button.clicked.connect(self.select_image)
        self.main_window.browse_lut_button.clicked.connect(self.select_lut)
        self.main_window.print_button.clicked.connect(self.start_print)
        self.main_window.stop_button.clicked.connect(self.stop_print)

    #def populate_luts(self):
    #    lut_names = self.lut_manager.get_lut_names()
    #    self.main_window.populate_lut_combo(lut_names)

    def select_image(self):
        """Handles image selection from the file dialog and loads the image."""
        file_path = self.main_window.get_image_file()
        if file_path:
            self.current_image_path = file_path
            self.main_window.update_processing_summary(
                f"Image selected: {os.path.basename(file_path)}"
            )
            try:
                self.loaded_image = self.image_processor.load_image(
                    self.current_image_path
                )
                self.main_window.update_processing_summary("Image loaded successfully.")
            except (FileNotFoundError, ValueError, tifffile.TiffFileError) as e:
                self.main_window.update_processing_summary(f"Error loading image: {e}")
                self.loaded_image = None

    def select_lut(self):
        """Handles LUT selection from the file dialog and loads the LUT."""
        lut_file = self.main_window.get_lut_file()
        if lut_file:
            try:
                self.loaded_lut = self.lut_manager.load_lut(lut_file)
                self.main_window.update_processing_summary(
                    f"LUT selected: {os.path.basename(lut_file)}"
                )
            except (FileNotFoundError, ValueError, tifffile.TiffFileError) as e:
                self.main_window.update_processing_summary(f"Error loading LUT: {e}")
                self.loaded_lut = None
        else:
            self.loaded_lut = None
            self.main_window.update_processing_summary("No LUT selected.")

    def start_print(self):
        """Initiates the image processing and display loop for printing."""
        if self.loaded_image is None:
            self.main_window.update_processing_summary("Please load an image first.")
            return
        if self.loaded_lut is None:
            self.main_window.update_processing_summary("Please select a LUT first.")
            return

        self.main_window.update_processing_summary("Processing image...")
        try:
            # Apply LUT
            processed_image = self.image_processor.apply_lut(
                self.loaded_image, self.loaded_lut
            )
            self.main_window.update_processing_summary("LUT applied.")

            # Invert image
            inverted_image = self.image_processor.invert_image(processed_image)
            self.main_window.update_processing_summary("Image inverted.")

            # Emulate 12-bit frames
            frames_8bit = self.image_processor.emulate_12bit_to_8bit_frames(
                inverted_image
            )
            self.main_window.update_processing_summary(
                f"Generated {len(frames_8bit)} 8-bit frames for 12-bit emulation."
            )

            exposure_duration_str = self.main_window.exposure_input.text()
            try:
                exposure_duration_s = float(exposure_duration_str)
                loop_duration_ms = int(exposure_duration_s * 1000)
            except ValueError:
                self.main_window.update_processing_summary("Invalid exposure duration. "
                                                            "Using default 30s.")
                loop_duration_ms = 30000 # Default to 30 seconds

            self.display_window.set_frames(frames_8bit, loop_duration_ms)
            self.display_window.show_on_secondary_monitor()
            self.display_window.start_display_loop()
            self.main_window.update_processing_summary("Display loop started.")

        except Exception as e:
            self.main_window.update_processing_summary(f"Error during processing: {e}")

    def stop_print(self):
        """Stops the image display loop."""
        self.display_window.stop_display_loop()
        self.main_window.update_processing_summary("Display loop stopped.")


