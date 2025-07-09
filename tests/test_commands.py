"""
Unit tests for command pattern implementation.

Tests the command pattern classes that encapsulate user actions
for undo/redo functionality and clean separation of concerns.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import tempfile
import os

from app.commands import (
    LoadImageCommand, LoadLUTCommand, ProcessImageCommand,
    StartPrintCommand, StopPrintCommand, CommandInvoker, BatchCommand
)


class TestLoadImageCommand(unittest.TestCase):
    """Test cases for LoadImageCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_processor = Mock()
        self.test_image_path = "/test/path/image.tif"

    @patch('os.path.exists')
    def test_execute_loads_image_when_given_valid_path(self, mock_exists):
        # GIVEN: A LoadImageCommand with a mock processor and valid path that exists
        mock_exists.return_value = True
        command = LoadImageCommand(self.mock_processor, self.test_image_path)
        expected_image = np.zeros((100, 256), dtype=np.uint16)
        self.mock_processor.load_image.return_value = expected_image

        # WHEN: We execute the command
        result = command.execute()

        # THEN: The processor should load the image and return it
        self.mock_processor.load_image.assert_called_once_with(self.test_image_path)
        np.testing.assert_array_equal(result, expected_image)

    @patch('os.path.exists')
    def test_can_execute_returns_true_when_given_existing_tiff_file(self, mock_exists):
        # GIVEN: A LoadImageCommand with a TIFF path that exists
        mock_exists.return_value = True
        command = LoadImageCommand(self.mock_processor, self.test_image_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True
        self.assertTrue(result)

    @patch('os.path.exists')
    def test_can_execute_returns_false_when_given_nonexistent_file(self, mock_exists):
        # GIVEN: A LoadImageCommand with a path that doesn't exist
        mock_exists.return_value = False
        command = LoadImageCommand(self.mock_processor, self.test_image_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_false_when_given_invalid_extension(self):
        # GIVEN: A LoadImageCommand with a non-TIFF file
        invalid_path = "/test/path/image.jpg"
        command = LoadImageCommand(self.mock_processor, invalid_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_false_when_given_empty_path(self):
        # GIVEN: A LoadImageCommand with empty path
        command = LoadImageCommand(self.mock_processor, "")

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    @patch('os.path.exists')
    def test_execute_raises_error_when_given_non_executable_command(self, mock_exists):
        # GIVEN: A LoadImageCommand that cannot execute (file doesn't exist)
        mock_exists.return_value = False
        command = LoadImageCommand(self.mock_processor, self.test_image_path)

        # WHEN: We attempt to execute the command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            command.execute()

        self.assertIn("Cannot load image: file does not exist", str(context.exception))

    @patch('os.path.exists')
    @patch('os.stat')
    def test_get_file_info_returns_details_when_given_existing_file(self, mock_stat, mock_exists):
        # GIVEN: A LoadImageCommand with an existing file
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024
        command = LoadImageCommand(self.mock_processor, self.test_image_path)

        # WHEN: We get file info
        info = command.get_file_info()

        # THEN: File information should be returned
        self.assertTrue(info['exists'])
        self.assertEqual(info['name'], 'image.tif')
        self.assertEqual(info['size'], 1024)
        self.assertEqual(info['path'], self.test_image_path)


class TestLoadLUTCommand(unittest.TestCase):
    """Test cases for LoadLUTCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_lut_manager = Mock()
        self.mock_lut_manager.lut_dir = "/test/luts"
        self.test_lut_path = "/test/path/lut.tif"

    @patch('os.path.exists')
    def test_execute_loads_lut_when_given_valid_path(self, mock_exists):
        # GIVEN: A LoadLUTCommand with a mock LUT manager and valid path that exists
        mock_exists.return_value = True
        command = LoadLUTCommand(self.mock_lut_manager, self.test_lut_path)
        expected_lut = np.zeros((256, 256), dtype=np.uint16)
        self.mock_lut_manager.load_lut.return_value = expected_lut

        # WHEN: We execute the command
        result = command.execute()

        # THEN: The LUT manager should load the LUT and return it
        self.mock_lut_manager.load_lut.assert_called_once_with(self.test_lut_path)
        np.testing.assert_array_equal(result, expected_lut)

    @patch('os.path.exists')
    def test_can_execute_returns_true_when_given_existing_tiff_file(self, mock_exists):
        # GIVEN: A LoadLUTCommand with a TIFF path that exists
        mock_exists.return_value = True
        command = LoadLUTCommand(self.mock_lut_manager, self.test_lut_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True
        self.assertTrue(result)

    @patch('os.path.exists')
    def test_can_execute_returns_false_when_given_nonexistent_file(self, mock_exists):
        # GIVEN: A LoadLUTCommand with a path that doesn't exist
        mock_exists.return_value = False
        command = LoadLUTCommand(self.mock_lut_manager, self.test_lut_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    @patch('os.path.exists')
    def test_can_execute_handles_relative_paths_correctly(self, mock_exists):
        # GIVEN: A LoadLUTCommand with a relative path
        relative_path = "test_lut.tif"
        mock_exists.return_value = True
        command = LoadLUTCommand(self.mock_lut_manager, relative_path)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should check the full path and return True
        expected_full_path = "/test/luts/test_lut.tif"
        mock_exists.assert_called_with(expected_full_path)
        self.assertTrue(result)

    @patch('os.path.exists')
    def test_execute_raises_error_when_given_non_executable_command(self, mock_exists):
        # GIVEN: A LoadLUTCommand that cannot execute (file doesn't exist)
        mock_exists.return_value = False
        command = LoadLUTCommand(self.mock_lut_manager, self.test_lut_path)

        # WHEN: We attempt to execute the command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            command.execute()

        self.assertIn("Cannot load LUT: file does not exist", str(context.exception))


class TestProcessImageCommand(unittest.TestCase):
    """Test cases for ProcessImageCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_processor = Mock()
        self.test_image = np.zeros((100, 256), dtype=np.uint16)
        self.test_lut = np.arange(65536, dtype=np.uint16).reshape(256, 256)

    def test_execute_processes_image_when_given_valid_image_and_lut(self):
        # GIVEN: A ProcessImageCommand with mock processor, image, and LUT
        command = ProcessImageCommand(self.mock_processor, self.test_image, self.test_lut)
        lut_applied_result = np.ones((100, 256), dtype=np.uint16) * 1000
        final_result = np.ones((100, 256), dtype=np.uint16) * 2000
        self.mock_processor.apply_lut.return_value = lut_applied_result
        self.mock_processor.invert_image.return_value = final_result

        # WHEN: We execute the command
        result = command.execute()

        # THEN: The processor should apply LUT and invert the image
        self.mock_processor.apply_lut.assert_called_once_with(self.test_image, self.test_lut)
        self.mock_processor.invert_image.assert_called_once_with(lut_applied_result)
        np.testing.assert_array_equal(result, final_result)

    def test_can_execute_returns_true_when_given_valid_image_and_lut(self):
        # GIVEN: A ProcessImageCommand with valid image and LUT
        command = ProcessImageCommand(self.mock_processor, self.test_image, self.test_lut)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True
        self.assertTrue(result)

    def test_can_execute_returns_false_when_given_none_image(self):
        # GIVEN: A ProcessImageCommand with None image
        command = ProcessImageCommand(self.mock_processor, None, self.test_lut)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_false_when_given_none_lut(self):
        # GIVEN: A ProcessImageCommand with None LUT
        command = ProcessImageCommand(self.mock_processor, self.test_image, None)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_execute_raises_error_when_given_non_executable_command(self):
        # GIVEN: A ProcessImageCommand that cannot execute (missing data)
        command = ProcessImageCommand(self.mock_processor, None, self.test_lut)

        # WHEN: We attempt to execute the command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            command.execute()

        self.assertIn("Cannot process image: missing image data or LUT data", str(context.exception))

    def test_undo_raises_not_implemented_error(self):
        # GIVEN: A ProcessImageCommand
        command = ProcessImageCommand(self.mock_processor, self.test_image, self.test_lut)

        # WHEN: We attempt to undo the command
        # THEN: A NotImplementedError should be raised
        with self.assertRaises(NotImplementedError) as context:
            command.undo()

        self.assertIn("Undo not implemented for this command", str(context.exception))


class TestStartPrintCommand(unittest.TestCase):
    """Test cases for StartPrintCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()
        self.test_image_data = np.zeros((100, 256), dtype=np.uint16)
        self.test_exposure_time = 5.0

    def test_execute_starts_print_when_given_valid_parameters(self):
        # GIVEN: A StartPrintCommand with mock display window and valid parameters
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, self.test_exposure_time)

        # WHEN: We execute the command
        result = command.execute()

        # THEN: The display window should be configured and started
        self.mock_display_window.set_frames.assert_called_once()
        self.mock_display_window.start_display_loop.assert_called_once_with(self.test_exposure_time)
        self.assertTrue(result)

    def test_can_execute_returns_true_when_given_valid_parameters(self):
        # GIVEN: A StartPrintCommand with valid image data and exposure time
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, self.test_exposure_time)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True
        self.assertTrue(result)

    def test_can_execute_returns_false_when_given_none_image_data(self):
        # GIVEN: A StartPrintCommand with None image data
        command = StartPrintCommand(self.mock_display_window, None, self.test_exposure_time)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_false_when_given_zero_exposure_time(self):
        # GIVEN: A StartPrintCommand with zero exposure time
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, 0.0)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_false_when_given_negative_exposure_time(self):
        # GIVEN: A StartPrintCommand with negative exposure time
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, -1.0)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_execute_raises_error_when_given_non_executable_command(self):
        # GIVEN: A StartPrintCommand that cannot execute (invalid parameters)
        command = StartPrintCommand(self.mock_display_window, None, self.test_exposure_time)

        # WHEN: We attempt to execute the command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            command.execute()

        self.assertIn("Cannot start print: invalid parameters", str(context.exception))

    def test_prepare_frames_returns_single_frame_list(self):
        # GIVEN: A StartPrintCommand with image data
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, self.test_exposure_time)

        # WHEN: We prepare frames from the image data
        frames = command._prepare_frames(self.test_image_data)

        # THEN: It should return a list with the image as a single frame
        self.assertEqual(len(frames), 1)
        np.testing.assert_array_equal(frames[0], self.test_image_data)

    def test_undo_raises_not_implemented_error(self):
        # GIVEN: A StartPrintCommand
        command = StartPrintCommand(self.mock_display_window, self.test_image_data, self.test_exposure_time)

        # WHEN: We attempt to undo the command
        # THEN: A NotImplementedError should be raised
        with self.assertRaises(NotImplementedError) as context:
            command.undo()

        self.assertIn("Undo not implemented for this command", str(context.exception))


class TestStopPrintCommand(unittest.TestCase):
    """Test cases for StopPrintCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()

    def test_execute_stops_print_when_given_display_window(self):
        # GIVEN: A StopPrintCommand with a mock display window
        command = StopPrintCommand(self.mock_display_window)

        # WHEN: We execute the command
        result = command.execute()

        # THEN: The display window should stop the print and return True
        self.mock_display_window.stop_display_loop.assert_called_once()
        self.assertTrue(result)

    def test_can_execute_returns_true_when_given_any_display_window(self):
        # GIVEN: A StopPrintCommand with any display window (including None)
        command = StopPrintCommand(self.mock_display_window)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True (can always attempt to stop)
        self.assertTrue(result)

    def test_can_execute_returns_true_when_given_none_display_window(self):
        # GIVEN: A StopPrintCommand with None display window
        command = StopPrintCommand(None)

        # WHEN: We check if the command can execute
        result = command.can_execute()

        # THEN: It should return True (implementation always returns True)
        self.assertTrue(result)

    def test_undo_raises_not_implemented_error(self):
        # GIVEN: A StopPrintCommand
        command = StopPrintCommand(self.mock_display_window)

        # WHEN: We attempt to undo the command
        # THEN: A NotImplementedError should be raised
        with self.assertRaises(NotImplementedError) as context:
            command.undo()

        self.assertIn("Undo not implemented for this command", str(context.exception))


class TestCommandInvoker(unittest.TestCase):
    """Test cases for CommandInvoker using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.invoker = CommandInvoker()
        self.mock_command = Mock()

    def test_execute_command_runs_command_when_given_executable_command(self):
        # GIVEN: A CommandInvoker and an executable command
        self.mock_command.can_execute.return_value = True
        self.mock_command.execute.return_value = "test_result"

        # WHEN: We execute the command through the invoker
        result = self.invoker.execute_command(self.mock_command)

        # THEN: The command should be executed and result returned
        self.mock_command.can_execute.assert_called_once()
        self.mock_command.execute.assert_called_once()
        self.assertEqual(result, "test_result")

    def test_execute_command_raises_error_when_given_non_executable_command(self):
        # GIVEN: A CommandInvoker and a non-executable command
        self.mock_command.can_execute.return_value = False

        # WHEN: We attempt to execute the non-executable command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            self.invoker.execute_command(self.mock_command)

        self.assertIn("Command cannot be executed", str(context.exception))
        self.mock_command.execute.assert_not_called()

    def test_undo_undoes_last_command_when_given_executed_command(self):
        # GIVEN: A CommandInvoker with an executed command
        self.mock_command.can_execute.return_value = True
        self.mock_command.undo.return_value = "undo_result"
        self.invoker.execute_command(self.mock_command)

        # WHEN: We undo the last command
        result = self.invoker.undo()

        # THEN: The command should be undone
        self.mock_command.undo.assert_called_once()
        self.assertEqual(result, "undo_result")

    def test_undo_returns_none_when_given_empty_history(self):
        # GIVEN: A CommandInvoker with no executed commands
        invoker = CommandInvoker()

        # WHEN: We attempt to undo the last command
        result = invoker.undo()

        # THEN: None should be returned (no commands to undo)
        self.assertIsNone(result)

    def test_redo_redoes_last_undone_command_when_available(self):
        # GIVEN: A CommandInvoker with an undone command
        self.mock_command.can_execute.return_value = True
        self.mock_command.execute.return_value = "execute_result"
        self.invoker.execute_command(self.mock_command)
        self.invoker.undo()

        # WHEN: We redo the last command
        result = self.invoker.redo()

        # THEN: The command should be executed again
        self.assertEqual(self.mock_command.execute.call_count, 2)
        self.assertEqual(result, "execute_result")

    def test_redo_returns_none_when_given_empty_redo_stack(self):
        # GIVEN: A CommandInvoker with no undone commands
        invoker = CommandInvoker()

        # WHEN: We attempt to redo the last command
        result = invoker.redo()

        # THEN: None should be returned (no commands to redo)
        self.assertIsNone(result)

    def test_can_undo_returns_true_when_commands_available(self):
        # GIVEN: A CommandInvoker with executed commands
        self.mock_command.can_execute.return_value = True
        self.invoker.execute_command(self.mock_command)

        # WHEN: We check if undo is possible
        result = self.invoker.can_undo()

        # THEN: It should return True
        self.assertTrue(result)

    def test_can_undo_returns_false_when_no_commands_available(self):
        # GIVEN: A CommandInvoker with no executed commands
        invoker = CommandInvoker()

        # WHEN: We check if undo is possible
        result = invoker.can_undo()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_redo_returns_true_when_undone_commands_available(self):
        # GIVEN: A CommandInvoker with undone commands
        self.mock_command.can_execute.return_value = True
        self.invoker.execute_command(self.mock_command)
        self.invoker.undo()

        # WHEN: We check if redo is possible
        result = self.invoker.can_redo()

        # THEN: It should return True
        self.assertTrue(result)

    def test_can_redo_returns_false_when_no_undone_commands_available(self):
        # GIVEN: A CommandInvoker with no undone commands
        invoker = CommandInvoker()

        # WHEN: We check if redo is possible
        result = invoker.can_redo()

        # THEN: It should return False
        self.assertFalse(result)

    def test_get_history_returns_copy_of_command_list(self):
        # GIVEN: A CommandInvoker with executed commands
        self.mock_command.can_execute.return_value = True
        self.invoker.execute_command(self.mock_command)

        # WHEN: We get the history
        history = self.invoker.get_history()

        # THEN: It should return a copy of the command list
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0], self.mock_command)
        # Verify it's a copy by modifying original
        self.invoker.clear_history()
        self.assertEqual(len(history), 1)  # Copy unchanged

    def test_clear_history_removes_all_commands(self):
        # GIVEN: A CommandInvoker with executed commands
        self.mock_command.can_execute.return_value = True
        self.invoker.execute_command(self.mock_command)

        # WHEN: We clear the history
        self.invoker.clear_history()

        # THEN: History should be empty and undo should not be possible
        self.assertEqual(len(self.invoker.get_history()), 0)
        self.assertFalse(self.invoker.can_undo())


class TestBatchCommand(unittest.TestCase):
    """Test cases for BatchCommand using Given-When-Then pattern."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_command1 = Mock()
        self.mock_command2 = Mock()
        self.mock_command3 = Mock()

    def test_execute_runs_all_commands_when_given_multiple_executable_commands(self):
        # GIVEN: A BatchCommand with multiple executable commands
        commands = [self.mock_command1, self.mock_command2, self.mock_command3]
        for i, cmd in enumerate(commands):
            cmd.can_execute.return_value = True
            cmd.execute.return_value = f"result_{i}"
        
        batch_command = BatchCommand(commands)

        # WHEN: We execute the batch command
        results = batch_command.execute()

        # THEN: All commands should be executed and results collected
        for cmd in commands:
            cmd.execute.assert_called_once()
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], "result_0")
        self.assertEqual(results[1], "result_1")
        self.assertEqual(results[2], "result_2")

    def test_can_execute_returns_true_when_given_all_executable_commands(self):
        # GIVEN: A BatchCommand with all executable commands
        commands = [self.mock_command1, self.mock_command2]
        for cmd in commands:
            cmd.can_execute.return_value = True
        
        batch_command = BatchCommand(commands)

        # WHEN: We check if the batch command can execute
        result = batch_command.can_execute()

        # THEN: It should return True
        self.assertTrue(result)

    def test_can_execute_returns_false_when_given_any_non_executable_command(self):
        # GIVEN: A BatchCommand with one non-executable command
        self.mock_command1.can_execute.return_value = True
        self.mock_command2.can_execute.return_value = False
        
        batch_command = BatchCommand([self.mock_command1, self.mock_command2])

        # WHEN: We check if the batch command can execute
        result = batch_command.can_execute()

        # THEN: It should return False
        self.assertFalse(result)

    def test_can_execute_returns_true_when_given_empty_command_list(self):
        # GIVEN: A BatchCommand with no commands
        batch_command = BatchCommand([])

        # WHEN: We check if the batch command can execute
        result = batch_command.can_execute()

        # THEN: It should return True (all() on empty list returns True)
        self.assertTrue(result)

    def test_execute_raises_error_when_given_non_executable_command_in_batch(self):
        # GIVEN: A BatchCommand with one non-executable command
        self.mock_command1.can_execute.return_value = True
        self.mock_command2.can_execute.return_value = False
        
        batch_command = BatchCommand([self.mock_command1, self.mock_command2])

        # WHEN: We attempt to execute the batch command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            batch_command.execute()

        self.assertIn("Command in batch cannot be executed", str(context.exception))

    def test_undo_reverses_all_executed_commands_in_reverse_order(self):
        # GIVEN: A BatchCommand that has been executed
        commands = [self.mock_command1, self.mock_command2, self.mock_command3]
        for i, cmd in enumerate(commands):
            cmd.can_execute.return_value = True
            cmd.execute.return_value = f"result_{i}"
            cmd.undo.return_value = f"undo_{i}"
        
        batch_command = BatchCommand(commands)
        batch_command.execute()

        # WHEN: We undo the batch command
        undo_results = batch_command.undo()

        # THEN: All commands should be undone in reverse order
        # Check that undo was called on all commands
        for cmd in commands:
            cmd.undo.assert_called_once()
        
        # Verify results are in reverse order
        self.assertEqual(len(undo_results), 3)
        self.assertEqual(undo_results[0], "undo_2")  # Last command undone first
        self.assertEqual(undo_results[1], "undo_1")
        self.assertEqual(undo_results[2], "undo_0")  # First command undone last

    def test_execute_tracks_executed_commands_for_undo(self):
        # GIVEN: A BatchCommand with commands that may partially execute
        self.mock_command1.can_execute.return_value = True
        self.mock_command1.execute.return_value = "result_1"
        self.mock_command2.can_execute.return_value = False  # This will cause failure
        
        batch_command = BatchCommand([self.mock_command1, self.mock_command2])

        # WHEN: We attempt to execute the batch (which will fail)
        with self.assertRaises(ValueError):
            batch_command.execute()

        # THEN: Commands executed before failure should be tracked
        # (First command executes successfully, second fails)
        self.assertEqual(len(batch_command.executed_commands), 1)
        self.assertEqual(batch_command.executed_commands[0], self.mock_command1)


if __name__ == '__main__':
    unittest.main()

