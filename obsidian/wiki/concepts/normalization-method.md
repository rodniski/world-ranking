---
type: concept
title: Metodo de Normalizacao
aliases: [z-score, clip, escala 0-100]
sources: [02_metodologia.md §5]
related: [[coverage-gate]], [[macro-gates]], [[collectors]]
created: 2026-05-04
updated: 2026-05-04
confidence: high
---

# Metodo de Normalizacao

## O que e

Pipeline determinístico de 4 passos por indicador para transformar valores brutos em scores comparáveis em `[0, 100]`.

## Como funciona no Country Innovation

Por indicador, na ordem:

1. **Inverter sinal** se "menor é melhor" — campo `direction` em `IndicatorMeta`: `+1` (maior melhor) ou `-1` (menor melhor — ex: Corruption Perceptions, Cost of Living, top tax rate, Fragile States).
2. **Z-score global**: `z = (x − μ) / σ` sobre toda a distribuicao de paises do escopo.
3. **Clip em [-3, +3]**: contem outliers sem descarta-los.
4. **Mapear pra 0-100**: `score = clip((z + 3) * 100/6, 0, 100)`.

A transformacao final pra 0-100 eh so pra leitura humana no dashboard. Internamente o calculo continua em z (somar dimensoes ponderadas, etc).

## Por que z-score e nao min-max

- Min-max eh sensivel a outliers extremos (ex: Singapura em "internet speed" puxaria todo mundo pra baixo).
- Z-score com clip preserva forma da distribuicao e neutraliza outliers.

## Regras

- **Direction obrigatoria** em `IndicatorMeta` — nao tem default, declarar explicito por indicador.
- **Z-score sobre o universo** dos paises do escopo (~190), nao sobre subset por dimensao.
- **Clip em ±3σ** (nao ±2 nem ±4) — confirmado em `02_metodologia.md §5`.
- Imputacao acontece **antes** da normalizacao (ver [[coverage-gate]]).

## Relacionados

- [[coverage-gate]] — quando descartar indicador / quando imputar
- [[macro-gates]] — penalizacao final aplicada apos normalizacao
- [[collectors]] — origem dos valores brutos
