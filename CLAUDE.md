# CLAUDE.md

## Comportamento Autonomo do Agente

O agente DEVE executar automaticamente sem esperar comando explicito:

### Inicio de sessao
- Ler `obsidian/wiki/hot.md` para herdar contexto recente
- Consultar `obsidian/wiki/` quando precisar de contexto sobre arquitetura, decisoes ou dominio

### Ao receber tarefa
- Pesquisar patterns existentes em `code/src/country_innovation/` antes de implementar
- Se complexa, criar plano antes de codar (skill: creating-implementation-plan)

### Durante implementacao
- Aplicar Clean Code: funcoes < 20 linhas, arquivos < 150 linhas, naming revela intencao
- Seguir o schema canonico LONG (`iso3, indicator_id, value, year, source_id`) — toda fonte normaliza
- Regra do escoteiro: deixar codigo melhor do que encontrou, sem pedir permissao

### Ao finalizar
- Rodar `ruff format .`, `ruff check .`, `pytest` (se houver testes relevantes)
- Se falhar, corrigir e re-rodar
- Commit convencional: `feat(escopo): descricao`, `fix(escopo): descricao`
- Se houve decisao ou aprendizado: salvar em `obsidian/wiki/`, atualizar `index.md` e `log.md`
- Atualizar `obsidian/wiki/hot.md` com estado atual

### Isolamento — NUNCA criar worktree
- **NUNCA** rodar `git worktree add` direto nem indiretamente
- **NUNCA** usar `isolation: "worktree"` no tool `Agent` ao delegar pra subagents
- **NUNCA** usar os tools `EnterWorktree` / `ExitWorktree`
- Branch eh suficiente para isolar trabalho — worktree duplica `.venv` e cria atrito desnecessario

## Projeto

**Country Innovation Ranking** — pipeline ETL Python que ranqueia ~190 paises pela viabilidade de imigracao de um software engineer brasileiro pleno→senior. Output final eh `data/final/countries.json`, consumido por dashboard HTML standalone (entregue como Cowork artifact, nao como app).

```
world-ranking/
  01_catalogo_fontes.xlsx       Catalogo de 33 fontes priorizadas
  02_metodologia.md             Decisoes fechadas (z-score, gates, etc)
  03_escopo_para_claude_code.md Escopo original (referencia historica)
  CLAUDE.md                     Este arquivo
  code/
    pyproject.toml              Python 3.11+, deps fixadas
    src/country_innovation/
      schema.py                 LONG_COLUMNS, IndicatorMeta, Direction, Dimension
      countries.py              to_iso3(), is_in_scope(), MANUAL_OVERRIDES
      collectors/               1 modulo por fonte, classe base em base.py
      normalizers/              direction, z-score, clip, escala 0-100
      aggregator.py             dimensao -> score final + gates
    scripts/
      run_collectors.py         Roda collectors, grava em ../data/raw/
  data/
    raw/                        CSV bruto por fonte
    clean/                      Long parquet canonico
    final/                      countries.json + manifests
  obsidian/                     Memoria persistente (wiki)
```

## Comandos

```bash
cd code
python -m venv .venv && source .venv/bin/activate
pip install -e .

python scripts/run_collectors.py    # Coleta raw/
ruff format .                       # Formata
ruff check .                        # Lint
pytest                              # Testes (quando existirem)
```

## Convencoes Rapidas

- **Schema canonico**: camada `clean/` em formato LONG (`iso3, indicator_id, value, year, source_id`). ISO3 eh a chave (Kosovo=XKX, Taiwan=TWN — ver `MANUAL_OVERRIDES`)
- **4 dimensoes**: TECH, VISA, PPP, MACRO (default 25% cada)
- **Normalizacao**: `direction` (+1/-1) → z-score → clip ±3σ → `(z+3)*100/6` → `[0,100]`
- **Imputacao**: descartar indicador se cobertura < 70%; imputar mediana global na fonte com `is_imputed=True`
- **Gates**: `VISA=0` se sem visto viavel; `MACRO<25 → ×0.7`; `MACRO<15 → ×0.4`
- **Sanity checks** (pipeline FALHA): top 10 default precisa ter ≥5 OECD; Brasil em [50,110]; sem `NaN` ou fora de `[0,100]`
- **Estilo**: `ruff format` (Black-compatible), funcoes <20 linhas, naming revela intencao, sem `data`/`utils`/`helpers` genericos
- **Testes**: `pytest` com fixtures pequenos (10 paises sinteticos), tudo deterministic
- **Sem novas deps**: nada de Playwright/Selenium/banco — pandas/numpy/requests/bs4 ja cobrem

