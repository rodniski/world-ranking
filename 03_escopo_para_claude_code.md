# Country Innovation — Escopo para Claude Code

**Como usar este documento:** copie ele pra raiz do repo como `CLAUDE.md` (Claude Code lê esse arquivo automaticamente como contexto persistente). Daí abra um Claude Code session na pasta e diga: *"Leia CLAUDE.md e implemente as tasks pendentes na ordem."*

---

## 1. O que é o projeto

Pipeline ETL + dashboard que ranqueia ~190 países pela viabilidade de imigração de um software engineer brasileiro pleno→sênior. O usuário é o Guilherme. Ele quer um ranking pessoalmente acionável (pesos ajustáveis), não um relatório acadêmico.

Duas modalidades de uso são suportadas:
- **Modo Local** — você se muda e trabalha pra empregador local.
- **Modo Remoto** — você trabalha remoto pra empregador estrangeiro (US/UK/DE/NL) e otimiza onde MORAR.

E dois perfis salariais: **pleno** (4-7 anos) e **sênior** (8+ anos), com salários medianos diferentes por perfil em cada país.

Total de rankings pré-computados: 2 perfis × 2 modos = **4 combinações**. Pesos rodam em JS no cliente (instantâneo).

## 2. Estado atual (o que JÁ EXISTE — não refazer)

```
Country Innovation/
├── 01_catalogo_fontes.xlsx       ← 33 fontes catalogadas (priorizadas)
├── 02_metodologia.md             ← decisões fechadas (z-score, gates, etc.)
├── 03_escopo_para_claude_code.md ← este arquivo
├── code/
│   ├── pyproject.toml            ← Python 3.11+, deps fixadas
│   ├── requirements.txt
│   ├── README.md
│   ├── src/country_innovation/
│   │   ├── __init__.py
│   │   ├── schema.py             ← LONG_COLUMNS, IndicatorMeta, Direction, Dimension
│   │   ├── countries.py          ← to_iso3(), is_in_scope(), MANUAL_OVERRIDES
│   │   ├── collectors/
│   │   │   ├── __init__.py
│   │   │   ├── base.py           ← class Collector(ABC) com fetch/normalize/save
│   │   │   ├── wb_ppp.py         ← FUNCIONAL: WB GNI per capita PPP
│   │   │   ├── heritage.py       ← FUNCIONAL: scrape all-country-scores
│   │   │   └── gii.py            ← FUNCIONAL: scrape WIPO results page
│   │   └── normalizers/__init__.py  ← STUB
│   └── scripts/
│       └── run_collectors.py     ← roda os 3 collectors e grava em ../data/raw/
└── data/{raw,clean,final}/       ← vazias, populadas pelo pipeline
```

**3 collectors prontos** (mas não testados em rede ainda — testar primeiro):
1. `WorldBankPPP` (source_id=`WB-PPP`) — API JSON pública, indicador `NY.GNP.PCAP.PP.CD`.
2. `Heritage` (source_id=`IEF-2026`) — HTML scrape de `https://economicfreedom.heritage.org/pages/all-country-scores`.
3. `GII` (source_id=`GII-2025`) — HTML scrape de `https://www.wipo.int/web-publications/global-innovation-index-2025/en/gii-2025-results.html`.

Se Heritage ou GII renderizarem a tabela client-side (JS), `pandas.read_html` falha. Os collectors têm fallback BS4 manual; se ambos falharem, investigar Network tab no DevTools, achar o JSON real, e reescrever o `fetch()`. **Não tentar `requests-html` ou Playwright a menos que seja estritamente necessário** — adiciona complexidade pesada de deploy.

## 3. Convenções fixadas (não mudar sem revalidar com Guilherme)

### 3.1 Schema canônico
Camada `clean/` é em formato **long**: `(iso3, indicator_id, value, year, source_id)`. Toda fonte normaliza pra esse schema. ISO3 é a chave, sempre. Casos especiais (Kosovo=XKX, Taiwan=TWN, etc.) já estão em `countries.MANUAL_OVERRIDES`.

