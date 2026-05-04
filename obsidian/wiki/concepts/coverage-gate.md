---
type: concept
title: Gate de Cobertura e Imputacao
aliases: [imputacao, threshold 70%, mediana global]
sources: [02_metodologia.md §4]
related: [[normalization-method]], [[macro-gates]], [[collectors]]
created: 2026-05-04
updated: 2026-05-04
confidence: high
---

# Gate de Cobertura e Imputacao

## O que e

Regra de aceitacao de indicadores e tratamento de missing data antes da normalizacao.

## Como funciona no Country Innovation

**Regra dura**: indicador com cobertura < 70% dos ~190 paises do escopo eh descartado.

Para os ate 30% restantes em indicadores aceitos:

1. **Imputar pela mediana global da fonte** (nao da dimensao), preservando flag `is_imputed=True`.
2. Dashboard mostra asterisco no pais quando ≥30% dos indicadores em uma dimensao foram imputados (sinal de baixa confianca).
3. Paises com >50% de imputacao no score final entram em secao separada "low-coverage countries".

## Por que mediana global e nao da dimensao

Imputar com media da dimensao tende a empurrar paises pra media e mascara onde estao os gaps. Mediana global eh conservadora — assume "pais parecido com mediana mundial" em vez de "pais parecido com a sua dimensao".

## Regras

- **Threshold 70%** eh fechado — mudar requer aprovacao do Guilherme.
- Flag `is_imputed=True` propaga ate o `countries.json` final.
- Imputacao acontece **antes** do z-score (ver [[normalization-method]]).
- Nao imputar nunca em VISA quando pais nao tem pathway viavel — usar gate `VISA=0` (ver [[macro-gates]]).

## Relacionados

- [[normalization-method]] — pipeline aplicado apos imputacao
- [[macro-gates]] — gates pos-normalizacao
- [[collectors]] — fonte dos dados brutos
