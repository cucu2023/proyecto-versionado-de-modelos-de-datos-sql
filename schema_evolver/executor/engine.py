from sqlalchemy import Engine, text
from schema_evolver.planner.engine import MigrationPlan
from schema_evolver.diff.engine import (
    AddTable, RemoveTable, AddColumn, RemoveColumn
)

class SQLExecutor:
    """Executes a MigrationPlan by translating it to SQL commands."""

    def __init__(self, engine: Engine):
        self.engine = engine

    def generate_sql(self, plan: MigrationPlan) -> list[str]:
        """Translates the plan into a list of SQL strings."""
        statements = []
        for op in plan.operations:
            if isinstance(op, AddTable):
                # Basic CREATE TABLE (simplified)
                cols_sql = []
                for col in op.table.columns.values():
                    pk = " PRIMARY KEY" if col.primary_key else ""
                    nullable = "" if col.nullable else " NOT NULL"
                    cols_sql.append(f"{col.name} {col.type}{pk}{nullable}")
                
                sql = f"CREATE TABLE {op.table_name} ({', '.join(cols_sql)})"
                statements.append(sql)

            elif isinstance(op, RemoveTable):
                statements.append(f"DROP TABLE {op.table_name}")

            elif isinstance(op, AddColumn):
                pk = " PRIMARY KEY" if op.column.primary_key else ""
                nullable = "" if op.column.nullable else " NOT NULL"
                statements.append(f"ALTER TABLE {op.table_name} ADD COLUMN {op.column_name} {op.column.type}{pk}{nullable}")

            elif isinstance(op, RemoveColumn):
                statements.append(f"ALTER TABLE {op.table_name} DROP COLUMN {op.column_name}")

        return statements

    def execute(self, plan: MigrationPlan):
        """Executes the plan directly on the database."""
        statements = self.generate_sql(plan)
        with self.engine.connect() as conn:
            for sql in statements:
                conn.execute(text(sql))
            conn.commit()
