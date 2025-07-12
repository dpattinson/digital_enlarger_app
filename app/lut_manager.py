import os
import tifffile
import numpy as np

class LUTManager:
    """Manages loading and validation of Look-Up Table (LUT) files."""
    def __init__(self, file_checker=None, dir_lister=None, tiff_reader=None):
        """Initializes the LUTManager.
        
        Args:
            file_checker (callable, optional): Function to check if file/dir exists.
                                             Defaults to os.path.exists.
            dir_lister (callable, optional): Function to list directory contents.
                                           Defaults to os.listdir.
            tiff_reader (callable, optional): Function to read TIFF files.
                                            Defaults to tifffile.imread.
        """
        self.file_checker = file_checker or os.path.exists
        self.dir_lister = dir_lister or os.listdir
        self.tiff_reader = tiff_reader or tifffile.imread

    def load_lut(self, lut_path):
        """Loads and validates a 16-bit TIFF LUT file that is 256x256 pixels.

        Args:
            lut_path (str): The path to the LUT file.

        Returns:
            numpy.ndarray: The loaded LUT data as a NumPy array.

        Raises:
            FileNotFoundError: If the LUT file does not exist.
            ValueError: If the LUT is not a 16-bit TIFF file or not 256x256 pixels.
        """
        # Handle absolute path
        if not os.path.isabs(lut_path):
            raise FileNotFoundError(f"invalid path: {lut_path}")
        
        # Check if file exists
        if not self.file_checker(lut_path):
            raise FileNotFoundError(f"LUT file not found: {lut_path}")
        
        # Check if file is a TIFF file
        if not lut_path.lower().endswith(('.tif', '.tiff')):
            raise ValueError("LUT file must be a TIFF file (.tif or .tiff)")
        
        try:
            lut = self.tiff_reader(lut_path)
        except Exception as e:
            raise ValueError(f"Failed to read TIFF LUT file: {e}")
        
        # Validate LUT format
        if lut.dtype != np.uint16:
            raise ValueError(f"LUT must be 16-bit (uint16). Found: {lut.dtype}")
        
        if lut.shape != (256, 256):
            raise ValueError(f"LUT must be 256x256 pixels. Found: {lut.shape}")
            
        return lut


