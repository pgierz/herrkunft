# Changelog

All notable changes to herrkunft will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Async YAML loading support
- Configuration diff tools
- Provenance visualization
- Remote configuration sources
- Streaming support for large files

## [0.1.0] - 2024-10-08

### Added
- Initial release of herrkunft
- Core provenance tracking with `Provenance` and `ProvenanceStep` classes
- Type wrappers for all Python built-in types
  - `DictWithProvenance`, `ListWithProvenance`
  - `StrWithProvenance`, `IntWithProvenance`, `FloatWithProvenance`, `BoolWithProvenance`
- YAML loading with provenance tracking via `ProvenanceLoader`
- YAML dumping with provenance comments via `ProvenanceDumper`
- Hierarchical configuration management with `HierarchyManager`
- Category-based conflict resolution
- Provenance history tracking for all modifications
- Utility functions:
  - `clean_provenance()` - Remove provenance wrappers
  - `extract_provenance_tree()` - Extract provenance metadata
  - `validate_provenance_*()` - Validation functions
  - `to_json()`, `from_json()` - JSON serialization
- Comprehensive test suite with >90% coverage
- Full type hints and Pydantic 2.0 integration
- Documentation with Jupyter Book

### Dependencies
- `pydantic>=2.0.0` - Type-safe data models
- `ruamel.yaml>=0.17.32` - YAML parsing with position tracking
- `loguru>=0.7.0` - Logging

### Documentation
- Complete user guide
- API reference documentation
- Interactive tutorials
- Architecture overview
- Contributing guidelines

## Version Scheme

herrkunft follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

### Pre-1.0.0 Versions

During the 0.x.y series:
- **0.x.0**: New features, potential breaking changes
- **0.x.y**: Bug fixes and minor improvements

## Migration Guides

### From esm_tools

herrkunft is extracted from esm_tools. To migrate:

1. **Install herrkunft**:
   ```bash
   pip install herrkunft
   ```

2. **Update imports**:
   ```python
   # Old (esm_tools)
   from esm_parser import yaml_to_dict

   # New (herrkunft)
   from provenance import load_yaml
   ```

3. **Update function calls**:
   ```python
   # Old
   config = yaml_to_dict("config.yaml")

   # New
   config = load_yaml("config.yaml", category="defaults")
   ```

4. **Access provenance**:
   ```python
   # New capability
   prov = config["key"].provenance.current
   print(f"From: {prov.yaml_file}:{prov.line}")
   ```

## Compatibility

### Python Versions

- **Python 3.9+**: Fully supported
- **Python 3.10+**: Recommended
- **Python 3.11+**: Best performance and type checking
- **Python 3.12**: Fully supported

### Operating Systems

- **Linux**: Fully supported
- **macOS**: Fully supported
- **Windows**: Fully supported

### Dependencies

herrkunft maintains compatibility with:
- Pydantic 2.x
- ruamel.yaml 0.17.x and 0.18.x
- loguru 0.7.x

## Breaking Changes

### 0.1.0

First release, no breaking changes.

## Deprecation Policy

Features are deprecated following this process:

1. **Deprecation Warning**: Added in minor version
2. **Documentation**: Updated with alternatives
3. **Removal**: In next major version (minimum 6 months)

Example:
- v0.5.0: Feature deprecated, warning added
- v0.6.0-v0.9.x: Warning remains
- v1.0.0: Feature removed

## Support Policy

### Current Version

- **Bug fixes**: Regular patches
- **Security fixes**: Immediate response
- **New features**: Active development

### Previous Major Version

- **Bug fixes**: 6 months after new major release
- **Security fixes**: 12 months after new major release
- **New features**: Not supported

### Older Versions

Not supported. Users should upgrade to current version.

## Security

### Reporting Vulnerabilities

Report security issues to: security@herrkunft.dev

Please include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fixes (if any)

### Security Updates

Critical security fixes are released immediately and backported to supported versions.

## See Also

- [GitHub Releases](https://github.com/pgierz/herrkunft/releases)
- [Migration Guide](https://herrkunft.readthedocs.io/migration)
- [Contributing](../contributing.md)
