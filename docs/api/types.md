# Types Module API

Type wrappers that add provenance tracking to Python built-in types.

## DictWithProvenance

Dictionary with provenance tracking.

```{eval-rst}
.. autoclass:: provenance.DictWithProvenance
   :members:
   :undoc-members:
   :show-inheritance:
```

Behaves exactly like a `dict` but tracks provenance for all operations.

### Example

```python
from provenance import load_yaml, DictWithProvenance

config = load_yaml("config.yaml")
assert isinstance(config, DictWithProvenance)

# Use like normal dict
config["new_key"] = "value"
keys = list(config.keys())
value = config.get("database", {})

# Access provenance
prov = config.provenance.current
print(f"Dict from: {prov.yaml_file}:{prov.line}")
```

## ListWithProvenance

List with provenance tracking.

```{eval-rst}
.. autoclass:: provenance.ListWithProvenance
   :members:
   :undoc-members:
   :show-inheritance:
```

Behaves exactly like a `list` but tracks provenance.

### Example

```python
from provenance import load_yaml

config = load_yaml("config.yaml")
servers = config["servers"]

# Use like normal list
servers.append({"name": "new-server"})
first = servers[0]
length = len(servers)

# Access provenance
prov = servers.provenance.current
print(f"List from: {prov.yaml_file}:{prov.line}")
```

## Scalar Types

### StrWithProvenance

String with provenance tracking.

```python
from provenance import load_yaml

config = load_yaml("config.yaml")
host = config["database"]["host"]

# Behaves like str
upper = host.upper()
contains = "localhost" in host
length = len(host)

# Has provenance
prov = host.provenance.current
```

### IntWithProvenance

Integer with provenance tracking.

```python
port = config["database"]["port"]

# Behaves like int
result = port + 100
is_valid = port > 1024

# Has provenance
prov = port.provenance.current
```

### FloatWithProvenance

Float with provenance tracking.

```python
timeout = config["server"]["timeout"]

# Behaves like float
doubled = timeout * 2
rounded = round(timeout, 2)

# Has provenance
prov = timeout.provenance.current
```

### BoolWithProvenance

Boolean with provenance tracking.

```python
debug = config["app"]["debug"]

# Behaves like bool
if debug:
    print("Debug mode")

# Has provenance
prov = debug.provenance.current
```

## HasProvenance

Base protocol for types with provenance.

```{eval-rst}
.. autoclass:: provenance.HasProvenance
   :members:
   :undoc-members:
   :show-inheritance:
```

### Example

```python
from provenance import HasProvenance

def process_with_provenance(value):
    if isinstance(value, HasProvenance):
        prov = value.provenance.current
        print(f"Processing value from {prov.yaml_file}")
    # Process value...
```

## ProvenanceWrapperFactory

Factory for creating provenance-wrapped types.

```{eval-rst}
.. autoclass:: provenance.ProvenanceWrapperFactory
   :members:
   :undoc-members:
   :show-inheritance:
```

### Methods

#### `wrap(value, provenance)`

Wrap a value with provenance tracking.

```python
from provenance import ProvenanceWrapperFactory, Provenance, ProvenanceStep

factory = ProvenanceWrapperFactory()

step = ProvenanceStep(category="test")
prov = Provenance()
prov.append(step)

wrapped = factory.wrap("hello", prov)
assert hasattr(wrapped, 'provenance')
```

#### `wrap_dict(data, provenance)`

Wrap dictionary recursively.

```python
data = {"key": "value", "nested": {"sub": "value"}}
wrapped = factory.wrap_dict(data, provenance)

assert isinstance(wrapped, DictWithProvenance)
assert hasattr(wrapped["key"], 'provenance')
assert hasattr(wrapped["nested"]["sub"], 'provenance')
```

#### `wrap_list(items, provenance)`

Wrap list recursively.

```python
items = ["item1", "item2", {"key": "value"}]
wrapped = factory.wrap_list(items, provenance)

assert isinstance(wrapped, ListWithProvenance)
assert hasattr(wrapped[0], 'provenance')
assert hasattr(wrapped[2]["key"], 'provenance')
```

### Example

```python
from provenance import (
    ProvenanceWrapperFactory,
    Provenance,
    ProvenanceStep
)

# Create factory
factory = ProvenanceWrapperFactory()

# Create provenance
step = ProvenanceStep(
    category="runtime",
    yaml_file=None,
    line=None,
    col=None
)
prov = Provenance()
prov.append(step)

# Wrap values
wrapped_str = factory.wrap("test", prov)
wrapped_int = factory.wrap(42, prov)
wrapped_dict = factory.wrap_dict({"key": "value"}, prov)

# All have provenance
assert wrapped_str.provenance.current.category == "runtime"
assert wrapped_int.provenance.current.category == "runtime"
assert wrapped_dict.provenance.current.category == "runtime"
```

## Type Preservation

All wrapped types preserve their base behavior:

```python
from provenance import load_yaml

config = load_yaml("config.yaml")

# Type checking
assert isinstance(config["database"]["host"], str)
assert isinstance(config["database"]["port"], int)
assert isinstance(config["app"]["debug"], bool)

# Operations work normally
host = config["database"]["host"]
assert host.upper() == host.value.upper()

port = config["database"]["port"]
assert port + 10 == config["database"]["port"] + 10

# But also have provenance
assert hasattr(host, 'provenance')
assert hasattr(port, 'provenance')
```

## See Also

- [Core Module](core.md) - Provenance classes
- [YAML Module](yaml.md) - YAML loading and dumping
- [User Guide: Loading YAML](../user-guide/loading-yaml.md)
