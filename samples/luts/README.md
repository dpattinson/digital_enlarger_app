# Sample LUT Files

This directory contains sample Look-Up Table (LUT) files for testing tone mapping in the Digital Enlarger Application. These LUTs simulate various paper characteristics and artistic effects commonly used in darkroom printing.

## File Requirements

All sample LUT files must meet these specifications:
- **Format:** TIFF (.tif or .tiff extension)
- **Bit Depth:** 16-bit grayscale
- **Dimensions:** Exactly 256x256 pixels
- **Color Space:** Grayscale (single channel)
- **Compression:** Uncompressed or LZW

## LUT Categories

### Paper Linearization
LUTs that compensate for photographic paper characteristics:
- **Ilford MGFB** - Multigrade fiber-based paper linearization
- **Kodak Polymax** - Traditional RC paper characteristics
- **Agfa MCP** - Classic paper response curves
- **Generic Grade 2** - Standard contrast paper simulation

### Contrast Adjustments
LUTs for contrast control:
- **High Contrast** - Increased contrast for flat negatives
- **Low Contrast** - Reduced contrast for contrasty negatives
- **Variable Contrast** - Simulated multigrade paper effects
- **Split Contrast** - Advanced contrast control techniques

### Artistic Effects
Creative LUTs for artistic interpretation:
- **Vintage Look** - Aged paper characteristics
- **High Key** - Bright, airy interpretation
- **Low Key** - Dark, moody interpretation
- **Solarization** - Partial tone reversal effects

### Technical Test LUTs
LUTs for system testing and calibration:
- **Identity** - No change (straight-through mapping)
- **Inversion** - Complete tone reversal
- **Gamma Curves** - Various gamma correction values
- **Step Functions** - Discrete tone mapping for testing

## LUT Structure

### 2D Lookup Table Format
LUTs are stored as 256x256 pixel images where:
- **X-axis (columns):** Input tone value (0-255, scaled to 16-bit)
- **Y-axis (rows):** Fine adjustment or paper characteristic
- **Pixel value:** Output tone value (16-bit)

### Mapping Function
```python
# LUT application example
def apply_lut(image, lut):
    """Apply 2D LUT to image."""
    # Scale 16-bit input to 8-bit indices
    x_index = image // 256  # Coarse value (0-255)
    y_index = image % 256   # Fine value (0-255)
    
    # Look up output value
    output = lut[y_index, x_index]
    return output
```

## Usage Examples

### Loading and Applying LUTs
```python
from app.lut_manager import LUTManager
from app.image_processor import ImageProcessor

# Initialize managers
lut_manager = LUTManager('samples/luts/')
processor = ImageProcessor()

# Load sample LUT
lut = lut_manager.load_lut('ilford_mgfb_grade2.tif')
print(f'LUT shape: {lut.shape}')
print(f'LUT range: {lut.min()} - {lut.max()}')

# Apply to sample image
image = processor.load_image('samples/images/portrait_negative.tif')
processed = processor.apply_lut(image, lut)
```

### Testing Different LUT Types
```python
# Test linearization LUT
linear_lut = lut_manager.load_lut('ilford_mgfb_linearization.tif')
linearized = processor.apply_lut(image, linear_lut)

# Test contrast adjustment
high_contrast_lut = lut_manager.load_lut('high_contrast_grade4.tif')
contrasty = processor.apply_lut(image, high_contrast_lut)

# Test artistic effect
vintage_lut = lut_manager.load_lut('vintage_paper_effect.tif')
vintage = processor.apply_lut(image, vintage_lut)
```

## File Naming Convention

Sample LUTs follow this naming pattern:
```
[category]_[description]_[characteristics].tif

Examples:
- ilford_mgfb_grade2_linearization.tif
- kodak_polymax_grade3_standard.tif
- artistic_vintage_warm_tone.tif
- test_identity_no_change.tif
- contrast_high_grade4_equivalent.tif
```

## LUT Creation Guidelines

### Mathematical Properties
- **Monotonic:** Output should generally increase with input
- **Smooth:** Avoid abrupt transitions unless intentional
- **Full Range:** Utilize the complete 16-bit output range when appropriate
- **Realistic:** Based on actual paper or artistic characteristics

