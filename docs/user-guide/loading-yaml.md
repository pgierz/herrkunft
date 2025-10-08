# Loading YAML Files

Learn how to load YAML configuration files with herrkunft's provenance tracking.

## Basic Loading

The simplest way to load a YAML file is using the `load_yaml()` function:

```python
from provenance import load_yaml

config = load_yaml("config.yaml", category="defaults")
```

This returns a `DictWithProvenance` object that behaves exactly like a regular Python dictionary but tracks provenance for all values.

## The ProvenanceLoader Class

For more control, use the `ProvenanceLoader` class directly:

```python
from provenance import ProvenanceLoader

loader = ProvenanceLoader(category="defaults", subcategory="main")
config = loader.load("config.yaml")
```

### Loader Parameters

```python
ProvenanceLoader(
    category: str = None,          # Main category for hierarchy resolution
    subcategory: str = None,       # Optional subcategory identifier
    strict: bool = False,          # Raise errors on YAML issues
    encoding: str = "utf-8",       # File encoding
)
```

## Categories and Subcategories

Categories are essential for hierarchical configuration management:

### Category

The category defines the priority level in the hierarchy:

```python
# Lower priority
defaults = load_yaml("defaults.yaml", category="defaults")

# Higher priority
production = load_yaml("production.yaml", category="production")
```

### Subcategory

Subcategories provide additional context without affecting hierarchy:

```python
loader = ProvenanceLoader()

# Load machine-specific configs with subcategory
hpc_config = loader.load("hpc.yaml", category="machines", subcategory="hpc_cluster")
laptop_config = loader.load("laptop.yaml", category="machines", subcategory="local_dev")
```

Both have the same category ("machines") but different subcategories for tracking.

## Loading Multiple Files

### Method 1: Sequential Loading

```python
from provenance import ProvenanceLoader

loader = ProvenanceLoader()

defaults = loader.load("defaults.yaml", category="defaults")
user_config = loader.load("user.yaml", category="user")
runtime_config = loader.load("runtime.yaml", category="runtime")

# Merge manually
final_config = defaults.copy()
final_config.update(user_config)
final_config.update(runtime_config)
```

### Method 2: Batch Loading

```python
configs = loader.load_multiple([
    ("defaults.yaml", "defaults"),
    ("machine.yaml", "machines", "hpc"),
    ("user.yaml", "user"),
    ("production.yaml", "production"),
])

# configs is a list of DictWithProvenance objects
```

### Method 3: Using HierarchyManager

```python
from provenance import ProvenanceLoader, HierarchyManager

loader = ProvenanceLoader()
hierarchy = HierarchyManager(["defaults", "machines", "user", "production"])

# Load all configs
defaults = loader.load("defaults.yaml", category="defaults")
machines = loader.load("machine.yaml", category="machines")
user = loader.load("user.yaml", category="user")
production = loader.load("production.yaml", category="production")

# Merge with hierarchy rules
final_config = hierarchy.merge_all([defaults, machines, user, production])
```

## Supported YAML Features

herrkunft supports all standard YAML features through ruamel.yaml:

### Basic Types

```yaml
# strings.yaml
string_value: "hello world"
multiline: |
  This is a
  multiline string
number: 42
float_value: 3.14
boolean: true
null_value: null
```

```python
config = load_yaml("strings.yaml")
assert isinstance(config["string_value"], str)
assert config["number"] == 42
assert config["boolean"] is True
```

### Collections

```yaml
# collections.yaml
list_example:
  - item1
  - item2
  - item3

dict_example:
  key1: value1
  key2: value2

nested:
  level1:
    level2:
      level3: deep_value
```

```python
config = load_yaml("collections.yaml")

# Access lists
items = config["list_example"]
assert len(items) == 3

# Access nested dicts
deep = config["nested"]["level1"]["level2"]["level3"]
assert deep == "deep_value"
```

### Anchors and Aliases

```yaml
# anchors.yaml
defaults: &defaults
  timeout: 30
  retries: 3

service1:
  <<: *defaults
  name: service1

service2:
  <<: *defaults
  name: service2
  timeout: 60  # Override
```

```python
config = load_yaml("anchors.yaml")

# Aliases are expanded, provenance points to original definition
assert config["service1"]["timeout"] == 30
assert config["service2"]["timeout"] == 60

# Provenance tracks the anchor source
prov = config["service1"]["retries"].provenance.current
print(f"Retries defined at line: {prov.line}")
```

