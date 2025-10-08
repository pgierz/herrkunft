# Examples

This page provides complete, runnable examples demonstrating herrkunft's features.

## Example 1: Basic Provenance Tracking

Track where configuration values come from:

```python
from provenance import load_yaml
from pathlib import Path

# Create a sample config file
config_content = """
application:
  name: MyApp
  version: 1.0.0

database:
  host: localhost
  port: 5432
  credentials:
    username: dbuser
    password: secret123
"""

Path("app_config.yaml").write_text(config_content)

# Load with provenance
config = load_yaml("app_config.yaml", category="application")

# Access values
db_host = config["database"]["host"]
print(f"Database host: {db_host}")

# Inspect provenance
prov = db_host.provenance.current
print(f"\nProvenance Information:")
print(f"  File: {prov.yaml_file}")
print(f"  Line: {prov.line}, Column: {prov.col}")
print(f"  Category: {prov.category}")

# Access nested values
username = config["database"]["credentials"]["username"]
print(f"\nUsername: {username}")
print(f"  From: {username.provenance.current.yaml_file}:{username.provenance.current.line}")
```

## Example 2: Hierarchical Configuration

Override settings based on priority levels:

::::{tab-set}

:::{tab-item} Defaults YAML
```yaml
database:
  host: localhost
  port: 5432
  pool_size: 5
  timeout: 30

logging:
  level: INFO
  format: standard
```
:::

:::{tab-item} Production YAML
```yaml
database:
  host: prod.db.example.com
  port: 5433
  pool_size: 50

logging:
  level: ERROR
```
:::

:::{tab-item} Merged Result
```yaml
database:
  # from production (overrides)
  host: prod.db.example.com
  # from production (overrides)
  port: 5433
  # from production (overrides)
  pool_size: 50
  # from defaults (preserved)
  timeout: 30

logging:
  # from production (overrides)
  level: ERROR
  # from defaults (preserved)
  format: standard
```
:::

::::

```python
from provenance import load_yaml, dump_yaml
from pathlib import Path

# Create default configuration
defaults = """
database:
  host: localhost
  port: 5432
  pool_size: 5
  timeout: 30

logging:
  level: INFO
  format: standard
"""

# Create production overrides
production = """
database:
  host: prod.db.example.com
  port: 5433
  pool_size: 50

logging:
  level: ERROR
"""

Path("defaults.yaml").write_text(defaults)
Path("production.yaml").write_text(production)

# Load both configurations
config_defaults = load_yaml("defaults.yaml", category="defaults")
config_prod = load_yaml("production.yaml", category="production")

# Merge with production overriding defaults
final_config = config_defaults.copy()
final_config.update(config_prod)

# Inspect where each value came from
print("Final Configuration Sources:")
print(f"  database.host: {final_config['database']['host'].provenance.current.category}")
print(f"  database.port: {final_config['database']['port'].provenance.current.category}")
print(f"  database.pool_size: {final_config['database']['pool_size'].provenance.current.category}")
print(f"  database.timeout: {final_config['database']['timeout'].provenance.current.category}")
print(f"  logging.level: {final_config['logging']['level'].provenance.current.category}")
print(f"  logging.format: {final_config['logging']['format'].provenance.current.category}")

# Save with provenance comments
dump_yaml(final_config, "final_config.yaml", include_provenance=True)
print("\nSaved to final_config.yaml with provenance comments")
```

## Example 3: Tracking Modification History

See how values change over time:

```python
from provenance import load_yaml

# Load initial config
config = load_yaml("defaults.yaml", category="defaults")

# Make several modifications
print("Initial value:", config["database"]["host"])
print("Initial history length:", len(config["database"]["host"].provenance))

config["database"]["host"] = "staging.db.example.com"
print("\nAfter 1st change:", config["database"]["host"])
print("History length:", len(config["database"]["host"].provenance))

config["database"]["host"] = "production.db.example.com"
print("\nAfter 2nd change:", config["database"]["host"])
print("History length:", len(config["database"]["host"].provenance))

# Inspect full history
print("\nComplete History:")
for i, step in enumerate(config["database"]["host"].provenance):
    source = step.yaml_file or "runtime modification"
    print(f"  [{i}] {source} (category: {step.category})")
```