### 3.2 Quatro dimensões
- **TECH** — mercado de trabalho tech / salário
- **VISA** — facilidade de visto / pathway pra residência+cidadania
- **PPP** — custo de vida e salário líquido em PPP
- **MACRO** — estabilidade macro e segurança

### 3.3 Normalização (ver `02_metodologia.md` §5)
Por indicador: aplicar direção (`+1`/`-1`) → z-score global → clip ±3σ → mapear pra 0-100 via `(z+3)*100/6`.

### 3.4 Imputação (§4)
Indicador descartado se cobertura < 70% dos países do escopo. Para missing nos aceitos: imputar pela mediana global da fonte e marcar `is_imputed=True`.

### 3.5 Gates de penalização (§7)
- País sem visto viável → `VISA = 0` (não imputa).
- `MACRO < 25` → fator `0.7` no score final.
- `MACRO < 15` → fator `0.4`.

### 3.6 Pesos default
25% × 4 (neutro). Sliders no dashboard renormalizam pra somar 100%.

### 3.7 Sanity checks (§8)
Pipeline FALHA se:
- Top 10 default não tiver ≥5 países OECD.
- Brasil cair fora de [50, 110] no ranking default.
- Algum país com score `NaN` ou fora de [0, 100].

## 4. Tasks pendentes (ordem de execução)

### Task A — Validar os 3 collectors em rede
```bash
cd code && python -m venv .venv && source .venv/bin/activate
pip install -e .
python scripts/run_collectors.py
```
Esperado: 3 CSVs em `../data/raw/` (`WB-PPP.csv`, `IEF-2026.csv`, `GII-2025.csv`), cada um com 130-200 linhas.

Se `Heritage` ou `GII` falharem com "tabela não encontrada":
1. `curl -s -A "Mozilla/5.0..." <url> | grep -o '<table' | wc -l` — quantas tabelas tem o HTML.
2. Se zero, o site renderiza client-side. Inspecionar Network tab pra achar o JSON real.
3. Reescrever `fetch()` pra consumir o endpoint JSON em vez de scrape HTML.

### Task B — Implementar collectors prioritários restantes (Prioridade=Alta no catálogo)
Lista de fontes Alta prio que ainda não têm collector — ver `01_catalogo_fontes.xlsx`. As mais importantes:
- HDI 2025 (UNDP) — CSV oficial, fácil
- Stack Overflow Survey 2024 — CSV público, mas precisa filtrar por país e calcular mediana de salário por perfil (pleno/sênior)
- GTCI 2023 (INSEAD) — Excel oficial
- IMF WEO Apr 2025 — API SDMX ou Excel
- WB Worldwide Governance Indicators (WGI) — API igual a `wb_ppp.py`, indicadores RL.EST, CC.EST etc
- Henley Passport Index 2026 — HTML scrape
- Numbeo COL 2026 — HTML, cuidado com rate limit
- OECD Taxing Wages — Excel
- GPI 2025 (IEP) — Excel
- EF EPI 2024 — HTML
- Speedtest Global Index — HTML

Cada collector segue o padrão de `wb_ppp.py` ou `heritage.py`. Adicionar à `run_collectors.py` quando pronto.

### Task C — Curar manualmente: Digital Nomad Visas + regimes fiscais
Não existe dataset pronto pra isso. Criar `data/manual/dnv_catalog.csv` com colunas:
```
iso3, has_dnv, income_threshold_usd_month, max_stay_months, path_to_pr_years,
family_inclusion, tax_regime_name, effective_rate_foreign_income, applies_to_employed
```
Cobrir ~50 países (todos com DNV ativo + os principais sem DNV mas com regime fiscal — Portugal IFICI, Espanha Beckham, Itália €100k flat, Cyprus non-dom, Geórgia 1%, EAU 0%, etc.). Fontes: nomadgate.com, sites oficiais, taxsummaries.pwc.com.

