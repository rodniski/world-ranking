# country-innovation

Pipeline ETL + ranking de países pela viabilidade de imigração de SWE BR pleno→sênior.
Modos suportados: local (você se muda) e remoto (você trabalha pra empregador estrangeiro e otimiza onde morar).

## Setup

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Ou, sem instalar como pacote:

```bash
pip install -r requirements.txt
```

## Rodar o pipeline

```bash
# 1. Coletar dados das fontes prioritárias
python scripts/run_collectors.py

# 2. Normalizar (z-score + clip + 0-100)
python scripts/run_normalize.py

# 3. Agregar e gerar countries.json
python scripts/run_aggregate.py
```

Saída final: `../data/final/countries.json` (consumido pelo dashboard).

## Estrutura

```
src/country_innovation/
├── schema.py              schemas pandas pra raw/clean/final
├── countries.py           ISO3 normalisation + 190-country whitelist
├── collectors/            um módulo por fonte (gii, heritage, wb_ppp, ...)
│   └── base.py            classe base Collector
├── normalizers/           direção, z-score, clip, escala 0-100
└── aggregator.py          dimensão → score final + gates
```

## Métodos

Ver `../02_metodologia.md` na raiz do projeto.