## Example 4: Scientific Workflow Configuration

Track simulation parameters for reproducibility:

```python
from provenance import load_yaml, extract_provenance_tree, dump_yaml
from pathlib import Path
import json

# Create simulation config
sim_config = """
simulation:
  model: climate_v2
  resolution: 1km
  timestep: 3600

parameters:
  temperature: 273.15
  pressure: 101325
  wind_speed: 5.0

output:
  directory: /data/simulations
  format: netcdf
  compression: gzip
"""

Path("simulation.yaml").write_text(sim_config)

# Load configuration
config = load_yaml("simulation.yaml", category="simulation", subcategory="experiment_001")

# Simulate running a model (mock)
def run_simulation(config):
    return {
        "status": "success",
        "runtime": 3600,
        "output_file": f"{config['output']['directory']}/result.nc"
    }

results = run_simulation(config)

# Extract provenance for reproducibility
provenance_tree = extract_provenance_tree(config)

# Save results with full provenance metadata
output_metadata = {
    "experiment": "experiment_001",
    "results": results,
    "configuration": {
        "simulation": dict(config["simulation"]),
        "parameters": dict(config["parameters"]),
        "output": dict(config["output"])
    },
    "provenance": provenance_tree
}

with open("experiment_001_metadata.json", "w") as f:
    json.dump(output_metadata, f, indent=2, default=str)

print("Simulation complete!")
print(f"Results saved with full provenance to experiment_001_metadata.json")
print(f"\nConfiguration sources:")
for key in config["parameters"]:
    prov = config["parameters"][key].provenance.current
    print(f"  {key}: {prov.yaml_file}:{prov.line}")
```

## Example 5: Multi-Environment Deployment

Manage configurations across different environments:

```python
from provenance import ProvenanceLoader, dump_yaml
from pathlib import Path
import os

# Create environment-specific configs
base_config = """
app:
  name: MyService
  version: 1.0.0

database:
  pool_size: 5
  timeout: 30
"""

dev_config = """
app:
  debug: true

database:
  host: localhost
  port: 5432
"""

staging_config = """
app:
  debug: false

database:
  host: staging.db.internal
  port: 5433
  pool_size: 20
"""

prod_config = """
app:
  debug: false

database:
  host: prod.db.internal
  port: 5433
  pool_size: 100
  ssl_mode: require
"""

Path("base.yaml").write_text(base_config)
Path("dev.yaml").write_text(dev_config)
Path("staging.yaml").write_text(staging_config)
Path("prod.yaml").write_text(prod_config)

# Load configuration based on environment
def load_environment_config(environment):
    loader = ProvenanceLoader()

    # Always start with base
    config = loader.load("base.yaml", category="base")

    # Load environment-specific
    env_config = loader.load(f"{environment}.yaml", category="environment", subcategory=environment)

    # Merge
    config.update(env_config)

    return config

# Example: Load staging configuration
staging_cfg = load_environment_config("staging")

print("Staging Configuration:")
print(f"  App Name: {staging_cfg['app']['name']}")
print(f"  Debug Mode: {staging_cfg['app']['debug']}")
print(f"  Database Host: {staging_cfg['database']['host']}")
print(f"  Pool Size: {staging_cfg['database']['pool_size']}")

print("\nConfiguration Sources:")
for key, value in staging_cfg['database'].items():
    prov = value.provenance.current
    print(f"  database.{key}: from {prov.category}/{prov.subcategory}")

# Save environment-specific config with full provenance
dump_yaml(staging_cfg, "deployed_staging.yaml", include_provenance=True)
```

## Example 6: Configuration Validation and Auditing

Validate configuration sources for security:

