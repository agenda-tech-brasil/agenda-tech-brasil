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


def validate_event(event, path):
    errors = []

    nome = event.get("nome", "")
    if not isinstance(nome, str) or not nome.strip():
        errors.append(f"{path}.nome: não pode ser vazio")

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
