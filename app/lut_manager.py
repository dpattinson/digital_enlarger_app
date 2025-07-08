"""Manages the loading and retrieval of Look-Up Tables (LUTs)."""
import os
import tifffile
import numpy as np

class LUTManager:
    """Handles finding, loading, and providing access to LUT files."""
    def __init__(self, lut_dir):
        """Initializes the LUTManager with the directory containing LUTs.

        Args:
            lut_dir (str): The path to the directory where LUT files are stored.
        """
        self.lut_dir = lut_dir
        self.lut_files = self._find_lut_files()

    def _find_lut_files(self):
        """Finds all TIFF LUT files in the specified directory.

        Returns:
            list: A list of LUT filenames found in the directory.
        """
        if not os.path.exists(self.lut_dir):
            return []
        return [f for f in os.listdir(self.lut_dir) if f.endswith((".tif", ".tiff"))]

    def get_lut_names(self):
        """Returns the names of the found LUT files.

        Returns:
            list: A list of LUT filenames.
        """
        return self.lut_files

    def load_lut(self, lut_filename):
        """Loads a specific LUT file.

        Args:
            lut_filename (str): The name of the LUT file to load.

        Returns:
            numpy.ndarray: The loaded LUT as a NumPy array.

        Raises:
            FileNotFoundError: If the LUT file does not exist.
            ValueError: If the LUT format is invalid (not 256x256 16-bit).
        """
        lut_path = os.path.join(self.lut_dir, lut_filename)
        if not os.path.exists(lut_path):
            raise FileNotFoundError(f"LUT file not found: {lut_path}")
        
        # Load the 16-bit grayscale TIFF LUT
        lut = tifffile.imread(lut_path)
        
        # Ensure LUT is 256x256 and 16-bit
        if lut.shape != (256, 256) or lut.dtype != np.uint16:
            raise ValueError(
                f"Invalid LUT format. Expected 256x256 16-bit, got {lut.shape} {lut.dtype}"
            )
            
        return lut