## Workflow

- Branch base: `main` (repo solo)
- Branch de trabalho: `{numero-issue}-{slug-curto}` (ex: `5-collector-hdi`, `7-normalizer-zscore`)
- PRs sempre para `main`
- Repo: [rodniski/world-ranking](https://github.com/rodniski/world-ranking)

## Wiki (Memoria Persistente)

Diretorio `obsidian/` — conhecimento compilado e incremental do projeto.

- `obsidian/wiki/hot.md` — contexto recente (ler no inicio)
- `obsidian/wiki/index.md` — catalogo de todas as paginas
- `obsidian/wiki/concepts/` — metodologia, normalizacao, gates
- `obsidian/wiki/entities/` — collectors, schema canonico, countries.json
- `obsidian/wiki/sources/` — fontes externas catalogadas

Regras: nunca deletar paginas, sempre atualizar `index.md` e `log.md`, sinalizar contradicoes.

## Skills

Skills relevantes a usar conforme contexto (todos disponiveis via Skill tool global):

- `framing-problems` — definir problema antes de codar
- `brainstorming` — explorar opcoes antes de implementar
- `creating-implementation-plan` — planos detalhados pra tarefas complexas
- `web-research` — buscar docs externas (pandas/scipy/IMF/WB)
- `locating-code` / `finding-code-patterns` — entender o que ja existe
- `testing-patterns` — testes deterministic com fixtures
- `verification-before-completion` — rodar `ruff check`/`pytest` antes de afirmar conclusao
- `clean-code` — refactor focado em naming, tamanho, intent
- `revising-prose` — pra textos do `02_metodologia.md`, README e wiki

## Tasks pendentes do MVP

Ver `03_escopo_para_claude_code.md` §4. Ordem:

- **A**: validar collectors em rede (`run_collectors.py`)
- **B**: implementar collectors prioritarios restantes (HDI, Stack Overflow, GTCI, IMF, WGI, Henley, Numbeo, OECD, GPI, EF EPI, Speedtest)
- **C**: curar manualmente DNV catalog + regimes fiscais → `data/manual/dnv_catalog.csv`
- **D**: implementar `normalizers/transforms.py` + `aggregator.py`
- **E**: gerar `data/final/countries.json` (schema documentado em `02_metodologia.md`)
- **F**: HTML standalone de preview em `code/scripts/preview_dashboard.html`
- **G**: `04_validacao.md` com top 20 + posicao do Brasil + 5 surpresas

## Pedir aprovacao do Guilherme antes de

- Adicionar dimensao alem das 4 atuais
- Mudar formula de normalizacao
- Mudar peso default (sair de 25%×4)
- Excluir fonte de prioridade Alta
- Mudar threshold dos gates
- Adicionar Playwright/Selenium ou banco de dados

## Decidir e seguir (so deixar registrado em commit)

- Adicionar collector de fonte Alta no catalogo
- Edge case de pais novo (atualizar `MANUAL_OVERRIDES`)
- Refatoracao interna que nao muda contratos

## Anti-Patterns

- Quebrar o schema LONG em `clean/`
- Imputar com media da dimensao em vez de mediana global
- Hardcodar pesos no codigo (sempre via `weights.yaml` ou parametro)
- Usar `pandas.read_html` sem fallback BS4 manual
- Adicionar Playwright/Selenium sem aprovar
- Introduzir banco de dados (CSV/parquet/JSON cabem em RAM)
- Funcoes > 20 linhas, arquivos > 150 linhas
- Nomes genericos (`data`, `utils`, `helpers`, `temp`)
- Criar git worktree (usar branch no repo principal)
- Mexer em `data/raw/` ou `data/manual/` no automatico (somente humano cura)
