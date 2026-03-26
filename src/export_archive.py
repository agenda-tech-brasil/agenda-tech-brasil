import os

from jinja2 import Environment, FileSystemLoader

from generate_page import format_date_list
from utils import get_db_path, load_database


def get_archived_years(data):
    return [y for y in data.get("eventos", []) if y.get("arquivado", False)]


def render_archive(year_data, template_path):
    env = Environment(
        loader=FileSystemLoader(template_path),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_date_list"] = format_date_list
    template = env.get_template("archive.md.j2")
    return template.render(ano=year_data)


def export_archives(db_path, template_path, output_dir):
    data = load_database(db_path)
    archived_years = get_archived_years(data)

    os.makedirs(output_dir, exist_ok=True)

    for year_data in archived_years:
        if not year_data.get("meses"):
            continue

        content = render_archive(year_data, template_path)
        output_path = os.path.join(output_dir, f"{year_data['ano']}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Arquivo {year_data['ano']}.md gerado com sucesso!")
