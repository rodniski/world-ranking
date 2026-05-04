---
type: entity
entity_type: contract
title: countries.json
sources: [03_escopo_para_claude_code.md §4 Task E, 02_metodologia.md §2]
related: [[normalization-method]], [[macro-gates]], [[coverage-gate]], [[collectors]]
created: 2026-05-04
updated: 2026-05-04
---

# countries.json

## O que e

Output final do pipeline em `data/final/countries.json`. Eh o **contrato estavel** entre o ETL Python e o dashboard HTML standalone (entregue como Cowork artifact). Quando uma reescrita do collector em Go/Rust/C# entrar (V2), `countries.json` permanece o ponto de integracao.

## Estrutura

```json
{
  "metadata": {
    "version": "1.0",
    "generated_at": "ISO timestamp",
    "indicators_used": [...],
    "sources": [...]
  },
  "countries": [
    {
      "iso3": "PRT",
      "name": "Portugal",
      "scores": {
        "pleno_local":  {"tech": 62.1, "visa": 71.0, "ppp": 58.4, "macro": 78.0, "final": 67.4},
        "pleno_remoto": {"tech": 88.0, "visa": 92.0, "ppp": 71.0, "macro": 78.0, "final": 82.3},
        "senior_local": {...},
        "senior_remoto": {...}
      },
      "indicators": {"gii_overall": 47.8, "ief_overall": 72.5, ...},
      "flags": {"is_imputed": false, "has_dnv": true, "low_coverage": false}
    }
  ]
}
```

## Dependencias

- **Upstream**: agregador (`aggregator.py`) consolida dimensoes apos normalizacao e gates
- **Downstream**: `code/scripts/preview_dashboard.html` (preview local) + Cowork artifact (dashboard de producao)

## Regras

- 4 combinacoes de score por pais: `{pleno,senior} × {local,remoto}` (ver `02_metodologia.md §7.5`)
- Sliders de peso rodam em JS no cliente — apenas **scores brutos por dimensao** vao no JSON, nao o final ja ponderado
- Flags expostas: `is_imputed`, `has_dnv`, `low_coverage`, `macro_penalty` (0.4 / 0.7 / 1.0)
- Schema versionado em `metadata.version` — qualquer breaking change incrementa versao maior
- Geracao deterministic — mesma entrada produz mesma saida byte-a-byte

## Sanity checks (pipeline FALHA se)

- Top 10 default sem ≥5 paises OECD
- Brasil fora de [50, 110] no ranking default
- Algum pais com `NaN` ou fora de `[0, 100]`
- Soma de pesos das 4 dimensoes ≠ 100% (tolerancia 0.01)

## Relacionados

- [[normalization-method]] — produz os scores que alimentam este JSON
- [[macro-gates]] — flags de penalizacao expostas aqui
- [[coverage-gate]] — flag `is_imputed` propagada ate aqui
- [[collectors]] — origem dos `indicators_used`
