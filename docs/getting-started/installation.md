# Installation

## Requirements

herrkunft requires Python 3.9 or higher. The library is designed to work with modern Python best practices and leverages the latest features of the Python ecosystem.

### Python Version

- **Python 3.9+** (Required)
- **Python 3.10+** (Recommended for best performance)
- **Python 3.11+** (Recommended for improved type checking)
- **Python 3.12** (Fully supported)

## Installing from PyPI

The simplest way to install herrkunft is via pip:

```bash
pip install herrkunft
```

This will install the core library with all required dependencies:
- `pydantic>=2.0.0` - Type-safe data models and settings
- `ruamel.yaml>=0.17.32` - YAML parsing with position tracking
- `loguru>=0.7.0` - Logging and debugging
- `typing-extensions>=4.0.0` - Type hints for Python <3.11

## Development Installation

If you want to contribute to herrkunft or run the test suite, install with development dependencies:

```bash
pip install herrkunft[dev]
```

This includes:
- `pytest>=7.4.0` - Testing framework
- `pytest-cov>=4.1.0` - Coverage reporting
- `pytest-xdist>=3.3.0` - Parallel test execution
- `mypy>=1.5.0` - Static type checking
- `black>=23.7.0` - Code formatting
- `ruff>=0.0.285` - Fast Python linter
- `pre-commit>=3.3.0` - Git hooks for code quality

## Documentation Dependencies

To build the documentation locally:

```bash
pip install herrkunft[docs]
```

This includes Sphinx and related documentation tools.

## Installing All Optional Dependencies

To install everything (core + dev + docs):

```bash
pip install herrkunft[all]
```

## Installing from Source

To install the latest development version from GitHub:

```bash
git clone https://github.com/pgierz/herrkunft.git
cd herrkunft
pip install -e .
```

For development with all dependencies:

```bash
git clone https://github.com/pgierz/herrkunft.git
cd herrkunft
pip install -e .[dev]
```

## Verifying Installation

After installation, verify that herrkunft is correctly installed:

```python
import provenance

# Check version
print(provenance.__version__)

# Load a simple YAML file
from provenance import load_yaml
config = load_yaml("config.yaml", category="test")
```

## Virtual Environments

We strongly recommend using a virtual environment to avoid dependency conflicts:

### Using venv

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install herrkunft
```

### Using conda

```bash
conda create -n herrkunft python=3.11
conda activate herrkunft
pip install herrkunft
```

### Using pipenv

```bash
pipenv install herrkunft
pipenv shell
```

### Using poetry

```bash
poetry add herrkunft
poetry shell
```

## Troubleshooting

### Import Errors

If you encounter import errors after installation:

1. Ensure you're using the correct Python version:
   ```bash
   python --version
   ```

2. Check that herrkunft is installed in the active environment:
   ```bash
   pip list | grep herrkunft
   ```

3. Try reinstalling:
   ```bash
   pip uninstall herrkunft
   pip install herrkunft
   ```

### ruamel.yaml Issues

If you have issues with `ruamel.yaml`:

```bash
pip install --upgrade ruamel.yaml
```

### Pydantic V2 Compatibility

herrkunft requires Pydantic 2.0+. If you have an older version:

```bash
pip install --upgrade "pydantic>=2.0.0"
```

## Platform-Specific Notes

### macOS

No special considerations. Install works out of the box.

### Linux

No special considerations. Install works out of the box.

### Windows

On Windows, make sure you have Microsoft Visual C++ 14.0 or greater installed for some dependencies. You can get it from:
- [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Next Steps

After successful installation:

1. Read the [Quick Start](quickstart.md) guide
2. Explore [Examples](examples.md)
3. Check out [Tutorials](../tutorials/basic-usage.ipynb)
4. Browse the [API Reference](../api/core.md)