### Task D — Implementar normalizers/aggregator (`02_metodologia.md` §5-7)
Módulo `normalizers/transforms.py`:
```python
def apply_direction(s: pd.Series, direction: int) -> pd.Series: ...
def zscore_clip(s: pd.Series, clip_sigma: float = 3.0) -> pd.Series: ...
def to_0_100(z: pd.Series, clip_sigma: float = 3.0) -> pd.Series: ...
def impute_global_median(df_long: pd.DataFrame) -> pd.DataFrame: ...
```
Módulo `aggregator.py`:
```python
def aggregate_dimension(df_wide: pd.DataFrame, dim: str, indicators_meta: dict) -> pd.Series: ...
def apply_gates(scores: pd.DataFrame) -> pd.DataFrame: ...
def final_score(scores: pd.DataFrame, weights: dict[str, float]) -> pd.Series: ...
```
Tudo deterministic — testes unitários com fixtures pequenos (10 países sintéticos).

### Task E — Gerar `data/final/countries.json`
Schema:
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
    },
    ...
  ]
}
```

### Task F — Dashboard
**Importante:** o dashboard é entregue como **Cowork artifact** (HTML standalone), não como app SvelteKit. Quando você terminar `countries.json`, o Guilherme vai trazer o JSON de volta pro Cowork e o dashboard é construído lá.

O que o Claude Code precisa entregar nessa frente é só:
1. Um exemplo HTML standalone em `code/scripts/preview_dashboard.html` que carrega `countries.json` por `fetch('../data/final/countries.json')` e mostra o ranking. Serve pra debugging local.
2. Documentar o schema de `countries.json` no README.

### Task G — Validação final
Criar `04_validacao.md` na raiz com:
- Top 20 default por modo×perfil.
- Posição do Brasil em cada cenário.
- Sanity checks (todos passaram?).
- 5 surpresas observadas no ranking, com explicação possível.

## 5. Stack e dependências

- Python 3.11+ (assume `venv` local, não `conda`).
- pandas, numpy, requests, beautifulsoup4, lxml, pdfplumber, country-converter, scipy, pyyaml, openpyxl. Versões fixadas em `pyproject.toml`.
- **Não introduzir Playwright/Selenium sem aprovar com Guilherme.** Se um site precisar JS rendering, primeiro investigar se há JSON endpoint subjacente.
- **Não introduzir banco de dados.** Tudo em CSV/parquet/JSON. O dataset cabe em RAM.

## 6. Decisões deferidas (V2)

A reescrita do coletor em **Go**, **Rust** ou **C#** entra depois do MVP funcional. Não começar antes de o ranking estar validado pelo Guilherme. Quando entrar, o reuso é o `countries.json` — é o contrato estável entre as camadas.

## 7. Como pedir ajuda ao Guilherme

Casos onde parar e perguntar (não decidir sozinho):
- Adicionar dimensão nova além das 4 atuais.
- Mudar fórmula de normalização (z-score → outra coisa).
- Mudar peso default (sair de 25%×4).
- Excluir uma fonte do catálogo Alta prioridade.
- Mudar threshold dos gates de MACRO.

Caso onde decidir e seguir (basta deixar registrado em commit message):
- Adicionar collector novo de fonte Alta no catálogo.
- Lidar com edge case de país (ex: país novo que apareceu numa fonte e não no `MANUAL_OVERRIDES`).
- Refatoração interna que não muda contratos.

## 8. Comando inicial sugerido

```
[no terminal, dentro da pasta do projeto]
$ cp 03_escopo_para_claude_code.md CLAUDE.md
$ git init && git add . && git commit -m "initial scaffold + decisões metodológicas"
$ claude
```

Daí na primeira mensagem:
> Leia CLAUDE.md, valide os 3 collectors existentes rodando `scripts/run_collectors.py`, e me reporte o resultado antes de começar Task B.
