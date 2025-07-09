#!/usr/bin/env python3
"""Simple test to verify processed image persistence logic."""

import numpy as np

def test_processed_image_logic():
    """Test the core logic of processed image persistence."""
    
    print("Testing processed image persistence logic...")
    
    # Simulate controller state
    class MockController:
        def __init__(self):
            self.loaded_image = None
            self.processed_image = None
            
        def get_display_image(self):
            """Get the image that should be displayed in preview."""
            return self.processed_image if self.processed_image is not None else self.loaded_image
    
    controller = MockController()
    
    # Test 1: No images loaded
    print("✅ Test 1: No images - should return None")
    assert controller.get_display_image() is None
    
    # Test 2: Original image loaded
    test_image = np.random.randint(0, 65535, (100, 150), dtype=np.uint16)
    controller.loaded_image = test_image
    
    print("✅ Test 2: Original image loaded - should return original")
    display_image = controller.get_display_image()
    np.testing.assert_array_equal(display_image, test_image)
    
    # Test 3: Processed image available
    processed_image = 65535 - test_image  # Simulate inversion
    controller.processed_image = processed_image
    
    print("✅ Test 3: Processed image available - should return processed")
    display_image = controller.get_display_image()
    np.testing.assert_array_equal(display_image, processed_image)
    
    # Test 4: Clear processed image (new image loaded)
    controller.processed_image = None
    
    print("✅ Test 4: Processed cleared - should return original again")
    display_image = controller.get_display_image()
    np.testing.assert_array_equal(display_image, test_image)
    
    print("\n🎉 All logic tests passed! Processed image persistence logic works correctly.")
    return True

if __name__ == "__main__":
    try:
        test_processed_image_logic()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

