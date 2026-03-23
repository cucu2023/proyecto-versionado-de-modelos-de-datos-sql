# Schema Evolver

A schema versioning and migration intelligence engine built with Python 3.11+, Pydantic, and SQLAlchemy.

## Features

- **Parser Layer**: Converts SQLAlchemy MetaData into framework-independent core models.
- **Diff Engine**: Computes semantic differences (Added/Removed Tables, Added/Removed Columns) between schema states.
- **CLI**: A modern CLI powered by `Typer` and `Rich`.
- **Clean Architecture**: Domain logic is decoupled from external frameworks.

## Installation

```bash
pip install .
```

## Quick Start

### Using the CLI

```bash
schema-evolver diff
```

### Programmatic Usage

Check `examples/basic_usage.py`:

```python
from schema_evolver.parser.sqlalchemy import SQLAlchemyParser
from schema_evolver.diff.engine import DiffEngine

parser = SQLAlchemyParser()
engine = DiffEngine()

schema_a = parser.parse_metadata(metadata_a)
schema_b = parser.parse_metadata(metadata_b)

diffs = engine.diff(schema_a, schema_b)
```

## Architecture

- `core/`: Pydantic domain models (Schema, Table, Column).
- `parser/`: ORM/Database specific parsers.
- `diff/`: Logic for schema comparison.
- `planner/`: (TODO) Converts diffs into migration operations.
- `executor/`: (TODO) Applies operations to target databases.
- `cli/`: Typer-based command line interface.
