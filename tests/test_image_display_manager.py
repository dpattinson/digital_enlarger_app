import numpy as np
import pytest
from app.image_display_manager import ImageDisplayManager

# -------------------- ImageDisplayManager Tests --------------------

def test_validate_image_data_returns_true_for_valid_uint16():
    # Given a valid 16-bit grayscale image
    image = np.ones((100, 100), dtype=np.uint16)
    manager = ImageDisplayManager()

    # When validating image data
    is_valid = manager.validate_image_data(image)

    # Then it should return True
    assert is_valid is True

def test_validate_image_data_returns_false_for_invalid_dtype():
    # Given an image with float32 dtype
    image = np.ones((100, 100), dtype=np.float32)
    manager = ImageDisplayManager()

    # When validating image data
    is_valid = manager.validate_image_data(image)

    # Then it should return False
    assert is_valid is False

def test_calculate_scaled_size_preserves_aspect_ratio():
    # Given an image and container with different aspect ratios
    image_size = (4000, 2000)
    container_size = (1000, 1000)
    manager = ImageDisplayManager()

    # When calculating scaled size
    scaled = manager.calculate_scaled_size(image_size, container_size)

    # Then the result should fit inside container and preserve aspect
    assert scaled[0] <= container_size[0]
    assert scaled[1] <= container_size[1]
    assert scaled[0] / scaled[1] == pytest.approx(image_size[0] / image_size[1])

def test_scale_image_for_display_resizes_image_correctly():
    # Given a valid image and target size
    image = np.ones((100, 200), dtype=np.uint16)
    target_size = (50, 25)
    manager = ImageDisplayManager()

    # When scaling the image
    scaled = manager.scale_image_for_display(image, target_size)

    # Then it should return the resized image
    assert scaled.shape == (25, 50)
    assert scaled.dtype == np.uint16

def test_prepare_image_for_qt_display_returns_expected_structure():
    # Given a valid 16-bit image and target size
    image = (np.random.rand(100, 200) * 65535).astype(np.uint16)
    target_size = (50, 50)
    manager = ImageDisplayManager()

    # When preparing for Qt display
    result = manager.prepare_image_for_qt_display(image, target_size)

    # Then it should return a tuple with valid image metadata
    qt_data, width, height, bytes_per_line = result
    assert isinstance(qt_data, np.ndarray)
    assert qt_data.dtype == np.uint16
    assert qt_data.shape == (height, width)
    assert width == 50
    assert height == 50
    assert bytes_per_line == width * 2

def test_calculate_display_info_returns_display_metadata():
    # Given a valid image and container size
    image = np.ones((100, 150), dtype=np.uint16)
    container = (200, 200)
    manager = ImageDisplayManager()

    # When calculating display info
    info = manager.calculate_display_info(image, container)

    # Then it should return a populated info dictionary
    assert isinstance(info, dict)
    assert info['is_valid'] is True
    assert 'scaled_size' in info
    assert info['scaled_size'][0] <= container[0]
    assert info['scaled_size'][1] <= container[1]
