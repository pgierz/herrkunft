# Contributing to herrkunft

Thank you for your interest in contributing to herrkunft! This guide will help you get started.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## Ways to Contribute

- **Report bugs**: Open an issue on GitHub
- **Suggest features**: Open a feature request issue
- **Improve documentation**: Submit PRs for docs
- **Write code**: Fix bugs or implement features
- **Write tests**: Improve test coverage
- **Review PRs**: Help review other contributions

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/herrkunft.git
cd herrkunft
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -e .[dev]
```

This installs herrkunft in editable mode with all development dependencies.

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

Branch naming convention:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Changes

Write your code following our style guidelines (see below).

### 3. Write Tests

All new code should include tests:

```python
# tests/test_my_feature.py
def test_my_new_feature():
    """Test description."""
    # Arrange
    config = load_yaml("test.yaml")

    # Act
    result = my_new_feature(config)

    # Assert
    assert result == expected_value
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_core/test_provenance.py

# Run with coverage
pytest --cov=provenance --cov-report=html

# Run in parallel
pytest -n auto
```

### 5. Check Code Quality

```bash
# Format code
black provenance tests

# Lint
ruff provenance tests

# Type check
mypy provenance
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Refactoring
- `chore:` - Maintenance

### 7. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use `ruff` for sorting
- **Docstrings**: Google style
- **Type hints**: Required for all functions

### Formatting

We use [Black](https://black.readthedocs.io/) for formatting:

```bash
black provenance tests
```

### Linting

We use [Ruff](https://github.com/charliermarsh/ruff) for linting:

```bash
ruff provenance tests
```

### Type Checking

We use [mypy](http://mypy-lang.org/) for type checking:

```bash
mypy provenance
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def load_yaml(path: str, category: str = None) -> DictWithProvenance:
    """
    Load YAML file with provenance tracking.

    Args:
        path: Path to YAML file
        category: Configuration category

    Returns:
        Dictionary with provenance tracking enabled

    Raises:
        LoaderError: If file cannot be loaded

    Example:
        >>> config = load_yaml("config.yaml", category="defaults")
        >>> print(config["key"])
    """
```

### Building Documentation

```bash
# Install docs dependencies
pip install -e .[docs]

# Build Jupyter Book
jupyter-book build docs/

# View locally
open docs/_build/html/index.html
```

## Testing Guidelines

### Test Structure

```python
import pytest
from provenance import load_yaml

class TestProvenanceLoading:
    """Test provenance loading functionality."""

    def test_loads_simple_yaml(self):
        """Should load simple YAML with provenance."""
        # Test implementation

    def test_tracks_line_numbers(self):
        """Should track correct line numbers."""
        # Test implementation

    @pytest.mark.slow
    def test_large_file_performance(self):
        """Should handle large files efficiently."""
        # Test implementation
```

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interaction
- **End-to-end tests**: Test complete workflows

### Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def sample_config():
    """Provide sample configuration for tests."""
    return {
        "database": {"host": "localhost", "port": 5432},
        "server": {"host": "0.0.0.0", "port": 8080}
    }

def test_with_fixture(sample_config):
    # Use sample_config
```

### Coverage Goals

- **New code**: 100% coverage
- **Modified code**: Maintain or improve coverage
- **Overall**: >90% coverage

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code is formatted (Black)
3. ✅ Linting passes (Ruff)
4. ✅ Type checking passes (mypy)
5. ✅ Documentation updated
6. ✅ Changelog updated
7. ✅ Tests added for new code

### PR Description

Include:
- **What**: Description of changes
- **Why**: Motivation and context
- **How**: Implementation approach
- **Testing**: How to test changes
- **Screenshots**: If UI changes (N/A for herrkunft)

Template:

```markdown
## Description
Brief description of changes

## Motivation
Why this change is needed

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Changelog updated
```

### Review Process

1. Automated checks run (CI)
2. Maintainers review code
3. Address feedback
4. Approval and merge

## Release Process

For maintainers:

### 1. Update Version

Edit `provenance/version.py`:

```python
__version__ = "0.2.0"
```

### 2. Update Changelog

Add entry to `docs/reference/changelog.md`

### 3. Create Release Tag

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 4. Build and Publish

```bash
# Build
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

## Issue Guidelines

### Bug Reports

Include:
- **Description**: Clear description of bug
- **Steps to reproduce**: Minimal example
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, etc.

Template:

```markdown
**Bug Description**
Clear description

**To Reproduce**
```python
# Minimal code to reproduce
```

**Expected**
What should happen

**Actual**
What actually happens

**Environment**
- Python: 3.11
- herrkunft: 0.1.0
- OS: macOS
```

### Feature Requests

Include:
- **Use case**: Why is this needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Examples**: Code examples if applicable

## Questions?

- **Documentation**: Check [docs](https://herrkunft.readthedocs.io)
- **Issues**: Search [existing issues](https://github.com/pgierz/herrkunft/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/pgierz/herrkunft/discussions)
- **Email**: Contact maintainers at dev@herrkunft.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all our contributors! Your efforts make herrkunft better for everyone.
