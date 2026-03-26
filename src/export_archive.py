import os

from jinja2 import Environment, FileSystemLoader

from utils import get_db_path, load_database


def get_archived_years(data):
    return [y for y in data.get("eventos", []) if y.get("arquivado", False)]
