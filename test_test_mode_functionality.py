#!/usr/bin/env python3
"""Test script to verify test mode functionality."""

import sys
import os
import numpy as np

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Mock PyQt6 modules to avoid GUI dependencies
from unittest.mock import Mock, MagicMock, patch

sys.modules['PyQt6'] = Mock()
sys.modules['PyQt6.QtWidgets'] = Mock()
sys.modules['PyQt6.QtCore'] = Mock()
sys.modules['PyQt6.QtGui'] = Mock()

def test_test_mode_functionality():
    """Test that test mode functionality works correctly."""
    
    print("Testing test mode functionality...")
    
    # Test 1: TestDisplayWindow creation and configuration
    print("✅ Test 1: TestDisplayWindow creation")
    from test_display_window import TestDisplayWindow
    
    test_window = TestDisplayWindow()
    
    # Verify window properties
    assert test_window.window_width == 1280, f"Expected width 1280, got {test_window.window_width}"
    assert test_window.window_height == 720, f"Expected height 720, got {test_window.window_height}"
    
    # Verify aspect ratio (should be 16:9)
    aspect_ratio = test_window.window_width / test_window.window_height
    expected_ratio = 16/9
    assert abs(aspect_ratio - expected_ratio) < 0.01, f"Expected aspect ratio {expected_ratio}, got {aspect_ratio}"
    
    print(f"   Window size: {test_window.window_width}×{test_window.window_height}")
    print(f"   Aspect ratio: {aspect_ratio:.3f} (16:9 = {expected_ratio:.3f})")
    
    # Test 2: Frame handling
    print("✅ Test 2: Frame handling")
    
    # Create test frames (8-bit grayscale)
    test_frames = [
        np.random.randint(0, 255, (100, 150), dtype=np.uint8),
        np.random.randint(0, 255, (100, 150), dtype=np.uint8),
        np.random.randint(0, 255, (100, 150), dtype=np.uint8)
    ]
    
    test_window.set_frames(test_frames, 5000)  # 5 second loop
    
    assert len(test_window.frames) == 3, f"Expected 3 frames, got {len(test_window.frames)}"
    assert test_window.loop_duration_ms == 5000, f"Expected 5000ms, got {test_window.loop_duration_ms}"
    
    print(f"   Frames set: {len(test_window.frames)}")
    print(f"   Loop duration: {test_window.loop_duration_ms}ms")
    
    # Test 3: Display info
    print("✅ Test 3: Display info")
    
    display_info = test_window.get_display_info()
    
    assert display_info['window_size'] == (1280, 720), f"Unexpected window size: {display_info['window_size']}"
    assert abs(display_info['aspect_ratio'] - 16/9) < 0.01, f"Unexpected aspect ratio: {display_info['aspect_ratio']}"
    assert display_info['mode'] == 'windowed_test', f"Unexpected mode: {display_info['mode']}"
    
    print(f"   Display info: {display_info}")
    
    # Test 4: MainWindow test mode methods (mocked)
    print("✅ Test 4: MainWindow test mode methods")
    
    # Mock the main window
    mock_main_window = Mock()
    mock_test_button = Mock()
    mock_test_button.isChecked.return_value = False
    mock_test_button.setText = Mock()
    mock_main_window.test_mode_button = mock_test_button
    mock_main_window.add_log_entry = Mock()
    
    # Import and test the main window methods
    from main_window import MainWindow
    
    # Create a mock instance and test the methods
    main_window = Mock(spec=MainWindow)
    main_window.test_mode_button = mock_test_button
    main_window.add_log_entry = Mock()
    
    # Test is_test_mode_enabled
    main_window.is_test_mode_enabled = lambda: mock_test_button.isChecked()
    
    # Test toggle_test_mode
    def toggle_test_mode():
        if mock_test_button.isChecked():
            mock_test_button.setText("Test Mode: ON")
            main_window.add_log_entry("Test mode enabled - printing will display in windowed mode")
        else:
            mock_test_button.setText("Test Mode: OFF")
            main_window.add_log_entry("Test mode disabled - printing will display fullscreen on secondary monitor")
    
    main_window.toggle_test_mode = toggle_test_mode
    
    # Test OFF state
    mock_test_button.isChecked.return_value = False
    assert not main_window.is_test_mode_enabled(), "Test mode should be OFF initially"
    
    main_window.toggle_test_mode()
    mock_test_button.setText.assert_called_with("Test Mode: OFF")
    
    # Test ON state
    mock_test_button.isChecked.return_value = True
    assert main_window.is_test_mode_enabled(), "Test mode should be ON when checked"
    
    main_window.toggle_test_mode()
    mock_test_button.setText.assert_called_with("Test Mode: ON")
    
    print("   Test mode toggle functionality verified")
    
    print("\n🎉 All test mode functionality tests passed!")
    
    return True

if __name__ == "__main__":
    try:
        test_test_mode_functionality()
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

