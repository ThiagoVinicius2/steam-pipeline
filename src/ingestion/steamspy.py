"""Módulo de ingestão da API do SteamSpy.

Responsável por buscar dados brutos de jogos e entregá-los
como estruturas Python, sem nenhuma transformação.
"""

import requests

URL_BASE = "https://steamspy.com/api.php"
TIMEOUT_SEGUNDOS = 30


def buscar_pagina(pagina: int) -> list[dict]:
    """Busca uma página de jogos no endpoint 'all' do SteamSpy.

    Cada página contém até 1.000 jogos, ordenados por popularidade.

    Args:
        pagina: número da página a buscar (começa em 0).

    Returns:
        Lista de dicionários, um por jogo. Lista vazia se a página
        não tiver jogos (sinal de que as páginas acabaram) ou se a
        requisição falhar.
    """
    parametros = {"request": "all", "page": pagina}

    try:
        resposta = requests.get(URL_BASE, params=parametros, timeout=TIMEOUT_SEGUNDOS)
    except requests.RequestException as erro:
        print(f"Erro de conexão na página {pagina}: {erro}")
        return []

    if resposta.status_code != 200:
        print(f"Página {pagina} retornou status {resposta.status_code}")
        return []

    jogos_por_appid = resposta.json()
    return list(jogos_por_appid.values())