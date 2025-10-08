---
title: herrkunft
subtitle: Configuration Provenance Tracking for Python
description: Track configuration value origins and modification history through YAML parsing
---

# herrkunft

**From German "Herkunft" (origin, provenance)**

Track configuration value origins and modification history through YAML parsing with modern Python best practices.

## What is herrkunft?

`herrkunft` is a standalone library that provides transparent provenance tracking for configuration values loaded from YAML files. It tracks:

- **Where** each value came from (file path, line number, column)
- **When** it was set or modified
- **How** conflicts were resolved using hierarchical categories
- **What** the complete modification history is

Perfect for scientific computing, workflow configuration, and any application where configuration traceability matters.

## Key Features

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} Transparent Tracking
:class-header: bg-light
Values behave like normal Python types while tracking their provenance
:::

:::{grid-item-card} Precise Location
:class-header: bg-light
Track exact file, line, and column for every configuration value
:::

:::{grid-item-card} Hierarchical Resolution
:class-header: bg-light
Category-based conflict resolution (e.g., defaults < user < runtime)
:::

:::{grid-item-card} Modification History
:class-header: bg-light
Complete audit trail of all changes to configuration values
:::

:::{grid-item-card} Type-Safe
:class-header: bg-light
Full type hints and Pydantic validation throughout
:::

:::{grid-item-card} YAML Round-Trip
:class-header: bg-light
Preserve provenance as comments when writing YAML
:::

::::

## Quick Example

```python
from provenance import load_yaml

# Load a configuration file with provenance tracking
config = load_yaml("config.yaml", category="defaults")

# Access values normally
database_url = config["database"]["url"]
print(database_url)  # postgresql://localhost/mydb

# Access provenance information
print(database_url.provenance.current.yaml_file)  # config.yaml
print(database_url.provenance.current.line)       # 15
print(database_url.provenance.current.column)     # 8
```

## Installation

Install from PyPI:

```bash
pip install herrkunft
```

For development with all dependencies:

```bash
pip install herrkunft[dev]
```

## Use Cases

### Scientific Computing

Track which configuration file and parameters were used for each simulation run:

```python
config = load_yaml("simulation.yaml")
run_simulation(config)

# Later, audit which file provided each parameter
for key, value in config.items():
    print(f"{key}: {value.provenance.current.yaml_file}")
```

### Multi-Environment Configuration

Manage development, staging, and production configs with clear conflict resolution:

```python
from provenance import ProvenanceLoader

loader = ProvenanceLoader()
config = loader.load_multiple([
    ("defaults.yaml", "defaults"),
    ("production.yaml", "production"),
    ("secrets.yaml", "secrets"),  # Highest priority
])
```

### Configuration Auditing

Export complete provenance history for compliance or debugging:

```python
from provenance import to_json_file

# Export config with full provenance metadata
to_json_file(config, "audit.json")
```

## Next Steps

::::{grid} 1 1 2 3
:gutter: 2

:::{grid-item-card}
:link: getting-started/quickstart
:link-type: doc

**Quick Start Guide**

Get up and running in 5 minutes
:::

:::{grid-item-card}
:link: tutorials/basic-usage
:link-type: doc

**Tutorials**

Step-by-step interactive tutorials
:::

:::{grid-item-card}
:link: api/core
:link-type: doc

**API Reference**

Complete API documentation
:::

::::

## Architecture

herrkunft is built with modern Python best practices:

- **Pydantic 2.0**: Type-safe data models and settings
- **ruamel.yaml**: YAML parsing with position tracking and comment preservation
- **loguru**: Simple, powerful logging
- **Type hints**: Full typing support for IDE autocomplete and type checking

```{mermaid}
graph LR
    A[YAML Files] --> B[ProvenanceLoader]
    B --> C[Types with Provenance]
    C --> D[DictWithProvenance]
    C --> E[ListWithProvenance]
    D --> F[HierarchyManager]
    E --> F
    F --> G[Merged Config]
    G --> H[ProvenanceDumper]
    H --> I[YAML with Comments]
```

## Community

- **GitHub**: [pgierz/herrkunft](https://github.com/pgierz/herrkunft)
- **Issues**: [Report bugs or request features](https://github.com/pgierz/herrkunft/issues)
- **Documentation**: [herrkunft.readthedocs.io](https://herrkunft.readthedocs.io)

## Authors

- **Paul Gierz** - [paul.gierz@awi.de](mailto:paul.gierz@awi.de)
- **Miguel Andrés-Martínez** - [miguel.andres-martinez@awi.de](mailto:miguel.andres-martinez@awi.de)

## License

MIT License - see [LICENSE](https://github.com/pgierz/herrkunft/blob/main/LICENSE) for details.

## Acknowledgments

Extracted from the [esm_tools](https://github.com/esm-tools/esm_tools) project, which provides workflow management for Earth System Models. The provenance tracking feature was originally developed to track configuration origins in complex HPC simulation workflows.

```{toctree}
:hidden:
:maxdepth: 2

getting-started/installation
getting-started/quickstart
getting-started/examples
```

```{toctree}
:caption: User Guide
:hidden:
:maxdepth: 2

user-guide/loading-yaml
user-guide/tracking-provenance
user-guide/hierarchical-config
user-guide/saving-yaml
```

```{toctree}
:caption: Tutorials
:hidden:
:maxdepth: 2

tutorials/basic-usage
tutorials/scientific-workflows
tutorials/multi-environment
```

```{toctree}
:caption: API Reference
:hidden:
:maxdepth: 2

api/core
api/types
api/yaml
api/utils
```

```{toctree}
:caption: Reference
:hidden:
:maxdepth: 2

reference/architecture
reference/changelog
contributing
```
