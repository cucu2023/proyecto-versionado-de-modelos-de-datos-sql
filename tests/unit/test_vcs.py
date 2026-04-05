import pytest
from datetime import datetime, timezone
from pathlib import Path
from schema_evolver.core.models import Schema, Table, Column
from schema_evolver.core.vcs import Commit
from schema_evolver.storage.repository import SchemaRepository
from schema_evolver.utils.serialization import deterministic_serialize
from schema_evolver.diff.engine import AddTable, RemoveTable

def test_serializer_determinism():
    data = {"b": 2, "a": 1, "c": [3, 2, 1]}
    assert deterministic_serialize(data) == '{"a": 1, "b": 2, "c": [3, 2, 1]}'

def test_commit_determinism():
    schema = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True)
        })
    })
    
    timestamp = datetime(2026, 3, 23, 12, 0, 0, tzinfo=timezone.utc)
    message = "Initial commit"
    
    commit1 = Commit.create(schema=schema, message=message, timestamp=timestamp)
    commit2 = Commit.create(schema=schema, message=message, timestamp=timestamp)
    
    assert commit1.commit_id == commit2.commit_id
    assert commit1.timestamp == "2026-03-23T12:00:00+00:00"

def test_commit_immutability():
    schema = Schema(tables={})
    commit = Commit.create(schema=schema, message="test")
    
    with pytest.raises(Exception): # Pydantic frozen model
        commit.message = "new message"

def test_repository_flow(tmp_path):
    repo = SchemaRepository(str(tmp_path))
    repo.init()
    
    # Verify directory structure
    assert (tmp_path / ".schema_evolver").exists()
    assert (tmp_path / ".schema_evolver" / "commits").exists()
    
    # First commit
    schema1 = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True)
        })
    })
    commit1 = repo.commit(schema1, "Initial commit")
    
    assert repo.get_head_id() == commit1.commit_id
    assert (tmp_path / ".schema_evolver" / "commits" / f"{commit1.commit_id}.json").exists()
    
    # Second commit
    schema2 = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True)
        }),
        "posts": Table(name="posts", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True),
            "user_id": Column(name="user_id", type="INTEGER")
        })
    })
    commit2 = repo.commit(schema2, "Add posts table")
    
    assert repo.get_head_id() == commit2.commit_id
    assert commit2.parent_id == commit1.commit_id
    
    # Load commit
    loaded_commit = repo.load_commit(commit1.commit_id)
    assert loaded_commit.message == "Initial commit"
    assert "users" in loaded_commit.schema_snapshot.tables

def test_repository_diff(tmp_path):
    repo = SchemaRepository(str(tmp_path))
    repo.init()
    
    schema1 = Schema(tables={
        "users": Table(name="users", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True)
        })
    })
    commit1 = repo.commit(schema1, "C1")
    
    schema2 = Schema(tables={
        "posts": Table(name="posts", columns={
            "id": Column(name="id", type="INTEGER", primary_key=True)
        })
    })
    commit2 = repo.commit(schema2, "C2")
    
    diff = repo.diff(commit1.commit_id, commit2.commit_id)
    
    # Expect: Remove users, Add posts
    ops = {op.type for op in diff}
    assert "remove_table" in ops
    assert "add_table" in ops
    
    remove_op = next(op for op in diff if isinstance(op, RemoveTable))
    add_op = next(op for op in diff if isinstance(op, AddTable))
    
    assert remove_op.table_name == "users"
    assert add_op.table_name == "posts"
