"""Tests for view interfaces and mock implementations."""
import unittest
from unittest.mock import Mock, patch
from app.view_interfaces import (
    MockFileDialog, MockMessageDisplay, MockMainView,
    MainViewAdapter, QtFileDialog, QtMessageDisplay
)


class TestMockFileDialog(unittest.TestCase):
    """Test cases for MockFileDialog."""
    
    def test_initialization_with_return_path(self):
        """Test initialization with return path."""
        test_path = "/test/file.tif"
        dialog = MockFileDialog(test_path)
        
        self.assertEqual(dialog.return_path, test_path)
        self.assertEqual(len(dialog.call_history), 0)
    
    def test_initialization_without_return_path(self):
        """Test initialization without return path."""
        dialog = MockFileDialog()
        
        self.assertIsNone(dialog.return_path)
        self.assertEqual(len(dialog.call_history), 0)
    
    def test_get_open_filename_with_path(self):
        """Test file dialog with return path."""
        test_path = "/test/file.tif"
        dialog = MockFileDialog(test_path)
        
        result = dialog.get_open_filename(
            None, "Test Title", "/test/dir", "TIFF Files (*.tif)"
        )
        
        self.assertEqual(result, (test_path, "TIFF Files (*.tif)"))
        self.assertEqual(len(dialog.call_history), 1)
        
        call = dialog.call_history[0]
        self.assertEqual(call['title'], "Test Title")
        self.assertEqual(call['directory'], "/test/dir")
        self.assertEqual(call['filter'], "TIFF Files (*.tif)")
    
    def test_get_open_filename_cancelled(self):
        """Test file dialog when cancelled (no return path)."""
        dialog = MockFileDialog(None)
        
        result = dialog.get_open_filename(
            None, "Test Title", "/test/dir", "TIFF Files (*.tif)"
        )
        
        self.assertEqual(result, ("", ""))
        self.assertEqual(len(dialog.call_history), 1)
    
    def test_call_history_tracking(self):
        """Test that call history is properly tracked."""
        dialog = MockFileDialog("/test/file.tif")
        
        # Make multiple calls
        dialog.get_open_filename(None, "Title 1", "/dir1", "Filter 1")
        dialog.get_open_filename(None, "Title 2", "/dir2", "Filter 2")
        
        self.assertEqual(len(dialog.call_history), 2)
        self.assertEqual(dialog.call_history[0]['title'], "Title 1")
        self.assertEqual(dialog.call_history[1]['title'], "Title 2")


