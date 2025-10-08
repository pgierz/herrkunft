# Scientific Workflows Tutorial

Learn how to use herrkunft to track configuration provenance in scientific computing workflows for reproducibility.

## Scenario

You're running climate model simulations and need to track:
- Which configuration file specified each parameter
- When parameters were modified
- The complete history of configuration changes

This ensures reproducibility and helps debug failed simulations.

## Setup

```python
from provenance import load_yaml, dump_yaml, extract_provenance_tree, to_json_file
from pathlib import Path
import tempfile
import json
from datetime import datetime

tmpdir = Path(tempfile.mkdtemp())
```

## Step 1: Create Simulation Configuration

```python
# Base model configuration
base_config = """
model:
  name: climate_model_v2
  version: 2.0.1
  resolution: 1km

physics:
  radiation:
    scheme: rrtmg
    bands: 16
  convection:
    scheme: zhang_mcfarlane
    timestep: 1800

initial_conditions:
  temperature: 273.15
  pressure: 101325
  wind_speed: 0.0

output:
  directory: /data/simulations
  format: netcdf
  frequency: 3600
  compression: gzip
"""

base_file = tmpdir / "model_base.yaml"
base_file.write_text(base_config)

# Load base configuration
config = load_yaml(str(base_file), category="model_defaults")

print("Base model configuration loaded")
print(f"  Model: {config['model']['name']} v{config['model']['version']}")
print(f"  Resolution: {config['model']['resolution']}")
```

## Step 2: Add Experiment-Specific Settings

```python
# Experiment configuration
experiment_config = """
experiment:
  id: exp_001
  name: sensitivity_test_co2
  description: Test CO2 sensitivity

physics:
  radiation:
    co2_concentration: 400  # ppm
  convection:
    timestep: 900  # Override for stability

initial_conditions:
  temperature: 288.15  # Warmer start
"""

exp_file = tmpdir / "experiment_001.yaml"
exp_file.write_text(experiment_config)

# Load and merge
exp_config = load_yaml(str(exp_file), category="experiment", subcategory="exp_001")
config.update(exp_config)

print("\nExperiment configuration merged")
print(f"  Experiment: {config['experiment']['name']}")
print(f"  CO2: {config['physics']['radiation']['co2_concentration']} ppm")
```

## Step 3: Add Machine-Specific Settings

```python
# HPC cluster configuration
hpc_config = """
compute:
  nodes: 16
  cores_per_node: 48
  memory_per_node: 192GB

output:
  directory: /scratch/user/climate/exp_001
  parallel_io: true
"""

hpc_file = tmpdir / "hpc_cluster.yaml"
hpc_file.write_text(hpc_config)

# Load and merge
hpc = load_yaml(str(hpc_file), category="machine", subcategory="hpc_cluster")
config.update(hpc)

print("\nMachine configuration merged")
print(f"  Nodes: {config['compute']['nodes']}")
print(f"  Total cores: {config['compute']['nodes'] * config['compute']['cores_per_node']}")
```

## Step 4: Apply Runtime Adjustments

```python
# Runtime modifications (e.g., from command line)
config["output"]["compression"] = "zstd"  # Better compression
config["physics"]["convection"]["timestep"] = 600  # Further adjustment

print("\nRuntime adjustments applied")
print(f"  Compression: {config['output']['compression']}")
print(f"  Convection timestep: {config['physics']['convection']['timestep']}s")
```

## Step 5: Track Configuration Sources

```python
# Show where each critical parameter came from
critical_params = [
    ("model.resolution", ["model", "resolution"]),
    ("physics.radiation.scheme", ["physics", "radiation", "scheme"]),
    ("physics.radiation.co2_concentration", ["physics", "radiation", "co2_concentration"]),
    ("physics.convection.timestep", ["physics", "convection", "timestep"]),
    ("initial_conditions.temperature", ["initial_conditions", "temperature"]),
    ("output.directory", ["output", "directory"]),
    ("output.compression", ["output", "compression"]),
]

print("\nConfiguration provenance:")
for param_name, keys in critical_params:
    value = config
    for key in keys:
        value = value[key]

    prov = value.provenance.current
    source = Path(prov.yaml_file).name if prov.yaml_file else "runtime"
    print(f"  {param_name}:")
    print(f"    value: {value}")
    print(f"    from: {prov.category}/{prov.subcategory or ''} ({source})")

    # Show history if modified
    if len(value.provenance) > 1:
        print(f"    modifications: {len(value.provenance) - 1}")
```

## Step 6: Save Simulation Configuration

```python
# Save final configuration with provenance
final_config_file = tmpdir / "simulation_exp_001.yaml"
dump_yaml(config, str(final_config_file), include_provenance=True)

print(f"\nSaved simulation configuration to: {final_config_file.name}")
print("\nConfig with provenance comments (excerpt):")
lines = final_config_file.read_text().split('\n')
for line in lines[15:25]:  # Show a sample
    print(f"  {line}")
```

## Step 7: Generate Metadata for Reproducibility

```python
# Extract complete provenance
prov_tree = extract_provenance_tree(config)

# Create simulation metadata
metadata = {
    "experiment": {
        "id": config["experiment"]["id"],
        "name": config["experiment"]["name"],
        "description": config["experiment"]["description"],
    },
    "timestamp": datetime.now().isoformat(),
    "model": {
        "name": config["model"]["name"],
        "version": config["model"]["version"],
    },
    "configuration_sources": {
        "base": str(base_file),
        "experiment": str(exp_file),
        "machine": str(hpc_file),
    },
    "provenance": prov_tree
}

# Save metadata
metadata_file = tmpdir / "exp_001_metadata.json"
with open(metadata_file, "w") as f:
    json.dump(metadata, f, indent=2, default=str)

print(f"\nGenerated metadata file: {metadata_file.name}")
print(f"  Size: {metadata_file.stat().st_size} bytes")
```

