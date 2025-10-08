# Hierarchical Configuration

Manage complex configuration hierarchies with automatic conflict resolution based on category priorities.

## Concept

Hierarchical configuration allows you to:
- Define configuration defaults
- Override with machine-specific settings
- Apply user preferences
- Add runtime modifications

All while tracking which file provided each value.

## Hierarchy Levels

Define priority levels from lowest to highest:

```python
from provenance import HierarchyManager

hierarchy = HierarchyManager([
    "defaults",      # Lowest priority
    "machines",
    "environment",
    "user",
    "runtime"        # Highest priority
])
```

## Basic Merging

### Simple Update

```python
from provenance import load_yaml

# Load configs with different categories
defaults = load_yaml("defaults.yaml", category="defaults")
production = load_yaml("production.yaml", category="production")

# Higher category wins
defaults.update(production)

# Check which won
for key, value in defaults["database"].items():
    print(f"{key}: {value.provenance.current.category}")
```

### Hierarchy-Aware Merging

```python
from provenance import HierarchyManager, ProvenanceLoader

loader = ProvenanceLoader()
hierarchy = HierarchyManager(["defaults", "production"])

defaults = loader.load("defaults.yaml", category="defaults")
production = loader.load("production.yaml", category="production")

# Merge respecting hierarchy
config = hierarchy.merge(defaults, production)
```

## Multi-Level Hierarchies

```python
from provenance import ProvenanceLoader, HierarchyManager

# Define 4-level hierarchy
hierarchy = HierarchyManager(["defaults", "machines", "user", "production"])

loader = ProvenanceLoader()

# Load each level
configs = {
    "defaults": loader.load("defaults.yaml", category="defaults"),
    "machines": loader.load("hpc.yaml", category="machines", subcategory="hpc"),
    "user": loader.load("user.yaml", category="user"),
    "production": loader.load("prod.yaml", category="production"),
}

# Merge all
final_config = hierarchy.merge_all(list(configs.values()))

# Inspect sources
for key, value in final_config["database"].items():
    prov = value.provenance.current
    print(f"{key}: {prov.category} ({prov.yaml_file})")
```

## Conflict Resolution

### Automatic Resolution

Higher categories automatically override lower ones:

```yaml
# defaults.yaml
database:
  host: localhost
  port: 5432
  pool_size: 5
```

```yaml
# production.yaml
database:
  host: prod.db.example.com
  pool_size: 100
```

```python
hierarchy = HierarchyManager(["defaults", "production"])

defaults = load_yaml("defaults.yaml", category="defaults")
production = load_yaml("production.yaml", category="production")

config = hierarchy.merge(defaults, production)

# Results:
# - database.host: prod.db.example.com (from production)
# - database.port: 5432 (from defaults, not overridden)
# - database.pool_size: 100 (from production)
```

### Tracking Conflicts

```python
def find_overrides(config):
    """Find values that were overridden."""
    overrides = []

    def search(obj, path=""):
        if hasattr(obj, 'provenance') and len(obj.provenance) > 1:
            history = obj.provenance
            original = history[0]
            current = history[-1]
            if original.category != current.category:
                overrides.append({
                    'path': path,
                    'original_category': original.category,
                    'current_category': current.category,
                    'original_file': original.yaml_file,
                    'current_file': current.yaml_file,
                })

        if isinstance(obj, dict):
            for key, value in obj.items():
                search(value, f"{path}.{key}" if path else key)

    search(config)
    return overrides

# Find all overridden values
overrides = find_overrides(final_config)
for override in overrides:
    print(f"{override['path']}: {override['original_category']} → {override['current_category']}")
```

## Environment-Based Configuration

```python
import os
from provenance import ProvenanceLoader

def load_environment_config():
    loader = ProvenanceLoader()

    # Load base config
    config = loader.load("config/base.yaml", category="defaults")

    # Load environment-specific
    env = os.getenv("ENVIRONMENT", "development")
    env_file = f"config/{env}.yaml"

    if Path(env_file).exists():
        env_config = loader.load(env_file, category="environment", subcategory=env)
        config.update(env_config)

    return config

# Usage
config = load_environment_config()
```

## Machine-Specific Configuration

