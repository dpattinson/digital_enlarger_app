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
    
    def test_can_execute_returns_true_when_given_valid_tiff_file_path(self):
        """Test that can_execute returns True for valid TIFF file paths."""
        # GIVEN: A LoadImageCommand with a valid TIFF file path
        image_processor = self.mock_image_processor
        valid_tiff_path = self.test_file_path
        command = LoadImageCommand(image_processor, valid_tiff_path)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should be executable
        self.assertTrue(result)
    
    def test_can_execute_returns_false_when_given_nonexistent_file_path(self):
        """Test that can_execute returns False for nonexistent file paths."""
        # GIVEN: A LoadImageCommand with a nonexistent file path
        image_processor = self.mock_image_processor
        nonexistent_path = "/nonexistent/file.tif"
        command = LoadImageCommand(image_processor, nonexistent_path)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should not be executable
        self.assertFalse(result)
    
    def test_can_execute_returns_false_when_given_invalid_file_extension(self):
        """Test that can_execute returns False for files with invalid extensions."""
        # GIVEN: A LoadImageCommand with a file that has invalid extension
        image_processor = self.mock_image_processor
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.close()
        invalid_extension_path = temp_file.name
        
        try:
            command = LoadImageCommand(image_processor, invalid_extension_path)
            
            # WHEN: We check if the command can execute
            result = command.can_execute()
            
            # THEN: The command should not be executable
            self.assertFalse(result)
        finally:
            os.unlink(invalid_extension_path)
    
    def test_execute_loads_image_successfully_when_given_valid_file_path(self):
        """Test that execute successfully loads image when given valid file path."""
        # GIVEN: A LoadImageCommand with valid file path and mock processor
        image_processor = self.mock_image_processor
        valid_file_path = self.test_file_path
        expected_image_data = self.test_image_data
        image_processor.load_image.return_value = expected_image_data
        command = LoadImageCommand(image_processor, valid_file_path)
        
        # WHEN: We execute the command
        result = command.execute()
        
        # THEN: Image processor should be called and image data returned
        image_processor.load_image.assert_called_once_with(valid_file_path)
        np.testing.assert_array_equal(result, expected_image_data)
    
    def test_execute_raises_exception_when_image_processor_fails(self):
        """Test that execute raises exception when image processor fails."""
        # GIVEN: A LoadImageCommand where image processor will fail
        image_processor = self.mock_image_processor
        valid_file_path = self.test_file_path
        error_message = "Failed to load image"
        image_processor.load_image.side_effect = ValueError(error_message)
        command = LoadImageCommand(image_processor, valid_file_path)
        
        # WHEN: We execute the command
        # THEN: The same exception should be raised
        with self.assertRaises(ValueError) as context:
            command.execute()
        
        # AND THEN: The error message should match
        self.assertEqual(str(context.exception), error_message)


