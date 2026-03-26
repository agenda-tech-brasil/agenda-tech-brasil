import json
from unittest.mock import patch

from validate_database import (
    validate_event,
    validate_month,
    validate_year,
    validate_tba,
    validate_database,
    main,
)


def write_db(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def read_db(path):
    return json.loads(path.read_text(encoding="utf-8"))


def valid_presencial_event():
    return {
        "nome": "Conf X",
        "data": ["10", "11"],
        "url": "https://confx.com",
        "cidade": "São Paulo",
        "uf": "SP",
        "tipo": "presencial",
    }


def valid_online_event():
    return {
        "nome": "Webinar Y",
        "data": ["05"],
        "url": "https://webinar.com",
        "cidade": "",
        "uf": "",
        "tipo": "online",
    }


def test_validate_event_valid_presencial_returns_no_errors():
    errors = validate_event(valid_presencial_event(), "test")
    assert errors == []


def test_validate_event_valid_online_returns_no_errors():
    errors = validate_event(valid_online_event(), "test")
    assert errors == []


def test_validate_event_empty_nome():
    event = valid_presencial_event()
    event["nome"] = ""
    errors = validate_event(event, "test")
    assert any("nome" in e for e in errors)


def test_validate_event_invalid_data_not_numeric():
    event = valid_presencial_event()
    event["data"] = ["abc"]
    errors = validate_event(event, "test")
    assert any("data" in e for e in errors)


def test_validate_event_data_out_of_range():
    event = valid_presencial_event()
    event["data"] = ["32"]
    errors = validate_event(event, "test")
    assert any("data" in e for e in errors)


def test_validate_event_data_without_zero_pad():
    event = valid_presencial_event()
    event["data"] = ["5"]
    errors = validate_event(event, "test")
    assert any("data" in e for e in errors)


def test_validate_event_invalid_url():
    event = valid_presencial_event()
    event["url"] = "ftp://bad"
    errors = validate_event(event, "test")
    assert any("url" in e for e in errors)


def test_validate_event_invalid_tipo():
    event = valid_presencial_event()
    event["tipo"] = "virtual"
    errors = validate_event(event, "test")
    assert any("tipo" in e for e in errors)


def test_validate_event_online_with_cidade():
    event = valid_online_event()
    event["cidade"] = "São Paulo"
    errors = validate_event(event, "test")
    assert any("cidade" in e for e in errors)


def test_validate_event_presencial_without_cidade():
    event = valid_presencial_event()
    event["cidade"] = ""
    errors = validate_event(event, "test")
    assert any("cidade" in e for e in errors)


def test_validate_event_invalid_uf():
    event = valid_presencial_event()
    event["uf"] = "XX"
    errors = validate_event(event, "test")
    assert any("uf" in e for e in errors)


def test_validate_month_valid_returns_no_errors():
    month = {
        "mes": "janeiro",
        "eventos": [valid_presencial_event()],
    }
    errors = validate_month(month, "test")
    assert errors == []


def test_validate_month_invalid_name():
    month = {
        "mes": "janero",
        "eventos": [valid_presencial_event()],
    }
    errors = validate_month(month, "test")
    assert any("mes" in e for e in errors)


def test_validate_month_empty_eventos():
    month = {
        "mes": "janeiro",
        "eventos": [],
    }
    errors = validate_month(month, "test")
    assert any("eventos" in e for e in errors)


def test_validate_year_valid_returns_no_errors():
    year = {
        "ano": 2026,
        "meses": [
            {"mes": "janeiro", "eventos": [valid_presencial_event()]},
            {"mes": "março", "eventos": [valid_online_event()]},
        ],
    }
    errors = validate_year(year, "test")
    assert errors == []


def test_validate_year_invalid_ano():
    year = {
        "ano": -1,
        "meses": [{"mes": "janeiro", "eventos": [valid_presencial_event()]}],
    }
    errors = validate_year(year, "test")
    assert any("ano" in e for e in errors)


def test_validate_event_empty_data():
    event = valid_presencial_event()
    event["data"] = []
    errors = validate_event(event, "test")
    assert any("data" in e for e in errors)


def test_validate_event_online_with_uf():
    event = valid_online_event()
    event["uf"] = "SP"
    errors = validate_event(event, "test")
    assert any("uf" in e for e in errors)


def test_validate_event_presencial_without_uf():
    event = valid_presencial_event()
    event["uf"] = ""
    errors = validate_event(event, "test")
    assert any("uf" in e for e in errors)


def test_validate_year_empty_meses():
    year = {
        "ano": 2026,
        "meses": [],
    }
    errors = validate_year(year, "test")
    assert any("meses" in e for e in errors)


def test_validate_year_months_out_of_order():
    year = {
        "ano": 2026,
        "meses": [
            {"mes": "março", "eventos": [valid_presencial_event()]},
            {"mes": "janeiro", "eventos": [valid_online_event()]},
        ],
    }
    errors = validate_year(year, "test")
    assert any("ordem" in e for e in errors)


def test_validate_tba_valid_returns_no_errors():
    tba = [
        {
            "nome": "Evento TBA",
            "url": "https://tba.com",
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        }
    ]
    errors = validate_tba(tba)
    assert errors == []


def test_validate_tba_detects_duplicates():
    tba = [
        {
            "nome": "Evento TBA",
            "url": "https://tba.com",
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
        {
            "nome": "Evento TBA",
            "url": "https://other.com",
            "cidade": "Recife",
            "uf": "PE",
            "tipo": "presencial",
        },
    ]
    errors = validate_tba(tba)
    assert any("duplicado" in e for e in errors)


def test_validate_database_valid_db(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {
                        "mes": "janeiro",
                        "eventos": [
                            {
                                "nome": "Evento A",
                                "data": ["10"],
                                "url": "https://a.com",
                                "cidade": "São Paulo",
                                "uf": "SP",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    errors = validate_database(str(db_path))

    assert errors == []


def test_validate_database_catches_nested_errors(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {
                        "mes": "janeiro",
                        "eventos": [
                            {
                                "nome": "",
                                "data": ["10"],
                                "url": "https://a.com",
                                "cidade": "São Paulo",
                                "uf": "SP",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    errors = validate_database(str(db_path))

    assert len(errors) > 0
    assert any("nome" in e for e in errors)


def test_validate_database_years_out_of_order(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {"mes": "janeiro", "eventos": [valid_presencial_event()]},
                ],
            },
            {
                "ano": 2025,
                "meses": [
                    {"mes": "janeiro", "eventos": [valid_presencial_event()]},
                ],
            },
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    errors = validate_database(str(db_path))
    assert any("ordem" in e for e in errors)


def test_validate_database_duplicate_years(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {"mes": "janeiro", "eventos": [valid_presencial_event()]},
                ],
            },
            {
                "ano": 2026,
                "meses": [
                    {"mes": "fevereiro", "eventos": [valid_presencial_event()]},
                ],
            },
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    errors = validate_database(str(db_path))
    assert any("duplicados" in e for e in errors)


def test_main_returns_zero_on_valid_db(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {
                        "mes": "janeiro",
                        "eventos": [
                            {
                                "nome": "Evento",
                                "data": ["01"],
                                "url": "https://e.com",
                                "cidade": "São Paulo",
                                "uf": "SP",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    with patch("validate_database.get_db_path", return_value=str(db_path)):
        exit_code = main()

    assert exit_code == 0


def test_main_returns_one_on_invalid_db(tmp_path):
    db_path = tmp_path / "db.json"
    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "meses": [
                    {
                        "mes": "janeiro",
                        "eventos": [
                            {
                                "nome": "",
                                "data": ["10"],
                                "url": "https://a.com",
                                "cidade": "São Paulo",
                                "uf": "SP",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    with patch("validate_database.get_db_path", return_value=str(db_path)):
        exit_code = main()

    assert exit_code == 1
