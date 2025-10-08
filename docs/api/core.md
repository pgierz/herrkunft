# Core Module API

The core module provides the fundamental provenance tracking classes.

## ProvenanceStep

Single step in provenance history.

```{eval-rst}
.. autoclass:: provenance.ProvenanceStep
   :members:
   :undoc-members:
   :show-inheritance:
```

### Attributes

- **category** (`str | None`): Configuration category (e.g., 'defaults', 'production')
- **subcategory** (`str | None`): Optional subcategory identifier
- **yaml_file** (`str | None`): Source YAML file path
- **line** (`int | None`): Line number in file (1-indexed)
- **col** (`int | None`): Column number in file (1-indexed)
- **modified_by** (`str | None`): Function that modified this value
- **extended_by** (`str | None`): Function that extended the provenance history
- **from_choose** (`list`): History of choose operations
- **timestamp** (`str | None`): ISO timestamp of modification

### Example

```python
from provenance import ProvenanceStep

step = ProvenanceStep(
    category="production",
    yaml_file="config.yaml",
    line=10,
    col=5
)

print(f"From {step.yaml_file}:{step.line}:{step.col}")
```

## Provenance

Container for provenance history.

```{eval-rst}
.. autoclass:: provenance.Provenance
   :members:
   :undoc-members:
   :show-inheritance:
```

### Properties

- **current** (`ProvenanceStep`): Most recent provenance step
- **history** (`list[ProvenanceStep]`): Complete provenance history

### Methods

#### `__len__()`

Get number of history steps.

```python
prov = value.provenance
num_steps = len(prov)
```

#### `__iter__()`

Iterate through history.

```python
for step in value.provenance:
    print(f"{step.yaml_file}:{step.line}")
```

#### `__getitem__(index)`

Access specific history step.

```python
first_step = prov[0]
latest_step = prov[-1]
```

#### `append(step)`

Add new provenance step.

```python
from provenance import ProvenanceStep

new_step = ProvenanceStep(category="runtime")
prov.append(new_step)
```

### Example

```python
from provenance import load_yaml

config = load_yaml("config.yaml", category="defaults")
value = config["database"]["host"]

# Access provenance
prov = value.provenance

# Get current step
current = prov.current
print(f"Current: {current.yaml_file}:{current.line}")

# Iterate history
print(f"History ({len(prov)} steps):")
for i, step in enumerate(prov):
    print(f"  [{i}] {step.category}: {step.yaml_file}")

# Access specific step
original = prov[0]
print(f"Original: {original.yaml_file}:{original.line}")
```

## HierarchyManager

Manages hierarchical configuration merging.

```{eval-rst}
.. autoclass:: provenance.HierarchyManager
   :members:
   :undoc-members:
   :show-inheritance:
```

### Constructor

```python
HierarchyManager(levels: list[str] | HierarchyConfig)
```

- **levels**: List of category names in priority order (low to high) or HierarchyConfig object

### Methods

#### `merge(base, override)`

Merge two configurations with hierarchy rules.

```python
hierarchy = HierarchyManager(["defaults", "production"])
result = hierarchy.merge(defaults_config, production_config)
```

#### `merge_all(configs)`

Merge multiple configurations.

```python
hierarchy = HierarchyManager(["defaults", "machines", "user"])
result = hierarchy.merge_all([defaults, machines, user])
```

#### `compare_priority(category1, category2)`

Compare priority of two categories.

```python
priority = hierarchy.compare_priority("defaults", "production")
# Returns: -1 (defaults < production)
```

### Example

```python
from provenance import HierarchyManager, ProvenanceLoader

# Define hierarchy
hierarchy = HierarchyManager([
    "defaults",
    "machines",
    "environment",
    "user",
    "runtime"
])

# Load configs
loader = ProvenanceLoader()
defaults = loader.load("defaults.yaml", category="defaults")
production = loader.load("production.yaml", category="environment")

# Merge with hierarchy
config = hierarchy.merge(defaults, production)

# Check which category won
for key, value in config["database"].items():
    prov = value.provenance.current
    print(f"{key}: {prov.category}")
```

## HierarchyConfig

Configuration for hierarchy levels.

```{eval-rst}
.. autoclass:: provenance.HierarchyConfig
   :members:
   :undoc-members:
   :show-inheritance:
```

### Constructor

```python
HierarchyConfig(levels: list[CategoryLevel])
```

### Example

```python
from provenance import HierarchyConfig, CategoryLevel

config = HierarchyConfig(
    levels=[
        CategoryLevel(name="system", priority=0),
        CategoryLevel(name="defaults", priority=10),
        CategoryLevel(name="user", priority=50),
        CategoryLevel(name="runtime", priority=100),
    ]
)

hierarchy = HierarchyManager(config)
```

## CategoryLevel

Single category level in hierarchy.

```{eval-rst}
.. autoclass:: provenance.CategoryLevel
   :members:
   :undoc-members:
   :show-inheritance:
```

### Attributes

- **name** (`str`): Category name
- **priority** (`int`): Priority value (higher = more important)

### Example

```python
from provenance import CategoryLevel

level = CategoryLevel(name="production", priority=100)
print(f"{level.name}: priority {level.priority}")
```

## See Also

- [Types Module](types.md) - Type wrappers with provenance
- [YAML Module](yaml.md) - YAML loading and dumping
- [Utils Module](utils.md) - Utility functions
