# Sample Files for Digital Enlarger Application

This directory contains sample files for testing and development of the Digital Enlarger Application. These files allow developers to quickly test the application without needing to source their own 16-bit TIFF images and LUT files.

## Directory Structure

```
samples/
├── README.md          # This file
├── images/            # Sample 16-bit grayscale TIFF images
│   ├── README.md      # Documentation for sample images
│   └── [sample files] # 16-bit grayscale TIFF files
└── luts/              # Sample LUT files
    ├── README.md      # Documentation for sample LUTs
    └── [sample files] # 256x256 16-bit TIFF LUT files
```

## Quick Start

1. **Load Sample Image:**
   - Run the application: `python3 main.py`
   - Click "Browse" and navigate to `samples/images/`
   - Select `L1000440-Edit_copy.tif` for high-quality photographic testing
   - Or `sample_image.tif` for basic testing or `test_step_wedge.tif` for calibration

2. **Apply Sample LUT:**
   - The application will automatically detect LUT files in `samples/luts/`
   - Select `ilford_mgfb_linearization_lut.tif` for realistic paper simulation
   - Or try `sample_lut_high_contrast_2x.tif` for dramatic contrast enhancement
   - Click "Start Print" to see the effect

## File Requirements

### Sample Images (`samples/images/`)
- **Format:** 16-bit grayscale TIFF (.tif or .tiff)
- **Purpose:** Test input images for the enlarger simulation
- **Typical Content:** Photographic negatives, test patterns, step wedges

### Sample LUTs (`samples/luts/`)
- **Format:** 16-bit grayscale TIFF (.tif or .tiff)
- **Dimensions:** Exactly 256x256 pixels
- **Purpose:** Tone mapping lookup tables for paper linearization
- **Typical Content:** Linearization curves, contrast adjustments, artistic effects

## Usage in Development

### Testing Workflows
```bash
# Run application with sample files
cd digital_enlarger_app
python3 main.py

# Run automated tests (uses programmatically generated test data)
python -m pytest tests/ -v

# Test specific image processing with samples
python3 -c "
from app.image_processor import ImageProcessor
processor = ImageProcessor()
image = processor.load_image('samples/images/sample_image.tif')
print(f'Loaded sample image: {image.shape}, dtype: {image.dtype}')
"
```

### Integration Testing
The sample files are particularly useful for:
- **Manual testing** of the complete application workflow
- **Visual verification** of LUT effects and image processing
- **Performance testing** with realistic file sizes
- **User acceptance testing** with representative content

## File Descriptions

See individual README files in each subdirectory for detailed descriptions of specific sample files, their characteristics, and intended use cases.

## Contributing Sample Files

When adding new sample files:

1. **Verify format requirements** using the application's validation
2. **Add descriptive documentation** to the appropriate README
3. **Keep file sizes reasonable** (< 10MB per file recommended)
4. **Use descriptive filenames** that indicate content and purpose
5. **Test files** with the application before committing

## License and Attribution

Sample files in this directory are provided for development and testing purposes. See individual file documentation for specific licensing information and attribution requirements.

