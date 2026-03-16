import json
import os


def get_db_path(src_file):
    """Retorna o caminho absoluto para db/database.json relativo ao arquivo chamador."""
    base_dir = os.path.dirname(os.path.abspath(src_file))
    return os.path.join(base_dir, "db", "database.json")


def load_database(file_path):
    """
    Carrega e retorna os dados de um arquivo JSON.
    Se o arquivo não existir, cria um novo com dicionário vazio.
    Se o JSON estiver corrompido, retorna dicionário vazio.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_database(file_path, data):
    """Salva data em um arquivo JSON com formatação padrão do projeto."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_year(data, year):
    """Busca e retorna a entrada do ano em data['eventos'], ou None."""
    return next((y for y in data["eventos"] if y["ano"] == year), None)


def find_month(year_data, month):
    """Busca e retorna a entrada do mês em year_data['meses'], ou None."""
    return next((m for m in year_data["meses"] if m["mes"] == month), None)
