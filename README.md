# steam-pipeline

Pipeline de dados end-to-end que coleta informações de jogos da Steam via API
do [SteamSpy](https://steamspy.com/api.php), transforma os dados em camadas
(`raw → staging → marts`) e entrega tabelas prontas para análise.

Projeto de estudo focado em boas práticas de engenharia de dados: código
modular e testado, versionamento disciplinado e arquitetura em camadas
inspirada no padrão de modelagem do dbt.

## Objetivo

Responder perguntas de negócio sobre o catálogo de jogos da Steam:

- Como os jogos se distribuem entre faixas de preço?
- Quais estúdios têm mais jogos consistentemente bem avaliados?
- Qual a relação entre preço e aprovação dos jogadores?

## Arquitetura

O pipeline segue o padrão de camadas, onde cada etapa consome a anterior e
nunca pula níveis:

| Camada | Formato | Papel |
|--------|---------|-------|
| `raw` | JSON | Foto fiel do que a API retornou, sem transformação |
| `staging` | Parquet | Dados limpos, tipados e enriquecidos |
| `marts` | Parquet | Tabelas agregadas, prontas para consumo |

Fluxo completo:

```
API SteamSpy  →  raw  →  staging  →  marts  →  análise
  ingestão      JSON     parquet    parquet    notebook
```

## Estrutura de pastas

```
steam-pipeline/
├── src/
│   ├── ingestion/     # coleta da API e persistência do raw
│   ├── transform/     # limpeza e tipagem (staging)
│   └── marts/         # métricas de negócio e agregações
├── data/
│   ├── raw/           # JSON bruto (não versionado)
│   ├── staging/       # parquet limpo (não versionado)
│   └── marts/         # parquet final (não versionado)
├── notebooks/         # análise e visualização
├── tests/             # testes com pytest
├── requirements.txt   # dependências
└── pyproject.toml     # configuração do projeto
```

## Como rodar

Pré-requisitos: Python 3.12+.

**1. Instalar dependências:**

```bash
pip install -r requirements.txt
```

**2. Executar o pipeline (na ordem):**

```bash
python -m src.ingestion.coletar     # coleta da API → data/raw
python -m src.transform.processar   # limpeza → data/staging
python -m src.marts.construir       # métricas → data/marts
```

**3. Explorar a análise:**

Abra `notebooks/analise_steam.ipynb` para ver as visualizações.

## Testes

```bash
pytest
```

Os testes cobrem as transformações críticas: conversão de preços,
cálculo de estimativa de donos e as métricas de negócio.

## Principais descobertas

- **Distribuição de preços:** o catálogo se concentra nas faixas Barato e
  Médio; jogos acima de US$ 30 são minoria.

- **Estúdios de destaque:** filtrando por aprovação ≥ 80% e volume relevante
  de avaliações, emergem nomes consagrados (Valve, Capcom, id Software) e
  indies consistentes (Klei, Obsidian).

- **Nota analítica:** a métrica de custo-benefício (aprovação ÷ preço) é
  enviesada a favor de jogos muito baratos — um lembrete de que toda métrica
  embute uma definição que molda o resultado.

## Stack

Python · pandas · requests · pyarrow · pytest · matplotlib · seaborn