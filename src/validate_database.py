import os
import sys

from utils import get_db_path, load_database


VALID_MONTHS = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

VALID_TYPES = {"presencial", "online", "híbrido"}

VALID_UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}


def validate_event(event, path, skip_data=False):
    errors = []

    nome = event.get("nome", "")
    if not isinstance(nome, str) or not nome.strip():
        errors.append(f"{path}.nome: não pode ser vazio")

    if not skip_data:
        data = event.get("data", [])
        if not isinstance(data, list) or len(data) == 0:
            errors.append(f"{path}.data: deve ser uma lista não vazia")
        else:
            for d in data:
                if not isinstance(d, str) or not d.isdigit() or not (1 <= int(d) <= 31):
                    errors.append(f"{path}.data: valor inválido '{d}', esperado string numérica de 01 a 31")

    url = event.get("url", "")
    if not isinstance(url, str) or not url.startswith("http"):
        errors.append(f"{path}.url: deve começar com http")

    tipo = event.get("tipo", "")
    if tipo not in VALID_TYPES:
        errors.append(f"{path}.tipo: valor inválido '{tipo}', esperado: presencial, online, híbrido")

    cidade = event.get("cidade", "")
    uf = event.get("uf", "")

    if tipo == "online":
        if cidade:
            errors.append(f"{path}.cidade: evento online não deve ter cidade preenchida")
        if uf:
            errors.append(f"{path}.uf: evento online não deve ter uf preenchido")
    elif tipo in ("presencial", "híbrido"):
        if not cidade:
            errors.append(f"{path}.cidade: evento {tipo} deve ter cidade preenchida")
        if not uf:
            errors.append(f"{path}.uf: evento {tipo} deve ter uf preenchido")
        elif uf not in VALID_UFS:
            errors.append(f"{path}.uf: valor inválido '{uf}', esperado sigla de UF brasileira")

    return errors


def validate_month(month, path):
    errors = []

    mes = month.get("mes", "")
    if mes not in VALID_MONTHS:
        errors.append(f"{path}.mes: valor inválido '{mes}', esperado mês em português")

    eventos = month.get("eventos", [])
    if not isinstance(eventos, list) or len(eventos) == 0:
        errors.append(f"{path}.eventos: lista de eventos não pode ser vazia")
    else:
        for i, evento in enumerate(eventos):
            errors.extend(validate_event(evento, f"{path}.eventos[{i}]"))

    return errors


def validate_year(year, path):
    errors = []

    ano = year.get("ano", 0)
    if not isinstance(ano, int) or ano <= 0:
        errors.append(f"{path}.ano: valor inválido '{ano}', esperado inteiro positivo")

    meses = year.get("meses", [])
    if not isinstance(meses, list) or len(meses) == 0:
        errors.append(f"{path}.meses: lista de meses não pode ser vazia")
    else:
        month_names = [m.get("mes", "") for m in meses]
        month_indices = []
        for name in month_names:
            if name in VALID_MONTHS:
                month_indices.append(VALID_MONTHS.index(name))

        if month_indices != sorted(month_indices):
            errors.append(f"{path}.meses: meses fora de ordem cronológica")

        for i, mes in enumerate(meses):
            errors.extend(validate_month(mes, f"{path}.meses[{i}]"))

    return errors


def validate_tba(tba_list):
    errors = []
    seen = set()

    for i, evento in enumerate(tba_list):
        path = f"tba[{i}]"
        errors.extend(validate_event(evento, path, skip_data=True))

        nome = evento.get("nome", "")
        cidade = evento.get("cidade", "")
        uf = evento.get("uf", "")
        tipo = evento.get("tipo", "")
        key = (nome, cidade, uf, tipo)
        if key in seen:
            errors.append(f"{path}: evento duplicado (nome+cidade+uf+tipo)")
        seen.add(key)

    return errors


def validate_database(file_path):
    data = load_database(file_path)
    errors = []

    for i, year in enumerate(data.get("eventos", [])):
        errors.extend(validate_year(year, f"eventos[{i}]"))

    errors.extend(validate_tba(data.get("tba", [])))

    return errors
