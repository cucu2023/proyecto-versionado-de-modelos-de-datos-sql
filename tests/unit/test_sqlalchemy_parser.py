from sqlalchemy.orm import declarative_base
from sqlalchemy import Column as SAColumn, Integer, String

from schema_evolver.parser.sqlalchemy_parser import parse_sqlalchemy

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = SAColumn(Integer, primary_key=True)
    name = SAColumn(String, nullable=False) 

def test_parse_multiple_tables():
    class Product(Base):
        __tablename__ = "products"
        id = SAColumn(Integer, primary_key=True)

    schema = parse_sqlalchemy(Base)

    assert "users" in schema.tables
    assert "products" in schema.tables