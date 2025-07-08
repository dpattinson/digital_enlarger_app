"""Tests for command pattern implementation."""
import unittest
from unittest.mock import Mock, patch
import numpy as np
import tempfile
import os
from app.commands import (
    LoadImageCommand, LoadLUTCommand, ProcessImageCommand,
    StartPrintCommand, StopPrintCommand, CommandInvoker, BatchCommand
)


class TestLoadImageCommand(unittest.TestCase):
    """Test cases for LoadImageCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_image_processor = Mock()
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        self.temp_file.close()
        self.test_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)
    
    def test_can_execute_valid_file(self):
        """Test can_execute with valid TIFF file."""
        command = LoadImageCommand(self.mock_image_processor, self.test_file_path)
        self.assertTrue(command.can_execute())
    
    def test_can_execute_nonexistent_file(self):
        """Test can_execute with nonexistent file."""
        command = LoadImageCommand(self.mock_image_processor, "/nonexistent/file.tif")
        self.assertFalse(command.can_execute())
    
    def test_can_execute_invalid_extension(self):
        """Test can_execute with invalid file extension."""
        # Create temp file with wrong extension
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.close()
        
        try:
            command = LoadImageCommand(self.mock_image_processor, temp_file.name)
            self.assertFalse(command.can_execute())
        finally:
            os.unlink(temp_file.name)
    
    def test_can_execute_empty_path(self):
        """Test can_execute with empty path."""
        command = LoadImageCommand(self.mock_image_processor, "")
        self.assertFalse(command.can_execute())
    
    def test_execute_success(self):
        """Test successful command execution."""
        self.mock_image_processor.load_image.return_value = self.test_image_data
        command = LoadImageCommand(self.mock_image_processor, self.test_file_path)
        
        result = command.execute()
        
        self.assertEqual(result, self.test_image_data)
        self.assertEqual(command.loaded_image, self.test_image_data)
        self.mock_image_processor.load_image.assert_called_once_with(self.test_file_path)
    
    def test_execute_file_not_found(self):
        """Test execution with nonexistent file."""
        command = LoadImageCommand(self.mock_image_processor, "/nonexistent/file.tif")
        
        with self.assertRaises(ValueError) as context:
            command.execute()
        
        self.assertIn("file does not exist", str(context.exception))
    
    def test_get_file_info_existing_file(self):
        """Test file info for existing file."""
        command = LoadImageCommand(self.mock_image_processor, self.test_file_path)
        info = command.get_file_info()
        
        self.assertTrue(info['exists'])
        self.assertEqual(info['name'], os.path.basename(self.test_file_path))
        self.assertEqual(info['path'], self.test_file_path)
        self.assertIn('size', info)
    
    def test_get_file_info_nonexistent_file(self):
        """Test file info for nonexistent file."""
        command = LoadImageCommand(self.mock_image_processor, "/nonexistent/file.tif")
        info = command.get_file_info()
        
        self.assertFalse(info['exists'])


class TestLoadLUTCommand(unittest.TestCase):
    """Test cases for LoadLUTCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_lut_manager = Mock()
        self.mock_lut_manager.lut_dir = "/test/luts"
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        self.temp_file.close()
        self.test_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)
    
    def test_can_execute_absolute_path(self):
        """Test can_execute with absolute path."""
        command = LoadLUTCommand(self.mock_lut_manager, self.test_file_path)
        self.assertTrue(command.can_execute())
    
    @patch('os.path.exists')
    def test_can_execute_relative_path(self, mock_exists):
        """Test can_execute with relative path."""
        mock_exists.return_value = True
        command = LoadLUTCommand(self.mock_lut_manager, "test_lut.tif")
        self.assertTrue(command.can_execute())
        
        # Should check the full path
        expected_path = os.path.join("/test/luts", "test_lut.tif")
        mock_exists.assert_called_with(expected_path)
    
    def test_execute_success(self):
        """Test successful LUT loading."""
        self.mock_lut_manager.load_lut.return_value = self.test_lut_data
        command = LoadLUTCommand(self.mock_lut_manager, self.test_file_path)
        
        result = command.execute()
        
        self.assertEqual(result, self.test_lut_data)
        self.assertEqual(command.loaded_lut, self.test_lut_data)
        self.mock_lut_manager.load_lut.assert_called_once_with(self.test_file_path)


