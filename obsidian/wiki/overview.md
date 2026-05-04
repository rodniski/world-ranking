---
type: overview
title: Country Innovation Overview
updated: 2026-05-04
---

# Country Innovation — Visao Geral

## O que e

Pipeline ETL Python + dashboard que ranqueia ~190 paises pela viabilidade de imigracao de um software engineer brasileiro pleno→senior. Output: `data/final/countries.json` consumido por dashboard HTML standalone.

## Arquitetura

- **Schema canonico LONG**: `(iso3, indicator_id, value, year, source_id)` em `data/clean/`
- **Camadas**: `raw/` (CSV bruto por fonte) → `clean/` (long parquet canonico) → `final/` (countries.json + manifests)
- **Codigo**: 1 collector por fonte herdando de `Collector(ABC)`; normalizers stateless; aggregator monta dimensoes e aplica gates
- **Sem banco**: tudo em CSV/parquet/JSON. Dataset cabe em RAM.

## Dimensoes (4)

- **TECH** — mercado de trabalho tech, salario SWE
- **VISA** — facilidade de visto, pathway pra residencia+cidadania, DNV
- **PPP** — custo de vida, salario liquido em PPP, regimes fiscais
- **MACRO** — estabilidade macro, governanca, seguranca

Default: 25% cada (peso neutro).

## Perfis e modos

- **Perfis**: Pleno (4-7 anos) e Senior (8+ anos) — mediana salarial diferente
- **Modos**: Local (mudar e trabalhar pra empregador local) vs Remoto (trabalhar pra empregador estrangeiro, otimizar onde MORAR)

Total de rankings pre-computados: 2 × 2 = **4 combinacoes**. Sliders rodam em JS no cliente.

## Stack

- Python 3.11+ (`venv`, sem conda)
- `pandas`, `numpy`, `requests`, `beautifulsoup4`, `lxml`, `pdfplumber`, `country-converter`, `scipy`, `pyyaml`, `openpyxl`
- Sem Playwright/Selenium sem aprovacao previa
- Sem banco de dados

## Workflow

- Branch base: `main` (repo solo em [rodniski/world-ranking](https://github.com/rodniski/world-ranking))
- Branches de trabalho: `{numero-issue}-{slug}`
- Commits convencionais (`feat`, `fix`, `refactor`, `chore`, `docs`, `test`)

## Memoria

- `obsidian/wiki/` — conhecimento compilado (concepts, entities, sources, comparisons, syntheses)
- `02_metodologia.md` — decisoes metodologicas fechadas
- `03_escopo_para_claude_code.md` — escopo original (referencia historica)
- `01_catalogo_fontes.xlsx` — 33 fontes catalogadas e priorizadas
