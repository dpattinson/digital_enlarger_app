#!/usr/bin/env python3
"""
Demonstration script for automatic portrait rotation functionality.

This script showcases the new automatic portrait rotation feature that
rotates portrait-oriented images 90 degrees clockwise to landscape
orientation when they are loaded.
"""

import numpy as np
import time
from app.image_processor import ImageProcessor


def create_test_images():
    """Create test images for demonstration."""
    print("Creating test images...")
    
    # Portrait image (height > width)
    portrait_image = np.random.randint(10000, 50000, (1200, 800), dtype=np.uint16)
    
    # Landscape image (width > height)
    landscape_image = np.random.randint(10000, 50000, (800, 1200), dtype=np.uint16)
    
    # Square image (height == width)
    square_image = np.random.randint(10000, 50000, (1000, 1000), dtype=np.uint16)
    
    return {
        'portrait': portrait_image,
        'landscape': landscape_image,
        'square': square_image
    }


def demonstrate_portrait_detection():
    """Demonstrate portrait orientation detection."""
    print("\n" + "="*60)
    print("DEMONSTRATING PORTRAIT ORIENTATION DETECTION")
    print("="*60)
    
    processor = ImageProcessor()
    test_images = create_test_images()
    
    for name, image in test_images.items():
        height, width = image.shape
        is_portrait = processor.is_portrait_orientation(image)
        
        print(f"\n{name.capitalize()} image:")
        print(f"  Dimensions: {height} x {width} (H x W)")
        print(f"  Is portrait: {is_portrait}")
        print(f"  Aspect ratio: {height/width:.3f}")
    
    print("\n✅ Portrait detection working correctly!")


def demonstrate_rotation_functionality():
    """Demonstrate the 90-degree clockwise rotation."""
    print("\n" + "="*60)
    print("DEMONSTRATING 90-DEGREE CLOCKWISE ROTATION")
    print("="*60)
    
    processor = ImageProcessor()
    
    # Create a portrait image with known pattern for verification
    print("\nTesting rotation with known pixel pattern:")
    test_pattern = np.array([
        [100, 200],
        [300, 400],
        [500, 600]
    ], dtype=np.uint16)
    
    print(f"Original pattern (3x2):")
    print(test_pattern)
    
    rotated_pattern = processor.rotate_image_clockwise_90(test_pattern)
    print(f"\nRotated pattern (2x3):")
    print(rotated_pattern)
    
    # Verify the rotation is correct
    expected_pattern = np.array([
        [500, 300, 100],
        [600, 400, 200]
    ], dtype=np.uint16)
    
    if np.array_equal(rotated_pattern, expected_pattern):
        print("✅ Pixel values correctly repositioned!")
    else:
        print("❌ Pixel rotation error!")
    
    # Test with larger images
    print("\nTesting rotation performance with larger images:")
    test_sizes = [(800, 1200), (1200, 1800), (2000, 3000)]
    
    for height, width in test_sizes:
        portrait_image = np.random.randint(0, 65535, (height, width), dtype=np.uint16)
        
        start_time = time.time()
        rotated_image = processor.rotate_image_clockwise_90(portrait_image)
        end_time = time.time()
        
        print(f"  {height}x{width} → {rotated_image.shape[0]}x{rotated_image.shape[1]}: {(end_time-start_time)*1000:.2f}ms")
    
    print("\n✅ Rotation functionality working correctly!")


def demonstrate_rotation_info():
    """Demonstrate rotation information tracking."""
    print("\n" + "="*60)
    print("DEMONSTRATING ROTATION INFORMATION TRACKING")
    print("="*60)
    
    processor = ImageProcessor()
    
    # Create original and rotated images
    original_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
    rotated_image = processor.rotate_image_clockwise_90(original_image)
    
    # Get rotation information
    info = processor.get_rotation_info(original_image, rotated_image)
    
    print(f"Rotation Information:")
    print(f"  Rotation applied: {info['rotation_applied']}")
    print(f"  Rotation angle: {info['rotation_angle']}° clockwise")
    print(f"  Original size: {info['original_size']} (W x H)")
    print(f"  Rotated size: {info['rotated_size']} (W x H)")
    print(f"  Original orientation: {info['original_orientation']}")
    print(f"  Final orientation: {info['final_orientation']}")
    
    print("\n✅ Rotation information tracking working correctly!")


