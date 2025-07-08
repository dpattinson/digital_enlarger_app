"""Command pattern implementation for the Darkroom Enlarger Application.

This module implements the Command pattern to encapsulate user actions
as objects, making them easily testable and providing undo/redo capabilities.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
import os


class Command(ABC):
    """Abstract base class for all commands."""
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command.
        
        Returns:
            Any: Result of command execution.
        """
        pass
    
    @abstractmethod
    def can_execute(self) -> bool:
        """Check if the command can be executed.
        
        Returns:
            bool: True if command can be executed, False otherwise.
        """
        pass
    
    def undo(self) -> Any:
        """Undo the command (optional implementation).
        
        Returns:
            Any: Result of undo operation.
        """
        raise NotImplementedError("Undo not implemented for this command")


class LoadImageCommand(Command):
    """Command to load an image file."""
    
    def __init__(self, image_processor, file_path: str):
        """Initialize the load image command.
        
        Args:
            image_processor: The image processor instance.
            file_path: Path to the image file to load.
        """
        self.image_processor = image_processor
        self.file_path = file_path
        self.loaded_image = None
    
    def execute(self) -> Any:
        """Execute the image loading.
        
        Returns:
            numpy.ndarray: The loaded image data.
            
        Raises:
            Exception: If image loading fails.
        """
        if not self.can_execute():
            raise ValueError(f"Cannot load image: file does not exist: {self.file_path}")
        
        self.loaded_image = self.image_processor.load_image(self.file_path)
        return self.loaded_image
    
    def can_execute(self) -> bool:
        """Check if the image can be loaded.
        
        Returns:
            bool: True if file exists and has valid extension.
        """
        if not self.file_path:
            return False
        
        if not os.path.exists(self.file_path):
            return False
        
        # Check file extension
        valid_extensions = ('.tif', '.tiff')
        return self.file_path.lower().endswith(valid_extensions)
    
    def get_file_info(self) -> dict:
        """Get information about the file.
        
        Returns:
            dict: File information including name, size, etc.
        """
        if not os.path.exists(self.file_path):
            return {'exists': False}
        
        stat = os.stat(self.file_path)
        return {
            'exists': True,
            'name': os.path.basename(self.file_path),
            'size': stat.st_size,
            'path': self.file_path
        }


class LoadLUTCommand(Command):
    """Command to load a LUT file."""
    
    def __init__(self, lut_manager, file_path: str):
        """Initialize the load LUT command.
        
        Args:
            lut_manager: The LUT manager instance.
            file_path: Path to the LUT file to load.
        """
        self.lut_manager = lut_manager
        self.file_path = file_path
        self.loaded_lut = None
    
    def execute(self) -> Any:
        """Execute the LUT loading.
        
        Returns:
            numpy.ndarray: The loaded LUT data.
            
        Raises:
            Exception: If LUT loading fails.
        """
        if not self.can_execute():
            raise ValueError(f"Cannot load LUT: file does not exist: {self.file_path}")
        
        self.loaded_lut = self.lut_manager.load_lut(self.file_path)
        return self.loaded_lut
    
    def can_execute(self) -> bool:
        """Check if the LUT can be loaded.
        
        Returns:
            bool: True if file exists and has valid extension.
        """
        if not self.file_path:
            return False
        
        # Handle both absolute and relative paths
        if os.path.isabs(self.file_path):
            full_path = self.file_path
        else:
            full_path = os.path.join(self.lut_manager.lut_dir, self.file_path)
        
        if not os.path.exists(full_path):
            return False
        
        # Check file extension
        valid_extensions = ('.tif', '.tiff')
        return full_path.lower().endswith(valid_extensions)


class ProcessImageCommand(Command):
    """Command to process an image (apply LUT and inversion)."""
    
    def __init__(self, image_processor, image_data, lut_data):
        """Initialize the process image command.
        
        Args:
            image_processor: The image processor instance.
            image_data: The image data to process.
            lut_data: The LUT data to apply.
        """
        self.image_processor = image_processor
        self.image_data = image_data
        self.lut_data = lut_data
        self.processed_image = None
    
    def execute(self) -> Any:
        """Execute the image processing.
        
        Returns:
            numpy.ndarray: The processed image data.
            
        Raises:
            Exception: If processing fails.
        """
        if not self.can_execute():
            raise ValueError("Cannot process image: missing image data or LUT data")
        
        # Apply LUT
        lut_applied = self.image_processor.apply_lut(self.image_data, self.lut_data)
        
        # Apply inversion
        self.processed_image = self.image_processor.invert_image(lut_applied)
        
        return self.processed_image
    
    def can_execute(self) -> bool:
        """Check if the image can be processed.
        
        Returns:
            bool: True if both image and LUT data are available.
        """
        return self.image_data is not None and self.lut_data is not None


