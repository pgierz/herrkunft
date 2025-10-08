# Multi-Environment Configuration Tutorial

Learn how to manage configurations across development, staging, and production environments with clear provenance tracking.

## Setup

```python
from provenance import ProvenanceLoader, HierarchyManager, dump_yaml
from pathlib import Path
import tempfile
import os

tmpdir = Path(tempfile.mkdtemp())
configs_dir = tmpdir / "configs"
configs_dir.mkdir()
```

## Step 1: Create Base Configuration

```python
# Base configuration (shared across all environments)
base_config = """
application:
  name: MyWebApp
  version: 1.0.0

database:
  driver: postgresql
  pool_size: 5
  timeout: 30
  ssl_mode: prefer

api:
  rate_limit: 100
  timeout: 30

logging:
  level: INFO
  format: json
  destination: stdout

features:
  caching: true
  analytics: false
  profiling: false
"""

base_file = configs_dir / "base.yaml"
base_file.write_text(base_config)

print("Created base configuration")
```

## Step 2: Create Environment Configurations

```python
# Development environment
dev_config = """
application:
  debug: true

database:
  host: localhost
  port: 5432
  name: myapp_dev
  username: dev_user
  password: dev_password

api:
  host: localhost
  port: 8000

logging:
  level: DEBUG

features:
  profiling: true
"""

dev_file = configs_dir / "development.yaml"
dev_file.write_text(dev_config)

# Staging environment
staging_config = """
application:
  debug: false

database:
  host: staging.db.internal
  port: 5432
  name: myapp_staging
  pool_size: 20

api:
  host: staging.api.internal
  port: 8080
  rate_limit: 500

logging:
  level: INFO
  destination: file
  file_path: /var/log/myapp/staging.log

features:
  analytics: true
"""

staging_file = configs_dir / "staging.yaml"
staging_file.write_text(staging_config)

# Production environment
production_config = """
application:
  debug: false

database:
  host: prod.db.example.com
  port: 5433
  name: myapp_production
  pool_size: 100
  ssl_mode: require

api:
  host: api.example.com
  port: 443
  rate_limit: 1000
  ssl: true

logging:
  level: WARNING
  destination: syslog
  syslog_address: /dev/log

features:
  analytics: true
  caching: true
"""

prod_file = configs_dir / "production.yaml"
prod_file.write_text(production_config)

print("Created environment configurations:")
print(f"  - {dev_file.name}")
print(f"  - {staging_file.name}")
print(f"  - {prod_file.name}")
```

## Step 3: Create Secrets Configuration

```python
# Secrets (would normally be in a secure vault)
secrets_dev = """
database:
  password: dev_secret_123

api:
  api_key: dev_key_xyz
"""

secrets_staging = """
database:
  password: staging_secret_456

api:
  api_key: staging_key_abc
"""

secrets_prod = """
database:
  password: prod_secret_789

api:
  api_key: prod_key_def
"""

secrets_dir = tmpdir / "secrets"
secrets_dir.mkdir()

(secrets_dir / "dev.yaml").write_text(secrets_dev)
(secrets_dir / "staging.yaml").write_text(secrets_staging)
(secrets_dir / "prod.yaml").write_text(secrets_prod)

print("\nCreated secrets configurations")
```

## Step 4: Load Configuration for Environment

```python
def load_config_for_environment(environment: str):
    """Load configuration for specified environment."""

    # Define hierarchy
    hierarchy = HierarchyManager([
        "base",
        "environment",
        "secrets",
        "runtime"
    ])

    loader = ProvenanceLoader()

    # Load base config
    config = loader.load(str(base_file), category="base")

    # Load environment config
    env_file = configs_dir / f"{environment}.yaml"
    if env_file.exists():
        env_config = loader.load(
            str(env_file),
            category="environment",
            subcategory=environment
        )
        config.update(env_config)

    # Load secrets
    secret_file = secrets_dir / f"{environment.split('_')[0]}.yaml"
    if secret_file.exists():
        secrets = loader.load(
            str(secret_file),
            category="secrets",
            subcategory=environment
        )
        config.update(secrets)

    return config

# Load development config
dev_config = load_config_for_environment("development")

print("\nDevelopment configuration loaded:")
print(f"  Database: {dev_config['database']['host']}:{dev_config['database']['port']}")
print(f"  API: {dev_config['api']['host']}:{dev_config['api']['port']}")
print(f"  Debug: {dev_config['application']['debug']}")
```

## Step 5: Inspect Configuration Sources

```python
from provenance import extract_provenance_tree

# Extract provenance
prov_tree = extract_provenance_tree(dev_config)

# Show where each database setting came from
print("\nDatabase configuration sources:")
for key, prov in prov_tree["database"].items():
    category = prov['category']
    subcategory = prov.get('subcategory', '')
    file_name = Path(prov['yaml_file']).name if prov.get('yaml_file') else 'runtime'

    source = f"{category}/{subcategory}".rstrip('/') if subcategory else category
    print(f"  {key}: {source} ({file_name})")
```

## Step 6: Environment-Based Loading