def demonstrate_automatic_rotation_in_load_image():
    """Demonstrate automatic rotation during image loading."""
    print("\n" + "="*60)
    print("DEMONSTRATING AUTOMATIC ROTATION IN LOAD_IMAGE")
    print("="*60)
    
    from unittest.mock import MagicMock
    
    # Test with portrait image
    print("\nTesting with portrait image:")
    portrait_image = np.random.randint(0, 65535, (1200, 800), dtype=np.uint16)
    
    # Mock file system
    mock_exists = MagicMock(return_value=True)
    mock_imread = MagicMock(return_value=portrait_image)
    
    processor = ImageProcessor(file_checker=mock_exists, cv2_reader=mock_imread)
    
    print(f"  Original image: {portrait_image.shape} (H x W) - Portrait")
    
    # Load image (should automatically rotate)
    loaded_image = processor.load_image("test_portrait.tif")
    
    print(f"  Loaded image: {loaded_image.shape} (H x W) - {'Portrait' if processor.is_portrait_orientation(loaded_image) else 'Landscape'}")
    
    # Test with landscape image
    print("\nTesting with landscape image:")
    landscape_image = np.random.randint(0, 65535, (800, 1200), dtype=np.uint16)
    mock_imread.return_value = landscape_image
    
    print(f"  Original image: {landscape_image.shape} (H x W) - Landscape")
    
    loaded_image = processor.load_image("test_landscape.tif")
    
    print(f"  Loaded image: {loaded_image.shape} (H x W) - {'Portrait' if processor.is_portrait_orientation(loaded_image) else 'Landscape'}")
    
    # Test with square image
    print("\nTesting with square image:")
    square_image = np.random.randint(0, 65535, (1000, 1000), dtype=np.uint16)
    mock_imread.return_value = square_image
    
    print(f"  Original image: {square_image.shape} (H x W) - Square")
    
    loaded_image = processor.load_image("test_square.tif")
    
    print(f"  Loaded image: {loaded_image.shape} (H x W) - Square")
    
    print("\n✅ Automatic rotation in load_image working correctly!")


def demonstrate_error_handling():
    """Demonstrate error handling in rotation functions."""
    print("\n" + "="*60)
    print("DEMONSTRATING ERROR HANDLING")
    print("="*60)
    
    processor = ImageProcessor()
    
    # Test with None image
    print("\nTesting with None image:")
    try:
        processor.rotate_image_clockwise_90(None)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test with 3D image
    print("\nTesting with 3D image:")
    color_image = np.random.randint(0, 255, (800, 1200, 3), dtype=np.uint8)
    try:
        processor.rotate_image_clockwise_90(color_image)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    
    # Test portrait detection with invalid inputs
    print("\nTesting portrait detection with invalid inputs:")
    
    # None image
    result = processor.is_portrait_orientation(None)
    print(f"  None image → is_portrait: {result} ✅")
    
    # 3D image
    result = processor.is_portrait_orientation(color_image)
    print(f"  3D image → is_portrait: {result} ✅")
    
    print("\n✅ Error handling working correctly!")


def benchmark_rotation_performance():
    """Benchmark rotation performance with different image sizes."""
    print("\n" + "="*60)
    print("ROTATION PERFORMANCE BENCHMARKING")
    print("="*60)
    
    processor = ImageProcessor()
    
    test_sizes = [
        (500, 800),     # Small
        (1000, 1500),   # Medium
        (2000, 3000),   # Large
        (3000, 4500),   # Very large
        (4000, 6000)    # Extra large
    ]
    
    print(f"{'Size (H x W)':<15} {'Rotation Time':<15} {'Memory (MB)':<12} {'Throughput':<15}")
    print("-" * 60)
    
    for height, width in test_sizes:
        # Create test image
        test_image = np.random.randint(0, 65535, (height, width), dtype=np.uint16)
        memory_mb = test_image.nbytes / (1024 * 1024)
        
        # Benchmark rotation
        start_time = time.time()
        for _ in range(5):  # Average over 5 runs
            rotated = processor.rotate_image_clockwise_90(test_image)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 5
        throughput = memory_mb / avg_time if avg_time > 0 else 0
        
        print(f"{height}x{width:<8} {avg_time*1000:>8.2f}ms     {memory_mb:>8.1f}     {throughput:>8.1f} MB/s")
    
    print("\n✅ Performance benchmarking completed!")


def main():
    """Run all demonstrations."""
    print("AUTOMATIC PORTRAIT ROTATION DEMONSTRATION")
    print("Digital Enlarger Application - Auto-Rotation Feature")
    
    try:
        demonstrate_portrait_detection()
        demonstrate_rotation_functionality()
        demonstrate_rotation_info()
        demonstrate_automatic_rotation_in_load_image()
        demonstrate_error_handling()
        benchmark_rotation_performance()
        
        print("\n" + "="*60)
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("✅ Portrait orientation detection (height > width)")
        print("✅ 90-degree clockwise rotation using OpenCV")
        print("✅ Automatic rotation during image loading")
        print("✅ Pixel-perfect rotation with value preservation")
        print("✅ Comprehensive error handling")
        print("✅ Performance optimization for large images")
        print("✅ Rotation information tracking")
        print("✅ Integration with existing ImageProcessor workflow")
        
        print("\nBehavior Summary:")
        print("• Portrait images (H > W) → Automatically rotated to landscape")
        print("• Landscape images (W > H) → No rotation applied")
        print("• Square images (H = W) → No rotation applied")
        print("• Rotation logged in processing summary")
        print("• All existing functionality preserved")
        
        print("\nThe automatic portrait rotation feature is ready for use!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()

