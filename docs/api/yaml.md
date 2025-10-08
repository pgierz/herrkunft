# YAML Module API

YAML loading and dumping with provenance tracking.

## ProvenanceLoader

Load YAML files with provenance tracking.

```{eval-rst}
.. autoclass:: provenance.ProvenanceLoader
   :members:
   :undoc-members:
   :show-inheritance:
```

### Constructor

```python
ProvenanceLoader(
    category: str = None,
    subcategory: str = None,
    strict: bool = False,
    encoding: str = "utf-8"
)
```

- **category**: Default category for loaded values
- **subcategory**: Default subcategory for loaded values
- **strict**: Raise errors on YAML parsing issues
- **encoding**: File encoding (default: utf-8)

### Methods

#### `load(file_path, category=None, subcategory=None)`

Load a single YAML file.

```python
loader = ProvenanceLoader()
config = loader.load("config.yaml", category="defaults")
```

#### `load_multiple(file_specs)`

Load multiple YAML files.

```python
loader = ProvenanceLoader()
configs = loader.load_multiple([
    ("defaults.yaml", "defaults"),
    ("production.yaml", "production", "prod-01"),
])
```

### Example

```python
from provenance import ProvenanceLoader

# Create loader
loader = ProvenanceLoader(
    category="defaults",
    subcategory="main",
    strict=True
)

# Load file
config = loader.load("config.yaml")

# Load with override
production = loader.load(
    "production.yaml",
    category="production"
)

# Batch load
all_configs = loader.load_multiple([
    ("base.yaml", "base"),
    ("machine.yaml", "machines", "hpc"),
    ("user.yaml", "user"),
])
```

## ProvenanceDumper

Dump configurations with provenance as comments.

```{eval-rst}
.. autoclass:: provenance.ProvenanceDumper
   :members:
   :undoc-members:
   :show-inheritance:
```

### Constructor

```python
ProvenanceDumper(
    include_provenance_comments: bool = True,
    comment_format: str = "{file}:{line}:{col} ({category})",
    encoding: str = "utf-8",
    width: int = 80,
    indent: int = 2
)
```

- **include_provenance_comments**: Add provenance as YAML comments
- **comment_format**: Format string for comments
- **encoding**: File encoding
- **width**: Maximum line width
- **indent**: Indentation spaces

### Methods

#### `dump(data, file_path, clean=False)`

Dump configuration to file.

```python
dumper = ProvenanceDumper()
dumper.dump(config, "output.yaml")
```

#### `dumps(data, clean=False)`

Dump configuration to string.

```python
dumper = ProvenanceDumper()
yaml_string = dumper.dumps(config)
```

### Comment Format Variables

Available in `comment_format`:

- `{file}` - Source file name
- `{yaml_file}` - Full source file path
- `{line}` - Line number
- `{col}` - Column number
- `{category}` - Category name
- `{subcategory}` - Subcategory name
- `{timestamp}` - Modification timestamp
- `{modified_by}` - Modification source

### Example

```python
from provenance import ProvenanceDumper, load_yaml

# Load config
config = load_yaml("config.yaml", category="defaults")

# Dump with default format
dumper = ProvenanceDumper()
dumper.dump(config, "output.yaml")
# Output includes: # config.yaml:2:8 (defaults)

# Custom format
custom_dumper = ProvenanceDumper(
    comment_format="from {category}: {file} line {line}"
)
custom_dumper.dump(config, "custom.yaml")
# Output includes: # from defaults: config.yaml line 2

# No comments
clean_dumper = ProvenanceDumper(include_provenance_comments=False)
clean_dumper.dump(config, "clean.yaml")
# Output has no provenance comments
```

## Convenience Functions

### load_yaml

Quick function to load a YAML file.

```python
from provenance import load_yaml

config = load_yaml("config.yaml", category="defaults", subcategory="main")
```

Equivalent to:

```python
loader = ProvenanceLoader(category="defaults", subcategory="main")
config = loader.load("config.yaml")
```

### dump_yaml

Quick function to dump a YAML file.

```python
from provenance import dump_yaml

dump_yaml(config, "output.yaml", include_provenance=True, clean=False)
```

Equivalent to:

```python
dumper = ProvenanceDumper(include_provenance_comments=True)
dumper.dump(config, "output.yaml", clean=False)
```

## Complete Example

```python
from provenance import ProvenanceLoader, ProvenanceDumper

# Load multiple configs
loader = ProvenanceLoader()
configs = loader.load_multiple([
    ("defaults.yaml", "defaults"),
    ("production.yaml", "production"),
])

# Merge
final_config = configs[0]
final_config.update(configs[1])

# Dump with custom format
dumper = ProvenanceDumper(
    include_provenance_comments=True,
    comment_format="{category}: {file}:{line}",
    indent=4
)

dumper.dump(final_config, "merged.yaml")
```

Output `merged.yaml`:

```yaml
database:
    host: prod.db.example.com    # production: production.yaml:2
    port: 5432    # defaults: defaults.yaml:3
    name: myapp    # defaults: defaults.yaml:4
```

## See Also

- [Core Module](core.md) - Provenance classes
- [Types Module](types.md) - Type wrappers
- [User Guide: Loading YAML](../user-guide/loading-yaml.md)
- [User Guide: Saving YAML](../user-guide/saving-yaml.md)
