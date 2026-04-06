import typer
import importlib
import sys
import os
from typing import Optional
from rich.console import Console
from rich.table import Table as RichTable
from sqlalchemy import create_engine
from schema_evolver.parser.sqlalchemy_parser import parse_sqlalchemy, parse_database
from schema_evolver.diff.engine import DiffEngine
from schema_evolver.planner.engine import Planner
from schema_evolver.executor.engine import SQLExecutor

app = typer.Typer(help="Schema Evolver: Schema Migration Intelligence Engine")
console = Console()

def get_base_from_module(module_path: str):
    """Dynamically imports the Base from a module path (e.g., 'myapp.models.Base')."""
    # Aseguramos que el directorio actual esté en el path para encontrar archivos locales
    sys.path.insert(0, os.getcwd())
    try:
        parts = module_path.split(".")
        if len(parts) < 2:
            raise ValueError("Debes proporcionar la ruta completa, ej: 'mi_archivo.Base'")
        
        module_name = ".".join(parts[:-1])
        attr_name = parts[-1]
        module = importlib.import_module(module_name)
        return getattr(module, attr_name)
    except Exception as e:
        console.print(f"[bold red]Error loading Base from {module_path}:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def check(
    db_url: str = typer.Option(..., help="Database URL (e.g., sqlite:///test.db)"),
    base_path: str = typer.Option(..., help="Module path to SQLAlchemy Base (e.g., myapp.models.Base)")
):
    """Check for differences between the code and the database."""
    engine = create_engine(db_url)
    base = get_base_from_module(base_path)

    console.print(f"[bold blue]Analizando base de datos...[/bold blue]")
    db_schema = parse_database(engine)
    
    console.print(f"[bold blue]Analizando modelos SQLAlchemy...[/bold blue]")
    code_schema = parse_sqlalchemy(base)

    diff_engine = DiffEngine()
    ops = diff_engine.diff(db_schema, code_schema)

    if not ops:
        console.print("[bold green]Esquema sincronizado. No se detectaron cambios.[/bold green]")
        return

    console.print("[bold cyan]Diferencias detectadas:[/bold cyan]")
    
    table = RichTable(show_header=True, header_style="bold magenta")
    table.add_column("Operación")
    table.add_column("Objetivo")
    table.add_column("Detalles")

    for op in ops:
        if op.type == "add_table":
            table.add_row("Crear Tabla", op.table_name, f"Columnas: {list(op.table.columns.keys())}")
        elif op.type == "add_column":
            table.add_row("Añadir Columna", f"{op.table_name}.{op.column_name}", f"Tipo: {op.column.type}")
        elif op.type == "remove_table":
            table.add_row("Borrar Tabla", op.table_name, "-")
        elif op.type == "remove_column":
            table.add_row("Borrar Columna", f"{op.table_name}.{op.column_name}", "-")

    console.print(table)

@app.command()
def plan(
    db_url: str = typer.Option(..., help="Database URL"),
    base_path: str = typer.Option(..., help="Module path to SQLAlchemy Base")
):
    """Generate the SQL plan for migration."""
    engine = create_engine(db_url)
    base = get_base_from_module(base_path)

    db_schema = parse_database(engine)
    code_schema = parse_sqlalchemy(base)

    diff_engine = DiffEngine()
    ops = diff_engine.diff(db_schema, code_schema)

    if not ops:
        console.print("[bold green]Nada que planificar.[/bold green]")
        return

    planner = Planner()
    migration_plan = planner.plan(ops)
    
    executor = SQLExecutor(engine)
    sql_statements = executor.generate_sql(migration_plan)

    console.print("[bold yellow]Plan de Migración (SQL):[/bold yellow]")
    for sql in sql_statements:
        console.print(f"  [green]{sql};[/green]")

@app.command()
def apply(
    db_url: str = typer.Option(..., help="Database URL"),
    base_path: str = typer.Option(..., help="Module path to SQLAlchemy Base"),
    force: bool = typer.Option(False, "--force", help="Execute without confirmation")
):
    """Apply the migration to the database."""
    engine = create_engine(db_url)
    base = get_base_from_module(base_path)

    db_schema = parse_database(engine)
    code_schema = parse_sqlalchemy(base)

    diff_engine = DiffEngine()
    ops = diff_engine.diff(db_schema, code_schema)

    if not ops:
        console.print("[bold green]No hay cambios pendientes.[/bold green]")
        return

    planner = Planner()
    migration_plan = planner.plan(ops)
    
    executor = SQLExecutor(engine)
    sql_statements = executor.generate_sql(migration_plan)

    console.print("[bold yellow]Se ejecutarán los siguientes comandos:[/bold yellow]")
    for sql in sql_statements:
        console.print(f"  [red]{sql};[/red]")

    if not force:
        confirm = typer.confirm("¿Deseas aplicar estos cambios?")
        if not confirm:
            console.print("[bold red]Operación cancelada.[/bold red]")
            return

    executor.execute(migration_plan)
    console.print("[bold green]¡Migración completada con éxito![/bold green]")

if __name__ == "__main__":
    app()
