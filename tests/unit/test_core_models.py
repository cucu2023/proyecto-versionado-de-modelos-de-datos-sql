from schema_evolver.core.models import Column, Table, Schema

def test_create_schema():
    col = Column(name="id", type="init", nullable=False)
    table = Table(name = "users", columns = {"id": col})
    schema = Schema(tables = {"users": table})
    assert "users" in schema.tables
    assert "id" in schema.tables["users"].columns

def test_column_signature():
    col = Column(name="price", type="float", nullable=False)
    assert col.signature() == "float | False | None"