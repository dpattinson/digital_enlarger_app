import numpy as np
from PyQt6.QtGui import QPixmap
from app.preview_image_manager import PreviewImageManager


# -------------------- PreviewImageManager Tests --------------------

def test_create_preview_pixmap_returns_qpixmap(qapp):
    # Given a 16-bit grayscale image of shape (100, 100)
    image = (np.random.rand(100, 100) * 65535).astype(np.uint16)

    manager = PreviewImageManager()

    # When creating a preview pixmap
    result = manager.create_preview_pixmap(image, container_size=(200, 200))

    # Then it should return a QPixmap (scaled preview) and quit cleanly
    assert isinstance(result, QPixmap)