class StartPrintCommand(Command):
    """Command to start printing (display) operation."""
    
    def __init__(self, display_window, image_data, exposure_time: float):
        """Initialize the start print command.
        
        Args:
            display_window: The display window instance.
            image_data: The image data to display.
            exposure_time: Exposure time in seconds.
        """
        self.display_window = display_window
        self.image_data = image_data
        self.exposure_time = exposure_time
    
    def execute(self) -> Any:
        """Execute the print start operation.
        
        Returns:
            bool: True if print started successfully.
            
        Raises:
            Exception: If print start fails.
        """
        if not self.can_execute():
            raise ValueError("Cannot start print: invalid parameters")
        
        # Convert image to frames for display
        frames = self._prepare_frames(self.image_data)
        
        # Start display
        self.display_window.set_frames(frames)
        self.display_window.start_display_loop(self.exposure_time)
        
        return True
    
    def can_execute(self) -> bool:
        """Check if printing can be started.
        
        Returns:
            bool: True if image data exists and exposure time is valid.
        """
        return (self.image_data is not None and 
                self.exposure_time > 0)
    
    def _prepare_frames(self, image_data):
        """Prepare image data for display.
        
        Args:
            image_data: The image data to prepare.
            
        Returns:
            List of frames for display.
        """
        # For now, return the image as a single frame
        # In a real implementation, this might convert 16-bit to 8-bit frames
        return [image_data]


class StopPrintCommand(Command):
    """Command to stop printing (display) operation."""
    
    def __init__(self, display_window):
        """Initialize the stop print command.
        
        Args:
            display_window: The display window instance.
        """
        self.display_window = display_window
    
    def execute(self) -> Any:
        """Execute the print stop operation.
        
        Returns:
            bool: True if print stopped successfully.
        """
        self.display_window.stop_display_loop()
        return True
    
    def can_execute(self) -> bool:
        """Check if printing can be stopped.
        
        Returns:
            bool: Always True (can always attempt to stop).
        """
        return True


class CommandInvoker:
    """Invoker class to execute commands and maintain history."""
    
    def __init__(self):
        """Initialize the command invoker."""
        self.history = []
        self.current_index = -1
    
    def execute_command(self, command: Command) -> Any:
        """Execute a command and add it to history.
        
        Args:
            command: The command to execute.
            
        Returns:
            Any: Result of command execution.
            
        Raises:
            Exception: If command execution fails.
        """
        if not command.can_execute():
            raise ValueError(f"Command cannot be executed: {type(command).__name__}")
        
        result = command.execute()
        
        # Add to history (remove any commands after current index)
        self.history = self.history[:self.current_index + 1]
        self.history.append(command)
        self.current_index += 1
        
        return result
    
    def can_undo(self) -> bool:
        """Check if undo is possible.
        
        Returns:
            bool: True if there are commands to undo.
        """
        return self.current_index >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible.
        
        Returns:
            bool: True if there are commands to redo.
        """
        return self.current_index < len(self.history) - 1
    
    def undo(self) -> Optional[Any]:
        """Undo the last command.
        
        Returns:
            Any: Result of undo operation, or None if no undo available.
        """
        if not self.can_undo():
            return None
        
        command = self.history[self.current_index]
        result = command.undo()
        self.current_index -= 1
        
        return result
    
    def redo(self) -> Optional[Any]:
        """Redo the next command.
        
        Returns:
            Any: Result of redo operation, or None if no redo available.
        """
        if not self.can_redo():
            return None
        
        self.current_index += 1
        command = self.history[self.current_index]
        
        return command.execute()
    
    def get_history(self) -> list:
        """Get command history.
        
        Returns:
            list: List of executed commands.
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear command history."""
        self.history.clear()
        self.current_index = -1


class BatchCommand(Command):
    """Command to execute multiple commands as a batch."""
    
    def __init__(self, commands: list[Command]):
        """Initialize the batch command.
        
        Args:
            commands: List of commands to execute.
        """
        self.commands = commands
        self.executed_commands = []
    
    def execute(self) -> list:
        """Execute all commands in the batch.
        
        Returns:
            list: Results from all command executions.
            
        Raises:
            Exception: If any command fails (partial execution possible).
        """
        results = []
        self.executed_commands = []
        
        for command in self.commands:
            if not command.can_execute():
                raise ValueError(f"Command in batch cannot be executed: {type(command).__name__}")
            
            result = command.execute()
            results.append(result)
            self.executed_commands.append(command)
        
        return results
    
    def can_execute(self) -> bool:
        """Check if all commands in the batch can be executed.
        
        Returns:
            bool: True if all commands can be executed.
        """
        return all(command.can_execute() for command in self.commands)
    
    def undo(self) -> list:
        """Undo all executed commands in reverse order.
        
        Returns:
            list: Results from all undo operations.
        """
        results = []
        
        # Undo in reverse order
        for command in reversed(self.executed_commands):
            result = command.undo()
            results.append(result)
        
        return results

