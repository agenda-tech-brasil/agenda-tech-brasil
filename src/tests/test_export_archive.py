import json
import os
from unittest.mock import patch

from export_archive import get_archived_years, render_archive, export_archives, main


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


def test_render_archive_produces_markdown(tmp_path):
    template_dir = tmp_path / "templates"
    template_dir.mkdir()

    template_content = (
        "{% for mes in ano.meses %}"
        "### {{ mes.mes | capitalize }}\n"
        "{% for evento in mes.eventos %}"
        "- {{ evento.data | format_date_list }}: [{{ evento.nome }}]({{ evento.url }})"
        "{% if evento.tipo != 'online' %} - _{{ evento.cidade }}/{{ evento.uf }}_{% endif %}"
        " ![{{ evento.tipo }}]\n"
        "{% endfor %}"
        "{% endfor %}"
    )
    (template_dir / "archive.md.j2").write_text(template_content, encoding="utf-8")

    year_data = {
        "ano": 2024,
        "arquivado": True,
        "meses": [
            {
                "mes": "janeiro",
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
            },
            {
                "mes": "fevereiro",
                "eventos": [
                    {
                        "nome": "Evento B",
                        "data": ["05"],
                        "url": "https://b",
                        "cidade": "",
                        "uf": "",
                        "tipo": "online",
                    }
                ],
            },
        ],
    }

    result = render_archive(year_data, str(template_dir))

    assert "### Janeiro" in result
    assert "10 e 11: [Evento A](https://a) - _São Paulo/SP_ ![presencial]" in result
    assert "### Fevereiro" in result
    assert "05: [Evento B](https://b) ![online]" in result


def test_export_archives_creates_year_files(tmp_path):
    db_path = tmp_path / "db.json"
    template_dir = tmp_path / "templates"
    output_dir = tmp_path / "arquivo"
    template_dir.mkdir()

    template_content = (
        "{% for mes in ano.meses %}"
        "### {{ mes.mes | capitalize }}\n"
        "{% for evento in mes.eventos %}"
        "- {{ evento.data | format_date_list }}: [{{ evento.nome }}]({{ evento.url }})"
        "{% if evento.tipo != 'online' %} - _{{ evento.cidade }}/{{ evento.uf }}_{% endif %}"
        " ![{{ evento.tipo }}]\n"
        "{% endfor %}"
        "{% endfor %}"
    )
    (template_dir / "archive.md.j2").write_text(template_content, encoding="utf-8")

    db_data = {
        "eventos": [
            {
                "ano": 2024,
                "arquivado": True,
                "meses": [
                    {
                        "mes": "março",
                        "eventos": [
                            {
                                "nome": "Conf X",
                                "data": ["15"],
                                "url": "https://x",
                                "cidade": "Recife",
                                "uf": "PE",
                                "tipo": "presencial",
                            }
                        ],
                    }
                ],
            },
            {
                "ano": 2026,
                "arquivado": False,
                "meses": [
                    {
                        "mes": "janeiro",
                        "eventos": [
                            {
                                "nome": "Evento Y",
                                "data": ["01"],
                                "url": "https://y",
                                "cidade": "",
                                "uf": "",
                                "tipo": "online",
                            }
                        ],
                    }
                ],
            },
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    export_archives(str(db_path), str(template_dir), str(output_dir))

    assert (output_dir / "2024.md").exists()
    content = (output_dir / "2024.md").read_text(encoding="utf-8")
    assert "### Março" in content
    assert "Conf X" in content
    assert not (output_dir / "2026.md").exists()


def test_export_archives_skips_archived_year_without_meses(tmp_path):
    db_path = tmp_path / "db.json"
    template_dir = tmp_path / "templates"
    output_dir = tmp_path / "arquivo"
    template_dir.mkdir()

    (template_dir / "archive.md.j2").write_text("{{ ano.ano }}", encoding="utf-8")

    db_data = {
        "eventos": [
            {"ano": 2022, "arquivado": True, "meses": []},
        ],
        "tba": [],
    }
    write_db(db_path, db_data)

    export_archives(str(db_path), str(template_dir), str(output_dir))

    assert not (output_dir / "2022.md").exists()


def test_main_calls_export_archives_with_expected_paths():
    with patch("export_archive.export_archives") as mocked_export, patch(
        "builtins.print"
    ) as mocked_print:
        main()

    mocked_export.assert_called_once()
    mocked_print.assert_called_once()
    db_path, template_path, output_dir = mocked_export.call_args.args

    assert db_path.endswith(os.path.join("src", "db", "database.json"))
    assert template_path.endswith(os.path.join("src", "templates"))
    assert output_dir.endswith(os.sep + "arquivo")
