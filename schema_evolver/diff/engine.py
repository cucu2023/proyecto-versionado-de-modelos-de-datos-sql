from typing import List, Optional, Union
from pydantic import BaseModel
from schema_evolver.core.models import Schema, Table, Column

class SchemaOperation(BaseModel):
    """Base class for schema operations."""
    type: str

class AddTable(SchemaOperation):
    type: str = "add_table"
    table_name: str
    table: Table

class RemoveTable(SchemaOperation):
    type: str = "remove_table"
    table_name: str

class AddColumn(SchemaOperation):
    type: str = "add_column"
    table_name: str
    column_name: str
    column: Column

class RemoveColumn(SchemaOperation):
    type: str = "remove_column"
    table_name: str
    column_name: str

class DiffEngine:
    """Computes semantic diffs between two schema versions."""

    def diff(self, old: Schema, new: Schema) -> List[SchemaOperation]:
        operations = []

        # Check for added/removed tables
        old_tables = set(old.tables.keys())
        new_tables = set(new.tables.keys())

        for table_name in new_tables - old_tables:
            operations.append(AddTable(table_name=table_name, table=new.tables[table_name]))

        for table_name in old_tables - new_tables:
            operations.append(RemoveTable(table_name=table_name))

        # Check for column changes in common tables
        for table_name in old_tables & new_tables:
            old_table = old.tables[table_name]
            new_table = new.tables[table_name]

            old_cols = set(old_table.columns.keys())
            new_cols = set(new_table.columns.keys())

            for col_name in new_cols - old_cols:
                operations.append(AddColumn(
                    table_name=table_name, 
                    column_name=col_name, 
                    column=new_table.columns[col_name]
                ))

            for col_name in old_cols - new_cols:
                operations.append(RemoveColumn(
                    table_name=table_name, 
                    column_name=col_name
                ))
            
            # TODO: Detect column type/property changes
            # TODO: Detect renamed tables/columns (semantic matching)

        return operations
