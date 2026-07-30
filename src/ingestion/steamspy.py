"""Módulo de ingestão da API do SteamSpy.

Responsável por buscar dados brutos de jogos e entregá-los
como estruturas Python, sem nenhuma transformação.
"""

import requests
import time
import json
from datetime import date
from pathlib import Path

URL_BASE = "https://steamspy.com/api.php"
TIMEOUT_SEGUNDOS = 30
PAUSA_ENTRE_PAGINAS_SEGUNDOS = 60


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

def buscar_todos(max_paginas: int = 5) -> list[dict]:
    """Busca várias páginas de jogos no SteamSpy e acumula os resultados.

    Respeita o rate limit da API (~1 requisição por minuto no
    endpoint 'all') com uma pausa entre as páginas.

    Args:
        max_paginas: limite de páginas a buscar (proteção contra
            coletas longas demais; cada página tem até 1.000 jogos).

    Returns:
        Lista de dicionários com todos os jogos acumulados.
    """
    todos_os_jogos: list[dict] = []

    for pagina in range(max_paginas):
        print(f"Buscando página {pagina}...")
        jogos_da_pagina = buscar_pagina(pagina)

        if not jogos_da_pagina:
            print(f"Página {pagina} vazia — fim da coleta.")
            break

        todos_os_jogos.extend(jogos_da_pagina)
        print(f"  +{len(jogos_da_pagina)} jogos (total: {len(todos_os_jogos)})")

        if pagina < max_paginas - 1:
            time.sleep(PAUSA_ENTRE_PAGINAS_SEGUNDOS)

    return todos_os_jogos

def salvar_raw(jogos: list[dict], pasta: str = "data/raw") -> Path:
    """Salva a lista de jogos como JSON na camada raw.

    O nome do arquivo inclui a data da coleta para preservar
    o histórico entre execuções.

    Args:
        jogos: lista de dicionários vinda de buscar_todos.
        pasta: diretório de destino (padrão: data/raw).

    Returns:
        O caminho do arquivo salvo.
    """
    data_hoje = date.today().isoformat()
    caminho = Path(pasta) / f"steamspy_raw_{data_hoje}.json"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(jogos, arquivo, ensure_ascii=False, indent=2)

    print(f"Salvos {len(jogos)} jogos em {caminho}")
    return caminho