class TestLoadLUTCommand(unittest.TestCase):
    """Test cases for LoadLUTCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_lut_manager = Mock()
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
        
        # Create temporary test file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.tif', delete=False)
        self.temp_file.close()
        self.test_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file_path):
            os.unlink(self.test_file_path)
    
    def test_can_execute_returns_true_when_given_valid_tiff_file_path(self):
        """Test that can_execute returns True for valid TIFF file paths."""
        # GIVEN: A LoadLUTCommand with a valid TIFF file path
        lut_manager = self.mock_lut_manager
        valid_tiff_path = self.test_file_path
        command = LoadLUTCommand(lut_manager, valid_tiff_path)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should be executable
        self.assertTrue(result)
    
    def test_execute_loads_lut_successfully_when_given_valid_file_path(self):
        """Test that execute successfully loads LUT when given valid file path."""
        # GIVEN: A LoadLUTCommand with valid file path and mock manager
        lut_manager = self.mock_lut_manager
        valid_file_path = self.test_file_path
        expected_lut_data = self.test_lut_data
        lut_manager.load_lut.return_value = expected_lut_data
        command = LoadLUTCommand(lut_manager, valid_file_path)
        
        # WHEN: We execute the command
        result = command.execute()
        
        # THEN: LUT manager should be called and LUT data returned
        lut_manager.load_lut.assert_called_once_with(valid_file_path)
        np.testing.assert_array_equal(result, expected_lut_data)


class TestProcessImageCommand(unittest.TestCase):
    """Test cases for ProcessImageCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_image_processor = Mock()
        self.test_image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
        self.test_lut_data = np.zeros((256, 256), dtype=np.uint16)
    
    def test_can_execute_returns_true_when_given_valid_image_and_lut_data(self):
        """Test that can_execute returns True when given valid image and LUT data."""
        # GIVEN: A ProcessImageCommand with valid image and LUT data
        image_processor = self.mock_image_processor
        valid_image = self.test_image_data
        valid_lut = self.test_lut_data
        command = ProcessImageCommand(image_processor, valid_image, valid_lut)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should be executable
        self.assertTrue(result)
    
    def test_can_execute_returns_false_when_given_none_image_data(self):
        """Test that can_execute returns False when image data is None."""
        # GIVEN: A ProcessImageCommand with None image data
        image_processor = self.mock_image_processor
        none_image = None
        valid_lut = self.test_lut_data
        command = ProcessImageCommand(image_processor, none_image, valid_lut)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should not be executable
        self.assertFalse(result)
    
    def test_can_execute_returns_false_when_given_none_lut_data(self):
        """Test that can_execute returns False when LUT data is None."""
        # GIVEN: A ProcessImageCommand with None LUT data
        image_processor = self.mock_image_processor
        valid_image = self.test_image_data
        none_lut = None
        command = ProcessImageCommand(image_processor, valid_image, none_lut)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should not be executable
        self.assertFalse(result)
    
    def test_execute_applies_lut_and_inverts_image_when_given_valid_data(self):
        """Test that execute applies LUT and inverts image correctly."""
        # GIVEN: A ProcessImageCommand with valid data and configured processor
        image_processor = self.mock_image_processor
        input_image = self.test_image_data
        input_lut = self.test_lut_data
        lut_applied_image = np.array([[2000, 4000], [6000, 8000]], dtype=np.uint16)
        final_inverted_image = 65535 - lut_applied_image
        
        image_processor.apply_lut.return_value = lut_applied_image
        image_processor.invert_image.return_value = final_inverted_image
        command = ProcessImageCommand(image_processor, input_image, input_lut)
        
        # WHEN: We execute the command
        result = command.execute()
        
        # THEN: LUT should be applied and image should be inverted
        image_processor.apply_lut.assert_called_once_with(input_image, input_lut)
        image_processor.invert_image.assert_called_once_with(lut_applied_image)
        np.testing.assert_array_equal(result, final_inverted_image)


class TestStartPrintCommand(unittest.TestCase):
    """Test cases for StartPrintCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()
        self.test_frames = [np.array([[100, 150]], dtype=np.uint8) for _ in range(4)]
        self.test_exposure_ms = 30000
    
    def test_can_execute_returns_true_when_given_valid_frames_and_exposure(self):
        """Test that can_execute returns True when given valid frames and exposure."""
        # GIVEN: A StartPrintCommand with valid frames and exposure
        display_window = self.mock_display_window
        valid_frames = self.test_frames
        valid_exposure = self.test_exposure_ms
        command = StartPrintCommand(display_window, valid_frames, valid_exposure)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should be executable
        self.assertTrue(result)
    
    def test_can_execute_returns_false_when_given_empty_frames_list(self):
        """Test that can_execute returns False when frames list is empty."""
        # GIVEN: A StartPrintCommand with empty frames list
        display_window = self.mock_display_window
        empty_frames = []
        valid_exposure = self.test_exposure_ms
        command = StartPrintCommand(display_window, empty_frames, valid_exposure)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should not be executable
        self.assertFalse(result)
    
    def test_execute_configures_display_and_starts_loop_when_given_valid_parameters(self):
        """Test that execute configures display window and starts display loop."""
        # GIVEN: A StartPrintCommand with valid parameters
        display_window = self.mock_display_window
        frames = self.test_frames
        exposure_ms = self.test_exposure_ms
        command = StartPrintCommand(display_window, frames, exposure_ms)
        
        # WHEN: We execute the command
        command.execute()
        
        # THEN: Display window should be configured and started
        display_window.set_frames.assert_called_once_with(frames, exposure_ms)
        display_window.show_on_secondary_monitor.assert_called_once()
        display_window.start_display_loop.assert_called_once()


class TestStopPrintCommand(unittest.TestCase):
    """Test cases for StopPrintCommand."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_display_window = Mock()
    
    def test_can_execute_always_returns_true(self):
        """Test that can_execute always returns True for stop commands."""
        # GIVEN: A StopPrintCommand with display window
        display_window = self.mock_display_window
        command = StopPrintCommand(display_window)
        
        # WHEN: We check if the command can execute
        result = command.can_execute()
        
        # THEN: The command should always be executable
        self.assertTrue(result)
    
    def test_execute_stops_display_loop_when_called(self):
        """Test that execute stops the display loop correctly."""
        # GIVEN: A StopPrintCommand with display window
        display_window = self.mock_display_window
        command = StopPrintCommand(display_window)
        
        # WHEN: We execute the command
        command.execute()
        
        # THEN: Display loop should be stopped
        display_window.stop_display_loop.assert_called_once()


