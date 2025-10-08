# Architecture

herrkunft's architecture is built around transparent provenance tracking using modern Python best practices.

## Design Principles

1. **Transparency**: Values behave exactly like their base types
2. **Immutability**: Provenance history is append-only
3. **Type Safety**: Full type hints throughout
4. **Modularity**: Clear separation of concerns
5. **Performance**: Minimal overhead for provenance tracking

## Core Components

```{mermaid}
graph TB
    A[YAML Files] --> B[ProvenanceLoader]
    B --> C[YAML Parser<br/>ruamel.yaml]
    C --> D[Type Factory]
    D --> E[Wrapped Types]
    E --> F[DictWithProvenance]
    E --> G[ListWithProvenance]
    E --> H[Scalar Types]
    F --> I[HierarchyManager]
    G --> I
    H --> I
    I --> J[Merged Config]
    J --> K[ProvenanceDumper]
    K --> L[YAML with Comments]
```

## Module Structure

```
provenance/
├── __init__.py              # Public API
├── version.py               # Version information
├── exceptions.py            # Custom exceptions
├── core/                    # Core provenance classes
│   ├── __init__.py
│   ├── provenance.py        # Provenance, ProvenanceStep
│   ├── hierarchy.py         # HierarchyManager
│   └── decorators.py        # Utility decorators
├── types/                   # Type wrappers
│   ├── __init__.py
│   ├── base.py              # HasProvenance protocol
│   ├── wrappers.py          # Scalar type wrappers
│   ├── mappings.py          # Dict/List wrappers
│   └── factory.py           # TypeWrapperFactory
├── yaml/                    # YAML handling
│   ├── __init__.py
│   ├── loader.py            # ProvenanceLoader
│   ├── dumper.py            # ProvenanceDumper
│   ├── constructors.py      # YAML constructors
│   └── utils.py             # YAML utilities
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── cleaning.py          # Provenance cleaning
│   ├── validation.py        # Validation functions
│   └── serialization.py     # JSON serialization
└── config/                  # Library configuration
    ├── __init__.py
    └── settings.py          # ProvenanceSettings
```

## Data Flow

### Loading YAML

1. **Parse YAML**: ruamel.yaml parses file with position tracking
2. **Create Provenance**: ProvenanceStep created for each value
3. **Wrap Types**: TypeWrapperFactory wraps values with provenance
4. **Build Tree**: Recursive wrapping creates complete tree
5. **Return Config**: DictWithProvenance returned to user

```python
# User code
config = load_yaml("config.yaml", category="defaults")

# Internal flow
1. ProvenanceLoader.load("config.yaml")
2. ruamel.yaml.load() -> raw dict with positions
3. For each value:
   - Create ProvenanceStep(yaml_file, line, col, category)
   - Create Provenance() and append step
   - Wrap value with provenance
4. Return DictWithProvenance
```

### Merging Configurations

1. **Load Configs**: Each loaded with different category
2. **Update Dict**: Standard dict.update() operation
3. **Hierarchy Check**: HierarchyManager compares categories
4. **Preserve Higher**: Higher category values win
5. **Append History**: Provenance history updated

```python
# User code
defaults = load_yaml("defaults.yaml", category="defaults")
production = load_yaml("prod.yaml", category="production")
defaults.update(production)

# Internal flow
1. For each key in production:
   - Get value from defaults (if exists)
   - Compare categories: defaults < production
   - Replace with production value
   - Append provenance step to history
```

### Saving YAML

1. **Extract Values**: Unwrap provenance-wrapped types
2. **Generate Comments**: Format provenance as comments
3. **Preserve Structure**: Maintain YAML structure
4. **Write File**: ruamel.yaml writes with comments

```python
# User code
dump_yaml(config, "output.yaml", include_provenance=True)

# Internal flow
1. ProvenanceDumper.dump(config, "output.yaml")
2. For each value with provenance:
   - Extract provenance.current
   - Format comment string
   - Attach to YAML node
3. ruamel.yaml.dump() with comments
```

## Type System

### Provenance Classes

```python
class ProvenanceStep(BaseModel):
    """Single provenance step."""
    category: Optional[str]
    subcategory: Optional[str]
    yaml_file: Optional[str]
    line: Optional[int]
    col: Optional[int]
    modified_by: Optional[str]
    timestamp: Optional[str]
    # ... other fields

class Provenance:
    """Provenance history container."""
    def __init__(self):
        self._history: List[ProvenanceStep] = []

    @property
    def current(self) -> ProvenanceStep:
        return self._history[-1]

    def append(self, step: ProvenanceStep):
        self._history.append(step)
```

### Type Wrappers

All wrappers inherit from their base type and add provenance:

