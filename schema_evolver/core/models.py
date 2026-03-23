from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class Column(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    type: str
    nullable: bool = True
    default: Optional[str] = None
    primary_key: bool = False

    def signature(self) -> str:
        """
        Representacion comprobable del campo.
        """
        return f"{self.type} | {self.nullable} | {self.default}"

class Table(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    columns: Dict[str, Column] = Field(default_factory=dict)

    def colum_names(self) -> set[str]:
        return set(self.columns.keys())

class Schema(BaseModel):
    model_config = ConfigDict(frozen=True)

    tables: Dict[str, Table] = Field(default_factory=dict)

    def table_names(self) -> set[str]:
        return set(self.tables.keys())
