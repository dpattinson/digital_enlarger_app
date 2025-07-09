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
    def test_controller_initializes_all_components_correctly_when_given_main_window(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that controller initialization sets up all components correctly."""
        # GIVEN: A mock main window for the controller
        main_window = self.mock_main_window
        
        # WHEN: We initialize the controller
        controller = Controller(main_window)
        
        # THEN: All components should be initialized correctly
        self.assertEqual(controller.main_window, main_window)
        mock_lut_manager.assert_called_once()
        mock_image_processor.assert_called_once()
        mock_display_window.assert_called_once()
        
        # AND THEN: Initial state should be properly set
        self.assertIsNone(controller.current_image_path)
        self.assertIsNone(controller.loaded_image)
        self.assertIsNone(controller.loaded_lut)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_controller_connects_all_ui_signals_correctly_when_initialized(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that all UI signals are properly connected during initialization."""
        # GIVEN: A mock main window with UI components
        main_window = self.mock_main_window
        
        # WHEN: We initialize the controller
        controller = Controller(main_window)
        
        # THEN: All UI signals should be connected to appropriate methods
        main_window.browse_image_button.clicked.connect.assert_called_with(controller.select_image)
        main_window.browse_lut_button.clicked.connect.assert_called_with(controller.select_lut)
        main_window.process_image_button.clicked.connect.assert_called_with(controller.process_image)
        main_window.print_button.clicked.connect.assert_called_with(controller.start_print)
        main_window.stop_button.clicked.connect.assert_called_with(controller.stop_print)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_loads_and_displays_image_when_given_valid_file_path(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image selection successfully loads and displays a valid image file."""
        # GIVEN: A controller with mocked components and a valid image file
        controller = Controller(self.mock_main_window)
        valid_image_path = self.test_image_path
        expected_image_data = self.test_image_data
        
        # AND GIVEN: File dialog returns the valid image path
        self.mock_main_window.get_image_file.return_value = valid_image_path
        controller.image_processor.load_image.return_value = expected_image_data
        
        # WHEN: We select an image
        controller.select_image()
        
        # THEN: The image should be loaded and stored correctly
        self.assertEqual(controller.current_image_path, valid_image_path)
        np.testing.assert_array_equal(controller.loaded_image, expected_image_data)
        
        # AND THEN: UI should be updated with success messages and image display
        self.mock_main_window.update_processing_summary.assert_any_call(
            f"Image selected: {os.path.basename(valid_image_path)}"
        )
        self.mock_main_window.update_processing_summary.assert_any_call("Image loaded successfully.")
        self.mock_main_window.display_image_in_preview.assert_called_with(expected_image_data)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_does_nothing_when_no_file_selected_in_dialog(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image selection handles gracefully when user cancels file dialog."""
        # GIVEN: A controller and file dialog that returns None (user cancelled)
        controller = Controller(self.mock_main_window)
        self.mock_main_window.get_image_file.return_value = None
        
        # WHEN: We attempt to select an image but cancel the dialog
        controller.select_image()
        
        # THEN: No changes should be made to the controller state
        self.assertIsNone(controller.current_image_path)
        self.assertIsNone(controller.loaded_image)
        
        # AND THEN: No image processing should be attempted
        controller.image_processor.load_image.assert_not_called()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_image_handles_load_error_gracefully_when_image_processor_fails(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image selection handles load errors gracefully and shows error message."""
        # GIVEN: A controller and an image file that causes loading to fail
        controller = Controller(self.mock_main_window)
        problematic_image_path = self.test_image_path
        error_message = "Invalid image format"
        
        # AND GIVEN: File dialog returns the path but image processor fails
        self.mock_main_window.get_image_file.return_value = problematic_image_path
        controller.image_processor.load_image.side_effect = ValueError(error_message)
        
        # WHEN: We attempt to select the problematic image
        controller.select_image()
        
        # THEN: The path should be stored but image should remain None
        self.assertEqual(controller.current_image_path, problematic_image_path)
        self.assertIsNone(controller.loaded_image)
        
        # AND THEN: Error message should be displayed and preview cleared
        self.mock_main_window.update_processing_summary.assert_any_call(f"Error loading image: {error_message}")
        self.mock_main_window.display_image_in_preview.assert_called_with(None)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_loads_lut_successfully_when_given_valid_file_path(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that LUT selection successfully loads a valid LUT file."""
        # GIVEN: A controller with mocked components and a valid LUT file
        controller = Controller(self.mock_main_window)
        valid_lut_path = self.test_lut_path
        expected_lut_data = self.test_lut_data
        
        # AND GIVEN: File dialog returns the valid LUT path
        self.mock_main_window.get_lut_file.return_value = valid_lut_path
        controller.lut_manager.load_lut.return_value = expected_lut_data
        
        # WHEN: We select a LUT
        controller.select_lut()
        
        # THEN: The LUT should be loaded and stored correctly
        np.testing.assert_array_equal(controller.loaded_lut, expected_lut_data)
        
        # AND THEN: UI should be updated with success message
        self.mock_main_window.update_processing_summary.assert_called_with(
            f"LUT selected: {os.path.basename(valid_lut_path)}"
        )

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_shows_message_when_no_file_selected_in_dialog(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that LUT selection shows appropriate message when user cancels file dialog."""
        # GIVEN: A controller and file dialog that returns None (user cancelled)
        controller = Controller(self.mock_main_window)
        self.mock_main_window.get_lut_file.return_value = None
        
        # WHEN: We attempt to select a LUT but cancel the dialog
        controller.select_lut()
        
        # THEN: No LUT should be loaded
        self.assertIsNone(controller.loaded_lut)
        
        # AND THEN: Appropriate message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("No LUT selected.")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_select_lut_handles_load_error_gracefully_when_lut_manager_fails(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that LUT selection handles load errors gracefully and shows error message."""
        # GIVEN: A controller and a LUT file that causes loading to fail
        controller = Controller(self.mock_main_window)
        problematic_lut_path = self.test_lut_path
        error_message = "Invalid LUT format"
        
        # AND GIVEN: File dialog returns the path but LUT manager fails
        self.mock_main_window.get_lut_file.return_value = problematic_lut_path
        controller.lut_manager.load_lut.side_effect = ValueError(error_message)
        
        # WHEN: We attempt to select the problematic LUT
        controller.select_lut()
        
        # THEN: No LUT should be loaded
        self.assertIsNone(controller.loaded_lut)
        
        # AND THEN: Error message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with(f"Error loading LUT: {error_message}")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_applies_lut_and_inversion_when_given_valid_image_and_lut(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image processing applies LUT and inversion correctly with valid inputs."""
        # GIVEN: A controller with loaded image and LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # AND GIVEN: Expected processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        
        # WHEN: We process the image
        controller.process_image()
        
        # THEN: LUT should be applied and image should be inverted
        controller.image_processor.apply_lut.assert_called_once_with(self.test_image_data, self.test_lut_data)
        controller.image_processor.invert_image.assert_called_once_with(processed_image)
        
        # AND THEN: UI should be updated with progress messages and final result
        self.mock_main_window.update_processing_summary.assert_any_call("Processing image...")
        self.mock_main_window.update_processing_summary.assert_any_call("LUT applied.")
        self.mock_main_window.update_processing_summary.assert_any_call("Image inverted.")
        self.mock_main_window.update_processing_summary.assert_any_call("Image processed and displayed in preview.")
        self.mock_main_window.display_image_in_preview.assert_called_with(inverted_image)

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_shows_error_when_no_image_loaded(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image processing shows error message when no image is loaded."""
        # GIVEN: A controller with no loaded image but with loaded LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = None
        controller.loaded_lut = self.test_lut_data
        
        # WHEN: We attempt to process without an image
        controller.process_image()
        
        # THEN: An error message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("Please load an image first.")
        
        # AND THEN: No processing should be attempted
        controller.image_processor.apply_lut.assert_not_called()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_shows_error_when_no_lut_selected(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image processing shows error message when no LUT is selected."""
        # GIVEN: A controller with loaded image but no LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = None
        
        # WHEN: We attempt to process without a LUT
        controller.process_image()
        
        # THEN: An error message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("Please select a LUT first.")
        
        # AND THEN: No processing should be attempted
        controller.image_processor.apply_lut.assert_not_called()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_process_image_handles_processing_error_gracefully_when_image_processor_fails(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that image processing handles errors gracefully when processing fails."""
        # GIVEN: A controller with loaded image and LUT but processing will fail
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        error_message = "Processing error"
        
        # AND GIVEN: Image processor will raise an error
        controller.image_processor.apply_lut.side_effect = ValueError(error_message)
        
        # WHEN: We attempt to process the image
        controller.process_image()
        
        # THEN: Error should be handled gracefully with appropriate message
        self.mock_main_window.update_processing_summary.assert_any_call(f"Error during processing: {error_message}")

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_processes_and_displays_frames_when_given_valid_inputs(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that print start processes image and displays frames correctly."""
        # GIVEN: A controller with loaded image and LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        
        # AND GIVEN: Expected processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        frames_8bit = [np.array([[100, 150, 200]], dtype=np.uint8) for _ in range(4)]
        
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        controller.image_processor.emulate_12bit_to_8bit_frames.return_value = frames_8bit
        
        # WHEN: We start the print process
        controller.start_print()
        
        # THEN: Complete processing pipeline should be executed
        controller.image_processor.apply_lut.assert_called_once_with(self.test_image_data, self.test_lut_data)
        controller.image_processor.invert_image.assert_called_once_with(processed_image)
        controller.image_processor.emulate_12bit_to_8bit_frames.assert_called_once_with(inverted_image)
        
        # AND THEN: Display window should be configured and started
        controller.display_window.set_frames.assert_called_once_with(frames_8bit, 30000)
        controller.display_window.show_on_secondary_monitor.assert_called_once()
        controller.display_window.start_display_loop.assert_called_once()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_uses_default_exposure_when_given_invalid_exposure_input(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that print start uses default exposure when user input is invalid."""
        # GIVEN: A controller with loaded image and LUT but invalid exposure input
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = self.test_lut_data
        self.mock_main_window.exposure_input.text.return_value = "invalid"
        
        # AND GIVEN: Expected processing results
        processed_image = np.array([[2000, 4000, 6000], [8000, 10000, 12000]], dtype=np.uint16)
        inverted_image = 65535 - processed_image
        frames_8bit = [np.array([[100, 150, 200]], dtype=np.uint8) for _ in range(4)]
        
        controller.image_processor.apply_lut.return_value = processed_image
        controller.image_processor.invert_image.return_value = inverted_image
        controller.image_processor.emulate_12bit_to_8bit_frames.return_value = frames_8bit
        
        # WHEN: We start the print process with invalid exposure
        controller.start_print()
        
        # THEN: Default exposure should be used (30000ms)
        controller.display_window.set_frames.assert_called_once_with(frames_8bit, 30000)
        
        # AND THEN: Warning message should be displayed
        self.mock_main_window.update_processing_summary.assert_any_call(
            "Invalid exposure duration. Using default 30s."
        )

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_shows_error_when_no_image_loaded(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that print start shows error message when no image is loaded."""
        # GIVEN: A controller with no loaded image but with loaded LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = None
        controller.loaded_lut = self.test_lut_data
        
        # WHEN: We attempt to start printing without an image
        controller.start_print()
        
        # THEN: An error message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("Please load an image first.")
        
        # AND THEN: No processing or display should be attempted
        controller.image_processor.apply_lut.assert_not_called()
        controller.display_window.set_frames.assert_not_called()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_start_print_shows_error_when_no_lut_selected(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that print start shows error message when no LUT is selected."""
        # GIVEN: A controller with loaded image but no LUT
        controller = Controller(self.mock_main_window)
        controller.loaded_image = self.test_image_data
        controller.loaded_lut = None
        
        # WHEN: We attempt to start printing without a LUT
        controller.start_print()
        
        # THEN: An error message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("Please select a LUT first.")
        
        # AND THEN: No processing or display should be attempted
        controller.image_processor.apply_lut.assert_not_called()
        controller.display_window.set_frames.assert_not_called()

    @patch('app.controller.DisplayWindow')
    @patch('app.controller.ImageProcessor')
    @patch('app.controller.LUTManager')
    def test_stop_print_stops_display_loop_and_shows_confirmation_message(self, mock_lut_manager, mock_image_processor, mock_display_window):
        """Test that print stop correctly stops the display loop and shows confirmation."""
        # GIVEN: A controller with display window
        controller = Controller(self.mock_main_window)
        
        # WHEN: We stop the print process
        controller.stop_print()
        
        # THEN: Display loop should be stopped
        controller.display_window.stop_display_loop.assert_called_once()
        
        # AND THEN: Confirmation message should be displayed
        self.mock_main_window.update_processing_summary.assert_called_with("Display loop stopped.")


if __name__ == '__main__':
    unittest.main()

