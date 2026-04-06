import pytest
from schema_evolver.core.models import Table, Column, Schema
from schema_evolver.diff.engine import AddTable, AddColumn, RemoveTable, RemoveColumn
from schema_evolver.planner.engine import Planner

def test_planner_order():
    planner = Planner()
    
    # Unordered operations
    ops = [
        AddColumn(table_name="users", column_name="email", column=Column(name="email", type="varchar")),
        AddTable(table_name="posts", table=Table(name="posts")),
        RemoveTable(table_name="old_logs"),
        RemoveColumn(table_name="users", column_name="phone")
    ]
    
    plan = planner.plan(ops)
    
    # Check order: Removals first (cols then tables), then additions (tables then cols)
    op_types = [op.type for op in plan.operations]
    
    assert op_types == ["remove_column", "remove_table", "add_table", "add_column"]
