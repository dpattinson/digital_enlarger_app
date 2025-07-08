# Digital Enlarger Application

A professional desktop application designed to simulate a photographic enlarger for darkroom work. This application allows users to load 16-bit grayscale TIFF images, apply tone mapping LUTs, invert images, and display them on a secondary monitor with 12-bit depth emulation.

## Features

### Core Functionality
- **Image Input:** Load 16-bit grayscale TIFF images with comprehensive validation
- **Tone Mapping:** Apply custom LUTs (256x256 16-bit grayscale TIFF)
- **Inversion:** Convert images to simulate photographic negatives
- **12-bit Emulation:** Display images as a sequence of 8-bit frames to simulate 12-bit depth
- **Display Control:** Start and stop the display loop with adjustable exposure duration
- **Secondary Display Output:** Designed for an 8K 8-bit monochrome LCD (SMP1018K13A0)

### User Experience
- **Touchscreen UI:** Large, accessible UI elements for touchscreen interaction
- **Darkroom-Friendly:** Dark color scheme suitable for darkroom environments
- **Offline Operation:** Fully functional without internet access
- **Cross-Platform:** Supports Windows, macOS, and Linux

### Developer Features
- **Comprehensive Testing:** 97% test coverage with 93+ automated tests
- **Testable Architecture:** MVP pattern with dependency injection
- **CI/CD Ready:** All tests run without deployment requirements
- **Modular Design:** Clean separation of concerns for maintainability

## Installation and Setup

### Prerequisites

- Python 3.11+
- PyQt6
- NumPy
- Tifffile
- pytest (for development)
- coverage (for test coverage analysis)

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dpattinson/digital_enlarger_app.git
    cd digital_enlarger_app
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install PyQt6 numpy tifffile pytest coverage
    ```

4.  **Prepare LUT files:**
    Place your 256x256 16-bit grayscale TIFF LUT files in the `luts/` directory.

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

## Architecture

### Design Patterns

The application follows modern software engineering principles with a focus on testability and maintainability:

- **MVP (Model-View-Presenter):** Clean separation between UI and business logic
- **Dependency Injection:** Testable components with mockable dependencies  
- **Command Pattern:** Encapsulated user actions with undo/redo support
- **Observer Pattern:** Loose coupling between components

### Project Structure

```
digital_enlarger_app/
├── .venv/                     # Python virtual environment
├── app/                       # Application source code
│   ├── __init__.py
│   ├── controller.py          # Main application controller (legacy)
│   ├── presenters.py          # MVP presenters for business logic
│   ├── commands.py            # Command pattern implementation
│   ├── view_interfaces.py     # View abstractions and mocks
│   ├── image_display_manager.py # Testable image display logic
│   ├── display_window.py      # Secondary display window
│   ├── image_processor.py     # Image loading, processing, validation
│   ├── lut_manager.py         # LUT file management
│   └── main_window.py         # Main application GUI
├── assets/                    # Sample images and resources
├── luts/                      # Tone Mapping LUT files directory
├── tests/                     # Comprehensive test suite
│   ├── test_image_processor.py      # Image processing tests
│   ├── test_lut_manager.py          # LUT management tests  
│   ├── test_controller.py           # Controller workflow tests
│   ├── test_image_display_manager.py # Display logic tests
│   ├── test_presenters.py           # MVP presenter tests
│   ├── test_commands.py             # Command pattern tests
│   ├── test_view_interfaces.py      # Mock framework tests
│   ├── test_main_window.py          # UI component tests
│   └── test_display_window.py       # Display window tests
├── htmlcov/                   # Test coverage reports
├── main.py                    # Application entry point
├── create_dummy_files.py      # Test data generation script
├── Building Standalone Application Bundles.md
└── README.md                  # This file
```

### Key Components

#### Core Business Logic
- **ImageProcessor:** Handles image loading, LUT application, and inversion with full validation
- **LUTManager:** Manages LUT file discovery and loading with dependency injection
- **ImageDisplayManager:** Pure functions for image scaling and Qt preparation (100% testable)

#### Presentation Layer  
- **MainWindowPresenter:** Coordinates image loading and processing workflows
- **PrintPresenter:** Manages print operations and display control
- **Command Classes:** Encapsulate user actions (LoadImage, ProcessImage, StartPrint, etc.)

#### View Layer
- **MainWindow:** PyQt6 GUI with dependency injection for testability
- **DisplayWindow:** Secondary monitor display with frame sequencing
- **View Interfaces:** Abstract interfaces and mocks for testing

## Development

### Running Tests

The application includes a comprehensive test suite with 97% coverage:

```bash
# Run all tests
python -m pytest tests/ -v

