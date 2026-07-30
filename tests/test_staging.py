"""Testes das funções de staging."""

import pandas as pd

from src.transform.staging import limpar_precos, limpar_owners


def test_limpar_precos_converte_centavos_para_dolares():
    """Preço em centavos-string vira dólares-float."""
    entrada = pd.DataFrame({
        "price": ["1499", "0", "999"],
        "initialprice": ["1499", "0", "1999"],
        "discount": ["0", "0", "50"],
    })

    resultado = limpar_precos(entrada)

    assert resultado["price"].tolist() == [14.99, 0.0, 9.99]
    assert resultado["price"].dtype == "float64"


def test_limpar_owners_calcula_ponto_medio():
    """A faixa de owners vira min, max e estimativa (ponto médio)."""
    entrada = pd.DataFrame({
        "owners": ["20,000,000 .. 50,000,000", "0 .. 20,000"],
    })

    resultado = limpar_owners(entrada)

    assert resultado["owners_min"].tolist() == [20_000_000, 0]
    assert resultado["owners_max"].tolist() == [50_000_000, 20_000]
    assert resultado["owners_estimate"].tolist() == [35_000_000, 10_000]