```python
def load_current_environment():
    """Load config based on ENVIRONMENT variable."""

    environment = os.getenv("ENVIRONMENT", "development")
    config = load_config_for_environment(environment)

    print(f"\nLoaded configuration for: {environment}")
    return config, environment

# Simulate different environments
os.environ["ENVIRONMENT"] = "staging"
staging_config, env = load_current_environment()

print(f"  Database host: {staging_config['database']['host']}")
print(f"  Pool size: {staging_config['database']['pool_size']}")
print(f"  Log level: {staging_config['logging']['level']}")
```

## Step 7: Apply Runtime Overrides

```python
def apply_runtime_overrides(config, **overrides):
    """Apply command-line or runtime overrides."""

    for key, value in overrides.items():
        keys = key.split('.')
        target = config

        # Navigate to parent
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        # Set value
        target[keys[-1]] = value

    return config

# Apply runtime overrides (e.g., from command line args)
runtime_overrides = {
    "database.pool_size": 50,
    "api.rate_limit": 750,
    "logging.level": "DEBUG"
}

staging_config = apply_runtime_overrides(staging_config, **runtime_overrides)

print("\nApplied runtime overrides:")
for key, value in runtime_overrides.items():
    print(f"  {key} = {value}")

# Check provenance
for key in runtime_overrides:
    keys = key.split('.')
    val = staging_config
    for k in keys:
        val = val[k]

    prov = val.provenance
    print(f"\n  {key}: {len(prov)} history steps")
    for i, step in enumerate(prov):
        source = step.yaml_file or "runtime"
        print(f"    [{i}] {step.category}: {Path(source).name if step.yaml_file else source}")
```

## Step 8: Configuration Validation

```python
def validate_environment_config(config, environment):
    """Validate configuration for environment."""

    issues = []

    # Check production requirements
    if environment == "production":
        # SSL must be required for production
        if config["database"].get("ssl_mode") != "require":
            issues.append("Production database must use SSL")

        # Debug must be off
        if config["application"].get("debug", False):
            issues.append("Debug mode must be off in production")

        # Logging should not be DEBUG
        if config["logging"]["level"] == "DEBUG":
            issues.append("Production logging should not be DEBUG")

    # Check secrets are from correct category
    if "password" in config["database"]:
        prov = config["database"]["password"].provenance.current
        if prov.category != "secrets":
            issues.append(f"Database password from '{prov.category}', should be 'secrets'")

    return issues

# Validate staging
issues = validate_environment_config(staging_config, "staging")
if issues:
    print("\nValidation issues:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\nConfiguration validation passed")
```

## Step 9: Save Environment Configs

```python
# Save final configurations with provenance
output_dir = tmpdir / "deployed"
output_dir.mkdir()

for env_name in ["development", "staging", "production"]:
    os.environ["ENVIRONMENT"] = env_name
    config, _ = load_current_environment()

    output_file = output_dir / f"{env_name}_config.yaml"
    dump_yaml(config, str(output_file), include_provenance=True)

    print(f"Saved: {output_file.name}")

# Show sample output
print(f"\nSample output from staging_config.yaml:")
sample_file = output_dir / "staging_config.yaml"
lines = sample_file.read_text().split('\n')
for line in lines[10:20]:
    print(f"  {line}")
```

## Step 10: Generate Deployment Report

```python
def generate_deployment_report(config, environment):
    """Generate deployment summary."""

    prov_tree = extract_provenance_tree(config)

    # Count sources
    sources = {}
    def count_sources(tree):
        for key, value in tree.items():
            if isinstance(value, dict) and 'category' in value:
                category = value['category']
                sources[category] = sources.get(category, 0) + 1
            elif isinstance(value, dict):
                count_sources(value)

    count_sources(prov_tree)

    report = {
        "environment": environment,
        "sources": sources,
        "critical_settings": {
            "database_host": config["database"]["host"],
            "database_ssl": config["database"].get("ssl_mode", "none"),
            "api_host": config["api"]["host"],
            "debug_mode": config["application"].get("debug", False),
            "log_level": config["logging"]["level"],
        }
    }

    return report

# Generate reports
for env_name in ["development", "staging", "production"]:
    os.environ["ENVIRONMENT"] = env_name
    config, _ = load_current_environment()

    report = generate_deployment_report(config, env_name)

    print(f"\nDeployment Report: {env_name}")
    print(f"  Configuration sources:")
    for source, count in sorted(report["sources"].items()):
        print(f"    {source}: {count} values")
    print(f"  Critical settings:")
    for key, value in report["critical_settings"].items():
        print(f"    {key}: {value}")
```

## Cleanup

```python
import shutil
shutil.rmtree(tmpdir)
print("\nCleaned up temporary files")
```

## Summary

This tutorial covered:

1. Creating layered configurations (base → environment → secrets)
2. Loading configurations based on environment variables
3. Tracking which file provided each setting
4. Applying runtime overrides with provenance
5. Validating environment-specific requirements
6. Saving deployment-ready configurations
7. Generating deployment reports

## Best Practices

1. **Separate concerns**: Keep base, environment, and secrets separate
2. **Use hierarchy**: Define clear priority levels
3. **Validate environments**: Enforce environment-specific rules
4. **Track secrets source**: Ensure sensitive data comes from secrets
5. **Document overrides**: Track runtime modifications
6. **Generate reports**: Audit configuration before deployment

## Next Steps

- Review the [User Guide](../user-guide/hierarchical-config.md)
- Explore the [API Reference](../api/core.md)
- Try the [Scientific Workflows Tutorial](scientific-workflows.md)
