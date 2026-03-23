from sqlalchemy import Column, Integer, String, Text, MetaData, Table as SATable
from sqlalchemy.orm import DeclarativeBase
from schema_evolver.parser.sqlalchemy import SQLAlchemyParser
from schema_evolver.diff.engine import DiffEngine

# 1. Define Old State (State A)
metadata_a = MetaData()
users_a = SATable(
    "users", metadata_a,
    Column("id", Integer, primary_key=True),
    Column("name", String(50))
)

# 2. Define New State (State B)
metadata_b = MetaData()
users_b = SATable(
    "users", metadata_b,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("email", String(100)) # Added Column
)
posts_b = SATable(
    "posts", metadata_b,
    Column("id", Integer, primary_key=True),
    Column("content", Text) # Added Table
)

# 3. Parse Metadata objects into Core Models
parser = SQLAlchemyParser()
schema_a = parser.parse_metadata(metadata_a)
schema_b = parser.parse_metadata(metadata_b)

# 4. Compute Diffs
engine = DiffEngine()
operations = engine.diff(schema_a, schema_b)

print(f"Detected {len(operations)} schema changes:")
for op in operations:
    print(f"- {op.type.upper()}: {op}")

# TODO: Connect to Planner to generate Migration Script
# TODO: Connect to Executor to apply Migration
