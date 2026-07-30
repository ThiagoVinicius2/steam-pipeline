"""Ponto de entrada dos marts.

Carrega o staging, cria as métricas de negócio, gera as tabelas
agregadas e salva os marts finais.

Uso:
    python -m src.marts.construir
"""

from src.marts.metricas import (
    adicionar_metricas,
    carregar_staging,
    resumo_por_faixa,
    salvar_marts,
)


def main() -> None:
    """Orquestra a construção completa dos marts."""
    print("Construindo marts...")
    df = carregar_staging()
    df_jogos = adicionar_metricas(df)
    df_resumo = resumo_por_faixa(df_jogos)
    salvar_marts(df_jogos, df_resumo)
    print("Marts finalizados.")


if __name__ == "__main__":
    main()