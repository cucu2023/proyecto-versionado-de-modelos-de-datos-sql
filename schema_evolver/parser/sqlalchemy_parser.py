from sqlalchemy import Engine, MetaData
from sqlalchemy.orm import DeclarativeMeta
from schema_evolver.core.models import Schema, Table, Column


def map_type(column_type) -> str:
    """
    Convierte tipos de SQLAlchemy a string simple.
    """
    return str(column_type).lower()


def parse_sqlalchemy(base: DeclarativeMeta) -> Schema:
    metadata = base.metadata
    return _parse_metadata(metadata)


def parse_database(engine: Engine) -> Schema:
    """
    Refleja la base de datos actual y la convierte al modelo de Schema interno.
    """
    metadata = MetaData()
    metadata.reflect(bind=engine)
    return _parse_metadata(metadata)


def _parse_metadata(metadata: MetaData) -> Schema:
    schema = Schema()

    for table_name, table_obj in metadata.tables.items():
        table = Table(name=table_name)

        for col in table_obj.columns:
            column = Column(
                name=col.name,
                type=map_type(col.type),
                nullable=col.nullable,
                primary_key=col.primary_key,
                default=str(col.default.arg) if col.default else None,
            )

            table.columns[col.name] = column

        schema.tables[table_name] = table

    return schema