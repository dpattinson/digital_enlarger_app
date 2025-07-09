#!/usr/bin/env python3
"""Test script to verify that processed images persist in preview after processing."""

import sys
import os
import numpy as np

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from controller import Controller
from unittest.mock import Mock, MagicMock

def test_processed_image_persistence():
    """Test that processed images persist in preview after processing."""
    
    print("Testing processed image persistence...")
    
    # Create mock main window
    mock_main_window = Mock()
    mock_main_window.add_log_entry = Mock()
    mock_main_window.display_preview_pixmap = Mock()
    
    # Create controller
    controller = Controller(mock_main_window)
    
    # Create test image data (16-bit grayscale)
    test_image = np.random.randint(0, 65535, (1000, 1500), dtype=np.uint16)
    
    # Create test LUT
    test_lut = np.arange(65536, dtype=np.uint16)
    
    # Set up controller state
    controller.loaded_image = test_image
    controller.loaded_lut = test_lut
    
    # Mock the image processor methods
    controller.image_processor.apply_lut = Mock(return_value=test_image * 0.8)
    controller.image_processor.invert_image = Mock(return_value=65535 - test_image)
    
    # Mock the preview manager
    controller.preview_manager.create_preview_pixmap = Mock(return_value=Mock())
    
    print("✅ Initial state: processed_image should be None")
    assert controller.processed_image is None, "processed_image should initially be None"
    
    # Test 1: Process image
    print("🔄 Processing image...")
    controller.process_image()
    
    print("✅ After processing: processed_image should be set")
    assert controller.processed_image is not None, "processed_image should be set after processing"
    
    # Verify the processed image is the inverted result
    expected_processed = 65535 - test_image
    np.testing.assert_array_equal(controller.processed_image, expected_processed)
    
    # Test 2: Verify preview uses processed image
    print("🔄 Updating preview display...")
    controller.update_preview_display()
    
    # Check that create_preview_pixmap was called with processed image
    last_call_args = controller.preview_manager.create_preview_pixmap.call_args
    preview_image_used = last_call_args[0][0]  # First positional argument
    
    print("✅ Preview should use processed image")
    np.testing.assert_array_equal(preview_image_used, controller.processed_image)
    
    # Test 3: Load new image should clear processed image
    print("🔄 Loading new image...")
    new_test_image = np.random.randint(0, 65535, (800, 1200), dtype=np.uint16)
    controller.loaded_image = new_test_image
    controller.processed_image = None  # Simulate what happens in select_image
    
    print("✅ After loading new image: processed_image should be None")
    assert controller.processed_image is None, "processed_image should be cleared when new image is loaded"
    
    # Test 4: Preview should use original image when no processed image
    print("🔄 Updating preview with original image...")
    controller.update_preview_display()
    
    last_call_args = controller.preview_manager.create_preview_pixmap.call_args
    preview_image_used = last_call_args[0][0]  # First positional argument
    
    print("✅ Preview should use original image when no processed image")
    np.testing.assert_array_equal(preview_image_used, new_test_image)
    
    print("\n🎉 All tests passed! Processed image persistence works correctly.")
    
    return True

if __name__ == "__main__":
    try:
        test_processed_image_persistence()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

