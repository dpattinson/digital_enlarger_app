"""Controller for the Darkroom Enlarger Application with separated preview/print concerns."""
import os
import cv2
import tifffile
from app.lut_manager import LUTManager
from app.image_processor import ImageProcessor
from app.display_window import DisplayWindow
from app.test_display_window import TestDisplayWindow
from app.preview_image_manager import PreviewImageManager
from app.print_image_manager import PrintImageManager

class Controller:
    """Handles the logic and interactions with separated preview and print processing pipelines."""
    
    def __init__(self, main_window):
        """Initializes the Controller with separated preview and print managers.

        Args:
            main_window: The main application window (MainWindow instance).
        """
        self.main_window = main_window
        self.lut_manager = LUTManager(os.path.join(os.path.dirname(__file__), "..", "luts"))
        self.image_processor = ImageProcessor()
        self.display_window = DisplayWindow()
        self.test_display_window = TestDisplayWindow()
        
        # Separate managers for preview and print concerns
        self.preview_manager = PreviewImageManager()
        self.print_manager = PrintImageManager()

        self.connect_signals()

        self.current_image_path = None
        self.loaded_image = None
        self.loaded_lut = None
        self.processed_image = None  # Store processed image (LUT + inversion applied)

    def connect_signals(self):
        """Connects UI signals to controller slots."""
        self.main_window.browse_image_button.clicked.connect(self.select_image)
        self.main_window.browse_lut_button.clicked.connect(self.select_lut)
        self.main_window.process_image_button.clicked.connect(self.process_image)
        self.main_window.print_button.clicked.connect(self.start_print)
        self.main_window.stop_button.clicked.connect(self.stop_print)
        self.main_window.test_mode_button.clicked.connect(self.main_window.toggle_test_mode)

    def select_image(self):
        """Handles image selection from the file dialog and loads the image."""
        file_path = self.main_window.get_image_file()
        if file_path:
            self.current_image_path = file_path
            self.main_window.add_log_entry(
                f"Image selected: {os.path.basename(file_path)}"
            )
            try:
                # Load image and check if rotation was applied
                original_image = self.image_processor.cv2_reader(file_path, cv2.IMREAD_UNCHANGED)
                self.loaded_image = self.image_processor.load_image(file_path)
                
                # Clear any previously processed image
                self.processed_image = None
                
                # Validate that the image is 16-bit grayscale TIFF
                self._validate_input_image(file_path, self.loaded_image)
                
                # Check if rotation was applied and log it
                if (original_image is not None and 
                    self.image_processor.is_portrait_orientation(original_image)):
                    self.main_window.add_log_entry(
                        "Portrait image detected - rotated 90° clockwise to landscape"
                    )
                
                # Update preview display using preview manager
                self.update_preview_display()
                
            except (ValueError, TypeError, RuntimeError) as e:
                self.main_window.add_log_entry(f"Error loading image: {e}")

    def update_preview_display(self):
        """Update the preview display using the preview manager (fast, preview-optimized)."""
        if self.loaded_image is None:
            return
            
        try:
            # Use processed image if available, otherwise use original loaded image
            display_image = self.processed_image if self.processed_image is not None else self.loaded_image
            
            # Use preview manager for fast preview display
            preview_pixmap = self.preview_manager.create_preview_pixmap(
                display_image, 
                container_size=(768, 432)  # Match actual preview_label size (16:9 aspect ratio)
            )
            
            # Display in preview area
            self.main_window.display_preview_pixmap(preview_pixmap)
            
            # Log what type of image is being displayed
            image_type = "processed (LUT + inverted)" if self.processed_image is not None else "original"
            self.main_window.add_log_entry(f"Preview updated ({image_type})")
            
        except (ValueError, TypeError, RuntimeError) as e:
            self.main_window.add_log_entry(f"Error updating preview: {e}")

    def select_lut(self):
        """Handles LUT selection from the file dialog and loads the LUT."""
        file_path = self.main_window.get_lut_file()
        if file_path:
            self.main_window.add_log_entry(
                f"LUT selected: {os.path.basename(file_path)}"
            )
            try:
                self.loaded_lut = self.lut_manager.load_lut(file_path)
                self.main_window.add_log_entry("LUT loaded successfully")
            except (ValueError, TypeError, RuntimeError) as e:
                self.main_window.add_log_entry(f"Error loading LUT: {e}")

    def process_image(self):
        """Process the image by applying LUT and inversion, then display in preview."""
        if self.loaded_image is None:
            self.main_window.add_log_entry("Please load an image first.")
            return
        if self.loaded_lut is None:
            self.main_window.add_log_entry("Please select a LUT first.")
            return

        try:
            self.main_window.add_log_entry("Processing image (applying LUT and inversion)...")
            
            # Apply LUT using image processor
            lut_applied = self.image_processor.apply_lut(self.loaded_image, self.loaded_lut)
            
            # Apply inversion using image processor  
            self.processed_image = self.image_processor.invert_image(lut_applied)
            
            # Update preview display to show processed image
            self.update_preview_display()
            self.main_window.add_log_entry("Image processed and displayed in preview (LUT applied + inverted).")

        except (ValueError, TypeError, RuntimeError) as e:
            self.main_window.add_log_entry(f"Error during processing: {e}")

    def start_print(self):
        """Initiates the high-quality print processing and display loop."""
        if self.loaded_image is None:
            self.main_window.add_log_entry("Please load an image first.")
            return
        if self.loaded_lut is None:
            self.main_window.add_log_entry("Please select a LUT first.")
            return

        self.main_window.add_log_entry("Processing image for printing...")
        try:
            # Use processed image if available, otherwise use original image with LUT processing
            if self.processed_image is not None:
                # Use already processed image (LUT + inversion applied)
                print_ready_image = self.processed_image
                self.main_window.add_log_entry("Using processed image for printing (LUT + inversion already applied)")
            else:
                # Use print manager for high-quality print processing
                print_ready_image = self.print_manager.prepare_print_image(
                    self.loaded_image, 
                    self.loaded_lut
                )
                self.main_window.add_log_entry("Print processing completed")
            
            # Generate frames for 12-bit emulation
            frames_8bit = self.print_manager.emulate_12bit_to_8bit_frames(print_ready_image)
            self.main_window.add_log_entry(
                f"Generated {len(frames_8bit)} 8-bit frames for 12-bit emulation"
            )

            # Get exposure duration from UI
            exposure_duration_str = self.main_window.exposure_input.text()
            try:
                exposure_duration_s = float(exposure_duration_str)
                loop_duration_ms = int(exposure_duration_s * 1000)
            except ValueError:
                self.main_window.add_log_entry("Invalid exposure duration. Using default 30s.")
                loop_duration_ms = 30000  # Default to 30 seconds

            # Configure and start display based on test mode
            if self.main_window.is_test_mode_enabled():
                # Test mode: use windowed display
                # self.test_display_window.set_frames(frames_8bit, loop_duration_ms)
                self.test_display_window.show_test_window()
                self.test_display_window.display_simple_print_image(print_ready_image)
                # self.test_display_window.start_display_loop()
                self.main_window.add_log_entry("Print started in test mode (windowed display)")
            else:
                # Normal mode: use fullscreen secondary monitor
                self.display_window.set_frames(frames_8bit, loop_duration_ms)
                self.display_window.show_on_secondary_monitor()
                self.display_window.start_display_loop()
                self.main_window.add_log_entry("Print started on secondary monitor")

        except (ValueError, TypeError, RuntimeError) as e:
            self.main_window.add_log_entry(f"Error during print processing: {e}")

    def stop_print(self):
        """Stops the image display loop for both normal and test mode."""
        # Stop both display windows to ensure clean state
        self.display_window.stop_display_loop()
        self.test_display_window.stop_display()
        self.main_window.add_log_entry("Print stopped")
        
    def get_preview_info(self):
        """Get information about current preview processing.
        
        Returns:
            dict: Preview processing information
        """
        if self.loaded_image is None:
            return {'error': 'No image loaded'}
            
        # Get preview info from preview manager
        preview_image = self.preview_manager.prepare_preview_image(self.loaded_image)
        return self.preview_manager.get_preview_info(self.loaded_image, preview_image)
        
    def get_print_info(self):
        """Get information about current print processing capabilities.
        
        Returns:
            dict: Print processing information
        """
        if self.loaded_image is None:
            return {'error': 'No image loaded'}
            
        # Get print info from print manager
        return self.print_manager.calculate_8k_display_info(self.loaded_image)
        
    def validate_print_readiness(self):
        """Validate if current image and LUT are ready for printing.
        
        Returns:
            dict: Validation results
        """
        return self.print_manager.validate_print_readiness(self.loaded_image, self.loaded_lut)


    def _validate_input_image(self, file_path, image_data):
        """Validate that the input image is a 16-bit grayscale TIFF file.
        
        Args:
            file_path (str): Path to the image file
            image_data (numpy.ndarray): Loaded image data
            
        Raises:
            ValueError: If the image doesn't meet requirements
        """
        import os
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ['.tif', '.tiff']:
            raise ValueError(f"Invalid file format: {file_ext}. Expected .tif or .tiff")
        
        # Check if image data is valid
        if image_data is None:
            raise ValueError("Failed to load image data")
        
        # Check if image is grayscale (2D array)
        if len(image_data.shape) != 2:
            raise ValueError(f"Expected grayscale image (2D), got {len(image_data.shape)}D image")
        
        # Check if image is 16-bit
        if image_data.dtype != 'uint16':
            raise ValueError(f"Expected 16-bit image (uint16), got {image_data.dtype}")
        
        # Log successful validation
        height, width = image_data.shape
        self.main_window.add_log_entry(
            f"Image validated: {width}×{height} 16-bit grayscale TIFF"
        )

