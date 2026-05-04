Ingerir novo conhecimento no wiki do projeto.

Input: $ARGUMENTS (pode ser um arquivo, URL, conceito, decisao, ou aprendizado)

Siga o protocolo de ingest:

1. **Identifique o tipo** do conteudo:
   - Source: material externo (artigo, doc oficial de IMF/WB/OECD, spec de uma fonte)
   - Concept: ideia, pattern, metodo (z-score, gates, imputacao)
   - Entity: modulo, collector, schema, contrato (countries.json)
   - Comparison: analise comparativa, ADR (z-score vs min-max, mediana global vs dimensional)
   - Synthesis: post-mortem, learning, ensaio (ex: "porque o ranking de Modo B coloca Geórgia no top 5")

2. **Crie a pagina** em `obsidian/wiki/{tipo}/` usando o template de `obsidian/templates/`

3. **Cross-reference**: identifique todas as paginas existentes relacionadas e adicione links bidirecionais (atualize as paginas existentes tambem)

4. **Atualize o index**: adicione a nova entrada em `obsidian/wiki/index.md`

5. **Atualize o log**: adicione entrada em `obsidian/wiki/log.md` com timestamp, acao e paginas tocadas

6. **Atualize hot.md**: se relevante para o contexto atual, atualize `obsidian/wiki/hot.md`

7. **Verifique contradicoes**: se o novo conteudo contradiz algo existente (ex: trocar threshold de gate sem aprovacao), sinalize explicitamente com `confidence: low` e documente a contradicao

Regras:

- NUNCA escrever em `data/raw/` ou `data/manual/` (somente humano coloca conteudo la)
- NUNCA deletar paginas existentes (marque como deprecated se necessario)
- Toda nova pagina deve ter no minimo 2 links para paginas existentes
- Use frontmatter YAML completo conforme os templates
