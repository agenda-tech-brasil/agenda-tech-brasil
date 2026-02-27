import json
from datetime import datetime

from generate_page import format_date_list, generate_readme, get_available_months


def test_format_date_list_multiple_dates():
    assert format_date_list(["01", "02", "03"]) == "01, 02 e 03"


def test_format_date_list_single_date():
    assert format_date_list(["15"]) == "15"


def test_get_available_months_filters_archived_months():
    data = {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {"mes": "janeiro", "arquivado": False},
                    {"mes": "fevereiro", "arquivado": True},
                ],
            }
        ]
    }

    assert get_available_months(data, 2026) == ["janeiro"]


def test_get_available_months_returns_empty_when_year_missing():
    assert get_available_months({"eventos": []}, 2026) == []


def test_generate_readme_renders_output(tmp_path):
    db_path = tmp_path / "database.json"
    template_dir = tmp_path / "templates"
    output_path = tmp_path / "README.md"
    template_dir.mkdir()

    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {
                        "mes": "janeiro",
                        "arquivado": False,
                        "eventos": [
                            {
                                "nome": "Evento A",
                                "data": ["10", "11"],
                                "url": "https://a",
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

    db_path.write_text(json.dumps(db_data, ensure_ascii=False), encoding="utf-8")
    template = (
        "Meses: {% for mes in link_meses %}{{ mes }} {% endfor %}\\n"
        "{% for ano in data.eventos %}{% for mes in ano.meses %}"
        "{% for evento in mes.eventos %}{{ evento.data|format_date_list }} - {{ evento.nome }}{% endfor %}"
        "{% endfor %}{% endfor %}"
    )
    (template_dir / "events.md.j2").write_text(template, encoding="utf-8")

    generate_readme(
        str(db_path),
        str(template_dir),
        str(output_path),
        now=datetime(2026, 1, 1),
    )

    output = output_path.read_text(encoding="utf-8")
    assert "Meses: janeiro" in output
    assert "10 e 11 - Evento A" in output


def test_generate_readme_renders_two_events(tmp_path):
    db_path = tmp_path / "database.json"
    template_dir = tmp_path / "templates"
    output_path = tmp_path / "README.md"
    template_dir.mkdir()

    db_data = {
        "eventos": [
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {
                        "mes": "janeiro",
                        "arquivado": False,
                        "eventos": [
                            {
                                "nome": "Evento A",
                                "data": ["10", "11"],
                                "url": "https://a",
                                "cidade": "São Paulo",
                                "uf": "SP",
                                "tipo": "presencial",
                            },
                            {
                                "nome": "Evento B",
                                "data": ["20"],
                                "url": "https://b",
                                "cidade": "Rio de Janeiro",
                                "uf": "RJ",
                                "tipo": "presencial",
                            },
                        ],
                    }
                ],
            }
        ],
        "tba": [],
    }

    db_path.write_text(json.dumps(db_data, ensure_ascii=False), encoding="utf-8")
    template = (
        "Meses: {% for mes in link_meses %}{{ mes }} {% endfor %}\\n"
        "{% for ano in data.eventos %}{% for mes in ano.meses %}"
        "{% for evento in mes.eventos %}{{ evento.data|format_date_list }} - {{ evento.nome }}{% endfor %}"
        "{% endfor %}{% endfor %}"
    )
    (template_dir / "events.md.j2").write_text(template, encoding="utf-8")

    generate_readme(
        str(db_path),
        str(template_dir),
        str(output_path),
        now=datetime(2026, 1, 1),
    )

    output = output_path.read_text(encoding="utf-8")
    assert "Meses: janeiro" in output
    assert "10 e 11 - Evento A" in output
    assert "20 - Evento B" in output
