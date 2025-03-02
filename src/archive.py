import json
import os

def open_database_file(file_path):
    """
    Abre um arquivo JSON para leitura e escrita de forma segura.
    Se o arquivo não existir, cria um novo com um dicionário vazio.
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    # Abre o arquivo em modo leitura e escrita
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)  # Lê o conteúdo do arquivo JSON
        except json.JSONDecodeError:
            data = {}  # Se o JSON estiver corrompido, usa um dicionário vazio

    return data


def archive_month(file_path, month_to_archive):        
    db = open_database_file(file_path=file_path)
    year = month_to_archive["ano"]
    month = month_to_archive["mes"]

    year_exist = next((y for y in db["eventos"] if y["ano"] == year), None)
    if not year_exist:
        print(f"Ano {year} não encontrado no arquivo.")
        return
    
    month_exist = next((m for m in year_exist["meses"] if m["mes"] == month), None)
    if not month_exist:
        print(f"Mês {month} não encontrado no ano {year}.")
        return

    for eventos in db["eventos"]:
        if eventos["ano"] == year:
            for meses in eventos["meses"]:
                if meses["mes"] == month:
                    meses["arquivado"] = True
    
    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(db, f, indent=2, ensure_ascii=False)

def archive_year(file_path, year_to_archive):        
    db = open_database_file(file_path=file_path)
    year = year_to_archive["ano"]

    year_exist = next((y for y in db["eventos"] if y["ano"] == year), None)
    if not year_exist:
        print(f"Ano {year} não encontrado no arquivo.")
        return

    for eventos in db["eventos"]:
        if eventos["ano"] == year:
            eventos["arquivado"] = True

    with open(file_path, "w", encoding="utf-8") as f:
      json.dump(db, f, indent=2, ensure_ascii=False)
    
def get_event_from_env():
    """
    Recebe informações do evento de variáveis de ambiente configuradas no GitHub Actions.
    """
    return {
        "ano": int(os.getenv("archive_year", 0)),
        "mes": os.getenv("archive_month", "").strip().lower(),
    }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'db', 'database.json')

    event = get_event_from_env()
    if event["mes"] == "":
        archive_year(db_path, event)
    else:
        archive_month(db_path, event)
