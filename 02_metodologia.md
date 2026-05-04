# Metodologia — Country Innovation Ranking

**Versão:** 0.2 (2026-05-04 — incorpora decisões 1-4 + trabalho remoto)
**Autor:** pipeline montado pelo Guilherme + Claude
**Status:** decisões fechadas, pronto pra codar

---

## 1. Objetivo

Construir um ranking ajustável dos ~190 países pela viabilidade de imigração de um software engineer pleno→sênior brasileiro, cruzando 4 dimensões objetivas e permitindo que o usuário (Guilherme) ajuste os pesos no dashboard.

## 2. Pipeline de dados

```
raw/                         clean/                       final/
├─ gii_2025.csv          ──> ├─ indicators_long.parquet ──> countries.json
├─ heritage_2026.csv         │   (iso3, indicator_id,      (consumido pelo
├─ wb_ppp.csv                │    value, year, source)      dashboard HTML)
├─ wb_wgi.csv                │
├─ ...                       └─ countries_wide.parquet
                                 (uma linha por país)
```

Cada fonte do catálogo (`01_catalogo_fontes.xlsx`) vira um CSV em `raw/`.
A camada `clean/` é a verdade canônica em formato *long*: uma linha = um país × um indicador × uma fonte × um ano. Isso permite:

- adicionar fontes novas sem refatorar o pipeline
- recalcular o score sem refazer a coleta
- auditar de onde veio cada valor no dashboard

## 3. Normalização de identidade de país

Chave canônica: **ISO 3166-1 alpha-3** (`BRA`, `DEU`, `PRT`...).

Casos especiais que precisam tratamento manual:

| Entidade | Código adotado | Por quê |
|---|---|---|
| Kosovo | `XKX` | não-ISO oficial mas é o código IMF/Banco Mundial |
| Taiwan | `TWN` | algumas fontes usam `TPE` ou omitem |
| Hong Kong / Macau | `HKG` / `MAC` | tratar como entidades, não como CN |
| Northern Cyprus, Western Sahara, Palestine | `incluir só se ≥3 fontes cobrirem` | senão fica enviesado |

Lib: `country_converter` (pip) com fallback manual para esses casos.

## 4. Tratamento de missing data

Regra dura: **um indicador é descartado se cobertura < 70% dos 190 países do escopo.**

Para os 30% restantes em indicadores aceitos:

1. **Imputação por mediana global da fonte** (não da dimensão), preservando flag `is_imputed=True`.
2. O dashboard mostra um asterisco no país quando ≥30% dos seus indicadores em uma dimensão foram imputados (sinaliza baixa confiança).
3. Países com >50% de imputação no score final entram em uma seção separada "low-coverage countries" no dashboard.

Justificativa: imputar com média da dimensão tende a empurrar países pra média e mascara onde estão os gaps. Mediana global é conservadora — assume "país parecido com mediana mundial" em vez de "país parecido com a sua dimensão".

## 5. Normalização de escala (z-score → 0-100)

**Por indicador**, na ordem:

1. **Inverter sinal** se "menor é melhor" (ex: Corruption Perceptions, Fragile States, Cost of Living, top tax rate).
   - Marcar isso explicitamente em uma coluna `direction` no metadado de indicador (`+1` = maior é melhor; `-1` = menor é melhor).
2. **Z-score** sobre a distribuição global: `z = (x − μ) / σ`.
3. **Clip em [-3, +3]** para conter outliers sem descartá-los.
4. **Mapear pra 0-100**: `score = clip((z + 3) * 100/6, 0, 100)`.

Por que z-score e não min-max?
- Min-max é sensível a outliers extremos (ex: Singapura em "internet speed" puxa todo mundo pra baixo).
- Z-score com clip preserva forma da distribuição e neutraliza outliers.
- A transformação final pra 0-100 é só pra leitura humana no dashboard — internamente o cálculo continua em z.

## 6. Agregação por dimensão

Quatro dimensões, cada uma com N indicadores:

| Dimensão | Indicadores candidatos (resumo) |
|---|---|
| **TECH** | salário SWE PPP-adj (Stack Overflow), GTCI, GII Innovation Output, English Proficiency Index, % de empresas tech |
| **VISA** | Henley Passport (após naturalização), existência de visto tech, threshold salarial, tempo até PR, EF EPI |
| **PPP** | GNI per capita PPP (WB), Cost of Living (Numbeo), Tax Wedge (OECD), Local Purchasing Power |
| **MACRO** | WGI (6 sub-indicadores), GPI, IMF GDP/inflação, IEF Rule of Law, EIU Democracy |