## Step 8: Simulate Running the Model

```python
def run_simulation(config):
    """Mock simulation runner."""
    return {
        "status": "success",
        "runtime_seconds": 3600,
        "output_files": [
            f"{config['output']['directory']}/output_000.nc",
            f"{config['output']['directory']}/output_001.nc",
        ],
        "diagnostics": {
            "mean_temperature": 287.5,
            "total_precipitation": 1250.0,
        }
    }

# Run simulation
results = run_simulation(config)

print(f"\nSimulation completed:")
print(f"  Status: {results['status']}")
print(f"  Runtime: {results['runtime_seconds']}s")
print(f"  Output files: {len(results['output_files'])}")
```

## Step 9: Save Results with Provenance

```python
# Combine results with configuration provenance
full_results = {
    "experiment_id": config["experiment"]["id"],
    "results": results,
    "configuration": {
        "model": dict(config["model"]),
        "physics": dict(config["physics"]),
        "initial_conditions": dict(config["initial_conditions"]),
    },
    "provenance": prov_tree,
    "timestamp": datetime.now().isoformat()
}

results_file = tmpdir / "exp_001_results.json"
with open(results_file, "w") as f:
    json.dump(full_results, f, indent=2, default=str)

print(f"\nSaved results with provenance: {results_file.name}")
```

## Step 10: Audit Configuration

```python
# Generate audit report
def audit_configuration(config):
    """Audit which files provided which parameters."""
    sources = {}

    prov_tree = extract_provenance_tree(config)

    def collect_sources(tree, path=""):
        for key, value in tree.items():
            if isinstance(value, dict) and 'yaml_file' in value:
                category = value['category']
                subcategory = value.get('subcategory', '')
                file_name = Path(value['yaml_file']).name if value['yaml_file'] else 'runtime'

                source_key = f"{category}/{subcategory}".rstrip('/')
                if source_key not in sources:
                    sources[source_key] = {
                        'file': file_name,
                        'parameters': []
                    }

                current_path = f"{path}.{key}" if path else key
                sources[source_key]['parameters'].append(current_path)

            elif isinstance(value, dict):
                current_path = f"{path}.{key}" if path else key
                collect_sources(value, current_path)

    collect_sources(prov_tree)
    return sources

audit = audit_configuration(config)

print("\nConfiguration Audit:")
for source, info in sorted(audit.items()):
    print(f"\n  {source} ({info['file']}):")
    for param in info['parameters'][:5]:  # Show first 5
        print(f"    - {param}")
    if len(info['parameters']) > 5:
        print(f"    ... and {len(info['parameters']) - 5} more")
```

## Step 11: Compare with Another Experiment

```python
# Create variant experiment
variant_config_content = """
experiment:
  id: exp_002
  name: sensitivity_test_solar
  description: Test solar forcing sensitivity

physics:
  radiation:
    solar_constant: 1361  # W/m^2 (slightly reduced)
    co2_concentration: 400
"""

variant_file = tmpdir / "experiment_002.yaml"
variant_file.write_text(variant_config_content)

# Load variant
variant_config = load_yaml(str(base_file), category="model_defaults")
variant_exp = load_yaml(str(variant_file), category="experiment", subcategory="exp_002")
variant_config.update(variant_exp)
variant_config.update(hpc)

# Compare key parameters
print("\nComparing experiments:")
comparison_params = [
    (["experiment", "name"]),
    (["physics", "radiation", "co2_concentration"]),
    (["physics", "radiation", "solar_constant"]),
]

for keys in comparison_params:
    param = ".".join(keys)

    # Get from exp_001
    val1 = config
    for key in keys:
        if key in val1:
            val1 = val1[key]
        else:
            val1 = "N/A"
            break

    # Get from exp_002
    val2 = variant_config
    for key in keys:
        if key in val2:
            val2 = val2[key]
        else:
            val2 = "N/A"
            break

    print(f"\n  {param}:")
    print(f"    exp_001: {val1}")
    print(f"    exp_002: {val2}")
```

## Cleanup

```python
import shutil
shutil.rmtree(tmpdir)
print("\nCleaned up temporary files")
```

## Summary

This tutorial demonstrated:

1. Building complex scientific configurations from multiple sources
2. Tracking exactly which file and category provided each parameter
3. Handling hierarchical merging (defaults → experiment → machine → runtime)
4. Generating reproducible metadata with full provenance
5. Saving results with configuration history
6. Auditing configuration sources
7. Comparing experiments

## Best Practices for Scientific Workflows

1. **Always use categories**: Clearly separate defaults, experiments, machine configs
2. **Save provenance metadata**: Include with all results for reproducibility
3. **Track modifications**: Capture runtime changes in provenance history
4. **Generate audit reports**: Document which files provided which parameters
5. **Version your configs**: Use git or similar for configuration files

## Next Steps

- Try the [Multi-Environment Tutorial](multi-environment.md)
- Read about [Hierarchical Configuration](../user-guide/hierarchical-config.md)
- Explore the [API Reference](../api/core.md)