class TestProcessImageCommand(unittest.TestCase):
    """Test cases for ProcessImageCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_image_processor = Mock()
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
    
    def test_can_execute_with_data(self):
        """Test can_execute with valid image and LUT data."""
        command = ProcessImageCommand(
            self.mock_image_processor,
            self.test_image_data,
            self.test_lut_data
        )
        self.assertTrue(command.can_execute())
    
    def test_can_execute_missing_image(self):
        """Test can_execute with missing image data."""
        command = ProcessImageCommand(
            self.mock_image_processor,
            None,
            self.test_lut_data
        )
        self.assertFalse(command.can_execute())
    
    def test_can_execute_missing_lut(self):
        """Test can_execute with missing LUT data."""
        command = ProcessImageCommand(
            self.mock_image_processor,
            self.test_image_data,
            None
        )
        self.assertFalse(command.can_execute())
    
    def test_execute_success(self):
        """Test successful image processing."""
        lut_applied = np.array([[2000, 4000], [6000, 8000]], dtype=np.uint16)
        processed = np.array([[63535, 61535], [59535, 57535]], dtype=np.uint16)
        
        self.mock_image_processor.apply_lut.return_value = lut_applied
        self.mock_image_processor.invert_image.return_value = processed
        
        command = ProcessImageCommand(
            self.mock_image_processor,
            self.test_image_data,
            self.test_lut_data
        )
        
        result = command.execute()
        
        self.assertEqual(result, processed)
        self.assertEqual(command.processed_image, processed)
        
        self.mock_image_processor.apply_lut.assert_called_once_with(
            self.test_image_data, self.test_lut_data
        )
        self.mock_image_processor.invert_image.assert_called_once_with(lut_applied)
    
    def test_execute_missing_data(self):
        """Test execution with missing data."""
        command = ProcessImageCommand(self.mock_image_processor, None, self.test_lut_data)
        
        with self.assertRaises(ValueError) as context:
            command.execute()
        
        self.assertIn("missing image data or LUT data", str(context.exception))


class TestStartPrintCommand(unittest.TestCase):
    """Test cases for StartPrintCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.test_exposure_time = 5.0
    
    def test_can_execute_valid_params(self):
        """Test can_execute with valid parameters."""
        command = StartPrintCommand(
            self.mock_display_window,
            self.test_image_data,
            self.test_exposure_time
        )
        self.assertTrue(command.can_execute())
    
    def test_can_execute_no_image(self):
        """Test can_execute with no image data."""
        command = StartPrintCommand(
            self.mock_display_window,
            None,
            self.test_exposure_time
        )
        self.assertFalse(command.can_execute())
    
    def test_can_execute_invalid_exposure(self):
        """Test can_execute with invalid exposure time."""
        command = StartPrintCommand(
            self.mock_display_window,
            self.test_image_data,
            0.0
        )
        self.assertFalse(command.can_execute())
    
    def test_execute_success(self):
        """Test successful print start."""
        command = StartPrintCommand(
            self.mock_display_window,
            self.test_image_data,
            self.test_exposure_time
        )
        
        result = command.execute()
        
        self.assertTrue(result)
        self.mock_display_window.set_frames.assert_called_once()
        self.mock_display_window.start_display_loop.assert_called_once_with(self.test_exposure_time)


