import typer
from rich.console import Console
from rich.table import Table as RichTable
from schema_evolver.core.models import Schema, Table, Column
from schema_evolver.diff.engine import DiffEngine

app = typer.Typer(help="Schema Evolver: Schema Migration Intelligence Engine")
console = Console()

@app.command()
def diff():
    """Compute diff between two schema versions (mocked for demo)."""
    
    # Mocking two states for demonstration
    old_schema = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True),
            "username": Column(name="username", type="VARCHAR(50)")
        })
    })

    new_schema = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True),
            "username": Column(name="username", type="VARCHAR(50)"),
            "email": Column(name="email", type="VARCHAR(100)", nullable=True)
        }),
        "posts": Table(name="posts", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True),
            "content": Column(name="content", type="TEXT")
        })
    })

    engine = DiffEngine()
    ops = engine.diff(old_schema, new_schema)

    console.print("[bold cyan]Schema Diffs Detected:[/bold cyan]")
    
    table = RichTable(show_header=True, header_style="bold magenta")
    table.add_column("Operation")
    table.add_column("Target")
    table.add_column("Details")

    for op in ops:
        if op.type == "add_table":
            table.add_row("Add Table", op.table_name, f"Columns: {list(op.table.columns.keys())}")
        elif op.type == "add_column":
            table.add_row("Add Column", f"{op.table_name}.{op.column_name}", f"Type: {op.column.type}")
        elif op.type == "remove_table":
            table.add_row("Remove Table", op.table_name, "-")
        elif op.type == "remove_column":
            table.add_row("Remove Column", f"{op.table_name}.{op.column_name}", "-")

    console.print(table)

if __name__ == "__main__":
    app()
