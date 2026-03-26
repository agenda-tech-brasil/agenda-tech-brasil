import json
import os
from unittest.mock import patch

from export_archive import get_archived_years


def write_db(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_db(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_get_archived_years_returns_only_archived():
    data = {
        "eventos": [
            {"ano": 2024, "arquivado": True, "meses": []},
            {"ano": 2025, "arquivado": False, "meses": []},
            {"ano": 2023, "arquivado": True, "meses": [{"mes": "janeiro", "eventos": []}]},
        ],
        "tba": [],
    }

    result = get_archived_years(data)

    assert len(result) == 2
    assert result[0]["ano"] == 2024
    assert result[1]["ano"] == 2023


def test_get_archived_years_returns_empty_when_none_archived():
    data = {
        "eventos": [
            {"ano": 2026, "arquivado": False, "meses": []},
        ],
        "tba": [],
    }

    result = get_archived_years(data)

    assert result == []
