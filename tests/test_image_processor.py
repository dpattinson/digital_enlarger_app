import pytest
import numpy as np
from app.image_processor import ImageProcessor


# -------------------- ImageProcessor Tests --------------------

def test_load_image_successful_when_valid_16bit_grayscale_tiff():
    # Given a valid 16-bit grayscale image and correct path
    dummy_path = "test_image.tif"
    dummy_image = np.ones((100, 100), dtype=np.uint16)
    processor = ImageProcessor(
        file_checker=lambda p: p == dummy_path,
        cv2_reader=lambda p, flag: dummy_image
    )

    # When loading the image
    result = processor.load_image(dummy_path)

    # Then it should return the image unchanged
    assert result.shape == (100, 100)
    assert result.dtype == np.uint16

def test_load_image_raises_when_file_not_found():
    # Given an image processor with a failing file checker
    processor = ImageProcessor(file_checker=lambda p: False)

    # When loading a missing file
    # Then it should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        processor.load_image("missing.tif")

def test_load_image_raises_when_invalid_extension():
    # Given an image with a non-TIFF extension
    processor = ImageProcessor(file_checker=lambda p: True)

    # When loading a .jpg file
    # Then it should raise ValueError about file format
    with pytest.raises(ValueError, match="TIFF file"):
        processor.load_image("image.jpg")

def test_load_image_raises_when_wrong_dtype():
    # Given a file that loads as 8-bit instead of 16-bit
    dummy_image = np.ones((100, 100), dtype=np.uint8)
    processor = ImageProcessor(
        file_checker=lambda p: True,
        cv2_reader=lambda p, flag: dummy_image
    )

    # When loading the image
    # Then it should raise ValueError about dtype
    with pytest.raises(ValueError, match="16-bit"):
        processor.load_image("image.tif")

def test_is_portrait_orientation_returns_true_for_tall_image():
    # Given a tall image
    processor = ImageProcessor()
    tall_image = np.ones((800, 400), dtype=np.uint16)

    # When checking orientation
    # Then it should return True
    assert processor.is_portrait_orientation(tall_image)

def test_is_portrait_orientation_returns_false_for_wide_image():
    # Given a wide image
    processor = ImageProcessor()
    wide_image = np.ones((400, 800), dtype=np.uint16)

    # When checking orientation
    # Then it should return False
    assert not processor.is_portrait_orientation(wide_image)

