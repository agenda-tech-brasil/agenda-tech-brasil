import os
import json
import pytest
from unittest.mock import patch, mock_open
from src.generate_ics import generate_ics

def test_generate_ics_success():
    fake_db = {
        "events": [
            {
                "name": "Live de Python",
                "date": "2026-05-20",
                "link": "https://exemplo.com",
                "location": "YouTube"
            }
        ]
    }
    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)) as mocked_file:
        with patch("os.path.exists", return_value=True):
            generate_ics()
            
            mocked_file.assert_any_call('agenda.ics', 'wb')

def test_generate_ics_no_db():

    with patch("os.path.exists", return_value=False):
      
        assert generate_ics() is None

def test_generate_ics_invalid_date():

    fake_db = [{"name": "Erro", "date": "data-errada"}]
    json_data = json.dumps(fake_db)

    with patch("builtins.open", mock_open(read_data=json_data)):
        with patch("os.path.exists", return_value=True):
         
            generate_ics()