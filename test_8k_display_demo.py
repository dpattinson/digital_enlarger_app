#!/usr/bin/env python3
"""
Demonstration script for 8K Display Optimization features.

This script showcases the new image squashing and padding algorithms
optimized for 7680x4320 secondary displays, similar to LCD-Alt-Print-Tools
but adapted for the Digital Enlarger Application.
"""

import numpy as np
import time
from app.image_display_manager import ImageDisplayManager


def create_test_images():
    """Create various test images for demonstration."""
    print("Creating test images...")
    
    # Small image (will need padding)
    small_image = np.random.randint(10000, 50000, (500, 800), dtype=np.uint16)
    
    # Medium image (good fit)
    medium_image = np.random.randint(10000, 50000, (2000, 3000), dtype=np.uint16)
    
    # Large image (will need scaling)
    large_image = np.random.randint(10000, 50000, (6000, 10000), dtype=np.uint16)
    
    # Wide image (good for squashing demo)
    wide_image = np.random.randint(10000, 50000, (1000, 6000), dtype=np.uint16)
    
    return {
        'small': small_image,
        'medium': medium_image, 
        'large': large_image,
        'wide': wide_image
    }


def demonstrate_image_squashing():
    """Demonstrate image squashing functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING IMAGE SQUASHING")
    print("="*60)
    
    manager = ImageDisplayManager()
    
    # Create a wide test image
    test_image = np.random.randint(10000, 50000, (1000, 6000), dtype=np.uint16)
    print(f"Original image size: {test_image.shape} (H x W)")
    
    # Test different compression ratios
    for ratio in [2, 3, 4]:
        start_time = time.time()
        squashed = manager.squash_image_for_display(test_image, ratio)
        end_time = time.time()
        
        print(f"Compression ratio {ratio}: {squashed.shape} (H x W) - {(end_time-start_time)*1000:.2f}ms")
        
        # Verify compression
        expected_width = test_image.shape[1] // ratio
        assert squashed.shape[1] == expected_width, f"Width compression failed for ratio {ratio}"
        assert squashed.shape[0] == test_image.shape[0], f"Height should remain unchanged"
    
    print("✅ Image squashing working correctly!")


def demonstrate_8k_padding():
    """Demonstrate 8K display padding functionality."""
    print("\n" + "="*60)
    print("DEMONSTRATING 8K DISPLAY PADDING")
    print("="*60)
    
    manager = ImageDisplayManager()
    test_images = create_test_images()
    
    for name, image in test_images.items():
        print(f"\nProcessing {name} image: {image.shape} (H x W)")
        
        start_time = time.time()
        padded = manager.pad_image_for_8k_display(image, center_image=True)
        end_time = time.time()
        
        print(f"  Result: {padded.shape} (H x W) - {(end_time-start_time)*1000:.2f}ms")
        
        # Verify 8K dimensions
        assert padded.shape == (4320, 7680), f"8K padding failed for {name} image"
        
        # Check for white borders
        border_pixels = np.sum(padded == 65535)
        total_pixels = padded.size
        border_percentage = (border_pixels / total_pixels) * 100
        print(f"  White border coverage: {border_percentage:.1f}%")
    
    print("✅ 8K display padding working correctly!")


def demonstrate_complete_pipeline():
    """Demonstrate the complete 8K preparation pipeline."""
    print("\n" + "="*60)
    print("DEMONSTRATING COMPLETE 8K PREPARATION PIPELINE")
    print("="*60)
    
    manager = ImageDisplayManager()
    
    # Test with a wide image that benefits from squashing
    test_image = np.random.randint(10000, 50000, (2000, 9000), dtype=np.uint16)
    print(f"Original image: {test_image.shape} (H x W)")
    
    # Test with squashing
    print("\nWith squashing (compression ratio 3):")
    start_time = time.time()
    result_with_squashing = manager.prepare_image_for_8k_display(
        test_image, 
        apply_squashing=True, 
        compression_ratio=3
    )
    end_time = time.time()
    
    print(f"  Result: {result_with_squashing.shape} (H x W) - {(end_time-start_time)*1000:.2f}ms")
    assert result_with_squashing.shape == (4320, 7680), "8K preparation with squashing failed"
    
    # Test without squashing
    print("\nWithout squashing:")
    start_time = time.time()
    result_without_squashing = manager.prepare_image_for_8k_display(
        test_image, 
        apply_squashing=False
    )
    end_time = time.time()
    
    print(f"  Result: {result_without_squashing.shape} (H x W) - {(end_time-start_time)*1000:.2f}ms")
    assert result_without_squashing.shape == (4320, 7680), "8K preparation without squashing failed"
    
    print("✅ Complete 8K preparation pipeline working correctly!")


def demonstrate_display_info_calculation():
    """Demonstrate 8K display information calculation."""
    print("\n" + "="*60)
    print("DEMONSTRATING 8K DISPLAY INFO CALCULATION")
    print("="*60)
    
    manager = ImageDisplayManager()
    test_images = create_test_images()
    
    for name, image in test_images.items():
        print(f"\nAnalyzing {name} image: {image.shape} (H x W)")
        
        # Calculate info with squashing
        info = manager.calculate_8k_display_info(
            image, 
            apply_squashing=True, 
            compression_ratio=3
        )
        
        print(f"  Original size: {info['original_size']}")
        print(f"  Squashed size: {info['squashed_size']}")
        print(f"  Final size: {info['final_size']}")
        print(f"  Padding: x={info['padding_info']['x']}, y={info['padding_info']['y']}")
        print(f"  Memory usage: {info['memory_usage_mb']:.1f} MB")
        print(f"  Compression applied: {info['compression_applied']}")
        print(f"  Scaling applied: {info['scaling_applied']}")
        if info['scaling_applied']:
            print(f"  Scaling factor: {info['scaling_factor']:.3f}")
    
    print("✅ 8K display info calculation working correctly!")


def demonstrate_display_readiness_validation():
    """Demonstrate display readiness validation."""
    print("\n" + "="*60)
    print("DEMONSTRATING DISPLAY READINESS VALIDATION")
    print("="*60)
    
    manager = ImageDisplayManager()
    
    # Test with different image types
    test_cases = [
        ("Very large image", np.random.randint(10000, 50000, (10000, 15000), dtype=np.uint16)),
        ("Very small image", np.random.randint(10000, 50000, (100, 200), dtype=np.uint16)),
        ("Good size image", np.random.randint(10000, 50000, (2000, 3000), dtype=np.uint16)),
        ("Wide aspect ratio", np.random.randint(10000, 50000, (1000, 8000), dtype=np.uint16))
    ]
    
    for name, image in test_cases:
        print(f"\nValidating {name}: {image.shape} (H x W)")
        
        validation = manager.validate_8k_display_readiness(image)
        
        print(f"  Ready for display: {validation['is_ready']}")
        print(f"  Warnings: {len(validation['warnings'])}")
        for warning in validation['warnings']:
            print(f"    - {warning}")
        print(f"  Recommendations: {len(validation['recommendations'])}")
        for rec in validation['recommendations']:
            print(f"    - {rec}")
        
        if 'info' in validation:
            info = validation['info']
            print(f"  Aspect ratio: {info['aspect_ratio']:.3f}")
            print(f"  Memory usage: {info['memory_mb']:.1f} MB")
            print(f"  Display compatible: {info['display_compatibility']}")
    
    print("✅ Display readiness validation working correctly!")


def benchmark_performance():
    """Benchmark the performance of 8K display operations."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARKING")
    print("="*60)
    
    manager = ImageDisplayManager()
    
    # Create test images of different sizes
    test_sizes = [
        (1000, 1500),   # Small
        (2000, 3000),   # Medium  
        (4000, 6000),   # Large
        (6000, 9000)    # Very large
    ]
    
    operations = ['squashing', 'padding', 'complete_pipeline']
    
    for height, width in test_sizes:
        print(f"\nBenchmarking with {height}x{width} image:")
        test_image = np.random.randint(10000, 50000, (height, width), dtype=np.uint16)
        
        # Benchmark squashing
        start_time = time.time()
        for _ in range(10):
            manager.squash_image_for_display(test_image, 3)
        squash_time = (time.time() - start_time) / 10
        
        # Benchmark padding
        start_time = time.time()
        for _ in range(10):
            manager.pad_image_for_8k_display(test_image)
        pad_time = (time.time() - start_time) / 10
        
        # Benchmark complete pipeline
        start_time = time.time()
        for _ in range(10):
            manager.prepare_image_for_8k_display(test_image, apply_squashing=True)
        pipeline_time = (time.time() - start_time) / 10
        
        print(f"  Squashing: {squash_time*1000:.2f}ms")
        print(f"  Padding: {pad_time*1000:.2f}ms") 
        print(f"  Complete pipeline: {pipeline_time*1000:.2f}ms")
    
    print("✅ Performance benchmarking completed!")


def main():
    """Run all demonstrations."""
    print("8K DISPLAY OPTIMIZATION DEMONSTRATION")
    print("Adapted from LCD-Alt-Print-Tools for 7680x4320 displays")
    print("Digital Enlarger Application")
    
    try:
        demonstrate_image_squashing()
        demonstrate_8k_padding()
        demonstrate_complete_pipeline()
        demonstrate_display_info_calculation()
        demonstrate_display_readiness_validation()
        benchmark_performance()
        
        print("\n" + "="*60)
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nKey Features Demonstrated:")
        print("✅ Image squashing with configurable compression ratios")
        print("✅ 8K display padding with white borders only")
        print("✅ Automatic scaling for oversized images")
        print("✅ Complete preparation pipeline")
        print("✅ Display information calculation")
        print("✅ Display readiness validation")
        print("✅ Performance optimization for 8K resolution")
        
        print("\nThe 8K display optimization algorithms are ready for integration!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()

