"""Presenter classes for the Darkroom Enlarger Application.

This module implements the Presenter layer of the MVP (Model-View-Presenter) pattern,
containing testable business logic separated from UI dependencies.
"""
from typing import Optional, Protocol
import os


class IMainView(Protocol):
    """Interface for the main view (UI) components."""
    
    def update_image_path_display(self, path: str) -> None:
        """Update the image path display field."""
        ...
    
    def update_lut_path_display(self, path: str) -> None:
        """Update the LUT path display field."""
        ...
    
    def update_processing_summary(self, message: str) -> None:
        """Update the processing summary message."""
        ...
    
    def display_image_in_preview(self, image_data) -> None:
        """Display image data in the preview area."""
        ...
    
    def show_file_dialog(self, title: str, file_filter: str) -> Optional[str]:
        """Show file dialog and return selected path."""
        ...


class IImageModel(Protocol):
    """Interface for image processing model."""
    
    def load_image(self, path: str):
        """Load image from path."""
        ...
    
    def apply_lut(self, image, lut):
        """Apply LUT to image."""
        ...
    
    def invert_image(self, image):
        """Invert image."""
        ...


class ILUTModel(Protocol):
    """Interface for LUT management model."""
    
    def load_lut(self, path: str):
        """Load LUT from path."""
        ...