**Score da dimensão** = média ponderada dos indicadores normalizados:

```
dim_score(país, dim) = Σ (w_i · score_i) / Σ w_i
```

Onde `w_i` é o peso de cada indicador dentro da dimensão. Default: pesos iguais. Pesos por indicador são editáveis em um arquivo `weights.yaml` antes do MVP, e podem virar sliders avançados no dashboard depois.

## 7. Score final

```
final_score(país) = w_tech · TECH + w_visa · VISA + w_ppp · PPP + w_macro · MACRO
```

**Pesos default:** 25% cada (neutro — confirmado por Guilherme 2026-05-04). O dashboard expõe quatro sliders e renormaliza automaticamente pra somar 100%.

**Brasil:** entra no ranking normalmente (confirmado). Funciona como referência calibradora — se o pipeline está correto, BR aparece em torno da posição 50-110 com pesos default.

**Penalizações duras (gates):** [decisão minha — Guilherme delegou]

- **Sem visto viável:** se um país não tem nenhum dos vistos catalogados pra SWE BR (Blue Card, programa nacional, DNV, etc.), `VISA = 0` em vez de imputar. Sinaliza que requer pathway alternativo (estudo, casamento, ancestralidade).
- **Instabilidade média:** se `MACRO < 25`, aplicar fator `0.7` no score final.
- **Instabilidade severa:** se `MACRO < 15` (países em conflito ativo, regimes em colapso), aplicar fator `0.4` no score final.

**Por que dois níveis em vez de um só:** um único threshold `MACRO < 30 → 0.7` punia injustamente países com macro fraco-mas-funcional (ex: alguns países do leste europeu) e ao mesmo tempo era leniente demais com casos extremos (Yemen, Síria, Afeganistão). Dois threshold separam "não recomendado mas possível" de "perigoso ativamente".

## 7.5 Perfis de salário e trabalho remoto

### 7.5.1 Perfis de carreira

Dois perfis paralelos (confirmado: pleno e sênior):

| Perfil | Anos exp | Stack Overflow bucket | Levels.fyi tier proxy |
|---|---|---|---|
| **Pleno** | 4-7 anos | "Mid-level developer" | P3 / IC3 |
| **Sênior** | 8+ anos | "Senior developer" | P5 / IC5 |

O dashboard tem um toggle entre os dois. Indicadores TECH (salário) usam medianas diferentes por perfil; resto da metodologia é igual.

### 7.5.2 Modo de trabalho — local vs. remoto

O dashboard expõe um **segundo toggle** com dois modos de cálculo:

#### Modo A — Imigração local (clássico)

Você se muda para o país e trabalha pra empregador local. Modelo descrito até aqui.

- Salário = mediana SWE local (Stack Overflow + Levels.fyi)
- Tributação = país de residência
- VISA = visto de trabalho tradicional (Blue Card, Skilled Worker, programa nacional)

#### Modo B — Base remota

Você trabalha remoto pra empregador estrangeiro (US/UK/DE/NL/CH) e otimiza onde MORAR.

Componentes recomputados:

- **Receita assumida** = mediana ponderada de salários SWE em mercados remote-friendly:
  - 50% US (mais vagas remote pra LatAm via Deel/Remote.com/EOR)
  - 20% UK
  - 15% Alemanha
  - 15% Países Baixos
  - Convertido pra USD, depois ajustado pelo PPP do país de residência.
- **Tributação** = país de residência. Aqui pesa muito o regime fiscal disponível pra remote workers (ver indicador novo abaixo).
- **VISA** = só conta se o país tem visto remoto-friendly (DNV, residência fiscal favorável, ou tolerância prática a freelancers estrangeiros).

#### Indicadores novos a coletar (entram em VISA + PPP)

| Indicador | Onde achar | Tipo |
|---|---|---|
| Tem Digital Nomad Visa | Curadoria manual + Nomad List | Binário |
| Threshold de receita pra DNV (USD/mês) | Sites oficiais por país | Numérico |
| Regime fiscal favorável pra remote (NHR PT-sucessor, Beckham ES, IFICI PT, non-dom CY/MT, Schengen 183d, etc.) | KPMG / PwC / curadoria | Categórico |
| Permite trabalhar pra empregador no exterior sem incorporação local | Curadoria | Binário |
| Carga tributária efetiva pra renda externa USD 80k/ano | Cálculo manual com OECD + KPMG | Numérico (%) |
| Internet speed mediana (Mbps) | Speedtest Global Index | Numérico |
| Diferença de fuso pra US East/West (horas) | Cálculo geográfico | Numérico |