class TestStopPrintCommand(unittest.TestCase):
    """Test cases for StopPrintCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()
    
    def test_can_execute(self):
        """Test can_execute always returns True."""
        command = StopPrintCommand(self.mock_display_window)
        self.assertTrue(command.can_execute())
    
    def test_execute_success(self):
        """Test successful print stop."""
        command = StopPrintCommand(self.mock_display_window)
        
        result = command.execute()
        
        self.assertTrue(result)
        self.mock_display_window.stop_display_loop.assert_called_once()


class TestCommandInvoker(unittest.TestCase):
    """Test cases for CommandInvoker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.invoker = CommandInvoker()
        self.mock_command = Mock()
        self.mock_command.can_execute.return_value = True
        self.mock_command.execute.return_value = "test_result"
    
    def test_initialization(self):
        """Test invoker initialization."""
        self.assertEqual(len(self.invoker.history), 0)
        self.assertEqual(self.invoker.current_index, -1)
    
    def test_execute_command_success(self):
        """Test successful command execution."""
        result = self.invoker.execute_command(self.mock_command)
        
        self.assertEqual(result, "test_result")
        self.assertEqual(len(self.invoker.history), 1)
        self.assertEqual(self.invoker.current_index, 0)
        self.mock_command.execute.assert_called_once()
    
    def test_execute_command_cannot_execute(self):
        """Test command execution when command cannot execute."""
        self.mock_command.can_execute.return_value = False
        
        with self.assertRaises(ValueError) as context:
            self.invoker.execute_command(self.mock_command)
        
        self.assertIn("Command cannot be executed", str(context.exception))
        self.assertEqual(len(self.invoker.history), 0)
    
    def test_can_undo_redo_initial_state(self):
        """Test undo/redo availability in initial state."""
        self.assertFalse(self.invoker.can_undo())
        self.assertFalse(self.invoker.can_redo())
    
    def test_can_undo_after_execution(self):
        """Test undo availability after command execution."""
        self.invoker.execute_command(self.mock_command)
        
        self.assertTrue(self.invoker.can_undo())
        self.assertFalse(self.invoker.can_redo())
    
    def test_undo_success(self):
        """Test successful undo operation."""
        self.mock_command.undo.return_value = "undo_result"
        self.invoker.execute_command(self.mock_command)
        
        result = self.invoker.undo()
        
        self.assertEqual(result, "undo_result")
        self.assertEqual(self.invoker.current_index, -1)
        self.mock_command.undo.assert_called_once()
    
    def test_undo_when_cannot_undo(self):
        """Test undo when no commands to undo."""
        result = self.invoker.undo()
        self.assertIsNone(result)
    
    def test_redo_success(self):
        """Test successful redo operation."""
        # Execute, undo, then redo
        self.invoker.execute_command(self.mock_command)
        self.invoker.undo()
        
        result = self.invoker.redo()
        
        self.assertEqual(result, "test_result")
        self.assertEqual(self.invoker.current_index, 0)
        # Execute should be called twice (initial + redo)
        self.assertEqual(self.mock_command.execute.call_count, 2)
    
    def test_get_history(self):
        """Test history retrieval."""
        self.invoker.execute_command(self.mock_command)
        history = self.invoker.get_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], self.mock_command)
    
    def test_clear_history(self):
        """Test history clearing."""
        self.invoker.execute_command(self.mock_command)
        self.invoker.clear_history()
        
        self.assertEqual(len(self.invoker.history), 0)
        self.assertEqual(self.invoker.current_index, -1)


class TestBatchCommand(unittest.TestCase):
    """Test cases for BatchCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_command1 = Mock()
        self.mock_command1.can_execute.return_value = True
        self.mock_command1.execute.return_value = "result1"
        
        self.mock_command2 = Mock()
        self.mock_command2.can_execute.return_value = True
        self.mock_command2.execute.return_value = "result2"
        
        self.commands = [self.mock_command1, self.mock_command2]
    
    def test_can_execute_all_valid(self):
        """Test can_execute when all commands are valid."""
        batch = BatchCommand(self.commands)
        self.assertTrue(batch.can_execute())
    
    def test_can_execute_one_invalid(self):
        """Test can_execute when one command is invalid."""
        self.mock_command2.can_execute.return_value = False
        batch = BatchCommand(self.commands)
        self.assertFalse(batch.can_execute())
    
    def test_execute_success(self):
        """Test successful batch execution."""
        batch = BatchCommand(self.commands)
        
        results = batch.execute()
        
        self.assertEqual(results, ["result1", "result2"])
        self.assertEqual(len(batch.executed_commands), 2)
        self.mock_command1.execute.assert_called_once()
        self.mock_command2.execute.assert_called_once()
    
    def test_execute_partial_failure(self):
        """Test batch execution with partial failure."""
        self.mock_command2.can_execute.return_value = False
        batch = BatchCommand(self.commands)
        
        with self.assertRaises(ValueError):
            batch.execute()
    
    def test_undo_success(self):
        """Test successful batch undo."""
        self.mock_command1.undo.return_value = "undo1"
        self.mock_command2.undo.return_value = "undo2"
        
        batch = BatchCommand(self.commands)
        batch.execute()  # Execute first
        
        undo_results = batch.undo()
        
        # Should undo in reverse order
        self.assertEqual(undo_results, ["undo2", "undo1"])
        self.mock_command1.undo.assert_called_once()
        self.mock_command2.undo.assert_called_once()


if __name__ == '__main__':
    unittest.main()

