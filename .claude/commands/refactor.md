Analise o codigo alterado ou o arquivo/modulo especificado e aplique refactoring baseado nos principios de Clean Code definidos no CLAUDE.md.

Alvo: $ARGUMENTS (se vazio, analise todos os arquivos modificados no git diff)

Checklist obrigatorio:

## Camadas (pipeline ETL)

- [ ] Cada arquivo pertence a sua camada? (`schema` / `countries` / `collectors` / `normalizers` / `aggregator` / `scripts`)
- [ ] Collectors so falam com fonte externa + normalizam pro schema LONG — sem regras de scoring
- [ ] Normalizers operam em DataFrame puro (sem I/O) — testaveis com fixtures
- [ ] Aggregator monta dimensoes e aplica gates — nao escreve raw
- [ ] Scripts orquestram I/O (raw → clean → final), nao tem logica de negocio

## Schema canonico

- [ ] Camada `clean/` em formato LONG (`iso3, indicator_id, value, year, source_id`)?
- [ ] ISO3 como chave (sem nomes de pais soltos)?
- [ ] `direction` (+1/-1) declarada explicitamente em `IndicatorMeta`?
- [ ] Imputacao marcada com `is_imputed=True`?

## Clean Code

- [ ] Todas as funcoes tem menos de 20 linhas?
- [ ] Todos os arquivos tem menos de 150 linhas?
- [ ] Nomes revelam intencao? (sem `data`, `df`, `tmp`, `helpers`, `utils`, `process`)
- [ ] Funcoes fazem UMA coisa?
- [ ] Maximo 3 parametros por funcao? (passar dataclass/dict se precisar mais)
- [ ] Early returns no lugar de nesting profundo?
- [ ] Imports organizados? (stdlib → terceiros → internos)
- [ ] Codigo morto removido?
- [ ] Duplicacao eliminada?
- [ ] Sem `print` debug — usar `logging` quando precisa

## DX e AX

- [ ] Type hints em assinaturas publicas?
- [ ] Docstrings curtas em modulos publicos (1-2 linhas)?
- [ ] `__init__.py` exporta o que outros modulos consomem?
- [ ] Determinismo: testes com fixtures pequenos cobrem comportamento critico?
- [ ] Nomes de arquivos sao previsiveis? (collector novo = `<source-slug>.py` em `collectors/`)

Para cada problema encontrado, corrija diretamente. Nao apenas liste — resolva.
