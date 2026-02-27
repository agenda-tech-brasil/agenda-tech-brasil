import json

from add_event import add_event_to_json, add_tba_to_json, get_event_from_env


def write_db(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_db(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_add_event_creates_year_month_and_sorts(tmp_path):
    db_path = tmp_path / "db.json"
    payload = {
        "eventos": [
            {
                "ano": 2025,
                "arquivado": False,
                "meses": [
                    {"mes": "março", "arquivado": False, "eventos": []},
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, payload)

    new_event = {
        "ano": 2024,
        "mes": "janeiro",
        "evento": {
            "nome": "Evento A",
            "data": ["10", "11"],
            "url": "https://exemplo.com",
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    }

    add_event_to_json(str(db_path), new_event)
    db = read_db(db_path)

    assert [y["ano"] for y in db["eventos"]] == [2024, 2025]
    assert db["eventos"][0]["meses"][0]["mes"] == "janeiro"
    assert db["eventos"][0]["meses"][0]["eventos"][0]["nome"] == "Evento A"


def test_add_event_sorts_events_by_date_and_duration(tmp_path):
    db_path = tmp_path / "db.json"
    payload = {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {
                        "mes": "abril",
                        "arquivado": False,
                        "eventos": [
                            {
                                "nome": "Evento Longo",
                                "data": ["15", "16"],
                                "url": "u1",
                                "cidade": "C",
                                "uf": "SP",
                                "tipo": "online",
                            },
                            {
                                "nome": "Evento Curto",
                                "data": ["15"],
                                "url": "u2",
                                "cidade": "C",
                                "uf": "SP",
                                "tipo": "online",
                            },
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, payload)

    new_event = {
        "ano": 2026,
        "mes": "abril",
        "evento": {
            "nome": "Evento Antes",
            "data": ["01"],
            "url": "u3",
            "cidade": "C",
            "uf": "SP",
            "tipo": "online",
        },
    }

    add_event_to_json(str(db_path), new_event)
    events = read_db(db_path)["eventos"][0]["meses"][0]["eventos"]

    assert [e["nome"] for e in events] == ["Evento Antes", "Evento Curto", "Evento Longo"]


def test_add_tba_deduplicates_event(tmp_path):
    db_path = tmp_path / "db.json"
    payload = {
        "eventos": [],
        "tba": [
            {
                "nome": "Evento TBA",
                "url": "https://tba.com",
                "cidade": "São Paulo",
                "uf": "SP",
                "tipo": "presencial",
            }
        ],
    }
    write_db(db_path, payload)

    new_event = {
        "evento": {
            "nome": "Evento TBA",
            "url": "https://tba.com",
            "cidade": "São Paulo",
            "uf": "SP",
            "tipo": "presencial",
        }
    }

    add_tba_to_json(str(db_path), new_event)
    db = read_db(db_path)

    assert len(db["tba"]) == 1


def test_add_tba_adds_new_event_when_missing(tmp_path):
    db_path = tmp_path / "db.json"
    payload = {
        "eventos": [],
        "tba": [],
    }
    write_db(db_path, payload)

    new_event = {
        "evento": {
            "nome": "Evento Novo",
            "url": "https://novo.com",
            "cidade": "São Paulo",
            "uf": "SP",
            "tipo": "presencial",
        }
    }

    add_tba_to_json(str(db_path), new_event)
    db = read_db(db_path)

    assert db["tba"] == [
        {
            "nome": "Evento Novo",
            "url": "https://novo.com",
            "cidade": "São Paulo",
            "uf": "SP",
            "tipo": "presencial",
        }
    ]


def test_get_event_from_env_normalizes_fields(monkeypatch):
    monkeypatch.setenv("event_year", "2027")
    monkeypatch.setenv("event_month", "  Março ")
    monkeypatch.setenv("event_name", "  Python Brasil  ")
    monkeypatch.setenv("event_day", " 03, 01 ,02 ")
    monkeypatch.setenv("event_url", " https://py.br ")
    monkeypatch.setenv("event_city", " são paulo ")
    monkeypatch.setenv("event_state", " SP ")
    monkeypatch.setenv("event_type", " online ")

    event = get_event_from_env()

    assert event["ano"] == 2027
    assert event["mes"] == "março"
    assert event["evento"]["nome"] == "Python Brasil"
    assert event["evento"]["data"] == ["01", "02", "03"]
    assert event["evento"]["cidade"] == "São Paulo"
    assert event["evento"]["uf"] == "SP"
    assert event["evento"]["tipo"] == "online"
