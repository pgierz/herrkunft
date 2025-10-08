# Tracking Provenance

Learn how to access and use provenance information in herrkunft.

## Understanding Provenance

Every value loaded from YAML automatically tracks its origin and modification history through the `Provenance` class.

## Accessing Provenance

### Current Provenance Step

Get the most recent provenance information:

```python
from provenance import load_yaml

config = load_yaml("config.yaml", category="defaults")

# Get a value
db_host = config["database"]["host"]

# Access current provenance
prov = db_host.provenance.current

print(f"File: {prov.yaml_file}")
print(f"Line: {prov.line}")
print(f"Column: {prov.col}")
print(f"Category: {prov.category}")
print(f"Subcategory: {prov.subcategory}")
```

### Provenance Attributes

Each `ProvenanceStep` contains:

| Attribute | Type | Description |
|-----------|------|-------------|
| `yaml_file` | `str \| None` | Source YAML file path |
| `line` | `int \| None` | Line number in file |
| `col` | `int \| None` | Column number in file |
| `category` | `str` | Configuration category |
| `subcategory` | `str \| None` | Optional subcategory |
| `timestamp` | `datetime` | When value was set |
| `modified_by` | `str \| None` | Description of modification |
| `choose_history` | `list \| None` | History of choose operations |

## Provenance History

### Full History

Access complete modification history:

```python
config = load_yaml("config.yaml", category="defaults")

# Modify the value
config["database"]["host"] = "staging.example.com"
config["database"]["host"] = "production.example.com"

# Get the value
host = config["database"]["host"]

# Iterate through history
print(f"Total history steps: {len(host.provenance)}")

for i, step in enumerate(host.provenance):
    source = step.yaml_file or "runtime"
    print(f"Step {i}: {source} ({step.category})")
    print(f"  Timestamp: {step.timestamp}")
```

### History Operations

```python
# Get first step (original)
original = host.provenance[0]
print(f"Originally from: {original.yaml_file}")

# Get last step (current)
current = host.provenance[-1]
print(f"Currently: {current.modified_by or 'loaded'}")

# Get specific step
second_step = host.provenance[1]

# Check history length
num_modifications = len(host.provenance) - 1
print(f"Modified {num_modifications} times")
```

## Type-Specific Provenance

### Dictionaries

```python
from provenance import DictWithProvenance

config = load_yaml("config.yaml")

# Dictionary itself has provenance
dict_prov = config.provenance.current
print(f"Dictionary loaded from: {dict_prov.yaml_file}")

# Each value has its own provenance
for key, value in config.items():
    if hasattr(value, 'provenance'):
        prov = value.provenance.current
        print(f"{key}: line {prov.line}")
```

### Lists

```python
config = load_yaml("servers.yaml")

servers = config["servers"]

# List has provenance
list_prov = servers.provenance.current
print(f"Server list from: {list_prov.yaml_file}:{list_prov.line}")

# Each item has provenance
for server in servers:
    name = server["name"]
    prov = name.provenance.current
    print(f"Server {name}: line {prov.line}")
```

### Scalars

```python
config = load_yaml("config.yaml")

# String with provenance
host = config["database"]["host"]
assert isinstance(host, str)  # Behaves like string
prov = host.provenance.current
print(f"String from: {prov.yaml_file}:{prov.line}")

# Integer with provenance
port = config["database"]["port"]
assert isinstance(port, int)  # Behaves like int
prov = port.provenance.current
print(f"Port from: {prov.yaml_file}:{prov.line}")

# Boolean with provenance
debug = config["app"]["debug"]
assert isinstance(debug, bool)  # Behaves like bool
prov = debug.provenance.current
print(f"Debug flag from: {prov.yaml_file}:{prov.line}")
```

## Extracting Provenance Trees

### Full Tree Extraction

Extract provenance for entire configuration:

```python
from provenance import extract_provenance_tree

config = load_yaml("config.yaml")

# Extract complete provenance tree
prov_tree = extract_provenance_tree(config)

# prov_tree is a dict with same structure as config
# but values are provenance information
print(prov_tree["database"]["host"])
# Output: {'yaml_file': 'config.yaml', 'line': 2, 'col': 8, ...}
```

### Historical Trees

Extract provenance at specific history index:

```python
# Get provenance from original load (index 0)
original_tree = extract_provenance_tree(config, index=0)

# Get provenance from current state (index -1)
current_tree = extract_provenance_tree(config, index=-1)

# Compare
if original_tree["database"]["host"] != current_tree["database"]["host"]:
    print("Database host was modified")
```

### Saving Provenance Trees

```python
import json
from provenance import extract_provenance_tree

config = load_yaml("config.yaml")
prov_tree = extract_provenance_tree(config)

# Save as JSON
with open("provenance.json", "w") as f:
    json.dump(prov_tree, f, indent=2, default=str)

# Load and inspect later
with open("provenance.json", "r") as f:
    loaded_prov = json.load(f)
    print(f"Config came from: {loaded_prov['yaml_file']}")
```

## Provenance Validation

### Validating Steps

```python
from provenance import validate_provenance_step, ValidationError

try:
    validate_provenance_step(prov_step)
    print("Provenance step is valid")
except ValidationError as e:
    print(f"Invalid provenance: {e}")
```

### Validating History

