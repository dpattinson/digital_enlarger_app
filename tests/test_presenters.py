"""Tests for presenter classes."""
import unittest
from unittest.mock import Mock, MagicMock
import numpy as np
from app.presenters import MainWindowPresenter, PrintPresenter
from app.view_interfaces import MockMainView, MockFileDialog


class TestMainWindowPresenter(unittest.TestCase):
    """Test cases for MainWindowPresenter."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_view = MockMainView()
        self.mock_image_model = Mock()
        self.mock_lut_model = Mock()
        
        # Create presenter
        self.presenter = MainWindowPresenter(
            self.mock_view,
            self.mock_image_model,
            self.mock_lut_model
        )
        
        # Test data
        self.test_image_path = "/test/image.tif"
        self.test_lut_path = "/test/lut.tif"
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
    
    def test_initialization(self):
        """Test presenter initialization."""
        self.assertEqual(self.presenter.view, self.mock_view)
        self.assertEqual(self.presenter.image_model, self.mock_image_model)
        self.assertEqual(self.presenter.lut_model, self.mock_lut_model)
        self.assertIsNone(self.presenter.current_image_path)
        self.assertIsNone(self.presenter.loaded_image)
        self.assertIsNone(self.presenter.loaded_lut)
    
    def test_handle_browse_image_success(self):
        """Test successful image browsing workflow."""
        # Setup mock file dialog to return a path
        self.mock_view.file_dialog = MockFileDialog(self.test_image_path)
        self.mock_image_model.load_image.return_value = self.test_image_data
        
        result = self.presenter.handle_browse_image()
        
        self.assertTrue(result)
        self.assertEqual(self.presenter.current_image_path, self.test_image_path)
        self.assertEqual(self.presenter.loaded_image, self.test_image_data)
        
        # Verify view interactions
        self.assertEqual(self.mock_view.image_path, self.test_image_path)
        self.assertEqual(self.mock_view.displayed_image, self.test_image_data)
        self.assertIn("Image loaded successfully", self.mock_view.processing_summary)
    
    def test_handle_browse_image_cancelled(self):
        """Test image browsing when user cancels dialog."""
        # Setup mock file dialog to return None (cancelled)
        self.mock_view.file_dialog = MockFileDialog(None)
        
        result = self.presenter.handle_browse_image()
        
        self.assertFalse(result)
        self.assertIsNone(self.presenter.current_image_path)
        self.assertIsNone(self.presenter.loaded_image)
    
    def test_handle_browse_image_load_error(self):
        """Test image browsing when loading fails."""
        # Setup mock file dialog to return a path
        self.mock_view.file_dialog = MockFileDialog(self.test_image_path)
        self.mock_image_model.load_image.side_effect = Exception("Load failed")
        
        result = self.presenter.handle_browse_image()
        
        self.assertFalse(result)
        self.assertIsNone(self.presenter.loaded_image)
        self.assertIn("Error loading image", self.mock_view.processing_summary)
    
    def test_load_image_success(self):
        """Test direct image loading success."""
        self.mock_image_model.load_image.return_value = self.test_image_data
        
        result = self.presenter.load_image(self.test_image_path)
        
        self.assertTrue(result)
        self.assertEqual(self.presenter.current_image_path, self.test_image_path)
        self.assertEqual(self.presenter.loaded_image, self.test_image_data)
        self.mock_image_model.load_image.assert_called_once_with(self.test_image_path)
    
    def test_handle_browse_lut_success(self):
        """Test successful LUT browsing workflow."""
        # Setup mock file dialog to return a path
        self.mock_view.file_dialog = MockFileDialog(self.test_lut_path)
        self.mock_lut_model.load_lut.return_value = self.test_lut_data
        
        result = self.presenter.handle_browse_lut()
        
        self.assertTrue(result)
        self.assertEqual(self.presenter.loaded_lut, self.test_lut_data)
        
        # Verify view interactions
        self.assertEqual(self.mock_view.lut_path, self.test_lut_path)
        self.assertIn("LUT loaded successfully", self.mock_view.processing_summary)
    
    def test_handle_browse_lut_cancelled(self):
        """Test LUT browsing when user cancels dialog."""
        # Setup mock file dialog to return None (cancelled)
        self.mock_view.file_dialog = MockFileDialog(None)
        
        result = self.presenter.handle_browse_lut()
        
        self.assertFalse(result)
        self.assertIsNone(self.presenter.loaded_lut)
    
    def test_handle_process_image_success(self):
        """Test successful image processing."""
        # Setup loaded image and LUT
        self.presenter.loaded_image = self.test_image_data
        self.presenter.loaded_lut = self.test_lut_data
        
        # Setup mock processing
        lut_applied_image = np.array([[2000, 4000], [6000, 8000]], dtype=np.uint16)
        processed_image = np.array([[63535, 61535], [59535, 57535]], dtype=np.uint16)
        
        self.mock_image_model.apply_lut.return_value = lut_applied_image
        self.mock_image_model.invert_image.return_value = processed_image
        
        result = self.presenter.handle_process_image()
        
        self.assertTrue(result)
        self.mock_image_model.apply_lut.assert_called_once_with(self.test_image_data, self.test_lut_data)
        self.mock_image_model.invert_image.assert_called_once_with(lut_applied_image)
        
        # Verify processed image is displayed
        self.assertEqual(self.mock_view.displayed_image, processed_image)
        self.assertIn("Image processed successfully", self.mock_view.processing_summary)
    
    def test_handle_process_image_no_image(self):
        """Test image processing without loaded image."""
        # Only load LUT, no image
        self.presenter.loaded_lut = self.test_lut_data
        
        result = self.presenter.handle_process_image()
        
        self.assertFalse(result)
        self.assertIn("Please load an image first", self.mock_view.processing_summary)
    
    def test_handle_process_image_no_lut(self):
        """Test image processing without loaded LUT."""
        # Only load image, no LUT
        self.presenter.loaded_image = self.test_image_data
        
        result = self.presenter.handle_process_image()
        
        self.assertFalse(result)
        self.assertIn("Please select a LUT first", self.mock_view.processing_summary)
    
    def test_handle_process_image_processing_error(self):
        """Test image processing when processing fails."""
        # Setup loaded image and LUT
        self.presenter.loaded_image = self.test_image_data
        self.presenter.loaded_lut = self.test_lut_data
        
        # Setup mock processing to fail
        self.mock_image_model.apply_lut.side_effect = Exception("Processing failed")
        
        result = self.presenter.handle_process_image()
        
        self.assertFalse(result)
        self.assertIn("Error during processing", self.mock_view.processing_summary)
    
    def test_can_process_image(self):
        """Test can_process_image logic."""
        # Initially should be False
        self.assertFalse(self.presenter.can_process_image())
        
        # With only image
        self.presenter.loaded_image = self.test_image_data
        self.assertFalse(self.presenter.can_process_image())
        
        # With only LUT
        self.presenter.loaded_image = None
        self.presenter.loaded_lut = self.test_lut_data
        self.assertFalse(self.presenter.can_process_image())
        
        # With both image and LUT
        self.presenter.loaded_image = self.test_image_data
        self.assertTrue(self.presenter.can_process_image())
    
    def test_get_current_state(self):
        """Test current state retrieval."""
        # Initial state
        state = self.presenter.get_current_state()
        expected = {
            'has_image': False,
            'has_lut': False,
            'image_path': None,
            'can_process': False
        }
        self.assertEqual(state, expected)
        
        # With loaded image and LUT
        self.presenter.loaded_image = self.test_image_data
        self.presenter.loaded_lut = self.test_lut_data
        self.presenter.current_image_path = self.test_image_path
        
        state = self.presenter.get_current_state()
        expected = {
            'has_image': True,
            'has_lut': True,
            'image_path': self.test_image_path,
            'can_process': True
        }
        self.assertEqual(state, expected)
    
    def test_reset_state(self):
        """Test state reset."""
        # Setup some state
        self.presenter.loaded_image = self.test_image_data
        self.presenter.loaded_lut = self.test_lut_data
        self.presenter.current_image_path = self.test_image_path
        
        self.presenter.reset_state()
        
        self.assertIsNone(self.presenter.current_image_path)
        self.assertIsNone(self.presenter.loaded_image)
        self.assertIsNone(self.presenter.loaded_lut)
        self.assertEqual(self.mock_view.processing_summary, "Ready")


class TestPrintPresenter(unittest.TestCase):
    """Test cases for PrintPresenter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_view = MockMainView()
        self.mock_display_window = Mock()
        
        self.presenter = PrintPresenter(self.mock_view, self.mock_display_window)
        
        # Test data
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.test_exposure_time = 5.0
    
    def test_initialization(self):
        """Test print presenter initialization."""
        self.assertEqual(self.presenter.view, self.mock_view)
        self.assertEqual(self.presenter.display_window, self.mock_display_window)
        self.assertFalse(self.presenter.is_printing)
    
    def test_handle_start_print_success(self):
        """Test successful print start."""
        result = self.presenter.handle_start_print(self.test_image_data, self.test_exposure_time)
        
        self.assertTrue(result)
        self.assertTrue(self.presenter.is_printing)
        
        # Verify display window interactions
        self.mock_display_window.set_frames.assert_called_once()
        self.mock_display_window.start_display_loop.assert_called_once_with(self.test_exposure_time)
        
        # Verify view update
        self.assertIn("Print started", self.mock_view.processing_summary)
    
    def test_handle_start_print_no_image(self):
        """Test print start without image data."""
        result = self.presenter.handle_start_print(None, self.test_exposure_time)
        
        self.assertFalse(result)
        self.assertFalse(self.presenter.is_printing)
        self.assertIn("No processed image available", self.mock_view.processing_summary)
    
    def test_handle_start_print_invalid_exposure(self):
        """Test print start with invalid exposure time."""
        result = self.presenter.handle_start_print(self.test_image_data, 0.0)
        
        self.assertFalse(result)
        self.assertFalse(self.presenter.is_printing)
        self.assertIn("Invalid exposure time", self.mock_view.processing_summary)
    
    def test_handle_start_print_display_error(self):
        """Test print start when display fails."""
        self.mock_display_window.start_display_loop.side_effect = Exception("Display failed")
        
        result = self.presenter.handle_start_print(self.test_image_data, self.test_exposure_time)
        
        self.assertFalse(result)
        self.assertIn("Error starting print", self.mock_view.processing_summary)
    
    def test_handle_stop_print_success(self):
        """Test successful print stop."""
        # Start printing first
        self.presenter.is_printing = True
        
        result = self.presenter.handle_stop_print()
        
        self.assertTrue(result)
        self.assertFalse(self.presenter.is_printing)
        
        # Verify display window interaction
        self.mock_display_window.stop_display_loop.assert_called_once()
        
        # Verify view update
        self.assertEqual(self.mock_view.processing_summary, "Print stopped")
    
    def test_handle_stop_print_error(self):
        """Test print stop when stop fails."""
        self.mock_display_window.stop_display_loop.side_effect = Exception("Stop failed")
        
        result = self.presenter.handle_stop_print()
        
        self.assertFalse(result)
        self.assertIn("Error stopping print", self.mock_view.processing_summary)
    
    def test_get_print_status(self):
        """Test print status retrieval."""
        # Initially not printing
        status = self.presenter.get_print_status()
        self.assertFalse(status['is_printing'])
        
        # When printing
        self.presenter.is_printing = True
        status = self.presenter.get_print_status()
        self.assertTrue(status['is_printing'])
    
    def test_prepare_frames_for_display(self):
        """Test frame preparation for display."""
        frames = self.presenter._prepare_frames_for_display(self.test_image_data)
        
        # Should return image as single frame
        self.assertEqual(len(frames), 1)
        np.testing.assert_array_equal(frames[0], self.test_image_data)


if __name__ == '__main__':
    unittest.main()

