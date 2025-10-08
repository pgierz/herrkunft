# Saving YAML Files

Learn how to save configurations with provenance metadata preserved as comments.

## Basic Saving

```python
from provenance import load_yaml, dump_yaml

# Load and modify config
config = load_yaml("config.yaml", category="defaults")
config["database"]["host"] = "production.example.com"

# Save with provenance
dump_yaml(config, "output.yaml", include_provenance=True)
```

## Provenance Comments

### With Provenance

```python
dump_yaml(config, "output.yaml", include_provenance=True)
```

::::{tab-set}

:::{tab-item} YAML with Provenance
Output includes provenance as comments:

```yaml
database:
  # modified at runtime
  host: production.example.com
  # from: config.yaml | line: 3 | col: 8 | category: defaults
  port: 5432
  # from: config.yaml | line: 4 | col: 8 | category: defaults
  name: myapp
```
:::

:::{tab-item} Clean YAML
Same content without provenance:

```yaml
database:
  host: production.example.com
  port: 5432
  name: myapp
```
:::

:::{tab-item} JSON Format
```json
{
  "database": {
    "host": "production.example.com",
    "port": 5432,
    "name": "myapp"
  }
}
```
:::

::::

### Without Provenance

```python
dump_yaml(config, "output.yaml", include_provenance=False, clean=True)
```

Output is clean YAML (no provenance comments).

## The ProvenanceDumper Class

For more control:

```python
from provenance import ProvenanceDumper

dumper = ProvenanceDumper(
    include_provenance_comments=True,
    comment_format="{file}:{line}:{col} ({category})",
)

dumper.dump(config, "output.yaml")
```

### Dumper Parameters

```python
ProvenanceDumper(
    include_provenance_comments: bool = True,
    comment_format: str = "{file}:{line}:{col} ({category})",
    encoding: str = "utf-8",
    width: int = 80,
    indent: int = 2,
)
```

## Comment Formats

### Custom Format

```python
dumper = ProvenanceDumper(
    comment_format="from {category}: {file} line {line}"
)
dumper.dump(config, "output.yaml")
```

::::{tab-set}

:::{tab-item} Custom Format YAML
Output with custom comment format:

```yaml
database:
  # from defaults: config.yaml line 2
  host: localhost
  # from defaults: config.yaml line 3
  port: 5432
```
:::

:::{tab-item} Default Format YAML
Default provenance format:

```yaml
database:
  # from: config.yaml | line: 2 | col: 8 | category: defaults
  host: localhost
  # from: config.yaml | line: 3 | col: 8 | category: defaults
  port: 5432
```
:::

:::{tab-item} Clean YAML
Without provenance:

```yaml
database:
  host: localhost
  port: 5432
```
:::

::::

### Multiple Formats

```python
# Include full history
dumper = ProvenanceDumper(
    comment_format="{file}:{line} | modified: {timestamp}"
)
```

### Conditional Comments

```python
def custom_comment_format(prov_step):
    if prov_step.yaml_file:
        return f"{prov_step.yaml_file}:{prov_step.line}"
    else:
        return f"runtime ({prov_step.timestamp})"

# Apply manually when constructing comments
```

## Cleaning Provenance

### Full Clean

Remove all provenance wrappers:

```python
from provenance import clean_provenance, dump_yaml

config = load_yaml("config.yaml")

# Clean provenance
clean_config = clean_provenance(config)

# Save without provenance
dump_yaml(clean_config, "clean.yaml", include_provenance=False, clean=True)
```

### Partial Clean

Clean specific parts:

```python
from provenance import strip_provenance

# Clean only sensitive data
config["database"]["password"] = strip_provenance(
    config["database"]["password"]
)

# Save with provenance for everything except password
dump_yaml(config, "output.yaml", include_provenance=True)
```

## Formatting Options

### Indentation

```python
dumper = ProvenanceDumper(indent=4)
dumper.dump(config, "output.yaml")
```

Output:

```yaml
database:
    host: localhost
    port: 5432
```

### Line Width

```python
dumper = ProvenanceDumper(width=120)
dumper.dump(config, "output.yaml")
```

### Encoding

```python
dumper = ProvenanceDumper(encoding="utf-8")
dumper.dump(config, "output.yaml")
```

## Preserving Structure

### Anchors and Aliases

Provenance is preserved with YAML anchors:

```python
config = {
    "defaults": {"timeout": 30, "retries": 3},
    "service1": {"timeout": 30, "retries": 3},
}

dump_yaml(config, "output.yaml", include_provenance=True)
```

### Multi-line Strings

```python
config = {
    "description": """
    This is a multi-line
    description that should
    be preserved.
    """
}

dump_yaml(config, "output.yaml", include_provenance=True)
```

## Selective Saving

### Save Specific Sections

```python
# Save only database config
dump_yaml(config["database"], "database.yaml", include_provenance=True)

# Save only modified values
modified = find_modified_values(config)
modified_config = {path: value for path, value, _ in modified}
dump_yaml(modified_config, "changes.yaml", include_provenance=True)
```

## Round-Trip Compatibility

Configurations can be saved and reloaded:

```python
# Load
config = load_yaml("config.yaml", category="defaults")

# Modify
config["new_key"] = "new_value"

# Save with provenance
dump_yaml(config, "modified.yaml", include_provenance=True)

# Reload
reloaded = load_yaml("modified.yaml", category="reloaded")

# Verify
assert reloaded["new_key"] == "new_value"
assert reloaded["new_key"].provenance.current.yaml_file == "modified.yaml"
```

## Error Handling

```python
from provenance import DumperError

try:
    dump_yaml(config, "/invalid/path/output.yaml")
except DumperError as e:
    print(f"Failed to save: {e}")
```

## Best Practices

### 1. Always Include Provenance for Auditing

```python
# For production configs
dump_yaml(config, "production.yaml", include_provenance=True)
```

### 2. Clean for External Use

```python
# For sharing with external systems
clean_config = clean_provenance(config)
dump_yaml(clean_config, "export.yaml", include_provenance=False, clean=True)
```

### 3. Use Consistent Formatting

```python
# Define standard dumper
standard_dumper = ProvenanceDumper(
    include_provenance_comments=True,
    indent=2,
    width=100,
)

# Use everywhere
standard_dumper.dump(config1, "config1.yaml")
standard_dumper.dump(config2, "config2.yaml")
```

### 4. Backup Before Overwriting

```python
from pathlib import Path
import shutil

def safe_dump(config, path, **kwargs):
    path = Path(path)
    if path.exists():
        backup = path.with_suffix(path.suffix + '.bak')
        shutil.copy(path, backup)

    dump_yaml(config, str(path), **kwargs)
```

### 5. Validate After Saving

```python
def save_and_validate(config, path):
    dump_yaml(config, path, include_provenance=True)

    # Reload and verify
    reloaded = load_yaml(path)

    # Compare keys
    if set(config.keys()) != set(reloaded.keys()):
        raise ValueError("Configuration keys don't match after save/load")

    return reloaded
```

## Next Steps

- Review [Loading YAML Files](loading-yaml.md)
- See [Tracking Provenance](tracking-provenance.md)
- Try the [Tutorials](../tutorials/basic-usage.ipynb)