```python
class StrWithProvenance(str):
    """String with provenance."""
    def __new__(cls, value, provenance):
        instance = super().__new__(cls, value)
        instance._provenance = provenance
        return instance

    @property
    def provenance(self):
        return self._provenance

# Similar for IntWithProvenance, FloatWithProvenance, etc.
```

### HasProvenance Protocol

```python
from typing import Protocol

class HasProvenance(Protocol):
    """Protocol for types with provenance."""
    @property
    def provenance(self) -> Provenance:
        ...
```

## Hierarchy System

### Category Levels

```python
class CategoryLevel(BaseModel):
    name: str
    priority: int

class HierarchyConfig(BaseModel):
    levels: List[CategoryLevel]

class HierarchyManager:
    def __init__(self, levels: List[str] | HierarchyConfig):
        # Convert to HierarchyConfig
        # Build priority map

    def compare_priority(self, cat1: str, cat2: str) -> int:
        # -1 if cat1 < cat2
        #  0 if cat1 == cat2
        #  1 if cat1 > cat2
```

### Merge Algorithm

```python
def merge(base: Dict, override: Dict) -> Dict:
    """Merge with hierarchy rules."""
    result = base.copy()

    for key, override_value in override.items():
        if key not in result:
            # New key, just add
            result[key] = override_value
        else:
            base_value = result[key]

            # Compare categories
            base_cat = base_value.provenance.current.category
            override_cat = override_value.provenance.current.category

            if hierarchy.compare_priority(base_cat, override_cat) < 0:
                # Override has higher priority
                result[key] = override_value

                # Append to history
                if hasattr(base_value, 'provenance'):
                    override_value.provenance.extend(base_value.provenance)

    return result
```

## Performance Considerations

### Memory Overhead

Each value carries:
- Base value (e.g., string, int)
- Provenance object (~200 bytes)
- History list (50-100 bytes per step)

Typical overhead: 250-500 bytes per value

### Optimization Strategies

1. **Lazy History**: Only create full history when accessed
2. **Shared Provenance**: Reuse ProvenanceStep objects
3. **Weak References**: Use weak refs for parent tracking
4. **Copy-on-Write**: Share provenance until modified

### Benchmarks

```python
# Load 1000-key config
# Memory: ~500KB (plain dict: ~100KB)
# Time: ~50ms (plain PyYAML: ~30ms)
# Overhead: 5x memory, 1.7x time
```

## Error Handling

### Exception Hierarchy

```python
class ProvenanceError(Exception):
    """Base exception for provenance errors."""

class LoaderError(ProvenanceError):
    """YAML loading errors."""

class DumperError(ProvenanceError):
    """YAML dumping errors."""

class ValidationError(ProvenanceError):
    """Provenance validation errors."""

class HierarchyError(ProvenanceError):
    """Hierarchy management errors."""
```

### Error Recovery

1. **Strict Mode**: Raise on any error
2. **Lenient Mode**: Log warnings, continue
3. **Fallback**: Return plain types if provenance fails

## Testing Strategy

### Test Levels

1. **Unit Tests**: Individual components
2. **Integration Tests**: Component interaction
3. **End-to-End Tests**: Full workflows
4. **Property Tests**: Type behavior verification

### Coverage

- Core: >95% coverage
- Types: >90% coverage
- YAML: >90% coverage
- Utils: >85% coverage

## Extension Points

### Custom Types

```python
from provenance import HasProvenance, Provenance

class CustomType(HasProvenance):
    def __init__(self, value, provenance: Provenance):
        self.value = value
        self._provenance = provenance

    @property
    def provenance(self):
        return self._provenance
```

### Custom Loaders

```python
from provenance import ProvenanceLoader

class CustomLoader(ProvenanceLoader):
    def load(self, path, **kwargs):
        # Custom loading logic
        data = super().load(path, **kwargs)
        # Post-process
        return data
```

### Custom Hierarchy

```python
from provenance import HierarchyManager, CategoryLevel

custom_hierarchy = HierarchyManager([
    CategoryLevel(name="system", priority=0),
    CategoryLevel(name="app", priority=100),
    CategoryLevel(name="user", priority=200),
])
```

## Future Enhancements

Planned features:

1. **Async Loading**: Async YAML loading
2. **Streaming**: Handle large files efficiently
3. **Compression**: Compress provenance history
4. **Diff Tools**: Compare configurations
5. **Visualization**: Graph provenance trees
6. **Remote Sources**: Load from URLs/databases

## See Also

- [Core Module API](../api/core.md)
- [Types Module API](../api/types.md)
- [YAML Module API](../api/yaml.md)
- [Contributing Guide](../contributing.md)
