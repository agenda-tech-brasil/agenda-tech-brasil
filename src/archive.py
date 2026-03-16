import os

from utils import find_month, find_year, get_db_path, load_database, save_database


def archive_month(file_path, month_to_archive):
    db = load_database(file_path)
    year = month_to_archive["ano"]
    month = month_to_archive["mes"]

    year_exist = find_year(db, year)
    if not year_exist:
        print(f"Ano {year} não encontrado no arquivo.")
        return

    month_exist = find_month(year_exist, month)
    if not month_exist:
        print(f"Mês {month} não encontrado no ano {year}.")
        return

    for eventos in db["eventos"]:
        if eventos["ano"] == year:
            for meses in eventos["meses"]:
                if meses["mes"] == month:
                    meses["arquivado"] = True

    save_database(file_path, db)

def archive_year(file_path, year_to_archive):
    db = load_database(file_path)
    year = year_to_archive["ano"]

    year_exist = find_year(db, year)
    if not year_exist:
        print(f"Ano {year} não encontrado no arquivo.")
        return

    for eventos in db["eventos"]:
        if eventos["ano"] == year:
            eventos["arquivado"] = True

    save_database(file_path, db)
    
def get_event_from_env():
    """
    Recebe informações do evento de variáveis de ambiente configuradas no GitHub Actions.
    """
    return {
        "ano": int(os.getenv("archive_year", 0)),
        "mes": os.getenv("archive_month", "").strip().lower(),
    }

def main():
    db_path = get_db_path(__file__)

    event = get_event_from_env()
    if event["mes"] == "":
        archive_year(db_path, event)
    else:
        archive_month(db_path, event)


if __name__ == "__main__":  # pragma: no cover
    main()