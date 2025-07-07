import os
import tifffile
import numpy as np

class LUTManager:
    def __init__(self, lut_dir):
        self.lut_dir = lut_dir
        self.lut_files = self._find_lut_files()

    def _find_lut_files(self):
        if not os.path.exists(self.lut_dir):
            return []
        return [f for f in os.listdir(self.lut_dir) if f.endswith(('.tif', '.tiff'))]

    def get_lut_names(self):
        return self.lut_files

    def load_lut(self, lut_filename):
        lut_path = os.path.join(self.lut_dir, lut_filename)
        if not os.path.exists(lut_path):
            raise FileNotFoundError(f"LUT file not found: {lut_path}")
        
        # Load the 16-bit grayscale TIFF LUT
        lut = tifffile.imread(lut_path)
        
        # Ensure LUT is 255x255 and 16-bit
        if lut.shape != (255, 255) or lut.dtype != np.uint16:
            raise ValueError(f"Invalid LUT format. Expected 255x255 16-bit, got {lut.shape} {lut.dtype}")
            
        return lut


