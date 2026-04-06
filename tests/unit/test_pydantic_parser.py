from pydantic import BaseModel, Field
from schema_evolver.parser.pydantic_parser import parse_pydantic_model

def test_pydantic_parsing():
    class User(BaseModel):
        id: int = Field(json_schema_extra={"primary_key": True})
        name: str
        email: str = None # Nullable

    table = parse_pydantic_model(User)
    
    assert table.name == "user"
    assert "id" in table.columns
    assert table.columns["id"].primary_key is True
    assert table.columns["id"].type == "integer"
    assert table.columns["name"].type == "varchar"
    assert table.columns["name"].nullable is False
    assert table.columns["email"].nullable is True