class MainWindowPresenter:
    """Presenter for the main window, handling business logic without UI dependencies."""
    
    def __init__(self, view: IMainView, image_model: IImageModel, lut_model: ILUTModel):
        """Initialize the presenter.
        
        Args:
            view: The view interface for UI operations.
            image_model: The model for image processing operations.
            lut_model: The model for LUT operations.
        """
        self.view = view
        self.image_model = image_model
        self.lut_model = lut_model
        
        # State
        self.current_image_path: Optional[str] = None
        self.loaded_image = None
        self.loaded_lut = None
    
    def handle_browse_image(self) -> bool:
        """Handle image browsing workflow.
        
        Returns:
            bool: True if image was successfully loaded, False otherwise.
        """
        file_path = self.view.show_file_dialog(
            "Select 16-bit TIFF Image", 
            "TIFF Images (*.tif *.tiff)"
        )
        
        if not file_path:
            return False
        
        return self.load_image(file_path)
    
    def load_image(self, file_path: str) -> bool:
        """Load image from the specified path.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.current_image_path = file_path
            self.view.update_image_path_display(file_path)
            self.view.update_processing_summary(f"Image selected: {os.path.basename(file_path)}")
            
            # Load the image
            self.loaded_image = self.image_model.load_image(file_path)
            
            # Display in preview
            self.view.display_image_in_preview(self.loaded_image)
            self.view.update_processing_summary(f"Image loaded successfully: {os.path.basename(file_path)}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error loading image: {str(e)}"
            self.view.update_processing_summary(error_msg)
            self.loaded_image = None
            return False
    
    def handle_browse_lut(self) -> bool:
        """Handle LUT browsing workflow.
        
        Returns:
            bool: True if LUT was successfully loaded, False otherwise.
        """
        file_path = self.view.show_file_dialog(
            "Select LUT File",
            "LUT Files (*.tif *.tiff)"
        )
        
        if not file_path:
            return False
        
        return self.load_lut(file_path)
    
    def load_lut(self, file_path: str) -> bool:
        """Load LUT from the specified path.
        
        Args:
            file_path: Path to the LUT file.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.view.update_lut_path_display(file_path)
            self.view.update_processing_summary(f"LUT selected: {os.path.basename(file_path)}")
            
            # Load the LUT
            self.loaded_lut = self.lut_model.load_lut(file_path)
            self.view.update_processing_summary(f"LUT loaded successfully: {os.path.basename(file_path)}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error loading LUT: {str(e)}"
            self.view.update_processing_summary(error_msg)
            self.loaded_lut = None
            return False
    
    def handle_process_image(self) -> bool:
        """Handle image processing workflow (apply LUT and inversion).
        
        Returns:
            bool: True if processing was successful, False otherwise.
        """
        # Validate prerequisites
        if not self.loaded_image:
            self.view.update_processing_summary("Error: Please load an image first.")
            return False
        
        if not self.loaded_lut:
            self.view.update_processing_summary("Error: Please select a LUT first.")
            return False
        
        try:
            self.view.update_processing_summary("Processing image...")
            
            # Apply LUT
            lut_applied_image = self.image_model.apply_lut(self.loaded_image, self.loaded_lut)
            
            # Apply inversion
            processed_image = self.image_model.invert_image(lut_applied_image)
            
            # Display result
            self.view.display_image_in_preview(processed_image)
            self.view.update_processing_summary("Image processed successfully (LUT applied + inverted)")
            
            return True
            
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.view.update_processing_summary(error_msg)
            return False
    
    def can_process_image(self) -> bool:
        """Check if image processing is possible.
        
        Returns:
            bool: True if both image and LUT are loaded.
        """
        return self.loaded_image is not None and self.loaded_lut is not None
    
    def get_current_state(self) -> dict:
        """Get current presenter state for testing/debugging.
        
        Returns:
            dict: Current state information.
        """
        return {
            'has_image': self.loaded_image is not None,
            'has_lut': self.loaded_lut is not None,
            'image_path': self.current_image_path,
            'can_process': self.can_process_image()
        }
    
    def reset_state(self) -> None:
        """Reset presenter state."""
        self.current_image_path = None
        self.loaded_image = None
        self.loaded_lut = None
        self.view.update_processing_summary("Ready")


class PrintPresenter:
    """Presenter for print operations."""
    
    def __init__(self, view: IMainView, display_window):
        """Initialize the print presenter.
        
        Args:
            view: The main view interface.
            display_window: The display window for printing.
        """
        self.view = view
        self.display_window = display_window
        self.is_printing = False
    
    def handle_start_print(self, image_data, exposure_time: float) -> bool:
        """Handle start print workflow.
        
        Args:
            image_data: The processed image data to print.
            exposure_time: Exposure time in seconds.
            
        Returns:
            bool: True if print started successfully.
        """
        if not image_data:
            self.view.update_processing_summary("Error: No processed image available for printing.")
            return False
        
        if exposure_time <= 0:
            self.view.update_processing_summary("Error: Invalid exposure time.")
            return False
        
        try:
            # Convert to frames for display
            frames = self._prepare_frames_for_display(image_data)
            
            # Start display
            self.display_window.set_frames(frames)
            self.display_window.start_display_loop(exposure_time)
            
            self.is_printing = True
            self.view.update_processing_summary(f"Print started - Exposure: {exposure_time}s")
            
            return True
            
        except Exception as e:
            error_msg = f"Error starting print: {str(e)}"
            self.view.update_processing_summary(error_msg)
            return False
    
    def handle_stop_print(self) -> bool:
        """Handle stop print workflow.
        
        Returns:
            bool: True if print stopped successfully.
        """
        try:
            self.display_window.stop_display_loop()
            self.is_printing = False
            self.view.update_processing_summary("Print stopped")
            return True
            
        except Exception as e:
            error_msg = f"Error stopping print: {str(e)}"
            self.view.update_processing_summary(error_msg)
            return False
    
    def _prepare_frames_for_display(self, image_data):
        """Prepare image data for display window.
        
        Args:
            image_data: The image data to prepare.
            
        Returns:
            List of frames for display.
        """
        # This would typically convert 16-bit to 8-bit frames
        # For now, return the image as a single frame
        return [image_data]
    
    def get_print_status(self) -> dict:
        """Get current print status.
        
        Returns:
            dict: Print status information.
        """
        return {
            'is_printing': self.is_printing,
            'display_active': getattr(self.display_window, 'is_active', False)
        }

