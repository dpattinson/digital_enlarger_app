import pytest
import numpy as np
from app.lut_manager import LUTManager


# -------------------- LUTManager Tests --------------------

def test_load_lut_successful_when_valid_lut_file():
    # Given a valid LUT with shape (256, 256) and an absolute path
    dummy_path = "/mock/path/lut.tif"
    dummy_lut = np.ones((256, 256), dtype=np.uint16)
    manager = LUTManager(
        file_checker=lambda p: p == dummy_path,
        tiff_reader=lambda p: dummy_lut
    )

    # When loading the LUT
    result = manager.load_lut(dummy_path)

    # Then it should return the LUT unchanged
    assert isinstance(result, np.ndarray)
    assert result.shape == (256, 256)
    assert result.dtype == np.uint16

def test_load_lut_raises_when_file_not_found():
    # Given a file checker that always fails
    manager = LUTManager(file_checker=lambda p: False)

    # When loading a non-existent LUT
    # Then it should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        manager.load_lut("/mock/path/missing_lut.tif")

def test_load_lut_raises_when_wrong_shape():
    # Given a LUT with incorrect shape but valid absolute path
    dummy_path = "/mock/path/bad_lut.tif"
    manager = LUTManager(
        file_checker=lambda p: True,
        tiff_reader=lambda p: np.ones((256, 1), dtype=np.uint16)
    )

    # When loading it
    # Then it should raise ValueError about 256x256 shape
    with pytest.raises(ValueError, match="256x256"):
        manager.load_lut(dummy_path)