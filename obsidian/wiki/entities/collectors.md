---
type: entity
entity_type: module
title: Collectors
sources: [03_escopo_para_claude_code.md §2]
related: [[normalization-method]], [[coverage-gate]], [[escopo-2026]]
created: 2026-05-04
updated: 2026-05-04
---

# Collectors

## O que e

Modulos Python que extraem dados de uma fonte externa (API, scrape HTML, CSV) e normalizam pro schema canonico LONG `(iso3, indicator_id, value, year, source_id)` em `data/raw/`.

## Estrutura

```
code/src/country_innovation/collectors/
  base.py      class Collector(ABC) com fetch / normalize / save
  wb_ppp.py    WorldBankPPP — API JSON, indicador NY.GNP.PCAP.PP.CD
  heritage.py  Heritage — HTML scrape de all-country-scores
  gii.py       GII — HTML scrape de WIPO 2025 results
```

Orquestrador: `code/scripts/run_collectors.py`.

## Collectors prontos (nao testados em rede)

| ID | Source | Tipo | URL |
|---|---|---|---|
| `WB-PPP` | World Bank GNI per capita PPP | API JSON | api.worldbank.org |
| `IEF-2026` | Heritage Index of Economic Freedom | HTML scrape | economicfreedom.heritage.org |
| `GII-2025` | WIPO Global Innovation Index | HTML scrape | wipo.int |

## Collectors prioritarios pendentes (Alta prio do catalogo)

- **HDI 2025** (UNDP) — CSV oficial, facil
- **Stack Overflow Survey 2024** — CSV publico, filtrar por pais e calcular mediana de salario por perfil (pleno/senior)
- **GTCI 2023** (INSEAD) — Excel oficial
- **IMF WEO Apr 2025** — API SDMX ou Excel
- **WB WGI** — API igual a wb_ppp, indicadores `RL.EST`, `CC.EST` etc
- **Henley Passport Index 2026** — HTML scrape
- **Numbeo COL 2026** — HTML, cuidado com rate limit
- **OECD Taxing Wages** — Excel
- **GPI 2025** (IEP) — Excel
- **EF EPI 2024** — HTML
- **Speedtest Global Index** — HTML

## Dependencias

- Output: `data/raw/<SOURCE-ID>.csv` no formato LONG canonico
- Schema definido em `code/src/country_innovation/schema.py` (`LONG_COLUMNS`, `IndicatorMeta`)
- Resolucao de pais via `countries.to_iso3()` + `MANUAL_OVERRIDES`
- Consumido por: normalizers (apos limpeza para `clean/`)

## Regras

- 1 collector = 1 fonte = 1 `source_id`
- Sempre normalizar pro schema LONG antes de salvar
- ISO3 obrigatorio (Kosovo=XKX, Taiwan=TWN, HK=HKG, MAC=MAC)
- Fallback BS4 manual quando `pandas.read_html` falha
- **Nao** introduzir Playwright/Selenium sem aprovar — investigar JSON endpoint subjacente primeiro
- Cobertura < 70% dos paises do escopo → indicador descartado (ver [[coverage-gate]])

## Relacionados

- [[normalization-method]] — proximo passo apos `data/raw/`
- [[coverage-gate]] — regra de aceitacao de indicador
- [[countries-json]] — destino final dos dados
- [[escopo-2026]] — contexto e prioridades