class TestMockMessageDisplay(unittest.TestCase):
    """Test cases for MockMessageDisplay."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.display = MockMessageDisplay()
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(len(self.display.messages), 0)
    
    def test_show_info(self):
        """Test info message display."""
        self.display.show_info("Info Title", "Info message")
        
        self.assertEqual(len(self.display.messages), 1)
        self.assertEqual(self.display.messages[0], ('info', "Info Title", "Info message"))
    
    def test_show_warning(self):
        """Test warning message display."""
        self.display.show_warning("Warning Title", "Warning message")
        
        self.assertEqual(len(self.display.messages), 1)
        self.assertEqual(self.display.messages[0], ('warning', "Warning Title", "Warning message"))
    
    def test_show_error(self):
        """Test error message display."""
        self.display.show_error("Error Title", "Error message")
        
        self.assertEqual(len(self.display.messages), 1)
        self.assertEqual(self.display.messages[0], ('error', "Error Title", "Error message"))
    
    def test_get_last_message(self):
        """Test getting last message."""
        # No messages initially
        self.assertIsNone(self.display.get_last_message())
        
        # Add messages
        self.display.show_info("Title 1", "Message 1")
        self.display.show_error("Title 2", "Message 2")
        
        last = self.display.get_last_message()
        self.assertEqual(last, ('error', "Title 2", "Message 2"))
    
    def test_clear_messages(self):
        """Test clearing messages."""
        self.display.show_info("Title", "Message")
        self.assertEqual(len(self.display.messages), 1)
        
        self.display.clear_messages()
        self.assertEqual(len(self.display.messages), 0)
        self.assertIsNone(self.display.get_last_message())


class TestMockMainView(unittest.TestCase):
    """Test cases for MockMainView."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_file_dialog = MockFileDialog("/test/file.tif")
        self.view = MockMainView(self.mock_file_dialog)
    
    def test_initialization(self):
        """Test initialization."""
        self.assertEqual(self.view.file_dialog, self.mock_file_dialog)
        self.assertEqual(self.view.image_path, "")
        self.assertEqual(self.view.lut_path, "")
        self.assertEqual(self.view.processing_summary, "")
        self.assertIsNone(self.view.displayed_image)
        self.assertEqual(len(self.view.method_calls), 0)
    
    def test_update_image_path_display(self):
        """Test image path display update."""
        test_path = "/test/image.tif"
        self.view.update_image_path_display(test_path)
        
        self.assertEqual(self.view.image_path, test_path)
        self.assertEqual(len(self.view.method_calls), 1)
        self.assertEqual(self.view.method_calls[0], ('update_image_path_display', test_path))
    
    def test_update_lut_path_display(self):
        """Test LUT path display update."""
        test_path = "/test/lut.tif"
        self.view.update_lut_path_display(test_path)
        
        self.assertEqual(self.view.lut_path, test_path)
        self.assertEqual(len(self.view.method_calls), 1)
        self.assertEqual(self.view.method_calls[0], ('update_lut_path_display', test_path))
    
    def test_update_processing_summary(self):
        """Test processing summary update."""
        test_message = "Processing complete"
        self.view.update_processing_summary(test_message)
        
        self.assertEqual(self.view.processing_summary, test_message)
        self.assertEqual(len(self.view.method_calls), 1)
        self.assertEqual(self.view.method_calls[0], ('update_processing_summary', test_message))
    
    def test_display_image_in_preview(self):
        """Test image display in preview."""
        test_image = "test_image_data"
        self.view.display_image_in_preview(test_image)
        
        self.assertEqual(self.view.displayed_image, test_image)
        self.assertEqual(len(self.view.method_calls), 1)
        self.assertEqual(self.view.method_calls[0], ('display_image_in_preview', test_image))
    
    def test_show_file_dialog(self):
        """Test file dialog display."""
        result = self.view.show_file_dialog("Test Title", "Test Filter")
        
        self.assertEqual(result, "/test/file.tif")
        self.assertEqual(len(self.view.method_calls), 1)
        self.assertEqual(self.view.method_calls[0], ('show_file_dialog', "Test Title", "Test Filter"))
    
    def test_show_file_dialog_cancelled(self):
        """Test file dialog when cancelled."""
        cancelled_dialog = MockFileDialog(None)
        view = MockMainView(cancelled_dialog)
        
        result = view.show_file_dialog("Test Title", "Test Filter")
        
        self.assertIsNone(result)
    
    def test_get_last_call(self):
        """Test getting last method call."""
        # No calls initially
        self.assertIsNone(self.view.get_last_call())
        
        # Make calls
        self.view.update_image_path_display("/test1.tif")
        self.view.update_lut_path_display("/test2.tif")
        
        last_call = self.view.get_last_call()
        self.assertEqual(last_call, ('update_lut_path_display', "/test2.tif"))
    
    def test_clear_calls(self):
        """Test clearing method calls."""
        self.view.update_image_path_display("/test.tif")
        self.assertEqual(len(self.view.method_calls), 1)
        
        self.view.clear_calls()
        self.assertEqual(len(self.view.method_calls), 0)
        self.assertIsNone(self.view.get_last_call())


