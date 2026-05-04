---
type: hot
title: Session Context
updated: 2026-05-04 (bootstrap da infra Claude Code)
---

# Hot Context

Rolling cache de ~500 palavras com o contexto mais recente. Lido pelo agente no inicio de cada sessao para herdar estado.

---

## Estado Atual

**main** — repo solo em [rodniski/world-ranking](https://github.com/rodniski/world-ranking). Infra Claude Code recem-bootstrapada (CLAUDE.md, `.claude/commands`, `obsidian/`). Pipeline em fase pre-MVP.

### Codigo pronto

- `code/src/country_innovation/schema.py` — `LONG_COLUMNS`, `IndicatorMeta`, `Direction`, `Dimension`
- `code/src/country_innovation/countries.py` — `to_iso3()`, `is_in_scope()`, `MANUAL_OVERRIDES` (Kosovo=XKX, Taiwan=TWN, etc)
- `code/src/country_innovation/collectors/base.py` — `class Collector(ABC)` com `fetch/normalize/save`
- 3 collectors funcionais mas **nao testados em rede**:
  - `WorldBankPPP` (`WB-PPP`) — API JSON publica, indicador `NY.GNP.PCAP.PP.CD`
  - `Heritage` (`IEF-2026`) — HTML scrape de `economicfreedom.heritage.org`
  - `GII` (`GII-2025`) — HTML scrape de `wipo.int`
- `code/scripts/run_collectors.py` — orquestra os 3 e grava em `data/raw/`

### Tasks pendentes (ordem)

- **A**: validar os 3 collectors em rede (`python scripts/run_collectors.py`). Esperado: 3 CSVs em `data/raw/` com 130-200 linhas cada.
- **B**: implementar collectors Alta prioridade restantes (HDI 2025, Stack Overflow Survey 2024, GTCI 2023, IMF WEO Apr 2025, WB WGI, Henley Passport 2026, Numbeo COL 2026, OECD Taxing Wages, GPI 2025, EF EPI 2024, Speedtest Global Index)
- **C**: curar manualmente `data/manual/dnv_catalog.csv` (~50 paises com DNV ativo + regimes fiscais)
- **D**: implementar `normalizers/transforms.py` (`apply_direction`, `zscore_clip`, `to_0_100`, `impute_global_median`) e `aggregator.py` (`aggregate_dimension`, `apply_gates`, `final_score`)
- **E**: gerar `data/final/countries.json` (schema documentado em `02_metodologia.md`)
- **F**: HTML standalone de preview em `code/scripts/preview_dashboard.html`
- **G**: `04_validacao.md` com top 20 + posicao do Brasil + 5 surpresas

### Decisoes consolidadas

- **Pesos default**: 25% × 4 (neutro)
- **Brasil**: entra no ranking como calibracao (esperado posicao 50-110 default)
- **Gates**: `MACRO < 25 → ×0.7`; `MACRO < 15 → ×0.4`; sem visto viavel → `VISA = 0`
- **Perfis**: Pleno e Senior (toggle no dashboard)
- **Modos**: Local (clássico) e Remoto (receita ponderada US/UK/DE/NL + DNV + regime fiscal)
- **Total**: 2 perfis × 2 modos = 4 rankings pre-computados; sliders rodam em JS no cliente

### Sanity checks (pipeline FALHA se)

- Top 10 default sem ≥5 paises OECD
- Brasil fora de [50, 110]
- Algum pais com `NaN` ou fora de `[0, 100]`
- Soma de pesos das 4 dimensoes ≠ 100% (tolerancia 0.01)

## Bookkeeping

- `02_metodologia.md` versao 0.2 (2026-05-04) — decisoes 1-4 + trabalho remoto incorporadas
- Catalogo: 33 fontes em `01_catalogo_fontes.xlsx`, 17-18 entram na fase 1 (Alta prio)
- Cronograma estimado: ~4.5 dias de trabalho focado pro MVP completo
