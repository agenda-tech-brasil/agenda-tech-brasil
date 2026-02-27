import json

from remove_event import remove_event_from_json, remove_tba_from_json, get_event_from_env


def write_db(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_db(path):
    return json.loads(path.read_text(encoding="utf-8"))


def base_payload():
    return {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {
                        "mes": "junho",
                        "arquivado": False,
                        "eventos": [
                            {
                                "nome": "Evento X",
                                "data": ["10"],
                                "url": "https://x",
                                "cidade": "Recife",
                                "uf": "PE",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            }
        ],
        "tba": [
            {
                "nome": "Evento TBA",
                "url": "https://tba",
                "cidade": "Rio",
                "uf": "RJ",
                "tipo": "híbrido",
            }
        ],
    }


def test_remove_event_deletes_month_and_year_when_empty(tmp_path):
    db_path = tmp_path / "db.json"
    write_db(db_path, base_payload())

    event = {
        "ano": 2026,
        "mes": "junho",
        "evento": {
            "nome": "Evento X",
            "data": ["10"],
            "cidade": "recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    }

    remove_event_from_json(str(db_path), event)
    db = read_db(db_path)

    assert db["eventos"] == []


def test_remove_event_keeps_file_when_not_found(tmp_path):
    db_path = tmp_path / "db.json"
    payload = base_payload()
    write_db(db_path, payload)

    event = {
        "ano": 2026,
        "mes": "junho",
        "evento": {
            "nome": "Inexistente",
            "data": ["10"],
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    }

    remove_event_from_json(str(db_path), event)
    db = read_db(db_path)

    assert db == payload


def test_remove_event_year_not_found_keeps_file(tmp_path):
    db_path = tmp_path / "db.json"
    payload = base_payload()
    write_db(db_path, payload)

    event = {
        "ano": 1999,
        "mes": "junho",
        "evento": {
            "nome": "Evento X",
            "data": ["10"],
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    }

    remove_event_from_json(str(db_path), event)
    assert read_db(db_path) == payload


def test_remove_event_month_not_found_keeps_file(tmp_path):
    db_path = tmp_path / "db.json"
    payload = base_payload()
    write_db(db_path, payload)

    event = {
        "ano": 2026,
        "mes": "julho",
        "evento": {
            "nome": "Evento X",
            "data": ["10"],
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    }

    remove_event_from_json(str(db_path), event)
    assert read_db(db_path) == payload


def test_remove_tba_removes_matching_event(tmp_path):
    db_path = tmp_path / "db.json"
    write_db(db_path, base_payload())

    event = {
        "evento": {
            "nome": "Evento TBA",
            "cidade": "rio",
            "uf": "RJ",
            "tipo": "híbrido",
        }
    }

    remove_tba_from_json(str(db_path), event)
    db = read_db(db_path)

    assert db["tba"] == []


def test_remove_tba_keeps_file_when_not_found(tmp_path):
    db_path = tmp_path / "db.json"
    payload = base_payload()
    write_db(db_path, payload)

    event = {
        "evento": {
            "nome": "Nao Existe",
            "cidade": "rio",
            "uf": "RJ",
            "tipo": "híbrido",
        }
    }

    remove_tba_from_json(str(db_path), event)
    assert read_db(db_path) == payload


def test_get_event_from_env_normalizes_fields(monkeypatch):
    monkeypatch.setenv("event_year", "2028")
    monkeypatch.setenv("event_month", " TBA ")
    monkeypatch.setenv("event_name", "  Evento Z  ")
    monkeypatch.setenv("event_day", " 15, 16 ")
    monkeypatch.setenv("event_url", " https://z ")
    monkeypatch.setenv("event_city", " belo horizonte ")
    monkeypatch.setenv("event_state", " MG ")
    monkeypatch.setenv("event_type", " ONLINE ")

    event = get_event_from_env()

    assert event["ano"] == 2028
    assert event["mes"] == "tba"
    assert event["evento"]["data"] == ["15", "16"]
    assert event["evento"]["cidade"] == "Belo Horizonte"
    assert event["evento"]["tipo"] == "online"
