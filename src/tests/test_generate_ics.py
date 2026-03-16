import sys
import os
import json
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.generate_ics import generate_ics


def test_generate_ics_success():

    fake_db = {
        "events": [
            {
                "name": "Live Python",
                "date": "2026-05-20",
                "link": "https://exemplo.com",
                "location": "YouTube"
            }
        ]
    }

    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)) as m:
        with patch("os.path.exists", return_value=True):
            result = generate_ics()

    assert result is True
    m.assert_any_call("agenda.ics", "wb")


def test_generate_ics_no_database():

    with patch("os.path.exists", return_value=False):
        result = generate_ics()

    assert result is None


def test_generate_ics_invalid_date():

    fake_db = [
        {"name": "Evento", "date": "data-errada"}
    ]

    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)):
        with patch("os.path.exists", return_value=True):
            result = generate_ics()

    assert result is True


def test_generate_ics_eventos_key():

    fake_db = {
        "eventos": [
            {"titulo": "Evento BR", "data": "2026-01-01"}
        ]
    }

    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)):
        with patch("os.path.exists", return_value=True):
            result = generate_ics()

    assert result is True


def test_generate_ics_non_dict_item():

    fake_db = [
        "evento invalido"
    ]

    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)):
        with patch("os.path.exists", return_value=True):
            result = generate_ics()

    assert result is True


def test_generate_ics_default_values():

    fake_db = [{}]

    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)):
        with patch("os.path.exists", return_value=True):
            result = generate_ics()

    assert result is True