### Complex Structures

```yaml
# complex.yaml
servers:
  - name: web-01
    host: 192.168.1.10
    ports:
      - 80
      - 443
    config:
      ssl: true
      workers: 4

  - name: db-01
    host: 192.168.1.20
    ports:
      - 5432
    config:
      pool_size: 20
```

```python
config = load_yaml("complex.yaml")

for server in config["servers"]:
    name = server["name"]
    prov = name.provenance.current
    print(f"{name}: defined at line {prov.line}")
```

## File Path Resolution

### Absolute Paths

```python
config = load_yaml("/absolute/path/to/config.yaml")
```

### Relative Paths

Relative to current working directory:

```python
config = load_yaml("./configs/app.yaml")
config = load_yaml("../shared/defaults.yaml")
```

### Path Objects

Using `pathlib.Path`:

```python
from pathlib import Path

config_file = Path("configs") / "app.yaml"
config = load_yaml(str(config_file))
```

## Error Handling

### File Not Found

```python
from provenance import LoaderError

try:
    config = load_yaml("nonexistent.yaml")
except LoaderError as e:
    print(f"Failed to load: {e}")
```

### Invalid YAML

```python
from provenance import LoaderError

try:
    # File contains invalid YAML syntax
    config = load_yaml("invalid.yaml", strict=True)
except LoaderError as e:
    print(f"YAML error: {e}")
```

### Encoding Issues

```python
# Specify encoding explicitly
config = load_yaml("config.yaml", encoding="utf-8")

# For files with different encoding
config = load_yaml("legacy.yaml", encoding="latin-1")
```

## Loading from Strings

For testing or dynamic configuration:

```python
from provenance import ProvenanceLoader
from io import StringIO

yaml_content = """
database:
  host: localhost
  port: 5432
"""

# Create a loader
loader = ProvenanceLoader(category="test")

# Load from string via StringIO
import tempfile
with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
    f.write(yaml_content)
    temp_file = f.name

config = loader.load(temp_file)

# Clean up
import os
os.unlink(temp_file)
```

## Performance Considerations

### Lazy Loading

For large files, consider lazy loading patterns:

```python
class ConfigManager:
    def __init__(self):
        self._config = None

    @property
    def config(self):
        if self._config is None:
            self._config = load_yaml("large_config.yaml")
        return self._config
```

### Caching

Cache loaded configurations:

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def load_cached_config(file_path: str, category: str):
    return load_yaml(file_path, category=category)

# First call loads from file
config1 = load_cached_config("config.yaml", "defaults")

# Second call uses cache
config2 = load_cached_config("config.yaml", "defaults")
```

### Memory Usage

For very large configurations, consider splitting into multiple files:

```python
# Load only what you need
database_config = load_yaml("configs/database.yaml")
server_config = load_yaml("configs/server.yaml")
logging_config = load_yaml("configs/logging.yaml")

# Combine
final_config = {
    "database": database_config,
    "server": server_config,
    "logging": logging_config,
}
```

## Best Practices

### 1. Always Use Categories

```python
# Good
config = load_yaml("config.yaml", category="defaults")

# Better
loader = ProvenanceLoader(category="defaults", subcategory="v1")
config = loader.load("config.yaml")
```

### 2. Validate After Loading

```python
config = load_yaml("config.yaml", category="production")

# Validate required keys exist
required_keys = ["database", "server", "logging"]
for key in required_keys:
    if key not in config:
        raise ValueError(f"Missing required key: {key}")
```

### 3. Use Type Hints

```python
from provenance import DictWithProvenance

def load_app_config() -> DictWithProvenance:
    return load_yaml("app.yaml", category="application")
```

### 4. Handle Missing Files Gracefully

```python
from pathlib import Path
from provenance import load_yaml, LoaderError

def load_config_with_fallback(primary: str, fallback: str):
    try:
        return load_yaml(primary, category="user")
    except LoaderError:
        if Path(fallback).exists():
            return load_yaml(fallback, category="defaults")
        raise
```

## Next Steps

- Learn about [Tracking Provenance](tracking-provenance.md)
- Explore [Hierarchical Configuration](hierarchical-config.md)
- See [Saving YAML Files](saving-yaml.md)
- Try the [Basic Usage Tutorial](../tutorials/basic-usage.ipynb)
