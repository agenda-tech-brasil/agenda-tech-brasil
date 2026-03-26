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
