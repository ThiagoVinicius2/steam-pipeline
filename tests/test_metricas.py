"""Testes das funções de métricas (marts)."""

import pandas as pd

from src.marts.metricas import adicionar_metricas


def _df_base(precos, positivos, negativos):
    """Monta um DataFrame mínimo com as colunas que adicionar_metricas usa."""
    return pd.DataFrame({
        "appid": range(len(precos)),
        "price": precos,
        "positive": positivos,
        "negative": negativos,
    })


def test_taxa_aprovacao_calcula_fracao_correta():
    """taxa_aprovacao = positivas / (positivas + negativas)."""
    df = _df_base(precos=[10.0], positivos=[90], negativos=[10])

    resultado = adicionar_metricas(df)

    assert resultado["taxa_aprovacao"].tolist() == [0.9]


def test_custo_beneficio_de_gratis_e_nulo():
    """Jogo grátis (price=0) tem custo_beneficio NA, não infinito."""
    df = _df_base(precos=[0.0], positivos=[100], negativos=[0])

    resultado = adicionar_metricas(df)

    assert pd.isna(resultado["custo_beneficio"].iloc[0])


def test_faixa_preco_nos_limites():
    """Preços nos limites caem na faixa correta."""
    df = _df_base(precos=[0.0, 10.0, 30.0, 60.0], positivos=[1, 1, 1, 1], negativos=[1, 1, 1, 1])

    resultado = adicionar_metricas(df)

    assert resultado["faixa_preco"].tolist() == ["Grátis", "Barato", "Médio", "Premium"]