```python
import socket
from provenance import ProvenanceLoader

def load_with_machine_config():
    loader = ProvenanceLoader()

    # Load defaults
    config = loader.load("defaults.yaml", category="defaults")

    # Load machine-specific if exists
    hostname = socket.gethostname()
    machine_file = f"machines/{hostname}.yaml"

    if Path(machine_file).exists():
        machine_config = loader.load(
            machine_file,
            category="machines",
            subcategory=hostname
        )
        config.update(machine_config)

    return config
```

## User Preferences

```python
from pathlib import Path
from provenance import ProvenanceLoader

def load_with_user_preferences():
    loader = ProvenanceLoader()

    # Load defaults
    config = loader.load("defaults.yaml", category="defaults")

    # Load user preferences from home directory
    user_config_file = Path.home() / ".myapp" / "config.yaml"

    if user_config_file.exists():
        user_config = loader.load(str(user_config_file), category="user")
        config.update(user_config)

    return config
```

## Runtime Modifications

```python
def apply_runtime_config(config, **overrides):
    """Apply runtime overrides to configuration."""
    for key, value in overrides.items():
        if '.' in key:
            # Handle nested keys
            keys = key.split('.')
            target = config
            for k in keys[:-1]:
                target = target[k]
            target[keys[-1]] = value
        else:
            config[key] = value

    return config

# Usage
config = load_yaml("config.yaml", category="defaults")
config = apply_runtime_config(
    config,
    **{
        "database.host": "override.example.com",
        "server.port": 9000,
    }
)

# Check provenance
host_prov = config["database"]["host"].provenance
print(f"History: {len(host_prov)} steps")
```

## Category Configuration

### Custom Hierarchies

```python
from provenance import HierarchyConfig, CategoryLevel

# Define custom hierarchy
hierarchy_config = HierarchyConfig(
    levels=[
        CategoryLevel(name="system", priority=0),
        CategoryLevel(name="defaults", priority=10),
        CategoryLevel(name="machine", priority=20),
        CategoryLevel(name="user", priority=30),
        CategoryLevel(name="runtime", priority=100),
    ]
)

hierarchy = HierarchyManager(config=hierarchy_config)
```

### Dynamic Priorities

```python
# Adjust priorities at runtime
hierarchy.set_priority("user", 50)
hierarchy.set_priority("machine", 40)
```

## Best Practices

### 1. Define Clear Hierarchy

```python
# Clear, documented hierarchy
HIERARCHY_LEVELS = [
    "system",       # System-wide defaults
    "defaults",     # Application defaults
    "machines",     # Machine-specific
    "environment",  # Environment (dev/staging/prod)
    "user",         # User preferences
    "runtime",      # Runtime overrides
]

hierarchy = HierarchyManager(HIERARCHY_LEVELS)
```

### 2. Validate Categories

```python
def validate_category(category, allowed_categories):
    if category not in allowed_categories:
        raise ValueError(f"Invalid category: {category}")

# Usage
ALLOWED = ["defaults", "user", "production"]
validate_category("defaults", ALLOWED)  # OK
validate_category("custom", ALLOWED)    # Raises error
```

### 3. Document Override Rules

```python
def merge_with_documentation(base_config, override_config):
    """
    Merge configurations with override documentation.

    Rules:
    - production overrides user
    - user overrides defaults
    - All overrides are logged
    """
    original = extract_provenance_tree(base_config)
    base_config.update(override_config)
    new = extract_provenance_tree(base_config)

    # Log changes
    for key in base_config:
        if original.get(key) != new.get(key):
            logger.info(f"Overridden: {key}")

    return base_config
```

### 4. Provide Configuration Summary

```python
def configuration_summary(config):
    """Generate summary of configuration sources."""
    summary = {}

    def collect(obj, path=""):
        if hasattr(obj, 'provenance'):
            prov = obj.provenance.current
            category = prov.category
            if category not in summary:
                summary[category] = []
            summary[category].append(path)

        if isinstance(obj, dict):
            for key, value in obj.items():
                collect(value, f"{path}.{key}" if path else key)

    collect(config)

    print("Configuration Sources:")
    for category, keys in sorted(summary.items()):
        print(f"  {category}: {len(keys)} values")
        for key in keys[:3]:  # Show first 3
            print(f"    - {key}")
        if len(keys) > 3:
            print(f"    ... and {len(keys) - 3} more")

    return summary
```

## Next Steps

- Learn about [Saving YAML Files](saving-yaml.md)
- See [Multi-Environment Tutorial](../tutorials/multi-environment.ipynb)
- Check the [API Reference](../api/core.md)