#### Países que provavelmente lideram modo B (hipótese a validar)

Portugal (IFICI, sucessor do NHR), Espanha (Beckham), Estônia (e-Residency + DNV), Cyprus (non-dom), Malta, Croácia, Grécia, Itália (regime imposto fixo), Argentina (LATAM tax-friendly), México, Costa Rica, Uruguai, Geórgia (1% até $155k), EAU/Dubai (zero IR).

Países que **só** fazem sentido em modo A (não modo B): EUA, Canadá, Reino Unido, Alemanha, Países Baixos, Austrália — você quer estar empregado lá pelo salário, não morar de fora.

### 7.5.3 Implicações no dashboard

```
┌─ Perfil: ( ) Pleno  (●) Sênior ───────────┐
├─ Modo:   (●) Local  ( ) Remoto ───────────┤
├─ Pesos:  TECH ─●──── 25%  ────────────────┤
│          VISA ─●──── 25%                  │
│          PPP  ─●──── 25%                  │
│          MACRO ─●─── 25%                  │
└────────────────────────────────────────────┘

[Top 20 ranking — atualiza em tempo real]
[Heatmap por dimensão]
[Detalhe do país selecionado]
```

Total de combinações: 2 perfis × 2 modos = **4 rankings pré-computados**. Pesos personalizados rodam em JS no cliente — instantâneo.

## 8. Validações automáticas (sanity checks no fim do pipeline)

O ETL falha se:

- Top 10 do score default **não tiver pelo menos 5 países OECD** (sinal de bug de normalização).
- Brasil cair fora do intervalo [posição 50-110] no ranking default (calibração).
- Algum país tiver score `NaN` ou fora do intervalo [0, 100].
- Soma de pesos das 4 dimensões ≠ 100% (fora de tolerância 0.01).

## 9. Fontes priorizadas pro MVP

Conforme `01_catalogo_fontes.xlsx` (filtro Prioridade=Alta) **+ adições do modo remoto**:

**META + multi-dim:** GII 2025, IEF 2026, HDI 2025
**TECH:** Stack Overflow Survey 2024, GTCI 2023
**VISA:** Henley 2026, OECD Migration, EU Blue Card, vistos nacionais (manual), **DNV catalog (manual)**
**PPP:** Numbeo, World Bank PPP, OECD Taxing Wages, **regimes fiscais expat (manual)**, **Speedtest Global Index**
**MACRO:** IMF WEO 2025, WB WGI, GPI 2025

~17-18 fontes na fase 1. Resto entra como Fase 2.

## 10. Cronograma estimado (MVP)

| Fase | Entregável | Tempo |
|---|---|---|
| 1. Catálogo (✅ feito) | `01_catalogo_fontes.xlsx` | — |
| 2. Metodologia (em revisão) | este doc | — |
| 3. Esqueleto Python | `pyproject.toml`, módulos vazios, fixtures | 0.5 dia |
| 4. Coleta das 15 fontes Alta | `data/raw/*.csv` | 1.5 dia |
| 5. Normalização + score | `data/final/countries.json` | 1 dia |
| 6. Dashboard artifact | HTML + Chart.js + sliders | 1 dia |
| 7. Validação manual | revisão dos top 20 com olhar crítico | 0.5 dia |

**Total MVP:** ~4.5 dias de trabalho focado.

---

## Decisões fechadas em 2026-05-04

1. **Pesos default:** 25% × 4 (neutros). [Guilherme]
2. **Brasil entra no ranking** (calibração + curiosidade). [Guilherme]
3. **Gates de instabilidade:** dois níveis — `MACRO < 25 → ×0.7` e `MACRO < 15 → ×0.4`. [Claude, delegado]
4. **Perfis salariais:** Pleno e Sênior (toggle no dashboard). [Guilherme]
5. **Trabalho remoto:** Modo A (local) e Modo B (base remota) como toggle no dashboard. Modo B usa receita ponderada US/UK/DE/NL e indicadores novos de DNV + regime fiscal + internet + fuso. [Guilherme — adição importante]

Total de rankings pré-computados: 2 perfis × 2 modos = 4. Pesos rodam no cliente.
