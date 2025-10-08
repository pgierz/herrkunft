# Utils Module API

Utility functions for provenance manipulation and serialization.

## Cleaning Functions

### clean_provenance

Remove all provenance wrappers from a data structure.

```python
from provenance import clean_provenance, load_yaml

config = load_yaml("config.yaml")
clean_config = clean_provenance(config)

# Now plain Python types
assert type(clean_config) == dict
assert type(clean_config["key"]) == str
```

### strip_provenance

Remove provenance from a single value.

```python
from provenance import strip_provenance

wrapped_value = config["database"]["host"]
plain_value = strip_provenance(wrapped_value)

assert type(plain_value) == str
assert not hasattr(plain_value, 'provenance')
```

### extract_provenance_tree

Extract provenance information as a nested dictionary.

```python
from provenance import extract_provenance_tree

config = load_yaml("config.yaml")
prov_tree = extract_provenance_tree(config)

# prov_tree has same structure as config
# but values are provenance dicts
print(prov_tree["database"]["host"])
# {'yaml_file': 'config.yaml', 'line': 2, 'col': 8, ...}
```

Parameters:
- **data**: Configuration to extract from
- **index** (`int`, optional): History index (-1 for current, 0 for original)

## Validation Functions

### validate_provenance_step

Validate a single provenance step.

```python
from provenance import validate_provenance_step, ValidationError

try:
    validate_provenance_step(step)
except ValidationError as e:
    print(f"Invalid step: {e}")
```

### validate_provenance_history

Validate complete provenance history.

```python
from provenance import validate_provenance_history

value = config["key"]
validate_provenance_history(value.provenance)
```

### validate_provenance_tree

Validate entire provenance tree.

```python
from provenance import validate_provenance_tree

prov_tree = extract_provenance_tree(config)
validate_provenance_tree(prov_tree)
```

### ensure_provenance_valid

Validate and raise error if invalid.

```python
from provenance import ensure_provenance_valid

# Raises ValidationError if invalid
ensure_provenance_valid(config)
```

## Serialization Functions

### to_dict

Convert configuration to plain dictionary.

```python
from provenance import to_dict

config = load_yaml("config.yaml")
plain_dict = to_dict(config)

# Plain Python dict
assert type(plain_dict) == dict
```

### to_json

Convert configuration to JSON string.

```python
from provenance import to_json

config = load_yaml("config.yaml")
json_string = to_json(config, include_provenance=True, indent=2)
```

Parameters:
- **data**: Configuration to serialize
- **include_provenance** (`bool`): Include provenance metadata
- **indent** (`int`): JSON indentation

### to_json_file

Save configuration as JSON file.

```python
from provenance import to_json_file

config = load_yaml("config.yaml")
to_json_file(config, "config.json", include_provenance=True, indent=2)
```

### from_dict

Load configuration from dictionary.

```python
from provenance import from_dict

data = {"key": "value"}
config = from_dict(data, category="runtime")
```

### from_json

Load configuration from JSON string.

```python
from provenance import from_json

json_str = '{"key": "value"}'
config = from_json(json_str, category="runtime")
```

### from_json_file

Load configuration from JSON file.

```python
from provenance import from_json_file

config = from_json_file("config.json", category="runtime")
```

## Complete Examples

### Cleaning Example

```python
from provenance import load_yaml, clean_provenance
import json

# Load with provenance
config = load_yaml("config.yaml")

# Clean for external use
clean_config = clean_provenance(config)

# Now safe for standard JSON
json.dump(clean_config, open("export.json", "w"), indent=2)
```

### Extraction Example

```python
from provenance import load_yaml, extract_provenance_tree
import json

config = load_yaml("config.yaml")

# Extract full provenance tree
prov_tree = extract_provenance_tree(config)

# Save provenance metadata
with open("provenance.json", "w") as f:
    json.dump(prov_tree, f, indent=2, default=str)

# Extract original provenance (index 0)
original_prov = extract_provenance_tree(config, index=0)

# Extract current provenance (index -1)
current_prov = extract_provenance_tree(config, index=-1)

# Compare
for key in config["database"]:
    if original_prov["database"][key] != current_prov["database"][key]:
        print(f"{key} was modified")
```

### Validation Example

```python
from provenance import (
    load_yaml,
    validate_provenance_step,
    validate_provenance_history,
    ensure_provenance_valid,
    ValidationError
)

config = load_yaml("config.yaml")

# Validate individual value
value = config["database"]["host"]
try:
    validate_provenance_history(value.provenance)
    print("Value provenance is valid")
except ValidationError as e:
    print(f"Invalid provenance: {e}")

# Validate entire config
try:
    ensure_provenance_valid(config)
    print("Configuration provenance is valid")
except ValidationError as e:
    print(f"Invalid configuration: {e}")
```

### Serialization Example

```python
from provenance import (
    load_yaml,
    to_json_file,
    from_json_file,
    extract_provenance_tree
)

# Load original
config = load_yaml("config.yaml", category="defaults")

# Modify
config["new_key"] = "new_value"

# Save with provenance
to_json_file(config, "config.json", include_provenance=True)

# The JSON includes both data and provenance
# Reload
reloaded = from_json_file("config.json", category="reloaded")

# Verify
assert reloaded["new_key"] == "new_value"
assert hasattr(reloaded["new_key"], 'provenance')
```

## Utility Patterns

### Audit Report

```python
from provenance import extract_provenance_tree

def generate_audit_report(config):
    """Generate configuration audit report."""
    prov_tree = extract_provenance_tree(config)

    report = []

    def traverse(tree, path=""):
        for key, value in tree.items():
            current_path = f"{path}.{key}" if path else key

            if isinstance(value, dict) and 'yaml_file' in value:
                # Leaf node with provenance
                report.append({
                    'path': current_path,
                    'file': value.get('yaml_file'),
                    'line': value.get('line'),
                    'category': value.get('category'),
                })
            elif isinstance(value, dict):
                # Nested structure
                traverse(value, current_path)

    traverse(prov_tree)
    return report

# Usage
audit = generate_audit_report(config)
for item in audit:
    print(f"{item['path']}: {item['file']}:{item['line']} ({item['category']})")
```

### Clean Export

```python
from provenance import clean_provenance, dump_yaml

def export_for_external_use(config, output_path):
    """Export configuration without provenance."""
    clean_config = clean_provenance(config)
    dump_yaml(clean_config, output_path, include_provenance=False, clean=True)

# Usage
export_for_external_use(config, "external_config.yaml")
```

## See Also

- [Core Module](core.md) - Provenance classes
- [Types Module](types.md) - Type wrappers
- [YAML Module](yaml.md) - YAML operations
- [User Guide: Tracking Provenance](../user-guide/tracking-provenance.md)
