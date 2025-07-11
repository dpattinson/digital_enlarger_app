# Developer Guide

This guide provides detailed information for developers working on the Digital Enlarger Application, including architecture details, testing strategies, and development workflows.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Testing Strategy](#testing-strategy)
3. [Development Workflow](#development-workflow)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Debugging](#debugging-workflow)
6. [Performance Considerations](#performance-considerations)
7. [Troubleshooting](#troubleshooting-common-issues)

## Architecture Overview

### Design Principles

The application follows several key design principles to ensure maintainability, testability, and scalability:

1. **Separation of Concerns:** UI, business logic, and data access are clearly separated
2. **Dependency Injection:** External dependencies are injected to enable testing
3. **Single Responsibility:** Each class has a single, well-defined purpose
4. **Open/Closed Principle:** Components are open for extension, closed for modification
5. **Interface Segregation:** Small, focused interfaces rather than large monolithic ones

### Architectural Patterns

#### Model-View-Presenter (MVP)

The application uses MVP pattern to separate business logic from UI concerns:

```python
# Presenter handles business logic
class MainWindowPresenter:
    def __init__(self, view, image_model, lut_model):
        self.view = view          # UI abstraction
        self.image_model = image_model  # Business logic
        self.lut_model = lut_model      # Business logic
    
    def handle_browse_image(self):
        # Pure business logic - no UI dependencies
        file_path = self.view.show_file_dialog()
        if file_path:
            image = self.image_model.load_image(file_path)
            self.view.display_image(image)
```

#### Dependency Injection

All external dependencies are injected through constructors:

```python
class ImageProcessor:
    def __init__(self, file_checker=None, tiff_reader=None):
        self.file_checker = file_checker or os.path.exists
        self.tiff_reader = tiff_reader or tifffile.imread
    
    def load_image(self, path):
        if not self.file_checker(path):  # Mockable dependency
            raise FileNotFoundError(f"File not found: {path}")
        return self.tiff_reader(path)    # Mockable dependency
```

#### Command Pattern

User actions are encapsulated as command objects:

```python
class LoadImageCommand:
    def __init__(self, processor, file_path):
        self.processor = processor
        self.file_path = file_path
    
    def can_execute(self):
        return os.path.exists(self.file_path) and self.file_path.endswith('.tif')
    
    def execute(self):
        if not self.can_execute():
            raise ValueError("Cannot execute command")
        return self.processor.load_image(self.file_path)
    
    def undo(self):
        # Undo logic here
        pass
```

### Component Responsibilities

#### Core Business Logic

**ImageProcessor** (`app/image_processor.py`)
- Loads and validates 16-bit TIFF images
- Applies LUT transformations
- Performs image inversion
- Handles 12-bit to 8-bit frame conversion
- **Dependencies:** `file_checker`, `tiff_reader` (injectable)
- **Test Coverage:** 100%

**LUTManager** (`app/lut_manager.py`)
- Discovers LUT files in specified directories
- Validates LUT file format (256x256, 16-bit TIFF)
- Loads LUT data for processing
- **Dependencies:** `file_checker`, `dir_lister`, `tiff_reader` (injectable)
- **Test Coverage:** 94%

**ImageDisplayManager** (`app/image_display_manager.py`)
- Pure functions for image display calculations
- Aspect ratio preservation and scaling
- Letterboxing and padding calculations
- Qt image format preparation
- **Dependencies:** None (pure functions)
- **Test Coverage:** 96%

#### Presentation Layer

**MainWindowPresenter** (`app/presenters.py`)
- Coordinates image loading workflows
- Manages application state
- Handles user interactions
- **Dependencies:** View interface, business logic models
- **Test Coverage:** Comprehensive with mocks

**PrintPresenter** (`app/presenters.py`)
- Manages print operations
- Controls display window
- Handles exposure timing
- **Dependencies:** View interface, display window
- **Test Coverage:** Comprehensive with mocks

#### View Layer

**MainWindow** (`app/main_window.py`)
- PyQt6 GUI implementation
- File dialog integration
- Image preview display
- **Dependencies:** `display_manager`, `file_dialog` (injectable)
- **Test Coverage:** UI integration tests

**View Interfaces** (`app/view_interfaces.py`)
- Abstract interfaces for UI components
- Mock implementations for testing
- Adapter pattern for real UI integration
- **Dependencies:** None (interfaces and mocks)
- **Test Coverage:** 87%

## Testing Strategy

### Test Categories

#### 1. Unit Tests (Zero Dependencies)

These tests run without any external dependencies and form the core of our CI/CD pipeline:

```bash
# Core business logic - 97% coverage
python -m pytest tests/test_image_processor.py tests/test_lut_manager.py tests/test_controller.py tests/test_image_display_manager.py -v
```

**Characteristics:**
- No PyQt6 dependencies
- No file system dependencies (mocked)
- Fast execution (< 1 second)
- Perfect for CI/CD pipelines

#### 2. Integration Tests (Mock Dependencies)

These tests verify component interactions using mocks:

```bash
# Mock framework tests
python -m pytest tests/test_view_interfaces.py tests/test_presenters.py tests/test_commands.py -v
```

**Characteristics:**
- Test component interactions
- Use dependency injection and mocks
- Verify business logic workflows
- No UI framework dependencies

#### 3. UI Tests (PyQt6 Dependencies)

These tests require PyQt6 and may need special CI setup:

```bash
# UI component tests (may require display)
python -m pytest tests/test_main_window.py tests/testmode_display_window.py -v
```

**Characteristics:**
- Test actual UI components
- May require virtual display (Xvfb) in CI
- Slower execution
- Platform-specific considerations

### Testing Best Practices

#### Writing Testable Code

1. **Use Dependency Injection:**
```python
# Good - testable
class ImageProcessor:
    def __init__(self, file_reader=None):
        self.file_reader = file_reader or default_file_reader

# Bad - hard to test
class ImageProcessor:
    def load_image(self, path):
        return tifffile.imread(path)  # Hard-coded dependency
```

2. **Separate Pure Functions:**
```python
# Good - pure function, easy to test
def calculate_scaled_size(original_size, target_size):
    # Pure calculation logic
    return scaled_width, scaled_height

# Bad - mixed concerns
def display_image_scaled(self, image):
    # Calculation mixed with UI code
    scaled_size = calculate_size_and_update_ui(image)
```

3. **Use Mock Objects:**
```python
def test_image_loading():
    mock_file_reader = Mock(return_value=test_image_data)
    processor = ImageProcessor(file_reader=mock_file_reader)
    
    result = processor.load_image("/test/path.tif")
    
    assert result == test_image_data
    mock_file_reader.assert_called_once_with("/test/path.tif")
```

#### Test Organization

```
tests/
├── test_image_processor.py      # Core image processing logic
├── test_lut_manager.py          # LUT file management
├── test_controller.py           # Application controller
├── test_image_display_manager.py # Display calculations
├── test_presenters.py           # MVP presenter logic
├── test_commands.py             # Command pattern implementation
├── test_view_interfaces.py      # Mock framework
├── test_main_window.py          # UI component tests
└── test_display_window.py       # Display window tests
```

### Coverage Analysis

Generate and analyze test coverage:

```bash
# Run tests with coverage
coverage run -m pytest tests/test_image_processor.py tests/test_lut_manager.py tests/test_controller.py tests/test_image_display_manager.py

# Generate reports
coverage report --show-missing
coverage html  # Creates htmlcov/index.html
```

**Coverage Targets:**
- Core business logic: 95%+ coverage
- Presentation layer: 90%+ coverage
- View layer: 80%+ coverage (UI testing complexity)

## Development Workflow

### Setting Up Development Environment

1. **Clone and setup:**
```bash
git clone https://github.com/dpattinson/digital_enlarger_app.git
cd digital_enlarger_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Install development dependencies:**
```bash
pip install pytest coverage pylint black isort
```

3. **Verify setup:**
```bash
python -m pytest tests/test_image_processor.py -v
```

### Feature Development Process

1. **Create feature branch:**
```bash
git checkout -b feature/new-feature-name
```

2. **Write tests first (TDD):**
```python
# tests/test_new_feature.py
def test_new_feature_behavior():
    # Arrange
    processor = ImageProcessor()
    
    # Act
    result = processor.new_feature(test_input)
    
    # Assert
    assert result == expected_output
```

3. **Implement feature:**
```python
# app/image_processor.py
def new_feature(self, input_data):
    # Implementation here
    return processed_data
```

4. **Run tests:**
```bash
python -m pytest tests/test_new_feature.py -v
python -m pytest tests/ -v  # Full suite
```

5. **Check coverage:**
```bash
coverage run -m pytest tests/
coverage report --show-missing
```

6. **Code quality checks:**
```bash
pylint app/
black app/ tests/
isort app/ tests/
```

7. **Commit and push:**
```bash
git add .
git commit -m "Add new feature with comprehensive tests"
git push origin feature/new-feature-name
```

8. **Create Pull Request**

### Debugging Workflow

#### Unit Test Debugging

```bash
# Run specific test with verbose output
python -m pytest tests/test_image_processor.py::TestImageProcessor::test_specific_method -v -s

# Run with debugger
python -m pytest tests/test_image_processor.py::TestImageProcessor::test_specific_method --pdb
```

#### Application Debugging

```bash
# Run with debug logging
python main.py --debug

# Run specific component tests
python -c "
from app.image_processor import ImageProcessor
processor = ImageProcessor()
result = processor.load_image('test_image.tif')
print(f'Loaded image shape: {result.shape}')
"
```

## Code Style Guidelines

### Python Style

Follow PEP 8 with these specific guidelines:

1. **Line Length:** 88 characters (Black default)
2. **Imports:** Use isort for consistent import ordering
3. **Docstrings:** Google style docstrings
4. **Type Hints:** Use type hints for public APIs

```python
from typing import Optional, Tuple
import numpy as np

def process_image(
    image_data: np.ndarray, 
    lut_data: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, bool]:
    """Process image with optional LUT application.
    
    Args:
        image_data: 16-bit grayscale image array
        lut_data: Optional 256x256 LUT array
        
    Returns:
        Tuple of (processed_image, success_flag)
        
    Raises:
        ValueError: If image_data is not 16-bit grayscale
    """
    # Implementation here
    return processed_image, True
```

### Testing Style

1. **Test Method Names:** Descriptive and specific
```python
def test_load_image_with_valid_16bit_tiff_returns_correct_array(self):
def test_load_image_with_invalid_file_raises_file_not_found_error(self):
```

2. **Test Structure:** Arrange-Act-Assert pattern
```python
def test_apply_lut_transforms_image_correctly(self):
    # Arrange
    image_data = np.array([[1000, 2000], [3000, 4000]], dtype=np.uint16)
    lut_data = create_test_lut()
    processor = ImageProcessor()
    
    # Act
    result = processor.apply_lut(image_data, lut_data)
    
    # Assert
    assert result.dtype == np.uint16
    assert result.shape == image_data.shape
    np.testing.assert_array_equal(result, expected_result)
```

3. **Mock Usage:** Clear and specific
```python
def test_load_image_with_mocked_file_reader(self):
    mock_reader = Mock(return_value=test_image_data)
    processor = ImageProcessor(file_reader=mock_reader)
    
    result = processor.load_image("/test/path.tif")
    
    mock_reader.assert_called_once_with("/test/path.tif")
    assert result is test_image_data
```

## Performance Considerations

### Image Processing Optimization

1. **Memory Management:**
```python
# Good - in-place operations when possible
def invert_image_inplace(image_data: np.ndarray) -> np.ndarray:
    np.subtract(65535, image_data, out=image_data)
    return image_data

# Avoid - unnecessary copies
def invert_image_copy(image_data: np.ndarray) -> np.ndarray:
    return 65535 - image_data  # Creates copy
```

2. **Efficient Array Operations:**
```python
# Good - vectorized operations
def apply_lut_vectorized(image: np.ndarray, lut: np.ndarray) -> np.ndarray:
    return lut[image // 256, image % 256]

# Avoid - loops
def apply_lut_loops(image: np.ndarray, lut: np.ndarray) -> np.ndarray:
    result = np.zeros_like(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            result[i, j] = lut[image[i, j] // 256, image[i, j] % 256]
    return result
```

### UI Performance

1. **Lazy Loading:**
```python
class MainWindow:
    def __init__(self):
        self._display_manager = None
    
    @property
    def display_manager(self):
        if self._display_manager is None:
            self._display_manager = ImageDisplayManager()
        return self._display_manager
```

2. **Background Processing:**
```python
# Use QThread for long-running operations
class ImageProcessingThread(QThread):
    finished = pyqtSignal(np.ndarray)
    
    def run(self):
        # Heavy processing in background
        result = self.processor.process_image(self.image_data)
        self.finished.emit(result)
```

### Testing Performance

1. **Fast Unit Tests:**
   - Use small test images (e.g., 10x10 pixels)
   - Mock file I/O operations
   - Avoid actual file system access

2. **Parallel Test Execution:**
```bash
# Run tests in parallel
python -m pytest tests/ -n auto  # Requires pytest-xdist
```

## Troubleshooting Common Issues

### Test Failures

1. **Import Errors:**
```bash
# Ensure PYTHONPATH includes app directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/
```

2. **Mock Assertion Failures:**
```python
# Check mock call arguments carefully
mock_function.assert_called_with(expected_arg1, expected_arg2)
# vs
mock_function.assert_called_once_with(expected_arg1, expected_arg2)
```

3. **Array Comparison Issues:**
```python
# Use numpy testing utilities
np.testing.assert_array_equal(actual, expected)
np.testing.assert_array_almost_equal(actual, expected, decimal=6)
```

### UI Issues

1. **PyQt6 Import Errors:**
```bash
# Install PyQt6 properly
pip install PyQt6
# On Linux, may need additional packages
sudo apt-get install python3-pyqt6
```

2. **Display Issues in CI:**
```bash
# Use virtual display
sudo apt-get install xvfb
xvfb-run -a python -m pytest tests/test_main_window.py
```

### Performance Issues

1. **Slow Tests:**
   - Profile test execution: `python -m pytest tests/ --durations=10`
   - Use smaller test data
   - Mock expensive operations

2. **Memory Issues:**
   - Monitor memory usage during tests
   - Use `del` to explicitly free large arrays
   - Consider using memory profilers

This developer guide should be updated as the application evolves and new patterns emerge.