class TestCommandInvoker(unittest.TestCase):
    """Test cases for CommandInvoker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.invoker = CommandInvoker()
        self.mock_command = Mock()
        self.mock_command.can_execute.return_value = True
        self.mock_command.execute.return_value = "test_result"
    
    def test_execute_command_runs_successfully_when_given_executable_command(self):
        """Test that execute_command runs successfully for executable commands."""
        # GIVEN: A CommandInvoker and an executable command
        invoker = self.invoker
        executable_command = self.mock_command
        
        # WHEN: We execute the command through the invoker
        result = invoker.execute_command(executable_command)
        
        # THEN: Command should be checked and executed
        executable_command.can_execute.assert_called_once()
        executable_command.execute.assert_called_once()
        self.assertEqual(result, "test_result")
    
    def test_execute_command_raises_exception_when_given_non_executable_command(self):
        """Test that execute_command raises exception for non-executable commands."""
        # GIVEN: A CommandInvoker and a non-executable command
        invoker = self.invoker
        non_executable_command = self.mock_command
        non_executable_command.can_execute.return_value = False
        
        # WHEN: We attempt to execute the non-executable command
        # THEN: A ValueError should be raised
        with self.assertRaises(ValueError) as context:
            invoker.execute_command(non_executable_command)
        
        # AND THEN: The error message should be appropriate
        self.assertIn("Command cannot be executed", str(context.exception))
        
        # AND THEN: Execute should not be called
        non_executable_command.execute.assert_not_called()


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
    
    def test_can_execute_returns_true_when_all_commands_are_executable(self):
        """Test that can_execute returns True when all commands are executable."""
        # GIVEN: A BatchCommand with all executable commands
        executable_commands = [self.mock_command1, self.mock_command2]
        batch_command = BatchCommand(executable_commands)
        
        # WHEN: We check if the batch command can execute
        result = batch_command.can_execute()
        
        # THEN: The batch command should be executable
        self.assertTrue(result)
        
        # AND THEN: All individual commands should be checked
        self.mock_command1.can_execute.assert_called_once()
        self.mock_command2.can_execute.assert_called_once()
    
    def test_can_execute_returns_false_when_any_command_is_not_executable(self):
        """Test that can_execute returns False when any command is not executable."""
        # GIVEN: A BatchCommand with one non-executable command
        self.mock_command2.can_execute.return_value = False
        mixed_commands = [self.mock_command1, self.mock_command2]
        batch_command = BatchCommand(mixed_commands)
        
        # WHEN: We check if the batch command can execute
        result = batch_command.can_execute()
        
        # THEN: The batch command should not be executable
        self.assertFalse(result)
    
    def test_execute_runs_all_commands_and_returns_results_when_all_executable(self):
        """Test that execute runs all commands and returns combined results."""
        # GIVEN: A BatchCommand with executable commands
        executable_commands = [self.mock_command1, self.mock_command2]
        batch_command = BatchCommand(executable_commands)
        
        # WHEN: We execute the batch command
        results = batch_command.execute()
        
        # THEN: All commands should be executed and results returned
        self.mock_command1.execute.assert_called_once()
        self.mock_command2.execute.assert_called_once()
        self.assertEqual(results, ["result1", "result2"])


if __name__ == '__main__':
    unittest.main()

