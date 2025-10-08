#!/usr/bin/env python3
"""
Demonstration script for ProvenanceDumper functionality.

This script demonstrates the key features of the ProvenanceDumper class,
showing how it can dump YAML with provenance comments.
"""

from provenance.yaml import ProvenanceLoader, ProvenanceDumper
from provenance.core.provenance import Provenance, ProvenanceStep
from provenance.types.factory import TypeWrapperFactory
import tempfile
from pathlib import Path


def demo_basic_dumping():
    """Demonstrate basic YAML dumping."""
    print("=" * 60)
    print("Demo 1: Basic YAML Dumping")
    print("=" * 60)

    dumper = ProvenanceDumper(include_provenance_comments=False)

    data = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "mydb"
        },
        "cache": {
            "enabled": True,
            "ttl": 300
        },
        "servers": ["server1", "server2", "server3"]
    }

    yaml_str = dumper.dumps(data)
    print("\nGenerated YAML:")
    print(yaml_str)


def demo_with_provenance_comments():
    """Demonstrate dumping with provenance comments."""
    print("\n" + "=" * 60)
    print("Demo 2: Dumping with Provenance Comments")
    print("=" * 60)

    dumper = ProvenanceDumper(include_provenance_comments=True)

    # Create wrapped values with provenance
    prov1 = Provenance(ProvenanceStep(
        yaml_file="/config/defaults.yaml",
        line=10,
        col=5,
        category="defaults"
    ))

    prov2 = Provenance(ProvenanceStep(
        yaml_file="/config/production.yaml",
        line=15,
        col=3,
        category="environment",
        subcategory="production"
    ))

    data = {
        "host": TypeWrapperFactory.wrap("localhost", prov1),
        "port": TypeWrapperFactory.wrap(5432, prov1),
        "database": TypeWrapperFactory.wrap("prod_db", prov2),
    }

    yaml_str = dumper.dumps(data)
    print("\nGenerated YAML with provenance comments:")
    print(yaml_str)


def demo_nested_with_comments():
    """Demonstrate nested structures with provenance."""
    print("\n" + "=" * 60)
    print("Demo 3: Nested Structures with Provenance")
    print("=" * 60)

    dumper = ProvenanceDumper(include_provenance_comments=True)

    prov_defaults = Provenance({"yaml_file": "defaults.yaml", "line": 5, "category": "defaults"})
    prov_machine = Provenance({"yaml_file": "levante.yaml", "line": 12, "category": "machines"})

    data = {
        "config": {
            "timeout": TypeWrapperFactory.wrap(30, prov_defaults),
            "max_retries": TypeWrapperFactory.wrap(3, prov_defaults),
        },
        "machine": {
            "cores": TypeWrapperFactory.wrap(128, prov_machine),
            "memory": TypeWrapperFactory.wrap("512GB", prov_machine),
        }
    }

    yaml_str = dumper.dumps(data)
    print("\nGenerated YAML with nested provenance:")
    print(yaml_str)


def demo_round_trip():
    """Demonstrate round-trip: load -> dump -> load."""
    print("\n" + "=" * 60)
    print("Demo 4: Round-Trip Load -> Dump -> Load")
    print("=" * 60)

    # Check if fixtures exist
    fixtures_dir = Path("tests/fixtures")
    if not fixtures_dir.exists():
        print("Fixtures directory not found, skipping round-trip demo")
        return

    simple_config = fixtures_dir / "simple_config.yaml"
    if not simple_config.exists():
        print(f"{simple_config} not found, skipping round-trip demo")
        return

    # Load
    loader = ProvenanceLoader(category="test")
    data, prov = loader.load(simple_config)

    print(f"\nLoaded from {simple_config}")
    print(f"Keys: {list(data.keys())}")

    # Dump
    dumper = ProvenanceDumper(include_provenance_comments=False)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = f.name

    try:
        dumper.dump(data, temp_path)
        print(f"\nDumped to {temp_path}")

        # Reload
        loader2 = ProvenanceLoader()
        data2, prov2 = loader2.load(temp_path)

        print(f"Reloaded successfully")
        print(f"Keys match: {list(data.keys()) == list(data2.keys())}")

        # Show a sample
        with open(temp_path, "r") as f:
            print("\nGenerated YAML (first 10 lines):")
            for i, line in enumerate(f):
                if i >= 10:
                    break
                print(line.rstrip())

    finally:
        import os
        os.unlink(temp_path)


def demo_clean_mode():
    """Demonstrate clean mode (removes provenance wrappers)."""
    print("\n" + "=" * 60)
    print("Demo 5: Clean Mode (No Wrappers)")
    print("=" * 60)

    dumper = ProvenanceDumper(include_provenance_comments=False)

    # Create data with wrapped values
    prov = Provenance({"category": "test"})
    data = {
        "wrapped_string": TypeWrapperFactory.wrap("hello", prov),
        "wrapped_int": TypeWrapperFactory.wrap(42, prov),
        "plain_value": "world",
    }

    print("\nDumping with clean=False (default):")
    yaml_str = dumper.dumps(data, clean=False)
    print(yaml_str)

    print("\nDumping with clean=True (removes all wrappers):")
    yaml_str_clean = dumper.dumps(data, clean=True)
    print(yaml_str_clean)


def main():
    """Run all demonstrations."""
    print("\n")
    print("#" * 60)
    print("# ProvenanceDumper Demonstration")
    print("#" * 60)

    demo_basic_dumping()
    demo_with_provenance_comments()
    demo_nested_with_comments()
    demo_clean_mode()
    demo_round_trip()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