```python
from provenance import load_yaml, extract_provenance_tree

# Create configs with mixed sources
user_config = """
api:
  endpoint: https://api.example.com
  timeout: 30

security:
  api_key: user-provided-key
"""

system_config = """
security:
  ssl_verify: true
  allowed_hosts:
    - example.com
    - api.example.com
"""

Path("user.yaml").write_text(user_config)
Path("system.yaml").write_text(system_config)

# Load both
user_cfg = load_yaml("user.yaml", category="user")
system_cfg = load_yaml("system.yaml", category="system")

# Merge
config = user_cfg.copy()
config.update(system_cfg)

# Audit: Ensure security settings come from system
def audit_security_config(config):
    issues = []

    # Check security settings
    for key, value in config.get('security', {}).items():
        prov = value.provenance.current
        if prov.category != 'system':
            issues.append(f"Security setting '{key}' from untrusted source: {prov.category}")

    return issues

issues = audit_security_config(config)

if issues:
    print("Security Audit FAILED:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Security Audit PASSED: All security settings from trusted sources")

# Show provenance tree
prov_tree = extract_provenance_tree(config)
print("\nComplete Provenance Tree:")
import json
print(json.dumps(prov_tree, indent=2, default=str))
```

## Example 7: Cleaning Provenance for Export

Remove provenance wrappers for external systems:

```python
from provenance import load_yaml, clean_provenance, dump_yaml, DictWithProvenance

# Load config with provenance
config = load_yaml("app_config.yaml", category="app")

print("Original type:", type(config))
print("Has provenance:", isinstance(config, DictWithProvenance))

# Clean provenance
clean_config = clean_provenance(config)

print("\nCleaned type:", type(clean_config))
print("Has provenance:", isinstance(clean_config, DictWithProvenance))

# Verify it's plain Python types
print("\nType verification:")
print(f"  config type: {type(clean_config)}")
print(f"  database type: {type(clean_config['database'])}")
print(f"  host type: {type(clean_config['database']['host'])}")

# Can now use with external libraries that don't support custom types
import json

# This works because it's plain Python types
json_output = json.dumps(clean_config, indent=2)
print(f"\nJSON output:\n{json_output}")

# Save clean version
dump_yaml(clean_config, "clean_export.yaml", include_provenance=False, clean=True)
print("\nSaved clean version to clean_export.yaml")
```

## Example 8: Working with Lists

Track provenance for list items:

```python
from provenance import load_yaml

# Create config with lists
list_config = """
servers:
  - name: web-01
    host: 192.168.1.10
    port: 8080
  - name: web-02
    host: 192.168.1.11
    port: 8080
  - name: db-01
    host: 192.168.1.20
    port: 5432

features:
  - caching
  - compression
  - ssl
"""

Path("servers.yaml").write_text(list_config)

# Load configuration
config = load_yaml("servers.yaml", category="infrastructure")

# Access list items
print("Servers:")
for server in config["servers"]:
    name = server["name"]
    prov = name.provenance.current
    print(f"  {name}: {prov.yaml_file}:{prov.line}")

print("\nFeatures:")
for feature in config["features"]:
    prov = feature.provenance.current
    print(f"  {feature}: line {prov.line}")

# Modify list
config["servers"].append({
    "name": "cache-01",
    "host": "192.168.1.30",
    "port": 6379
})

print("\nAfter adding server:")
new_server = config["servers"][-1]
print(f"  New server: {new_server['name']}")
print(f"  Provenance: {new_server['name'].provenance.current.modified_by or 'runtime'}")
```

## Running the Examples

All examples above are complete and can be run directly. To try them:

1. Create a new Python file (e.g., `example.py`)
2. Copy any example code
3. Run with: `python example.py`

Or try them in an interactive Python session:

```python
from provenance import load_yaml
# ... paste example code
```

## Next Steps

- Work through the [Basic Usage Tutorial](../tutorials/basic-usage.ipynb)
- Read the [User Guide](../user-guide/loading-yaml.md)
- Explore the [API Reference](../api/core.md)
