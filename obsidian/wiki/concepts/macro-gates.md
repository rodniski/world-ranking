---
type: concept
title: Gates de Penalizacao (VISA e MACRO)
aliases: [penalizacao MACRO, dois niveis, visa zero]
sources: [02_metodologia.md §7]
related: [[normalization-method]], [[coverage-gate]], [[countries-json]]
created: 2026-05-04
updated: 2026-05-04
confidence: high
---

# Gates de Penalizacao

## O que e

Penalizacoes duras aplicadas apos normalizacao e antes do score final, sinalizando casos onde o ranking simples eh enganoso.

## Como funciona no Country Innovation

### Sem visto viavel
Se um pais nao tem nenhum dos vistos catalogados pra SWE BR (Blue Card, programa nacional, DNV, etc.), `VISA = 0` em vez de imputar.

Sinaliza que requer pathway alternativo (estudo, casamento, ancestralidade) — nao eh "viavel direto".

### Instabilidade — dois niveis

| Condicao | Fator no score final |
|---|---|
| `MACRO < 25` | `× 0.7` |
| `MACRO < 15` | `× 0.4` |

## Por que dois niveis em vez de um so

Threshold unico (`MACRO < 30 → ×0.7`) punia injustamente paises com macro fraco-mas-funcional (ex: alguns paises do leste europeu) e ao mesmo tempo era leniente demais com casos extremos (Yemen, Siria, Afeganistao). Dois thresholds separam "nao recomendado mas possivel" de "perigoso ativamente".

## Regras

- Gates sao aplicados **depois** da agregacao por dimensao, **antes** da media ponderada final.
- Mudanca de threshold requer aprovacao do Guilherme.
- Flag explicita no `countries.json` quando gate foi aplicado (`flags.macro_penalty: 0.7 | 0.4 | 1.0`).
- VISA=0 nao se confunde com imputacao — eh decisao deliberada.

## Relacionados

- [[normalization-method]] — gera o `MACRO` que alimenta o gate
- [[coverage-gate]] — imputacao normal NAO se aplica a `VISA` quando pais nao tem pathway
- [[countries-json]] — flags de gate expostas no schema final
