# Sample Images

This directory contains sample 16-bit grayscale TIFF images for testing the Digital Enlarger Application. These images simulate photographic negatives and test patterns commonly used in darkroom work.

## File Requirements

All sample images must meet these specifications:
- **Format:** TIFF (.tif or .tiff extension)
- **Bit Depth:** 16-bit grayscale
- **Color Space:** Grayscale (single channel)
- **Compression:** Uncompressed or LZW (application supports both)

## Sample Image Categories

### Photographic Negatives
Simulated film negatives for realistic testing:
- **Portrait subjects** - Human faces with varied tonal ranges
- **Landscape scenes** - Natural scenes with sky, water, vegetation
- **Architecture** - Buildings with geometric patterns and textures
- **Still life** - Objects with varied materials and reflectance

### Test Patterns
Technical images for systematic testing:
- **Step wedges** - Graduated tone scales for linearization testing
- **Resolution charts** - Fine detail patterns for sharpness evaluation
- **Gray cards** - Uniform tone patches for calibration
- **Noise patterns** - Various noise characteristics for processing tests

### Artistic Content
Creative images for aesthetic evaluation:
- **High contrast** - Images with strong blacks and whites
- **Low contrast** - Subtle tonal variations
- **Fine detail** - Images with intricate textures and patterns
- **Large areas** - Images with significant uniform regions

## Usage Examples

### Loading in Application
```python
from app.image_processor import ImageProcessor

processor = ImageProcessor()

# Load a sample image
image = processor.load_image('samples/images/portrait_negative.tif')
print(f'Image shape: {image.shape}')
print(f'Data type: {image.dtype}')
print(f'Value range: {image.min()} - {image.max()}')
```

### Testing Different Scenarios
```python
# Test with high contrast image
high_contrast = processor.load_image('samples/images/high_contrast_scene.tif')

# Test with fine detail image  
fine_detail = processor.load_image('samples/images/resolution_chart.tif')

# Test with step wedge
step_wedge = processor.load_image('samples/images/step_wedge_21.tif')
```

## File Naming Convention

Sample images follow this naming pattern:
```
[category]_[description]_[characteristics].tif

Examples:
- portrait_woman_high_contrast.tif
- landscape_mountains_low_contrast.tif
- test_step_wedge_21_steps.tif
- architecture_building_fine_detail.tif
```

## Technical Specifications

### Recommended Image Sizes
- **Small:** 512x512 pixels (for quick testing)
- **Medium:** 1024x1024 pixels (typical development)
- **Large:** 2048x2048 pixels (performance testing)
- **Full Size:** 4096x4096 pixels (production simulation)

### Tonal Characteristics
- **Full Range:** Images using the complete 0-65535 16-bit range
- **Restricted Range:** Images using typical negative density ranges
- **Highlight Detail:** Images with important detail in bright areas
- **Shadow Detail:** Images with important detail in dark areas

## Quality Guidelines

Sample images should:
- ✅ **Be properly exposed** with good tonal distribution
- ✅ **Have sharp focus** (unless testing blur effects)
- ✅ **Be free of artifacts** (compression, noise, etc.)
- ✅ **Represent realistic content** for darkroom work
- ✅ **Include varied subjects** for comprehensive testing

## File Descriptions

*[This section will be updated as sample files are added]*

### Currently Available Files

#### **sample_image.tif**
- **Dimensions:** 256x100 pixels
- **Type:** Test image for basic functionality testing
- **Characteristics:** 16-bit grayscale TIFF
- **Purpose:** General testing of image loading and processing workflows
- **Content:** Synthetic test pattern suitable for development and debugging

#### **test_step_wedge.tif**
- **Dimensions:** 1050x100 pixels  
- **Type:** Step wedge calibration image
- **Characteristics:** 16-bit grayscale TIFF with graduated tone steps
- **Purpose:** Testing linearization and tone mapping accuracy
- **Content:** Precise step wedge pattern for calibration and validation
- **Usage:** Ideal for testing LUT application and verifying tone reproduction

#### **test_step_wedge_linearized.tif**
- **Dimensions:** 1050x100 pixels
- **Type:** Pre-linearized step wedge
- **Characteristics:** 16-bit grayscale TIFF, linearized version of test_step_wedge.tif
- **Purpose:** Reference for comparing linearization results
- **Content:** Step wedge processed with linearization LUT
- **Usage:** Validation of linearization accuracy and before/after comparison

## Adding New Sample Images

When contributing new sample images:

1. **Verify 16-bit TIFF format** using the application's validation
2. **Test loading** in the application to ensure compatibility
3. **Add description** to this README with technical details
4. **Use descriptive filename** following the naming convention
5. **Keep reasonable file size** (< 10MB recommended)

## License Information

Sample images are provided for development and testing purposes. Specific licensing information for each file will be documented here as files are added.

