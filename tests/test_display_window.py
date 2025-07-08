import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock PyQt6 before importing the display window
sys.modules['PyQt6'] = Mock()
sys.modules['PyQt6.QtWidgets'] = Mock()
sys.modules['PyQt6.QtCore'] = Mock()
sys.modules['PyQt6.QtGui'] = Mock()

from app.display_window import DisplayWindow


class TestDisplayWindow(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        # Patch PyQt6 classes before creating DisplayWindow
        with patch('app.display_window.QMainWindow'), \
             patch('app.display_window.QLabel'), \
             patch('app.display_window.QTimer'), \
             patch('app.display_window.QPixmap'), \
             patch('app.display_window.QImage'), \
             patch('app.display_window.QApplication'):
            
            self.display_window = DisplayWindow()

    def test_display_window_initialization(self):
        """Test display window initialization."""
        # Verify display window was created
        self.assertIsNotNone(self.display_window)
        
        # Verify initial state
        self.assertEqual(self.display_window.frames, [])
        self.assertEqual(self.display_window.current_frame_index, 0)
        self.assertEqual(self.display_window.loop_duration_ms, 30000)  # Default 30 seconds
        
        # Verify UI components exist
        self.assertTrue(hasattr(self.display_window, 'image_label'))
        self.assertTrue(hasattr(self.display_window, 'timer'))

    def test_set_frames_valid(self):
        """Test setting valid frames."""
        # Create test frames
        test_frames = [
            np.array([[100, 150], [200, 250]], dtype=np.uint8),
            np.array([[110, 160], [210, 260]], dtype=np.uint8),
            np.array([[120, 170], [220, 270]], dtype=np.uint8),
            np.array([[130, 180], [230, 280]], dtype=np.uint8)
        ]
        test_duration = 5000  # 5 seconds
        
        # Call set_frames
        self.display_window.set_frames(test_frames, test_duration)
        
        # Verify frames were set
        self.assertEqual(len(self.display_window.frames), 4)
        self.assertEqual(self.display_window.loop_duration_ms, test_duration)
        self.assertEqual(self.display_window.current_frame_index, 0)
        
        # Verify frames are stored correctly
        for i, frame in enumerate(test_frames):
            np.testing.assert_array_equal(self.display_window.frames[i], frame)

    def test_set_frames_empty_list(self):
        """Test setting empty frames list."""
        # Call set_frames with empty list
        self.display_window.set_frames([], 1000)
        
        # Verify frames were set
        self.assertEqual(len(self.display_window.frames), 0)
        self.assertEqual(self.display_window.loop_duration_ms, 1000)
        self.assertEqual(self.display_window.current_frame_index, 0)

    def test_set_frames_single_frame(self):
        """Test setting single frame."""
        # Create single test frame
        test_frame = np.array([[100, 150], [200, 250]], dtype=np.uint8)
        test_frames = [test_frame]
        
        # Call set_frames
        self.display_window.set_frames(test_frames, 2000)
        
        # Verify frame was set
        self.assertEqual(len(self.display_window.frames), 1)
        np.testing.assert_array_equal(self.display_window.frames[0], test_frame)

    @patch('app.display_window.QApplication.screens')
    def test_show_on_secondary_monitor_multiple_screens(self, mock_screens):
        """Test showing on secondary monitor when multiple screens exist."""
        # Mock multiple screens
        mock_screen1 = Mock()
        mock_screen2 = Mock()
        mock_screen1.geometry.return_value = Mock(x=lambda: 0, y=lambda: 0, width=lambda: 1920, height=lambda: 1080)
        mock_screen2.geometry.return_value = Mock(x=lambda: 1920, y=lambda: 0, width=lambda: 1920, height=lambda: 1080)
        mock_screens.return_value = [mock_screen1, mock_screen2]
        
        # Mock display window methods
        self.display_window.move = Mock()
        self.display_window.showFullScreen = Mock()
        
        # Call show_on_secondary_monitor
        self.display_window.show_on_secondary_monitor()
        
        # Verify window was moved to secondary screen and shown fullscreen
        self.display_window.move.assert_called_once_with(1920, 0)
        self.display_window.showFullScreen.assert_called_once()

    @patch('app.display_window.QApplication.screens')
    def test_show_on_secondary_monitor_single_screen(self, mock_screens):
        """Test showing on secondary monitor when only one screen exists."""
        # Mock single screen
        mock_screen = Mock()
        mock_screen.geometry.return_value = Mock(x=lambda: 0, y=lambda: 0, width=lambda: 1920, height=lambda: 1080)
        mock_screens.return_value = [mock_screen]
        
        # Mock display window methods
        self.display_window.move = Mock()
        self.display_window.showFullScreen = Mock()
        
        # Call show_on_secondary_monitor
        self.display_window.show_on_secondary_monitor()
        
        # Verify window was shown fullscreen on primary screen
        self.display_window.move.assert_called_once_with(0, 0)
        self.display_window.showFullScreen.assert_called_once()

    def test_start_display_loop_with_frames(self):
        """Test starting display loop with frames."""
        # Set up test frames
        test_frames = [
            np.array([[100, 150]], dtype=np.uint8),
            np.array([[110, 160]], dtype=np.uint8)
        ]
        self.display_window.set_frames(test_frames, 4000)  # 4 seconds total
        
        # Mock timer
        self.display_window.timer = Mock()
        
        # Call start_display_loop
        self.display_window.start_display_loop()
        
        # Verify timer was started with correct interval
        # 4000ms / 2 frames = 2000ms per frame
        expected_interval = 4000 // 2
        self.display_window.timer.start.assert_called_once_with(expected_interval)

    def test_start_display_loop_no_frames(self):
        """Test starting display loop without frames."""
        # No frames set
        self.display_window.frames = []
        
        # Mock timer
        self.display_window.timer = Mock()
        
        # Call start_display_loop
        self.display_window.start_display_loop()
        
        # Verify timer was not started
        self.display_window.timer.start.assert_not_called()

    def test_stop_display_loop(self):
        """Test stopping display loop."""
        # Mock timer
        self.display_window.timer = Mock()
        
        # Call stop_display_loop
        self.display_window.stop_display_loop()
        
        # Verify timer was stopped
        self.display_window.timer.stop.assert_called_once()

    @patch('app.display_window.QImage')
    @patch('app.display_window.QPixmap')
    def test_display_next_frame_valid_frames(self, mock_qpixmap, mock_qimage):
        """Test displaying next frame with valid frames."""
        # Set up test frames
        test_frames = [
            np.array([[100, 150]], dtype=np.uint8),
            np.array([[110, 160]], dtype=np.uint8),
            np.array([[120, 170]], dtype=np.uint8)
        ]
        self.display_window.set_frames(test_frames, 3000)
        
        # Mock QImage and QPixmap
        mock_qimage_instance = Mock()
        mock_qpixmap_instance = Mock()
        mock_qimage.return_value = mock_qimage_instance
        mock_qpixmap.fromImage.return_value = mock_qpixmap_instance
        
        # Mock image label
        self.display_window.image_label = Mock()
        
        # Call display_next_frame multiple times
        self.display_window.display_next_frame()  # Frame 0
        self.assertEqual(self.display_window.current_frame_index, 1)
        
        self.display_window.display_next_frame()  # Frame 1
        self.assertEqual(self.display_window.current_frame_index, 2)
        
        self.display_window.display_next_frame()  # Frame 2
        self.assertEqual(self.display_window.current_frame_index, 0)  # Should wrap around
        
        # Verify QImage was called for each frame
        self.assertEqual(mock_qimage.call_count, 3)
        
        # Verify image label was updated
        self.assertEqual(self.display_window.image_label.setPixmap.call_count, 3)

    def test_display_next_frame_no_frames(self):
        """Test displaying next frame with no frames."""
        # No frames set
        self.display_window.frames = []
        
        # Mock image label
        self.display_window.image_label = Mock()
        
        # Call display_next_frame
        self.display_window.display_next_frame()
        
        # Verify image label was not updated
        self.display_window.image_label.setPixmap.assert_not_called()
        
        # Verify frame index remains 0
        self.assertEqual(self.display_window.current_frame_index, 0)

    def test_frame_index_wrapping(self):
        """Test frame index wrapping behavior."""
        # Set up test frames
        test_frames = [
            np.array([[100]], dtype=np.uint8),
            np.array([[110]], dtype=np.uint8)
        ]
        self.display_window.set_frames(test_frames, 2000)
        
        # Mock components to avoid actual display
        with patch('app.display_window.QImage'), \
             patch('app.display_window.QPixmap'):
            
            self.display_window.image_label = Mock()
            
            # Test wrapping
            self.assertEqual(self.display_window.current_frame_index, 0)
            
            self.display_window.display_next_frame()  # 0 -> 1
            self.assertEqual(self.display_window.current_frame_index, 1)
            
            self.display_window.display_next_frame()  # 1 -> 0 (wrap)
            self.assertEqual(self.display_window.current_frame_index, 0)
            
            self.display_window.display_next_frame()  # 0 -> 1
            self.assertEqual(self.display_window.current_frame_index, 1)

    def test_timer_interval_calculation(self):
        """Test timer interval calculation for different frame counts."""
        # Test with 4 frames, 8000ms total
        test_frames = [np.array([[i]], dtype=np.uint8) for i in range(4)]
        self.display_window.set_frames(test_frames, 8000)
        
        self.display_window.timer = Mock()
        self.display_window.start_display_loop()
        
        # Expected: 8000ms / 4 frames = 2000ms per frame
        self.display_window.timer.start.assert_called_once_with(2000)

    def test_timer_interval_calculation_single_frame(self):
        """Test timer interval calculation with single frame."""
        # Test with 1 frame, 5000ms total
        test_frames = [np.array([[100]], dtype=np.uint8)]
        self.display_window.set_frames(test_frames, 5000)
        
        self.display_window.timer = Mock()
        self.display_window.start_display_loop()
        
        # Expected: 5000ms / 1 frame = 5000ms per frame
        self.display_window.timer.start.assert_called_once_with(5000)

    def test_display_window_state_management(self):
        """Test display window state management."""
        # Initial state
        self.assertEqual(self.display_window.current_frame_index, 0)
        self.assertEqual(len(self.display_window.frames), 0)
        
        # Set frames and verify state
        test_frames = [np.array([[i]], dtype=np.uint8) for i in range(3)]
        self.display_window.set_frames(test_frames, 3000)
        
        self.assertEqual(len(self.display_window.frames), 3)
        self.assertEqual(self.display_window.current_frame_index, 0)
        self.assertEqual(self.display_window.loop_duration_ms, 3000)


if __name__ == '__main__':
    unittest.main()

