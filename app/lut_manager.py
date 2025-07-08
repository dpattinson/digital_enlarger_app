import os
import tifffile
import numpy as np

class LUTManager:
    """Manages loading and validation of Look-Up Table (LUT) files."""
    def __init__(self, lut_dir):
        self.lut_dir = lut_dir
        self.lut_files = self._find_lut_files()

    def _find_lut_files(self):
        if not os.path.exists(self.lut_dir):
            return []
        return [f for f in os.listdir(self.lut_dir) if f.endswith(('.tif', '.tiff'))]

    def get_lut_names(self):
        return self.lut_files

    def load_lut(self, lut_path):
        """Loads and validates a 16-bit TIFF LUT file that is 256x256 pixels.

        Args:
            lut_path (str): The path to the LUT file (can be absolute or relative to lut_dir).

        Returns:
            numpy.ndarray: The loaded LUT data as a NumPy array.

        Raises:
            FileNotFoundError: If the LUT file does not exist.
            ValueError: If the LUT is not a 16-bit TIFF file or not 256x256 pixels.
        """
        # Handle both absolute paths and filenames
        if os.path.isabs(lut_path):
            full_path = lut_path
        else:
            full_path = os.path.join(self.lut_dir, lut_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"LUT file not found: {full_path}")
        
        # Check if file is a TIFF file
        if not full_path.lower().endswith(('.tif', '.tiff')):
            raise ValueError("LUT file must be a TIFF file (.tif or .tiff)")
        
        try:
            lut = tifffile.imread(full_path)
        except Exception as e:
            raise ValueError(f"Failed to read TIFF LUT file: {e}")
        
        # Validate LUT format
        if lut.dtype != np.uint16:
            raise ValueError(f"LUT must be 16-bit (uint16). Found: {lut.dtype}")
        
        if lut.shape != (256, 256):
            raise ValueError(f"LUT must be 256x256 pixels. Found: {lut.shape}")
            
        return lut