# Run core business logic tests (no UI dependencies)
python -m pytest tests/test_image_processor.py tests/test_lut_manager.py tests/test_controller.py tests/test_image_display_manager.py -v

# Run with coverage analysis
coverage run -m pytest tests/test_image_processor.py tests/test_lut_manager.py tests/test_controller.py tests/test_image_display_manager.py
coverage report
coverage html  # Generates htmlcov/index.html
```

### Test Categories

1. **Core Business Logic (97% coverage, 65 tests)**
   - Image processing and validation
   - LUT management and loading
   - Controller workflows
   - Display calculations

2. **Mock Framework (100% coverage, 28 tests)**
   - File dialog mocking
   - View interface testing
   - Presenter testing infrastructure

3. **UI Integration Tests**
   - PyQt6 component testing
   - User workflow validation
   - Error handling verification

### CI/CD Ready

All core business logic tests run without deployment requirements:

```yaml
# Example GitHub Actions workflow
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pytest numpy tifffile coverage
      - name: Run headless tests
        run: |
          coverage run -m pytest tests/test_image_processor.py tests/test_lut_manager.py tests/test_controller.py tests/test_image_display_manager.py tests/test_view_interfaces.py::TestMockFileDialog tests/test_view_interfaces.py::TestMockMessageDisplay tests/test_view_interfaces.py::TestMockMainView tests/test_view_interfaces.py::TestMainViewAdapter
          coverage report --fail-under=95
```

### Code Quality

- **Dependency Injection:** All external dependencies are injectable for testing
- **Pure Functions:** Image processing logic separated from UI concerns
- **Error Handling:** Comprehensive validation with descriptive error messages
- **Type Safety:** Clear interfaces and contracts between components
- **Documentation:** Comprehensive docstrings and inline comments

## Technical Notes

### Image Processing
- **16-bit Support:** Full 16-bit grayscale TIFF processing pipeline
- **LUT Validation:** Ensures LUT files are exactly 256x256 pixels and 16-bit
- **Memory Efficient:** Optimized for large image processing
- **Error Recovery:** Graceful handling of corrupted or invalid files

### Display Technology
- **12-bit Emulation:** Frame sequencing method to simulate 12-bit depth on 8-bit displays
- **Monitor Selection:** Automatic secondary monitor detection and configuration
- **Performance Optimized:** Efficient frame generation and display loops

### Testing Philosophy
- **Zero Deployment Testing:** 93+ tests run without PyQt6 or GUI dependencies
- **Mock Everything:** File dialogs, message boxes, and UI components are mockable
- **Business Logic Focus:** Core functionality tested independently of UI framework
- **Integration Testing:** End-to-end workflows validated with realistic scenarios

## Building Standalone Applications

See [Building Standalone Application Bundles.md](Building%20Standalone%20Application%20Bundles.md) for detailed instructions on creating executable bundles for Windows, macOS, and Linux using PyInstaller.

## Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Write tests:** Ensure new code has comprehensive test coverage
4. **Run the test suite:** `python -m pytest tests/ -v`
5. **Check coverage:** `coverage run -m pytest && coverage report`
6. **Commit changes:** `git commit -m 'Add amazing feature'`
7. **Push to branch:** `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines

- **Test-Driven Development:** Write tests before implementing features
- **Dependency Injection:** Use constructor injection for testable components
- **Pure Functions:** Separate business logic from UI concerns
- **Error Handling:** Provide clear, actionable error messages
- **Documentation:** Update README and docstrings for new features

## License

[Specify your license here, e.g., MIT License]

## Acknowledgments

- Built with PyQt6 for cross-platform GUI development
- Uses NumPy for efficient image processing
- Tifffile library for robust TIFF image handling
- Pytest framework for comprehensive testing
- Coverage.py for test coverage analysis

