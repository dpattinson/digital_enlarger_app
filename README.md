# Darkroom Enlarger Application

This is a desktop application designed to simulate a photographic enlarger, allowing users to load 16-bit grayscale TIFF images, apply tone mapping LUTs, invert images, and display them on a secondary monitor with 12-bit depth emulation.

## Features

- **Image Input:** Load 16-bit grayscale TIFF images.
- **Tone Mapping:** Apply custom LUTs (255x255 16-bit grayscale TIFF).
- **Inversion:** Convert images to simulate photographic negatives.
- **12-bit Emulation:** Display images as a sequence of 8-bit frames to simulate 12-bit depth.
- **Display Control:** Start and stop the display loop with adjustable exposure duration.
- **Secondary Display Output:** Designed for an 8K 8-bit monochrome LCD (SMP1018K13A0).
- **Touchscreen UI:** Large, accessible UI elements for touchscreen interaction.
- **Offline Operation:** Fully functional without internet access.
- **Cross-Platform:** Supports Windows and macOS.

## Installation and Setup

### Prerequisites

- Python 3.x
- PyQt6
- NumPy
- Imageio
- Tifffile

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/darkroom_enlarger_app.git
    cd darkroom_enlarger_app
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install PyQt6 numpy imageio tifffile
    ```

4.  **Prepare LUT files:**
    Place your 255x255 16-bit grayscale TIFF LUT files in the `luts/` directory.

## Usage

1.  **Run the application:**
    ```bash
    python3 main.py
    ```

2.  **Load Image:** Click the "Browse" button to select a 16-bit grayscale TIFF image.

3.  **Select LUT:** Choose a tone mapping LUT from the dropdown menu.

4.  **Set Exposure Duration:** (Optional) Enter the desired exposure time in seconds.

5.  **Start Print:** Click "Start Print" to begin the display loop on the secondary monitor.

6.  **Stop Print:** Click "Stop Print" to halt the display loop.

## Technical Notes

-   **Simulated 12-bit Output:** The application uses a frame sequencing method to simulate 12-bit depth on an 8-bit display. This can be further optimized for visual quality.
-   **Monitor Selection:** The application attempts to display on a secondary monitor. Ensure your 8K display is connected and configured as a secondary monitor.
-   **Darkroom-Friendly UI:** The user interface is designed with a dark color scheme suitable for darkroom environments.

## Development

### Project Structure

```
darkroom_enlarger_app/
├── .venv/                # Python virtual environment
├── app/                  # Application source code
│   ├── __init__.py
│   ├── controller.py     # Handles UI events and logic flow
│   ├── display_window.py # Secondary display window for image output
│   ├── image_processor.py# Image loading, LUT application, inversion, 12-bit emulation
│   └── lut_manager.py    # Manages LUT file loading
│   └── main_window.py    # Main application GUI
├── assets/               # Placeholder for sample images or other assets
├── luts/                 # Directory for Tone Mapping LUT files
├── tests/                # Unit tests
│   └── test_image_processor.py
├── main.py               # Main application entry point
├── create_dummy_files.py # Script to create dummy test files
└── README.md             # This file
```

### Running Tests

To run the unit tests:

```bash
cd darkroom_enlarger_app
source .venv/bin/activate
python3 -m unittest tests/test_image_processor.py
```

## License

[Specify your license here, e.g., MIT License]

