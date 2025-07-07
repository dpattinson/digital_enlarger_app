import numpy as np
import tifffile

def create_dummy_image(path, width=1024, height=768):
    # Create a dummy 16-bit grayscale image with a gradient
    image = np.linspace(0, 65535, width * height, dtype=np.uint16).reshape((height, width))
    tifffile.imwrite(path, image)
    print(f"Dummy 16-bit TIFF image created at: {path}")

def create_dummy_lut(path, size=255):
    # Create a dummy 255x255 16-bit grayscale LUT
    # For simplicity, let's make it a linear mapping from 0-255 to 0-65535
    # The LUT is 255x255, representing input intensity (0-254) to output intensity (0-65535)
    lut = np.zeros((size, size), dtype=np.uint16)
    for i in range(size):
        # Simple linear mapping for testing purposes
        lut[i, :] = np.linspace(0, 65535, size, dtype=np.uint16)
    tifffile.imwrite(path, lut)
    print(f"Dummy 16-bit TIFF LUT created at: {path}")

if __name__ == "__main__":
    # Create dummy image in the assets folder
    create_dummy_image("assets/dummy_image.tif")
    # Create dummy LUT in the luts folder
    create_dummy_lut("luts/dummy_lut.tif")


