from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def database_path() -> Path:
    override = os.getenv("AGENDA_DB_PATH")
    if override:
        return Path(override)
    return repo_root() / "data" / "database.json"


def readme_path() -> Path:
    override = os.getenv("AGENDA_README_PATH")
    if override:
        return Path(override)
    return repo_root() / "README.md"
