from typing import Type, Any
from pydantic import BaseModel
from schema_evolver.core.models import Table, Column

def map_pydantic_type(python_type: Any) -> str:
    """Mapea tipos de Python/Pydantic a nombres de tipos SQL genéricos."""
    if python_type == int:
        return "integer"
    if python_type == str:
        return "varchar"
    if python_type == bool:
        return "boolean"
    if python_type == float:
        return "float"
    return "text"

def parse_pydantic_model(model: Type[BaseModel]) -> Table:
    """
    Convierte un modelo de Pydantic en una definición de Tabla interna.
    """
    table_name = model.__name__.lower()
    table = Table(name=table_name)

    for name, field in model.model_fields.items():
        # Extraer metadatos si están presentes en Field()
        # En el futuro podrías usar Field(json_schema_extra={"primary_key": True})
        
        is_pk = False
        # Buscamos metadatos personalizados si el usuario los pone en Field
        if field.json_schema_extra and isinstance(field.json_schema_extra, dict):
            is_pk = field.json_schema_extra.get("primary_key", False)

        column = Column(
            name=name,
            type=map_pydantic_type(field.annotation),
            nullable=not field.is_required(),
            primary_key=is_pk,
            default=str(field.default) if field.default is not None else None
        )
        table.columns[name] = column

    return table
