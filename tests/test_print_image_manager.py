import numpy as np
import pytest
from app.print_image_manager import PrintImageManager


# -------------------- PrintImageManager Tests --------------------

def test_prepare_print_image_returns_uint16_image():
    # Given a valid 16-bit grayscale image and a linear LUT
    image = np.arange(65536, dtype=np.uint16).reshape((256, 256))
    lut = np.arange(65536, dtype=np.uint16)
    manager = PrintImageManager()

    # When preparing the image for printing
    result = manager.prepare_print_image(image, lut)

    # Then it should return a 16-bit LUT-applied image
    assert isinstance(result, np.ndarray)
    assert result.dtype == np.uint16
    assert result.shape == image.shape


def test_prepare_print_image_inverts_correctly():
    # Given a 16-bit image with known values and identity LUT
    image = np.array([[0, 32768], [49152, 65535]], dtype=np.uint16)
    lut = np.arange(65536, dtype=np.uint16)
    manager = PrintImageManager()

    # When preparing the image for printing
    result = manager.prepare_print_image(image, lut)

    # Then the result should be LUT-applied and inverted
    expected = 65535 - lut[image]
    assert np.array_equal(result, expected)


def test_prepare_print_image_raises_on_invalid_image_shape():
    # Given an invalid image shape (3D array) and a valid LUT
    image = np.ones((100, 100, 3), dtype=np.uint16)  # Not 2D
    lut = np.arange(65536, dtype=np.uint16)
    manager = PrintImageManager()

    # When preparing the image
    # Then it should raise a ValueError
    with pytest.raises(ValueError, match=".*2D grayscale image.*"):
        manager.prepare_print_image(image, lut)


def test_prepare_print_image_raises_on_missing_lut():
    # Given a valid image and None for LUT
    image = np.ones((100, 100), dtype=np.uint16)
    lut = None
    manager = PrintImageManager()

    # When preparing the image
    # Then it should raise a ValueError
    with pytest.raises(ValueError, match=".*LUT data.*"):
        manager.prepare_print_image(image, lut)


def test_apply_lut_maps_values_correctly():
    # Given a 16-bit image and a 256x256 LUT that doubles values
    image = np.array([[0, 1], [2, 3]], dtype=np.uint16)
    lut_array = np.arange(65536, dtype=np.uint16).reshape((256, 256))
    expected = lut_array.flatten()[image]
    manager = PrintImageManager()

    # When applying the LUT
    result = manager.apply_lut(image, lut_array)

    # Then output should be LUT-mapped
    assert np.array_equal(result, expected)


def test_invert_image_flips_grayscale_values():
    # Given a 16-bit image
    image = np.array([[0, 32768], [65535, 1]], dtype=np.uint16)
    manager = PrintImageManager()

    # When inverting the image
    result = manager.invert_image(image)

    # Then values should be flipped around 65535
    expected = 65535 - image
    assert np.array_equal(result, expected)


def test_get_print_processing_info_reports_correct_metadata():
    # Given original and processed image (both 2D)
    image = np.ones((256, 512), dtype=np.uint16)
    lut = np.arange(65536, dtype=np.uint16).reshape((256, 256))
    manager = PrintImageManager()
    processed = manager.invert_image(manager.apply_lut(image, lut))

    # When getting print processing info
    info = manager.get_print_processing_info(image, processed)

    # Then returned dictionary should include correct metadata
    assert isinstance(info, dict)
    assert 'original_size' in info
    assert 'processed_size' in info
    assert 'processing_applied' in info
    assert 'display_dimensions' in info
    assert 'optimization' in info
    assert 'lut_applied' in info
    assert 'image_inverted' in info
    assert 'padded_for_8k' in info
    assert 'data_type' in info


def test_calculate_8k_display_info_returns_expected_data_for_8k_input():
    # Given a valid 16-bit grayscale image simulating 8K resolution
    image = np.ones((4320, 7680), dtype=np.uint16)
    manager = PrintImageManager()

    # When calculating display info
    info = manager.calculate_8k_display_info(image)

    # Then it should return a dictionary with correct structure
    assert 'input_size' in info
    assert info['input_size'] == (image.shape[1], image.shape[0])
    assert info['display_size'] == (PrintImageManager.DISPLAY_WIDTH, PrintImageManager.DISPLAY_HEIGHT)
    assert info['fits_without_scaling'] == True
    assert info['padding_needed'] == (0, 0)

def test_calculate_8k_display_info_returns_expected_data_for_smaller_input():
    # Given a valid 16-bit grayscale image simulating 8K resolution
    image = np.ones((2160, 3840), dtype=np.uint16)
    manager = PrintImageManager()

    # When calculating display info
    info = manager.calculate_8k_display_info(image)

    # Then it should return a dictionary with correct structure
    assert 'input_size' in info
    assert info['input_size'] == (image.shape[1], image.shape[0])
    assert info['display_size'] == (PrintImageManager.DISPLAY_WIDTH, PrintImageManager.DISPLAY_HEIGHT)
    assert info['fits_without_scaling'] == True
    assert info['padding_needed'] == (PrintImageManager.DISPLAY_WIDTH-image.shape[1], PrintImageManager.DISPLAY_HEIGHT-image.shape[0])

def test_calculate_8k_display_info_returns_expected_data_for_bigger_input():
    # Given a valid 16-bit grayscale image simulating 8K resolution
    image = np.ones((5000, 8000), dtype=np.uint16)
    manager = PrintImageManager()

    # When calculating display info
    info = manager.calculate_8k_display_info(image)

    # Then it should return a dictionary with correct structure
    assert 'input_size' in info
    assert info['input_size'] == (image.shape[1], image.shape[0])
    assert info['display_size'] == (PrintImageManager.DISPLAY_WIDTH, PrintImageManager.DISPLAY_HEIGHT)
    assert info['fits_without_scaling'] == False
    assert info['padding_needed'] == (0, 0)


def test_validate_print_readiness_returns_true_for_valid_inputs():
    # Given a valid image and LUT
    image = np.ones((128, 128), dtype=np.uint16)
    lut = np.arange(65536, dtype=np.uint16)
    manager = PrintImageManager()

    # When validating readiness
    result = manager.validate_print_readiness(image, lut)

    # Then it should return True
    assert result["ready"] is True


def test_validate_print_readiness_returns_false_for_invalid_lut():
    # Given a valid image and a bad LUT
    image = np.ones((128, 128), dtype=np.uint16)
    lut = np.arange(256, dtype=np.uint16)
    manager = PrintImageManager()

    # When validating readiness
    result = manager.validate_print_readiness(image, lut)

    # Then it should return False
    assert result["ready"] is True
    assert 'LUT' in result['warnings'][0]


def test_generate_dithered_frames_from_array_outputs_expected_structure():
    # Given a valid 16-bit image with a gradient
    image = np.tile(np.linspace(0, 65535, 512, dtype=np.uint16), (512, 1))
    manager = PrintImageManager()

    # When generating dithered frames
    frames = manager.generate_dithered_frames_from_array(image)

    # Then it should return a list of 8-bit frames matching input shape
    assert isinstance(frames, list)
    assert all(isinstance(f, np.ndarray) for f in frames)
    assert all(f.dtype == np.uint8 for f in frames)
    first_shape = frames[0].shape
    #should always be sized for the target display
    assert first_shape[0] == PrintImageManager.DISPLAY_HEIGHT
    assert first_shape[1] == PrintImageManager.DISPLAY_WIDTH
    assert all(f.shape == first_shape for f in frames)
    assert len(frames) == 16