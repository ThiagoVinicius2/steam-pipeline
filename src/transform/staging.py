"""Módulo de staging: transforma dados brutos do SteamSpy em
um DataFrame limpo e tipado, pronto para análise.
"""

import json
from pathlib import Path
import pandas as pd
from datetime import date


def encontrar_raw_mais_recente(pasta: str = "data/raw") -> Path:
    """Encontra o arquivo raw mais recente na pasta de dados brutos.

    Como o nome dos arquivos segue o padrão 'steamspy_raw_AAAA-MM-DD.json'
    e a data está em formato ISO, a ordenação alfabética coincide com a
    ordenação cronológica — o maior nome é o mais recente.

    Args:
        pasta: diretório onde ficam os arquivos raw.

    Returns:
        O caminho do arquivo raw mais recente.

    Raises:
        FileNotFoundError: se não houver nenhum arquivo raw na pasta.
    """
    arquivos = sorted(Path(pasta).glob("steamspy_raw_*.json"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo raw encontrado em {pasta}")

    return arquivos[-1]

def carregar_raw(caminho: Path) -> pd.DataFrame:
    """Carrega um arquivo raw JSON em um DataFrame, sem transformações.

    Args:
        caminho: caminho do arquivo JSON a carregar.

    Returns:
        DataFrame com os dados brutos, uma linha por jogo.
    """
    with open(caminho, "r", encoding="utf-8") as arquivo:
        jogos = json.load(arquivo)

    return pd.DataFrame(jogos)

def limpar_precos(df: pd.DataFrame) -> pd.DataFrame:
    """Converte colunas de preço de centavos-string para dólares-float.

    A API do SteamSpy retorna preços como string em centavos
    (ex.: '1499' = US$ 14,99). Esta função converte para float
    em dólares, adequado para análises (médias, comparações).

    Args:
        df: DataFrame com as colunas de preço como string.

    Returns:
        Novo DataFrame com 'price', 'initialprice' e 'discount' numéricos.
    """
    df = df.copy()

    colunas_centavos = ["price", "initialprice"]
    for coluna in colunas_centavos:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce") / 100

    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")

    return df

def limpar_owners(df: pd.DataFrame) -> pd.DataFrame:
    """Converte a faixa de donos (string) em colunas numéricas.

    A API retorna 'owners' como uma faixa em texto, ex.:
    '20,000,000 .. 50,000,000'. Esta função extrai o mínimo e o
    máximo e calcula um ponto médio como estimativa única.

    Args:
        df: DataFrame com a coluna 'owners' como string.

    Returns:
        Novo DataFrame com 'owners_min', 'owners_max' e
        'owners_estimate' numéricos. A coluna 'owners' original é mantida.
    """
    df = df.copy()

    extremos = df["owners"].str.split(" .. ", expand=True)

    df["owners_min"] = (
        extremos[0].str.replace(",", "", regex=False).astype("int64")
    )
    df["owners_max"] = (
        extremos[1].str.replace(",", "", regex=False).astype("int64")
    )
    df["owners_estimate"] = (df["owners_min"] + df["owners_max"]) // 2

    return df

COLUNAS_PARA_DESCARTAR = [
    "score_rank",
    "userscore",
    "average_forever",
    "average_2weeks",
    "median_forever",
    "median_2weeks",
]


def descartar_colunas_mortas(df: pd.DataFrame) -> pd.DataFrame:
    """Remove colunas sem valor analítico do DataFrame.

    A API do SteamSpy não preenche mais certos campos (retornam
    zerados ou vazios), então eles são descartados no staging.

    Args:
        df: DataFrame com as colunas mortas ainda presentes.

    Returns:
        Novo DataFrame sem as colunas listadas em COLUNAS_PARA_DESCARTAR.
    """
    df = df.copy()
    return df.drop(columns=COLUNAS_PARA_DESCARTAR)

def processar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica todas as transformações de staging em sequência.

    Encadeia as limpezas — preços, owners e descarte de colunas
    mortas — sobre o DataFrame bruto, produzindo a versão limpa
    e tipada pronta para a camada de análise.

    Args:
        df: DataFrame bruto carregado do raw.

    Returns:
        DataFrame limpo e tipado.
    """
    df = limpar_precos(df)
    df = limpar_owners(df)
    df = descartar_colunas_mortas(df)
    return df


def salvar_staging(df: pd.DataFrame, pasta: str = "data/staging") -> Path:
    """Salva o DataFrame limpo em formato parquet na camada staging.

    Args:
        df: DataFrame já processado.
        pasta: diretório de destino (padrão: data/staging).

    Returns:
        O caminho do arquivo parquet salvo.
    """
    data_hoje = date.today().isoformat()
    caminho = Path(pasta) / f"steamspy_staging_{data_hoje}.parquet"
    df.to_parquet(caminho, index=False)
    print(f"Salvos {len(df)} jogos limpos em {caminho}")
    return caminho