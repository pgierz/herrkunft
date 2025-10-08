# Herrkunft Library - Examples

This directory contains working examples demonstrating the key features of the herrkunft library.

## Running the Examples

To run any example:

```bash
# From the project root directory
PYTHONPATH=/path/to/provenance-as-library python3 examples/basic_usage.py
```

Or install the library in development mode:

```bash
pip install -e .
python3 examples/basic_usage.py
```

## Available Examples

### 1. Basic Usage (`basic_usage.py`)

**What it demonstrates**:
- Loading YAML files with provenance tracking
- Accessing values and provenance information
- Modifying configuration values
- Saving configurations with provenance comments
- Saving clean configurations without provenance
- Round-trip loading to verify data integrity

**Best for**: Getting started with the library

**Key concepts**:
- `load_yaml()` convenience function
- `dump_yaml()` convenience function
- Accessing `.provenance` attribute on values
- Provenance history tracking

**Sample output**:
```
Loading YAML file with provenance tracking...
   Loaded config type: DictWithProvenance
   Config keys: ['database', 'server']

Inspecting provenance information...
   Source file: config.yaml
   Line number: 3
   Column number: 9
   Category: defaults
```

### 2. Hierarchical Configuration (`hierarchical_config.py`)

**What it demonstrates**:
- Loading multiple configuration files with different priorities
- Automatic hierarchical conflict resolution
- Category-based provenance tracking (defaults < machines < environment)
- Merging configurations while preserving provenance history
- Using `ProvenanceLoader.load_multiple()` for batch loading

**Best for**: Understanding how herrkunft handles complex configuration hierarchies

**Key concepts**:
- Configuration categories (defaults, machines, components, environment, etc.)
- Automatic override based on category priority
- Provenance tracking across multiple files
- `.update()` method for merging with hierarchy resolution

**Hierarchy demonstration**:
```
defaults.yaml (category: defaults)         <- Lowest priority
machine_hpc.yaml (category: machines)      <- Medium priority
production.yaml (category: environment)    <- Highest priority
```

### 3. Provenance Tracking (`provenance_tracking.py`)

**What it demonstrates**:
- Inspecting detailed provenance information
- Tracking provenance history through multiple modifications
- Extracting complete provenance trees
- Exporting provenance as JSON
- Cleaning provenance from configurations
- Accessing historical provenance at specific points

**Best for**: Understanding provenance inspection and analysis capabilities

**Key concepts**:
- Provenance history (`provenance[0]`, `provenance[1]`, etc.)
- `extract_provenance_tree()` utility function
- `clean_provenance()` for removing wrapper types
- Provenance step structure (yaml_file, line, col, category, modified_by)
- Historical provenance access with index parameter

**Features shown**:
- Full provenance history inspection
- Modification tracking
- Provenance tree extraction and export
- Nested structure provenance
- Clean export for production use

## Example Scenarios

### Scenario 1: Simple Configuration Loading

```python
from provenance import load_yaml

# Load a configuration file
config = load_yaml("myapp.yaml", category="defaults")

# Access values normally
db_host = config["database"]["host"]
print(f"Database host: {db_host}")

# Inspect where it came from
prov = db_host.provenance.current
print(f"From {prov.yaml_file} line {prov.line}")
```

### Scenario 2: Multi-Environment Configuration

```python
from provenance import load_yaml

# Load base configuration
config = load_yaml("defaults.yaml", category="defaults")

# Overlay production settings (higher priority)
prod = load_yaml("production.yaml", category="environment")
config.update(prod)  # Automatically resolves conflicts

# Production values override defaults
print(config["database"]["host"])  # production.db.example.com
```

### Scenario 3: Configuration with Provenance Export

```python
from provenance import load_yaml, dump_yaml

# Load and modify
config = load_yaml("config.yaml", category="defaults")
config["new_feature"] = "enabled"

# Save with provenance comments
dump_yaml(config, "output.yaml", include_provenance=True)

# Result:
# database:
# #  from: config.yaml | line: 3 | category: defaults
#   host: localhost
# new_feature: enabled
```

## Understanding Provenance Structure

Every value in a loaded configuration has a `.provenance` attribute that contains:

```python
value.provenance        # Provenance object (list of steps)
value.provenance[0]     # First provenance step (original)
value.provenance[-1]    # Current provenance step
value.provenance.current  # Same as value.provenance[-1]

# Each step contains:
step.yaml_file      # Source YAML file path
step.line           # Line number in file (1-indexed)
step.col            # Column number in file (1-indexed)
step.category       # Configuration category
step.subcategory    # Optional subcategory
step.modified_by    # Operation that created this step
step.choose_history # For choose block resolution
```

## Configuration Categories

Herrkunft uses a hierarchy of configuration categories:

1. **defaults** (Lowest) - Base configuration
2. **machines** - Machine-specific settings
3. **components** - Component/module settings
4. **setups** - Setup-specific configuration
5. **runscript** - Runtime script settings
6. **command_line** - Command line arguments
7. **environment** (Highest) - Environment variables and runtime overrides

Higher categories automatically override lower categories when merging configurations.

## Tips and Best Practices

1. **Always specify a category** when loading files:
   ```python
   config = load_yaml("file.yaml", category="defaults")
   ```

2. **Use hierarchical loading** for complex configurations:
   ```python
   # Load in order from lowest to highest priority
   config = load_yaml("defaults.yaml", category="defaults")
   config.update(load_yaml("machine.yaml", category="machines"))
   config.update(load_yaml("prod.yaml", category="environment"))
   ```

3. **Save with provenance** for debugging:
   ```python
   dump_yaml(config, "debug_config.yaml", include_provenance=True)
   # You can see exactly where each value came from
   ```

4. **Save clean** for production:
   ```python
   dump_yaml(config, "production_config.yaml", clean=True)
   # Removes all provenance wrappers for clean YAML
   ```

5. **Extract provenance** for analysis:
   ```python
   from provenance import extract_provenance_tree
   prov_tree = extract_provenance_tree(config)
   # Now you have a dict with same structure but provenance info
   ```

## Next Steps

After running these examples:

1. Read the [ARCHITECTURE.md](../AI-STATUS/ARCHITECTURE.md) for design details
2. Review the [Integration Report](../AI-STATUS/INTEGRATION_REPORT_CYCLE2.md) for test results
3. Explore the [test suite](../tests/) for more usage patterns
4. Check the [implementation guide](../AI-STATUS/IMPLEMENTATION_GUIDE.md) for advanced features

## Troubleshooting

### Module not found error

If you get `ModuleNotFoundError: No module named 'provenance'`:
```bash
# Set PYTHONPATH or install in development mode
PYTHONPATH=/path/to/provenance-as-library python3 examples/basic_usage.py
# Or
pip install -e .
```

### Import warnings

If you see import warnings about missing implementations:
- Check that Expert 2 completed DictWithProvenance and ListWithProvenance
- Check that Expert 3 completed ProvenanceDumper
- See [INTEGRATION_REPORT_CYCLE2.md](../AI-STATUS/INTEGRATION_REPORT_CYCLE2.md) for status

### Need help?

Check the integration report or run the test suite:
```bash
pytest tests/ -v
```
