"""View interfaces for the Darkroom Enlarger Application.

This module defines interfaces for UI components to enable dependency injection
and improve testability.
"""
from typing import Optional, Protocol


class IFileDialog(Protocol):
    """Interface for file dialog operations."""
    
    def get_open_filename(self, parent, title: str, directory: str, filter: str) -> tuple[str, str]:
        """Show open file dialog.
        
        Args:
            parent: Parent widget.
            title: Dialog title.
            directory: Initial directory.
            filter: File filter string.
            
        Returns:
            Tuple of (selected_file_path, selected_filter).
        """
        ...


class IMessageDisplay(Protocol):
    """Interface for message display operations."""
    
    def show_info(self, title: str, message: str) -> None:
        """Show information message."""
        ...
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning message."""
        ...
    
    def show_error(self, title: str, message: str) -> None:
        """Show error message."""
        ...


class QtFileDialog:
    """PyQt6 implementation of file dialog interface."""
    
    def __init__(self):
        """Initialize Qt file dialog."""
        from PyQt6.QtWidgets import QFileDialog
        self.QFileDialog = QFileDialog
    
    def get_open_filename(self, parent, title: str, directory: str, filter: str) -> tuple[str, str]:
        """Show Qt open file dialog."""
        return self.QFileDialog.getOpenFileName(parent, title, directory, filter)


class MockFileDialog:
    """Mock implementation of file dialog for testing."""
    
    def __init__(self, return_path: Optional[str] = None):
        """Initialize mock file dialog.
        
        Args:
            return_path: Path to return from dialog, None for cancelled dialog.
        """
        self.return_path = return_path
        self.call_history = []
    
    def get_open_filename(self, parent, title: str, directory: str, filter: str) -> tuple[str, str]:
        """Mock file dialog that returns predetermined path."""
        self.call_history.append({
            'title': title,
            'directory': directory,
            'filter': filter
        })
        
        if self.return_path:
            return (self.return_path, filter)
        else:
            return ("", "")


class QtMessageDisplay:
    """PyQt6 implementation of message display interface."""
    
    def __init__(self):
        """Initialize Qt message display."""
        from PyQt6.QtWidgets import QMessageBox
        self.QMessageBox = QMessageBox
    
    def show_info(self, title: str, message: str) -> None:
        """Show Qt information message."""
        self.QMessageBox.information(None, title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show Qt warning message."""
        self.QMessageBox.warning(None, title, message)
    
    def show_error(self, title: str, message: str) -> None:
        """Show Qt error message."""
        self.QMessageBox.critical(None, title, message)


class MockMessageDisplay:
    """Mock implementation of message display for testing."""
    
    def __init__(self):
        """Initialize mock message display."""
        self.messages = []
    
    def show_info(self, title: str, message: str) -> None:
        """Record info message."""
        self.messages.append(('info', title, message))
    
    def show_warning(self, title: str, message: str) -> None:
        """Record warning message."""
        self.messages.append(('warning', title, message))
    
    def show_error(self, title: str, message: str) -> None:
        """Record error message."""
        self.messages.append(('error', title, message))
    
    def get_last_message(self) -> Optional[tuple]:
        """Get the last message that was displayed.
        
        Returns:
            Tuple of (type, title, message) or None if no messages.
        """
        return self.messages[-1] if self.messages else None
    
    def clear_messages(self) -> None:
        """Clear all recorded messages."""
        self.messages.clear()


class MainViewAdapter:
    """Adapter to make MainWindow compatible with IMainView interface."""
    
    def __init__(self, main_window, file_dialog: IFileDialog = None):
        """Initialize the adapter.
        
        Args:
            main_window: The MainWindow instance.
            file_dialog: File dialog implementation to use.
        """
        self.main_window = main_window
        self.file_dialog = file_dialog or QtFileDialog()
    
    def update_image_path_display(self, path: str) -> None:
        """Update the image path display field."""
        self.main_window.image_path_display.setText(path)
    
    def update_lut_path_display(self, path: str) -> None:
        """Update the LUT path display field."""
        self.main_window.lut_path_display.setText(path)
    
    def update_processing_summary(self, message: str) -> None:
        """Update the processing summary message."""
        self.main_window.update_processing_summary(message)
    
    def display_image_in_preview(self, image_data) -> None:
        """Display image data in the preview area."""
        self.main_window.display_image_in_preview(image_data)
    
    def show_file_dialog(self, title: str, file_filter: str) -> Optional[str]:
        """Show file dialog and return selected path."""
        file_path, _ = self.file_dialog.get_open_filename(
            self.main_window, title, "", file_filter
        )
        return file_path if file_path else None


class MockMainView:
    """Mock implementation of main view for testing."""
    
    def __init__(self, file_dialog: IFileDialog = None):
        """Initialize mock main view.
        
        Args:
            file_dialog: File dialog implementation to use.
        """
        self.file_dialog = file_dialog or MockFileDialog()
        
        # State tracking
        self.image_path = ""
        self.lut_path = ""
        self.processing_summary = ""
        self.displayed_image = None
        
        # Call history
        self.method_calls = []
    
    def update_image_path_display(self, path: str) -> None:
        """Update the image path display field."""
        self.image_path = path
        self.method_calls.append(('update_image_path_display', path))
    
    def update_lut_path_display(self, path: str) -> None:
        """Update the LUT path display field."""
        self.lut_path = path
        self.method_calls.append(('update_lut_path_display', path))
    
    def update_processing_summary(self, message: str) -> None:
        """Update the processing summary message."""
        self.processing_summary = message
        self.method_calls.append(('update_processing_summary', message))
    
    def display_image_in_preview(self, image_data) -> None:
        """Display image data in the preview area."""
        self.displayed_image = image_data
        self.method_calls.append(('display_image_in_preview', image_data))
    
    def show_file_dialog(self, title: str, file_filter: str) -> Optional[str]:
        """Show file dialog and return selected path."""
        self.method_calls.append(('show_file_dialog', title, file_filter))
        return self.file_dialog.get_open_filename(None, title, "", file_filter)[0] or None
    
    def get_last_call(self) -> Optional[tuple]:
        """Get the last method call.
        
        Returns:
            Tuple of method call details or None.
        """
        return self.method_calls[-1] if self.method_calls else None
    
    def clear_calls(self) -> None:
        """Clear method call history."""
        self.method_calls.clear()

