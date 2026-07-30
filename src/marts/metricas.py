"""Módulo de marts: cria métricas de negócio a partir dos dados
limpos do staging, produzindo tabelas prontas para análise.
"""

import pandas as pd
from pathlib import Path


def carregar_staging(pasta: str = "data/staging") -> pd.DataFrame:
    """Carrega o parquet de staging mais recente em um DataFrame.

    Args:
        pasta: diretório onde ficam os arquivos de staging.

    Returns:
        DataFrame limpo e tipado vindo da camada staging.

    Raises:
        FileNotFoundError: se não houver nenhum parquet de staging.
    """
    arquivos = sorted(Path(pasta).glob("steamspy_staging_*.parquet"))

    if not arquivos:
        raise FileNotFoundError(f"Nenhum staging encontrado em {pasta}")

    return pd.read_parquet(arquivos[-1])


def adicionar_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """Cria colunas derivadas de negócio a partir dos dados limpos.

    Métricas criadas:
        - total_avaliacoes: soma de positivas e negativas (popularidade).
        - taxa_aprovacao: fração de avaliações positivas (0 a 1).
        - faixa_preco: categoria textual do preço.
        - custo_beneficio: aprovação por dólar (só para jogos pagos).

    Args:
        df: DataFrame vindo do staging.

    Returns:
        Novo DataFrame com as colunas de métricas adicionadas.
    """
    df = df.copy()

    df["total_avaliacoes"] = df["positive"] + df["negative"]

    df["taxa_aprovacao"] = df["positive"] / df["total_avaliacoes"]

    df["faixa_preco"] = pd.cut(
        df["price"],
        bins=[-0.01, 0, 10, 30, float("inf")],
        labels=["Grátis", "Barato", "Médio", "Premium"],
    )

    df["custo_beneficio"] = df["taxa_aprovacao"] / df["price"]
    df.loc[df["price"] == 0, "custo_beneficio"] = pd.NA

    return df

def resumo_por_faixa(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega métricas médias por faixa de preço.

    Args:
        df: DataFrame já com as métricas derivadas.

    Returns:
        DataFrame com uma linha por faixa de preço e as médias
        das principais métricas.
    """
    resumo = df.groupby("faixa_preco", observed=True).agg(
        qtd_jogos=("appid", "count"),
        aprovacao_media=("taxa_aprovacao", "mean"),
        avaliacoes_medias=("total_avaliacoes", "mean"),
        preco_medio=("price", "mean"),
    )
    return resumo.round(2)

from datetime import date


def salvar_marts(df_jogos: pd.DataFrame, df_resumo: pd.DataFrame, pasta: str = "data/marts") -> list[Path]:
    """Salva as tabelas finais de marts em parquet.

    Args:
        df_jogos: tabela de jogos com métricas (grão fino).
        df_resumo: resumo agregado por faixa de preço.
        pasta: diretório de destino.

    Returns:
        Lista com os caminhos dos arquivos salvos.
    """
    data_hoje = date.today().isoformat()
    caminho_jogos = Path(pasta) / f"mart_jogos_{data_hoje}.parquet"
    caminho_resumo = Path(pasta) / f"mart_resumo_faixa_{data_hoje}.parquet"

    df_jogos.to_parquet(caminho_jogos, index=False)
    df_resumo.to_parquet(caminho_resumo)

    print(f"Mart de jogos salvo: {caminho_jogos} ({len(df_jogos)} linhas)")
    print(f"Mart de resumo salvo: {caminho_resumo} ({len(df_resumo)} linhas)")
    return [caminho_jogos, caminho_resumo]