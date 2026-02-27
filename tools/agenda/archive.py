"""CLI para arquivar mês ou ano no database.

Arquivar aqui significa marcar `arquivado: True` para um mês (dentro de um ano)
ou para um ano inteiro, para que ele deixe de aparecer na página principal.

Este script é chamado via GitHub Actions e lê as variáveis de ambiente:
- archive_year: ano a ser arquivado
- archive_month: mês a ser arquivado (opcional)

Se `archive_month` vier vazio, o script arquiva o ano inteiro.
"""

import json
import os

from tools.agenda._paths import database_path


def open_database_file(file_path):
    """
    Abre um arquivo JSON para leitura e escrita de forma segura.
    Se o arquivo não existir, cria um novo com um dicionário vazio.

    Comportamento:
    - se o arquivo não existe: cria
    - se o JSON estiver inválido/corrompido: retorna `{}`
    """
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4)

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    return data


def archive_month(file_path, month_to_archive):        
    """Marca um mês específico como arquivado dentro de um ano.

    A operação é feita marcando `arquivado: True` no mês encontrado.
    """
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
    """Marca um ano inteiro como arquivado."""
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

    Campos esperados (definidos nos workflows):
    - archive_year
    - archive_month (opcional)
    """
    return {
        "ano": int(os.getenv("archive_year", 0)),
        "mes": os.getenv("archive_month", "").strip().lower(),
    }


def main() -> None:
    """Entry-point do CLI.

    Se `archive_month` vier vazio, arquiva o ano inteiro; caso contrário,
    arquiva somente o mês informado.
    """
    db_path = str(database_path())

    event = get_event_from_env()
    if event["mes"] == "":
        archive_year(db_path, event)
    else:
        archive_month(db_path, event)

if __name__ == "__main__":
    main()
