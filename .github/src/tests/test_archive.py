import json

from archive import archive_month, archive_year, open_database_file


def write_db(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_db(path):
    return json.loads(path.read_text(encoding="utf-8"))


def payload():
    return {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {"mes": "janeiro", "arquivado": False, "eventos": []},
                    {"mes": "fevereiro", "arquivado": False, "eventos": []},
                ],
            }
        ],
        "tba": [],
    }


def test_open_database_file_creates_nonexistent_file(tmp_path):
    db_path = tmp_path / "new.json"

    data = open_database_file(str(db_path))

    assert db_path.exists()
    assert data == {}


def test_open_database_file_handles_invalid_json(tmp_path):
    db_path = tmp_path / "broken.json"
    db_path.write_text("{invalid", encoding="utf-8")

    data = open_database_file(str(db_path))

    assert data == {}


def test_archive_month_marks_only_target_month(tmp_path):
    db_path = tmp_path / "db.json"
    write_db(db_path, payload())

    archive_month(str(db_path), {"ano": 2026, "mes": "fevereiro"})
    db = read_db(db_path)

    jan = db["eventos"][0]["meses"][0]
    feb = db["eventos"][0]["meses"][1]
    assert jan["arquivado"] is False
    assert feb["arquivado"] is True


def test_archive_year_marks_year_as_archived(tmp_path):
    db_path = tmp_path / "db.json"
    write_db(db_path, payload())

    archive_year(str(db_path), {"ano": 2026})
    db = read_db(db_path)

    assert db["eventos"][0]["arquivado"] is True


def test_archive_month_not_found_keeps_data(tmp_path):
    db_path = tmp_path / "db.json"
    original = payload()
    write_db(db_path, original)

    archive_month(str(db_path), {"ano": 2026, "mes": "março"})

    assert read_db(db_path) == original


def test_archive_month_year_not_found_keeps_data(tmp_path):
    db_path = tmp_path / "db.json"
    original = payload()
    write_db(db_path, original)

    archive_month(str(db_path), {"ano": 1999, "mes": "janeiro"})

    assert read_db(db_path) == original


def test_archive_year_year_not_found_keeps_data(tmp_path):
    db_path = tmp_path / "db.json"
    original = payload()
    write_db(db_path, original)

    archive_year(str(db_path), {"ano": 1999})

    assert read_db(db_path) == original
