Realizar auditoria de saude do wiki do projeto.

Escopo: $ARGUMENTS (se vazio, audita o wiki inteiro)

Execute as verificacoes:

1. **Paginas orfas**: identifique paginas sem nenhum inbound link de outras paginas

2. **Links quebrados**: encontre [[links]] que apontam para paginas inexistentes

3. **Conceitos sem pagina**: busque termos mencionados 3+ vezes em diferentes paginas que nao tem pagina propria (ex: se "imputacao" aparece em 4 paginas mas nao tem `concepts/imputation.md`, sugira criar)

4. **Contradicoes**: compare claims entre paginas — se houver informacoes conflitantes (ex: dois thresholds diferentes pro gate de MACRO), sinalize

5. **Paginas desatualizadas**: compare `updated` do frontmatter com mudancas recentes no codigo. Se o codigo mudou (ex: collector novo) mas a pagina nao, sinalize

6. **Index desatualizado**: verifique se todas as paginas existentes em `concepts/`, `entities/`, `sources/` estao listadas no index

7. **Frontmatter incompleto**: identifique paginas sem frontmatter obrigatorio (`type`, `title`, `sources`, `related`, `confidence`)

Para cada problema encontrado, sugira a correcao. Pergunte ao usuario antes de aplicar.

Recomendacao: rodar semanalmente ou apos grandes mudancas (novo collector, nova fonte ingerida, mudanca de metodologia).
