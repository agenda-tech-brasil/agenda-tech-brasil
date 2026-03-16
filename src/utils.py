import json
import os


def get_db_path(src_file):
    """Retorna o caminho absoluto para db/database.json relativo ao arquivo chamador."""
    base_dir = os.path.dirname(os.path.abspath(src_file))
    return os.path.join(base_dir, "db", "database.json")


def load_database(file_path):
    """
    Carrega e retorna os dados de um arquivo JSON.
    Se o arquivo não existir, cria um novo com o schema mínimo esperado.
    Se o JSON estiver corrompido ou em formato inesperado, retorna o schema mínimo.
    O schema mínimo é {"eventos": [], "tba": []}.
    """
    default_data = {"eventos": [], "tba": []}

    # Se o arquivo não existir, cria com o schema mínimo usando o mesmo formato de save_database().
    if not os.path.exists(file_path):
        # Garante que o diretório pai exista antes de criar o arquivo.
        dir_path = os.path.dirname(file_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        # Retorna um novo dicionário para evitar compartilhamento acidental de referências mutáveis.
        return {"eventos": [], "tba": []}

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # JSON inválido: retorna sempre o schema mínimo esperado.
            return {"eventos": [], "tba": []}

    # Se o conteúdo não for um dicionário, normaliza para o schema mínimo.
    if not isinstance(data, dict):
        return {"eventos": [], "tba": []}

    # Garante que as chaves mínimas existam para evitar KeyError em outros pontos do código.
    data.setdefault("eventos", [])
    data.setdefault("tba", [])

    # Normaliza tipos inesperados: se "eventos" ou "tba" não forem listas, zera para [].
    if not isinstance(data.get("eventos"), list):
        data["eventos"] = []
    if not isinstance(data.get("tba"), list):
        data["tba"] = []

    return data


def save_database(file_path, data):
    """Salva data em um arquivo JSON com formatação padrão do projeto."""
    # Garante que o diretório pai exista antes de tentar salvar o arquivo.
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_year(data, year):
    """Busca e retorna a entrada do ano em data['eventos'], ou None."""
    return next((y for y in data["eventos"] if y["ano"] == year), None)


def find_month(year_data, month):
    """Busca e retorna a entrada do mês em year_data['meses'], ou None."""
    return next((m for m in year_data["meses"] if m["mes"] == month), None)