### Technical Validation
```python
# Validate LUT properties
def validate_lut(lut):
    assert lut.shape == (256, 256), "LUT must be 256x256"
    assert lut.dtype == np.uint16, "LUT must be 16-bit"
    assert 0 <= lut.min() <= lut.max() <= 65535, "Values must be in 16-bit range"
    
    # Check for reasonable monotonicity (optional)
    diagonal = np.diag(lut)
    assert np.all(np.diff(diagonal) >= 0), "Diagonal should be monotonic"
```

## File Descriptions

*[This section will be updated as sample files are added]*

### Currently Available Files

#### **ilford_mgfb_linearization_lut.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Paper linearization LUT
- **Paper:** Ilford MGFB Classic (Multigrade Fiber-Based)
- **Purpose:** Compensates for paper's non-linear response characteristics
- **Characteristics:** Professional linearization curve for darkroom printing
- **Usage:** Apply to images before printing on Ilford MGFB Classic paper
- **Technical:** Based on measured paper response curves

#### **sample_lut_identity_no_change.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Identity/pass-through LUT
- **Purpose:** No tone mapping (straight-through processing)
- **Characteristics:** Linear diagonal mapping (output = input)
- **Usage:** Testing baseline performance, debugging LUT application
- **Mathematical:** f(x) = x for all input values

#### **sample_lut_inversion_negative.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Tone inversion LUT
- **Purpose:** Complete tone reversal (negative effect)
- **Characteristics:** Inverts all tone values
- **Usage:** Creating negative effects, testing tone reversal
- **Mathematical:** f(x) = 65535 - x for 16-bit values

#### **sample_lut_high_contrast_2x.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Contrast enhancement LUT
- **Purpose:** Increases image contrast by factor of 2
- **Characteristics:** Steeper tone curve for enhanced contrast
- **Usage:** Correcting flat/low-contrast negatives
- **Effect:** Expands tonal range, increases separation

#### **sample_lut_low_contrast_0.5x.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Contrast reduction LUT
- **Purpose:** Reduces image contrast by factor of 0.5
- **Characteristics:** Gentler tone curve for reduced contrast
- **Usage:** Taming overly contrasty negatives
- **Effect:** Compresses tonal range, softer gradations

#### **sample_lut_gamma_correction_γ=2.2.tif**
- **Dimensions:** 256x256 pixels
- **Type:** Gamma correction LUT
- **Purpose:** Standard gamma correction (γ = 2.2)
- **Characteristics:** Power law tone mapping
- **Usage:** Display calibration, standard gamma correction
- **Mathematical:** f(x) = x^(1/2.2) normalized to 16-bit range

## Performance Considerations

### LUT Application Speed
- **Memory Access:** 2D LUTs require careful memory layout for performance
- **Vectorization:** NumPy operations are optimized for large arrays
- **Caching:** Frequently used LUTs can be cached in memory

### File Size Optimization
- **Compression:** LZW compression reduces file size without quality loss
- **Precision:** 16-bit precision is required for professional results
- **Storage:** Each LUT file is approximately 128KB uncompressed

## Adding New Sample LUTs

When contributing new sample LUTs:

1. **Verify dimensions** (exactly 256x256 pixels)
2. **Confirm 16-bit depth** using image analysis tools
3. **Test application** in the Digital Enlarger Application
4. **Document characteristics** in this README
5. **Use descriptive filename** following naming convention
6. **Validate mathematical properties** using provided validation code

## Technical References

### Paper Characteristics
- **Ilford MGFB:** Multigrade fiber-based paper response curves
- **Kodak Polymax:** Traditional RC paper gamma characteristics
- **Zone System:** Ansel Adams zone system tone mapping

### Gamma Correction
- **Standard Gamma:** 2.2 for typical display systems
- **Paper Gamma:** Variable based on paper type and developer
- **Linear Response:** Identity mapping for technical applications

## License Information

Sample LUT files are provided for development and testing purposes. Specific licensing and attribution information for each file will be documented here as files are added.

