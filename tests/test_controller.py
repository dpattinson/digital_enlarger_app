import unittest
import numpy as np
import tifffile
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from app.controller import Controller


class TestController(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Create mock main window
        self.mock_main_window = Mock()
        self.mock_main_window.browse_image_button = Mock()
        self.mock_main_window.browse_lut_button = Mock()
        self.mock_main_window.process_image_button = Mock()
        self.mock_main_window.print_button = Mock()
        self.mock_main_window.stop_button = Mock()
        self.mock_main_window.exposure_input = Mock()
        self.mock_main_window.exposure_input.text.return_value = "30.0"
        
        # Create temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test image and LUT data
        self.test_image_data = np.array([[1000, 2000, 3000], [4000, 5000, 6000]], dtype=np.uint16)
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
        for i in range(256):
            self.test_lut_data[i, :] = np.linspace(0, 65535, 256, dtype=np.uint16)
        
        # Create test files
        self.test_image_path = os.path.join(self.temp_dir, "test_image.tif")
        self.test_lut_path = os.path.join(self.temp_dir, "test_lut.tif")
        tifffile.imwrite(self.test_image_path, self.test_image_data)
        tifffile.imwrite(self.test_lut_path, self.test_lut_data)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_controller_initialization(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test controller initialization."""
        controller = Controller(self.mock_main_window)
        
        # Verify components are initialized
        self.assertEqual(controller.main_window, self.mock_main_window)
        mock_lut_manager.assert_called_once()
        mock_image_processor.assert_called_once()
        mock_display_window.assert_called_once()
        
        # Verify initial state
        self.assertIsNone(controller.current_image_path)
        self.assertIsNone(controller.loaded_image)
        self.assertIsNone(controller.loaded_lut)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_connect_signals(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test signal connections."""
        controller = Controller(self.mock_main_window)
        
        # Verify signals are connected
        self.mock_main_window.browse_image_button.clicked.connect.assert_called_with(controller.select_image)
        self.mock_main_window.browse_lut_button.clicked.connect.assert_called_with(controller.select_lut)
        self.mock_main_window.process_image_button.clicked.connect.assert_called_with(controller.process_image)
        self.mock_main_window.print_button.clicked.connect.assert_called_with(controller.start_print)
        self.mock_main_window.stop_button.clicked.connect.assert_called_with(controller.stop_print)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_success(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test successful image selection."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return
        self.mock_main_window.get_image_file.return_value = self.test_image_path
        
        # Mock image processor
        controller.image_processor.load_image.return_value = self.test_image_data
        
        # Call select_image
        controller.select_image()
        
        # Verify results
        self.assertEqual(controller.current_image_path, self.test_image_path)
        np.testing.assert_array_equal(controller.loaded_image, self.test_image_data)
        
        # Verify UI updates
        self.mock_main_window.update_processing_summary.assert_any_call(
            f"Image selected: {os.path.basename(self.test_image_path)}"
        )
        self.mock_main_window.update_processing_summary.assert_any_call("Image loaded successfully.")
        self.mock_main_window.display_image_in_preview.assert_called_with(self.test_image_data)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_no_file(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test image selection when no file is selected."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return (no file selected)
        self.mock_main_window.get_image_file.return_value = None
        
        # Call select_image
        controller.select_image()
        
        # Verify no changes
        self.assertIsNone(controller.current_image_path)
        self.assertIsNone(controller.loaded_image)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_load_error(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test image selection with load error."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return
        self.mock_main_window.get_image_file.return_value = self.test_image_path
        
        # Mock image processor to raise error
        controller.image_processor.load_image.side_effect = ValueError("Invalid image format")
        
        # Call select_image
        controller.select_image()
        
        # Verify error handling
        self.assertEqual(controller.current_image_path, self.test_image_path)
        self.assertIsNone(controller.loaded_image)
        
        # Verify UI updates
        self.mock_main_window.update_processing_summary.assert_any_call("Error loading image: Invalid image format")
        self.mock_main_window.display_image_in_preview.assert_called_with(None)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_success(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test successful LUT selection."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return
        self.mock_main_window.get_lut_file.return_value = self.test_lut_path
        
        # Mock LUT manager
        controller.lut_manager.load_lut.return_value = self.test_lut_data
        
        # Call select_lut
        controller.select_lut()
        
        # Verify results
        np.testing.assert_array_equal(controller.loaded_lut, self.test_lut_data)
        
        # Verify UI updates
        self.mock_main_window.update_processing_summary.assert_called_with(
            f"LUT selected: {os.path.basename(self.test_lut_path)}"
        )

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_no_file(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test LUT selection when no file is selected."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return (no file selected)
        self.mock_main_window.get_lut_file.return_value = None
        
        # Call select_lut
        controller.select_lut()
        
        # Verify results
        self.assertIsNone(controller.loaded_lut)
        self.mock_main_window.update_processing_summary.assert_called_with("No LUT selected.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_load_error(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test LUT selection with load error."""
        controller = Controller(self.mock_main_window)
        
        # Mock file dialog return
        self.mock_main_window.get_lut_file.return_value = self.test_lut_path
        
        # Mock LUT manager to raise error
        controller.lut_manager.load_lut.side_effect = ValueError("Invalid LUT format")
        
        # Call select_lut
        controller.select_lut()
        
        # Verify error handling
        self.assertIsNone(controller.loaded_lut)
        self.mock_main_window.update_processing_summary.assert_called_with("Error loading LUT: Invalid LUT format")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_success(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test successful image processing."""
        controller = Controller(self.mock_main_window)
        
        # Set up loaded image and LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # Mock processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        
        # Call process_image
        controller.process_image()
        
        # Verify processing calls
        controller.image_processor.apply_lut.assert_called_once_with(self.test_image_data, self.test_lut_data)
        controller.image_processor.invert_image.assert_called_once_with(processed_image)
        
        # Verify UI updates
        self.mock_main_window.update_processing_summary.assert_any_call("Processing image...")
        self.mock_main_window.update_processing_summary.assert_any_call("LUT applied.")
        self.mock_main_window.update_processing_summary.assert_any_call("Image inverted.")
        self.mock_main_window.update_processing_summary.assert_any_call("Image processed and displayed in preview.")
        self.mock_main_window.display_image_in_preview.assert_called_with(inverted_image)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_no_image(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test image processing without loaded image."""
        controller = Controller(self.mock_main_window)
        
        # No loaded image
        controller.loaded_image = None
        controller.loaded_lut = self.test_lut_data
        
        # Call process_image
        controller.process_image()
        
        # Verify error message
        self.mock_main_window.update_processing_summary.assert_called_with("Please load an image first.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_no_lut(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test image processing without loaded LUT."""
        controller = Controller(self.mock_main_window)
        
        # No loaded LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = None
        
        # Call process_image
        controller.process_image()
        
        # Verify error message
        self.mock_main_window.update_processing_summary.assert_called_with("Please select a LUT first.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_processing_error(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test image processing with processing error."""
        controller = Controller(self.mock_main_window)
        
        # Set up loaded image and LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # Mock processing error
        controller.image_processor.apply_lut.side_effect = ValueError("Processing error")
        
        # Call process_image
        controller.process_image()
        
        # Verify error handling
        self.mock_main_window.update_processing_summary.assert_any_call("Error during processing: Processing error")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_success(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test successful print start."""
        controller = Controller(self.mock_main_window)
        
        # Set up loaded image and LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # Mock processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        frames_8bit = [np.array([[100, 150, 200]], dtype=np.uint8) for _ in range(4)]
        
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        controller.image_processor.emulate_12bit_to_8bit_frames.return_value = frames_8bit
        
        # Call start_print
        controller.start_print()
        
        # Verify processing calls
        controller.image_processor.apply_lut.assert_called_once_with(self.test_image_data, self.test_lut_data)
        controller.image_processor.invert_image.assert_called_once_with(processed_image)
        controller.image_processor.emulate_12bit_to_8bit_frames.assert_called_once_with(inverted_image)
        
        # Verify display window calls
        controller.display_window.set_frames.assert_called_once_with(frames_8bit, 30000)
        controller.display_window.show_on_secondary_monitor.assert_called_once()
        controller.display_window.start_display_loop.assert_called_once()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_invalid_exposure(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test print start with invalid exposure duration."""
        controller = Controller(self.mock_main_window)
        
        # Set up loaded image and LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # Mock invalid exposure input
        self.mock_main_window.exposure_input.text.return_value = "invalid"
        
        # Mock processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        frames_8bit = [np.array([[100, 150, 200]], dtype=np.uint8) for _ in range(4)]
        
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        controller.image_processor.emulate_12bit_to_8bit_frames.return_value = frames_8bit
        
        # Call start_print
        controller.start_print()
        
        # Verify default exposure is used (30000ms)
        controller.display_window.set_frames.assert_called_once_with(frames_8bit, 30000)
        self.mock_main_window.update_processing_summary.assert_any_call(
            "Invalid exposure duration. Using default 30s."
        )

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_no_image(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test print start without loaded image."""
        controller = Controller(self.mock_main_window)
        
        # No loaded image
        controller.loaded_image = None
        controller.loaded_lut = self.test_lut_data
        
        # Call start_print
        controller.start_print()
        
        # Verify error message
        self.mock_main_window.update_processing_summary.assert_called_with("Please load an image first.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_no_lut(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test print start without loaded LUT."""
        controller = Controller(self.mock_main_window)
        
        # No loaded LUT
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = None
        
        # Call start_print
        controller.start_print()
        
        # Verify error message
        self.mock_main_window.update_processing_summary.assert_called_with("Please select a LUT first.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_stop_print(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test stopping print."""
        controller = Controller(self.mock_main_window)
        
        # Call stop_print
        controller.stop_print()
        
        # Verify display window call
        controller.display_window.stop_display_loop.assert_called_once()
        self.mock_main_window.update_processing_summary.assert_called_with("Display loop stopped.")


if __name__ == '__main__':
    unittest.main()

