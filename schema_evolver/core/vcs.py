from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from schema_evolver.core.models import Schema
from schema_evolver.utils.serialization import deterministic_serialize
from schema_evolver.utils.hashing import hash_string

class Commit(BaseModel):
    model_config = ConfigDict(frozen=True)

    commit_id: str
    parent_id: Optional[str] = None
    message: str
    timestamp: str
    schema_snapshot: Schema

    @classmethod
    def create(cls, schema: Schema, message: str, parent_id: Optional[str] = None, timestamp: Optional[datetime] = None) -> "Commit":
        """Factory method to create a new deterministic commit."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        timestamp_str = timestamp.isoformat()
        
        # Temporary commit to compute hash
        # We need to exclude commit_id for the hash calculation
        content_to_hash = {
            "parent_id": parent_id,
            "message": message,
            "timestamp": timestamp_str,
            "schema_snapshot": schema.model_dump()
        }
        
        commit_id = hash_string(deterministic_serialize(content_to_hash))
        
        return cls(
            commit_id=commit_id,
            parent_id=parent_id,
            message=message,
            timestamp=timestamp_str,
            schema_snapshot=schema
        )
