---
type: source
title: Escopo para Claude Code (2026-05-04)
slug: escopo-2026
source_file: 03_escopo_para_claude_code.md
author: Guilherme + Claude
date_published: 2026-05-04
date_ingested: 2026-05-04
key_claims:
  - "Pipeline ETL + dashboard ranqueando ~190 paises pela viabilidade de imigracao SWE BR pleno→senior"
  - "2 perfis (pleno, senior) × 2 modos (local, remoto) = 4 rankings pre-computados"
  - "Schema canonico LONG: (iso3, indicator_id, value, year, source_id) com ISO3 como chave"
  - "4 dimensoes (TECH, VISA, PPP, MACRO) com peso default 25% cada"
  - "Sliders rodam em JS no cliente — instantaneo"
  - "Dashboard final eh HTML standalone (Cowork artifact), nao app SvelteKit"
related: [[collectors]], [[countries-json]], [[normalization-method]], [[coverage-gate]], [[macro-gates]]
confidence: high
---

# Escopo para Claude Code (2026-05-04)

## Resumo

- Define o projeto como pipeline ETL + dashboard ranqueando ~190 paises pra imigracao SWE BR pleno→senior
- Estabelece 2 modos de uso (Local: muda e trabalha pra empregador local | Remoto: trabalha pra estrangeiro e otimiza onde morar) e 2 perfis salariais (pleno 4-7 anos, senior 8+ anos)
- Catalogo de 33 fontes priorizadas em `01_catalogo_fontes.xlsx`; 17-18 entram na fase 1
- Convencoes fechadas: schema LONG, 4 dimensoes, normalizacao z-score, imputacao mediana, gates de penalizacao, sanity checks de pipeline
- Tasks A-G ordenadas pra MVP (~4.5 dias)

## Detalhes

Codigo ja entregue:

- `code/pyproject.toml` — Python 3.11+, deps fixadas
- `code/src/country_innovation/{schema,countries}.py` — schema canonico + ISO3 normalization
- `code/src/country_innovation/collectors/{base,wb_ppp,heritage,gii}.py` — 3 collectors funcionais nao testados
- `code/scripts/run_collectors.py` — orquestrador

Decisoes deferidas pra V2: reescrita em Go/Rust/C# do coletor, contrato estavel = `countries.json`.

## Implicacoes para o ranking

- **Skills mencionados**: framing-problems, brainstorming, creating-implementation-plan, locating-code, web-research, testing-patterns, verification-before-completion (ver CLAUDE.md)
- **Constraint forte**: nao introduzir Playwright/Selenium sem aprovacao previa; investigar JSON endpoint subjacente primeiro
- **Constraint forte**: nao introduzir banco de dados; tudo em CSV/parquet/JSON cabe em RAM
- **Pedir aprovacao** antes de: mudar pesos default, mudar formula de normalizacao, adicionar dimensao, excluir fonte Alta, mudar threshold de gate
- **Decidir e seguir**: novo collector de fonte Alta no catalogo, edge case de pais (atualizar `MANUAL_OVERRIDES`), refatoracao interna que nao muda contratos

## Relacionados

- [[collectors]] — 3 prontos + 11 prioritarios pendentes (Task B)
- [[countries-json]] — output final (Task E)
- [[normalization-method]] — pipeline (Task D)
- [[coverage-gate]] — regra de aceitacao
- [[macro-gates]] — penalizacoes finais
