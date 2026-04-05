import json
from pydantic import BaseModel
from typing import Any

def deterministic_serialize(data: Any) -> str:
    """Serializes pydantic models or any data to a deterministic JSON string."""
    if isinstance(data, BaseModel):
        # Convert to dict first to ensure we can sort everything recursively
        data = data.model_dump()
    return json.dumps(data, sort_keys=True)