class TestMainViewAdapter(unittest.TestCase):
    """Test cases for MainViewAdapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_main_window = Mock()
        self.mock_file_dialog = MockFileDialog("/test/file.tif")
        self.adapter = MainViewAdapter(self.mock_main_window, self.mock_file_dialog)
    
    def test_initialization(self):
        """Test adapter initialization."""
        self.assertEqual(self.adapter.main_window, self.mock_main_window)
        self.assertEqual(self.adapter.file_dialog, self.mock_file_dialog)
    
    def test_initialization_default_file_dialog(self):
        """Test adapter initialization with default file dialog."""
        with patch('app.view_interfaces.QtFileDialog') as mock_qt_dialog:
            adapter = MainViewAdapter(self.mock_main_window)
            mock_qt_dialog.assert_called_once()
    
    def test_update_image_path_display(self):
        """Test image path display update."""
        test_path = "/test/image.tif"
        self.adapter.update_image_path_display(test_path)
        
        self.mock_main_window.image_path_display.setText.assert_called_once_with(test_path)
    
    def test_update_lut_path_display(self):
        """Test LUT path display update."""
        test_path = "/test/lut.tif"
        self.adapter.update_lut_path_display(test_path)
        
        self.mock_main_window.lut_path_display.setText.assert_called_once_with(test_path)
    
    def test_update_processing_summary(self):
        """Test processing summary update."""
        test_message = "Processing complete"
        self.adapter.update_processing_summary(test_message)
        
        self.mock_main_window.update_processing_summary.assert_called_once_with(test_message)
    
    def test_display_image_in_preview(self):
        """Test image display in preview."""
        test_image = "test_image_data"
        self.adapter.display_image_in_preview(test_image)
        
        self.mock_main_window.display_image_in_preview.assert_called_once_with(test_image)
    
    def test_show_file_dialog_with_result(self):
        """Test file dialog with result."""
        result = self.adapter.show_file_dialog("Test Title", "Test Filter")
        
        self.assertEqual(result, "/test/file.tif")
    
    def test_show_file_dialog_cancelled(self):
        """Test file dialog when cancelled."""
        cancelled_dialog = MockFileDialog(None)
        adapter = MainViewAdapter(self.mock_main_window, cancelled_dialog)
        
        result = adapter.show_file_dialog("Test Title", "Test Filter")
        
        self.assertIsNone(result)


class TestQtFileDialog(unittest.TestCase):
    """Test cases for QtFileDialog."""
    
    @patch('app.view_interfaces.QFileDialog')
    def test_initialization(self, mock_qfiledialog):
        """Test Qt file dialog initialization."""
        dialog = QtFileDialog()
        self.assertEqual(dialog.QFileDialog, mock_qfiledialog)
    
    @patch('app.view_interfaces.QFileDialog')
    def test_get_open_filename(self, mock_qfiledialog):
        """Test Qt file dialog get_open_filename."""
        mock_qfiledialog.getOpenFileName.return_value = ("/test/file.tif", "TIFF Files (*.tif)")
        
        dialog = QtFileDialog()
        result = dialog.get_open_filename(None, "Test Title", "/test/dir", "TIFF Files (*.tif)")
        
        self.assertEqual(result, ("/test/file.tif", "TIFF Files (*.tif)"))
        mock_qfiledialog.getOpenFileName.assert_called_once_with(
            None, "Test Title", "/test/dir", "TIFF Files (*.tif)"
        )


class TestQtMessageDisplay(unittest.TestCase):
    """Test cases for QtMessageDisplay."""
    
    @patch('app.view_interfaces.QMessageBox')
    def test_initialization(self, mock_qmessagebox):
        """Test Qt message display initialization."""
        display = QtMessageDisplay()
        self.assertEqual(display.QMessageBox, mock_qmessagebox)
    
    @patch('app.view_interfaces.QMessageBox')
    def test_show_info(self, mock_qmessagebox):
        """Test Qt info message display."""
        display = QtMessageDisplay()
        display.show_info("Info Title", "Info message")
        
        mock_qmessagebox.information.assert_called_once_with(None, "Info Title", "Info message")
    
    @patch('app.view_interfaces.QMessageBox')
    def test_show_warning(self, mock_qmessagebox):
        """Test Qt warning message display."""
        display = QtMessageDisplay()
        display.show_warning("Warning Title", "Warning message")
        
        mock_qmessagebox.warning.assert_called_once_with(None, "Warning Title", "Warning message")
    
    @patch('app.view_interfaces.QMessageBox')
    def test_show_error(self, mock_qmessagebox):
        """Test Qt error message display."""
        display = QtMessageDisplay()
        display.show_error("Error Title", "Error message")
        
        mock_qmessagebox.critical.assert_called_once_with(None, "Error Title", "Error message")


if __name__ == '__main__':
    unittest.main()

