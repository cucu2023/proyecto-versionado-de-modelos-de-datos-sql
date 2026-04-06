from typing import List
from pydantic import BaseModel, Field
from schema_evolver.diff.engine import (
    SchemaOperation, AddTable, RemoveTable, AddColumn, RemoveColumn
)

class MigrationPlan(BaseModel):
    """Represents a sequence of operations to evolve the schema."""
    operations: List[SchemaOperation] = Field(default_factory=list)

    def __len__(self):
        return len(self.operations)

class Planner:
    """Orchestrates the order of schema operations to ensure safety."""

    def plan(self, operations: List[SchemaOperation]) -> MigrationPlan:
        """
        Takes a raw list of operations and produces an ordered MigrationPlan.
        """
        # Current strategy: 
        # 1. Remove columns
        # 2. Remove tables
        # 3. Add tables
        # 4. Add columns
        
        removals_cols = [op for op in operations if isinstance(op, RemoveColumn)]
        removals_tables = [op for op in operations if isinstance(op, RemoveTable)]
        additions_tables = [op for op in operations if isinstance(op, AddTable)]
        additions_cols = [op for op in operations if isinstance(op, AddColumn)]

        # Join everything in the defined order
        ordered_ops = (
            removals_cols + 
            removals_tables + 
            additions_tables + 
            additions_cols
        )

        return MigrationPlan(operations=ordered_ops)
