"""Ponto de entrada do staging.

Carrega o raw mais recente, aplica as transformações de limpeza
e salva o resultado limpo na camada staging.

Uso:
    python -m src.transform.processar
"""

from src.transform.staging import (
    carregar_raw,
    encontrar_raw_mais_recente,
    processar,
    salvar_staging,
)


def main() -> None:
    """Orquestra o staging completo: raw -> limpo -> parquet."""
    print("Iniciando staging...")
    caminho_raw = encontrar_raw_mais_recente()
    print(f"Lendo raw: {caminho_raw}")

    df = carregar_raw(caminho_raw)
    df_limpo = processar(df)
    caminho_staging = salvar_staging(df_limpo)

    print(f"Staging finalizado: {df_limpo.shape[0]} jogos em {caminho_staging}")


if __name__ == "__main__":
    main()