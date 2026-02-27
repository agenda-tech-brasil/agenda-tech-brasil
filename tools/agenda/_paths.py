from __future__ import annotations

"""Centralização de paths do repositório.

Este módulo existe para manter em um único lugar a lógica de:
- descobrir a raiz do repo (a partir deste arquivo)
- localizar o database JSON (fonte de verdade dos eventos)
- localizar o README gerado

Também suporta overrides via variáveis de ambiente, o que facilita:
- rodar os scripts localmente apontando para um arquivo temporário
- rodar testes sem tocar no database real

Variáveis de ambiente suportadas:
- AGENDA_DB_PATH: caminho completo para o arquivo JSON do database
- AGENDA_README_PATH: caminho completo para o README de saída
"""

import os
from pathlib import Path


def repo_root() -> Path:
    """Retorna o diretório raiz do repositório."""
    return Path(__file__).resolve().parents[2]


def database_path() -> Path:
    """Caminho do database JSON (com override opcional via env var)."""
    override = os.getenv("AGENDA_DB_PATH")
    if override:
        return Path(override)
    return repo_root() / "data" / "database.json"


def readme_path() -> Path:
    """Caminho do README gerado (com override opcional via env var)."""
    override = os.getenv("AGENDA_README_PATH")
    if override:
        return Path(override)
    return repo_root() / "README.md"
