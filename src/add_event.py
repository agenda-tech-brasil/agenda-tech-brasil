import json
import os

CALENDAR_ORDER = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]

def add_event_to_json(file_path, new_event):

    with open(file_path, "r") as f:
        data = json.load(f)

    year = new_event["ano"]
    month = new_event["mes"]

    year_exist = next((y for y in data["eventos"] if y["ano"] == year), None)
    if not year_exist:
        year_exist = {"ano": year, "arquivado": False, "meses": []}
        data["eventos"].append(year_exist)

    month_exist = next((m for m in year_exist["meses"] if m["mes"] == month), None)
    if not month_exist:
        month_exist = {"mes": month, "arquivado": False, "eventos": []}
        year_exist["meses"].append(month_exist)

    month_exist["eventos"].append(new_event["evento"])

    year_exist["meses"] = sorted(
        year_exist["meses"],
        key=lambda m: CALENDAR_ORDER.index(m["mes"].lower())
    )

    month_exist["eventos"] = sorted(
        month_exist["eventos"],
        key=lambda e: (
            min(map(int, e["data"])),
            len(e["data"])
        ),
    )

    data["eventos"] = sorted(data["eventos"], key=lambda y: y["ano"])

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Evento adicionado e arquivo {file_path} atualizado com sucesso!")


def add_tba_to_json(file_path, new_event):

    with open(file_path, "r") as f:
        data = json.load(f)

    for event in data["tba"]:
        if event["nome"] == new_event["evento"]["nome"] and event["url"] == new_event["evento"]["url"] and event["cidade"] == new_event["evento"]["cidade"] and event["uf"] == new_event["evento"]["uf"] and event["tipo"] == new_event["evento"]["tipo"]:
            print("Este evento jé existe. Ignorando adição.")
            return

    event_tba = {
        "nome": new_event["evento"]["nome"],
        "url": new_event["evento"]["url"],
        "cidade": new_event["evento"]["cidade"],
        "uf": new_event["evento"]["uf"],
        "tipo": new_event["evento"]["tipo"],
    }

    data["tba"].append(event_tba)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Evento adicionado e arquivo {file_path} atualizado com sucesso!")


def get_event_from_env():
    """
    Recebe informações do evento de variáveis de ambiente configuradas no GitHub Actions.
    """
    return {
        "ano": int(os.getenv("event_year", 0)),
        "mes": os.getenv("event_month", "").strip().lower(),
        "evento": {
            "nome": os.getenv("event_name", "").strip(),
            "data": sorted(os.getenv("event_day", "").strip().replace(" ", "").split(",")),
            "url": os.getenv("event_url", "").strip(),
            "cidade": os.getenv("event_city", "").strip().title(),
            "uf": os.getenv("event_state", "").strip(),
            "tipo": os.getenv("event_type", "").strip(),
        },
    }


if __name__ == "__main__":

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'db', 'database.json')

    new_event = get_event_from_env()
    if new_event["mes"] == "tba":
        add_tba_to_json(db_path, new_event)
    else:
        add_event_to_json(db_path, new_event)