"""CLI para cancelar/remover evento/agenda do database.

Este script é chamado pelos workflows do GitHub Actions. Ele lê os dados do
evento a remover através de variáveis de ambiente e atualiza `data/database.json`.

Regras importantes:
- Se `event_month` for `tba`, remove da lista `tba`.
- Caso contrário, remove de `eventos[ano].meses[mes].eventos`.
"""

import json
import os

from tools.agenda._paths import database_path


def remove_event_from_json(file_path, event_to_remove):
    """Remove um evento com data definida (ano/mês/dia) do database.

    Estratégia:
    - carrega o JSON inteiro
    - remove apenas o evento que casa todos os campos (nome/data/cidade/uf/tipo)
    - remove mês/ano caso fiquem vazios após a remoção
    - escreve o JSON de volta no mesmo arquivo
    """
    with open(file_path, "r") as f:
        data = json.load(f)

    year = event_to_remove["ano"]
    month = event_to_remove["mes"].lower()

    year_exist = next((y for y in data["eventos"] if y["ano"] == year), None)
    if not year_exist:
        print(f"Ano {year} não encontrado no arquivo.")
        return

    month_exist = next((m for m in year_exist["meses"] if m["mes"] == month), None)
    if not month_exist:
        print(f"Mês {month} não encontrado no ano {year}.")
        return

    events_before = len(month_exist["eventos"])
    month_exist["eventos"] = [
        e for e in month_exist["eventos"] if not (
            e["nome"] == event_to_remove["evento"]["nome"]
            and e["data"] == event_to_remove["evento"]["data"]
            and e["cidade"].lower() == event_to_remove["evento"]["cidade"].lower()
            and e["uf"] == event_to_remove["evento"]["uf"]
            and e["tipo"] == event_to_remove["evento"]["tipo"]
        )
    ]
    events_after = len(month_exist["eventos"])

    if events_before == events_after:
        print(f"Evento não encontrado no mês {month}, ano {year}.")
    else:
        print(f"Evento '{event_to_remove['evento']['nome']}' removido com sucesso do mês {month}, ano {year}.")

    if not month_exist["eventos"]:
        year_exist["meses"] = [m for m in year_exist["meses"] if m["mes"] != month]
        print(f"Mês {month} removido porque ficou vazio.")

    if not year_exist["meses"]:
        data["eventos"] = [y for y in data["eventos"] if y["ano"] != year]
        print(f"Ano {year} removido porque ficou vazio.")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Arquivo '{file_path}' atualizado com sucesso!")


def remove_tba_from_json(file_path, event_to_remove):
    """Remove um evento da lista `tba` (sem data definida)."""

    with open(file_path, "r") as f:
        data = json.load(f)
    
    events_before = len(data["tba"])
    data["tba"] = [
        e for e in data["tba"] if not (
            e["nome"] == event_to_remove["evento"]["nome"]
            and e["cidade"].lower() == event_to_remove["evento"]["cidade"].lower()
            and e["uf"] == event_to_remove["evento"]["uf"]
            and e["tipo"] == event_to_remove["evento"]["tipo"]
        )
    ]
    events_after = len(data["tba"])

    if events_before == events_after:
        print(f"Evento não encontrado como 'to be announced'.")
    else:
        print(f"Evento '{event_to_remove['evento']['nome']}' removido com sucesso.")

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Arquivo '{file_path}' atualizado com sucesso!")

def get_event_from_env():
    """
    Recebe informações do evento de variáveis de ambiente configuradas no GitHub Actions.

    Campos esperados (definidos nos workflows):
    - event_year, event_month
    - event_name, event_day (pode ser vazio para TBA), event_url
    - event_city, event_state, event_type
    """
    return {
        "ano": int(os.getenv("event_year", 0)),
        "mes": os.getenv("event_month", "").strip().lower(),
        "evento": {
            "nome": os.getenv("event_name", "").strip(),
            "data": os.getenv("event_day", "").strip().replace(" ", "").split(","),
            "url": os.getenv("event_url", "").strip(),
            "cidade": os.getenv("event_city", "").strip().title(),
            "uf": os.getenv("event_state", "").strip(),
            "tipo": os.getenv("event_type", "").strip().lower(),
        },
    }


def main() -> None:
    """Entry-point do CLI.

    Resolve o caminho do database via `tools.agenda._paths.database_path()` e
    executa a operação de remoção conforme `event_month`.
    """
    db_path = str(database_path())

    event = get_event_from_env()
    if event["mes"] == "tba":
        remove_tba_from_json(db_path, event)
    else:
        remove_event_from_json(db_path, event)

if __name__ == "__main__":
    main()
