import os
import json
from typing import List, Optional
from pathlib import Path
from schema_evolver.core.models import Schema
from schema_evolver.core.vcs import Commit
from schema_evolver.diff.engine import DiffEngine, SchemaOperation

class SchemaRepository:
    """Filesystem-based repository for schema commits."""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.repo_dir = self.base_path / ".schema_evolver"
        self.commits_dir = self.repo_dir / "commits"
        self.head_file = self.repo_dir / "HEAD"

    def init(self):
        """Initializes the repository structure."""
        self.repo_dir.mkdir(parents=True, exist_ok=True)
        self.commits_dir.mkdir(parents=True, exist_ok=True)

    def save_commit(self, commit: Commit):
        """Persists a commit to disk."""
        commit_path = self.commits_dir / f"{commit.commit_id}.json"
        with open(commit_path, "w", encoding="utf-8") as f:
            f.write(commit.model_dump_json(indent=2))
        
        # Update HEAD
        with open(self.head_file, "w", encoding="utf-8") as f:
            f.write(commit.commit_id)

    def load_commit(self, commit_id: str) -> Commit:
        """Loads a commit from disk."""
        commit_path = self.commits_dir / f"{commit_id}.json"
        if not commit_path.exists():
            raise FileNotFoundError(f"Commit {commit_id} not found.")
        
        with open(commit_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Commit(**data)

    def get_head_id(self) -> Optional[str]:
        """Returns the current HEAD commit ID."""
        if not self.head_file.exists():
            return None
        with open(self.head_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    def commit(self, schema: Schema, message: str) -> Commit:
        """Creates and saves a new commit."""
        parent_id = self.get_head_id()
        new_commit = Commit.create(schema=schema, message=message, parent_id=parent_id)
        self.save_commit(new_commit)
        return new_commit

    def diff(self, commit_id_1: str, commit_id_2: str) -> List[SchemaOperation]:
        """Computes a semantic diff between two commits."""
        commit_1 = self.load_commit(commit_id_1)
        commit_2 = self.load_commit(commit_id_2)
        
        engine = DiffEngine()
        return engine.diff(commit_1.schema_snapshot, commit_2.schema_snapshot)