```python
from provenance import validate_provenance_history

value = config["database"]["host"]

try:
    validate_provenance_history(value.provenance)
    print("Provenance history is valid")
except ValidationError as e:
    print(f"Invalid history: {e}")
```

### Validating Trees

```python
from provenance import validate_provenance_tree

prov_tree = extract_provenance_tree(config)

try:
    validate_provenance_tree(prov_tree)
    print("Provenance tree is valid")
except ValidationError as e:
    print(f"Invalid tree: {e}")
```

## Provenance Queries

### Finding Values by Source

```python
def find_values_from_file(config, filename):
    """Find all values loaded from specific file."""
    results = []

    def search(obj, path=""):
        if hasattr(obj, 'provenance'):
            prov = obj.provenance.current
            if prov.yaml_file and filename in prov.yaml_file:
                results.append((path, obj, prov))

        if isinstance(obj, dict):
            for key, value in obj.items():
                search(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                search(value, f"{path}[{i}]")

    search(config)
    return results

# Usage
from_config = find_values_from_file(config, "config.yaml")
for path, value, prov in from_config:
    print(f"{path}: {value} (line {prov.line})")
```

### Finding Values by Category

```python
def find_values_by_category(config, category):
    """Find all values from specific category."""
    results = []

    def search(obj, path=""):
        if hasattr(obj, 'provenance'):
            prov = obj.provenance.current
            if prov.category == category:
                results.append((path, obj, prov))

        if isinstance(obj, dict):
            for key, value in obj.items():
                search(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                search(value, f"{path}[{i}]")

    search(config)
    return results

# Find all production values
prod_values = find_values_by_category(config, "production")
for path, value, prov in prod_values:
    print(f"{path}: from {prov.yaml_file}:{prov.line}")
```

### Finding Modified Values

```python
def find_modified_values(config):
    """Find all values modified after loading."""
    results = []

    def search(obj, path=""):
        if hasattr(obj, 'provenance'):
            # Check if history > 1 (modified after load)
            if len(obj.provenance) > 1:
                results.append((path, obj, obj.provenance))

        if isinstance(obj, dict):
            for key, value in obj.items():
                search(value, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                search(value, f"{path}[{i}]")

    search(config)
    return results

# Find all modified values
modified = find_modified_values(config)
for path, value, history in modified:
    print(f"{path}: modified {len(history) - 1} times")
    print(f"  Original: {history[0].yaml_file}:{history[0].line}")
    print(f"  Current: {history[-1].modified_by or 'runtime'}")
```

## Custom Provenance

### Adding Custom Metadata

When modifying values, add custom provenance information:

```python
from provenance import ProvenanceStep
from datetime import datetime

# Modify with custom provenance
config["database"]["host"] = "new-host.example.com"

# Access and inspect
host = config["database"]["host"]
current_step = host.provenance.current

# The modification is tracked automatically
print(f"Modified at: {current_step.timestamp}")
```

## Provenance Utilities

### Stripping Provenance

Remove provenance from specific values:

```python
from provenance import strip_provenance

# Strip provenance from a value
plain_host = strip_provenance(config["database"]["host"])
assert type(plain_host) == str
assert not hasattr(plain_host, 'provenance')
```

### Cleaning Provenance

Remove provenance from entire structures:

```python
from provenance import clean_provenance

# Clean entire config
clean_config = clean_provenance(config)

# Now it's plain Python types
assert type(clean_config) == dict
assert type(clean_config["database"]["host"]) == str
```

### Ensuring Valid Provenance

```python
from provenance import ensure_provenance_valid

# Validate and raise if invalid
ensure_provenance_valid(config)
```

## Best Practices

### 1. Always Check for Provenance

```python
def get_provenance_safe(value):
    if hasattr(value, 'provenance'):
        return value.provenance.current
    return None

prov = get_provenance_safe(some_value)
if prov:
    print(f"From: {prov.yaml_file}:{prov.line}")
```

### 2. Use Type Guards

```python
from provenance import HasProvenance

def process_with_provenance(value):
    if isinstance(value, HasProvenance):
        prov = value.provenance.current
        print(f"Processing value from {prov.yaml_file}")
    # Process value...
```

### 3. Log Provenance for Debugging

```python
from loguru import logger

def debug_provenance(config, key_path):
    keys = key_path.split('.')
    value = config
    for key in keys:
        value = value[key]

    if hasattr(value, 'provenance'):
        prov = value.provenance.current
        logger.debug(f"{key_path}: {value}")
        logger.debug(f"  Source: {prov.yaml_file}:{prov.line}")
        logger.debug(f"  Category: {prov.category}")
```

### 4. Track Configuration Sources

```python
def audit_configuration(config):
    """Generate audit report of configuration sources."""
    report = {}

    def collect(obj, path=""):
        if hasattr(obj, 'provenance'):
            prov = obj.provenance.current
            report[path] = {
                'file': prov.yaml_file,
                'line': prov.line,
                'category': prov.category,
                'value': str(obj)
            }

        if isinstance(obj, dict):
            for key, value in obj.items():
                collect(value, f"{path}.{key}" if path else key)

    collect(config)
    return report

# Generate audit
audit = audit_configuration(config)
for key, info in audit.items():
    print(f"{key}: {info['file']}:{info['line']} ({info['category']})")
```

## Next Steps

- Learn about [Hierarchical Configuration](hierarchical-config.md)
- Explore [Saving YAML Files](saving-yaml.md)
- See the [API Reference](../api/core.md)
