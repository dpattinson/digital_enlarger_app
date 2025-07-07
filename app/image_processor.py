import numpy as np
import tifffile
from PIL import Image

class ImageProcessor:
    def __init__(self):
        pass

    def load_image(self, image_path):
        # Load 16-bit grayscale TIFF image
        img = tifffile.imread(image_path)
        if img.dtype != np.uint16:
            raise ValueError(f"Image must be 16-bit grayscale, got {img.dtype}")
        return img

    def apply_lut(self, image, lut):
        # Apply tone mapping LUT
        # The LUT is 255x255, representing input intensity (0-65535) to output intensity (0-65535)
        # We need to map the 16-bit image values to the 0-254 range for LUT lookup
        # And then map the LUT output back to 16-bit

        # Scale 16-bit image values (0-65535) to 0-254 for indexing into the 255-entry LUT
        # Ensure values are clamped to 0-254 to avoid out-of-bounds indexing
        scaled_image = np.clip((image / 65535.0 * 254), 0, 254).astype(np.uint8)

        if lut.shape == (255, 255):
            # Assuming the LUT is a 1D mapping where lut[input_value] = output_value
            # and the 255x255 structure means each row is a potential LUT, or it's a 2D interpolation table.
            # For simplicity and based on common LUT usage, we'll use the first row as the 1D LUT.
            lut_1d = lut[0, :]
            
            # Apply the 1D LUT to the scaled image
            # The values in scaled_image (0-254) are used as indices into lut_1d
            processed_image = lut_1d[scaled_image]
        else:
            raise ValueError("Unsupported LUT format. Expected 255x255.")

        return processed_image.astype(np.uint16)

    def invert_image(self, image):
        # Invert 16-bit image
        return 65535 - image

    def emulate_12bit_to_8bit_frames(self, image_16bit, num_frames=4):
        # Convert 16-bit image to a sequence of 8-bit frames to simulate 12-bit depth
        # This is a simplified temporal dithering/frame sequencing approach.
        # The idea is to distribute the 16-bit value across multiple 8-bit frames.
        # For 12-bit emulation on an 8-bit display, we need to simulate 4096 levels.
        # An 8-bit display has 256 levels.
        # 4096 / 256 = 16. So each 8-bit step represents 16 12-bit steps.

        frames = []
        # Scale 16-bit image to 12-bit range (0-4095)
        image_12bit = (image_16bit / 65535.0 * 4095).astype(np.uint16)

        for i in range(num_frames):
            # Simple approach: create frames by shifting bits or distributing intensity
            # This is a very basic example and will likely need a more advanced algorithm
            # for proper temporal dithering or frame sequencing.
            
            # For demonstration, let's just create slightly varied 8-bit versions
            # This is NOT a proper 12-bit emulation, but a starting point.
            frame = (image_12bit >> (4 - i)) & 0xFF # Shift and mask to get 8-bit component
            frames.append(frame.astype(np.uint8))
            
        return frames


