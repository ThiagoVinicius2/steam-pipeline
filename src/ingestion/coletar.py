"""Ponto de entrada da coleta de dados do SteamSpy.

Executa a ingestão completa: busca as páginas, acumula os jogos
e salva o resultado bruto na camada raw.

Uso:
    python -m src.ingestion.coletar
"""

from src.ingestion.steamspy import buscar_todos, salvar_raw


def main() -> None:
    """Orquestra a coleta completa e persiste o resultado."""
    print("Iniciando coleta do SteamSpy...")
    jogos = buscar_todos(max_paginas=5)
    caminho = salvar_raw(jogos)
    print(f"Coleta finalizada: {len(jogos)} jogos em {caminho}")


if __name__ == "__main__":
    main()