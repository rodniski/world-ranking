Estamos iniciando trabalho em uma nova tarefa.

Descricao da tarefa: $ARGUMENTS

Siga este fluxo obrigatoriamente:

1. **Classifique o tipo**: analise a descricao e determine se eh `feat`, `fix`, `refactor`, `chore`, `docs` ou `test`.

2. **Enquadre o problema** (skill: framing-problems):
   - O que exatamente precisa mudar?
   - Qual o resultado esperado?
   - Quais areas do codigo sao afetadas? (collectors / normalizers / aggregator / schema / dashboard)
   - Ha riscos ou dependencias?

3. **Pesquise a codebase** antes de codar:
   - Identifique patterns existentes em `code/src/country_innovation/`
   - Verifique se ja existe collector base, normalizer ou util reutilizavel
   - Confirme se o schema LONG (`iso3, indicator_id, value, year, source_id`) cobre o caso

4. **Crie a issue no GitHub**:
   - Use `gh issue create` no repo atual
   - Titulo curto e claro (max 70 chars)
   - Body com: contexto, o que sera feito, areas afetadas, criterios de aceite
   - Labels: `enhancement`, `bug`, `refactor`, `data-source`, etc
   - Guarde o numero da issue

5. **Crie a branch a partir de `main`**:
   - Formato: `{numero-da-issue}-{slug-curto}`
   - Exemplo: `5-collector-hdi` ou `7-normalizer-zscore`
   - Faca checkout da branch nova

6. **Confirme o setup** mostrando:
   - Link da issue criada
   - Nome da branch
   - Enquadramento do problema (1-3 frases)
   - Plano de ataque resumido
   - Arquivos/areas que serao tocados

7. **Comece a trabalhar** seguindo as convencoes do CLAUDE.md.
   - Para tarefas complexas (collector novo, normalizer, gerador de countries.json), crie um plano antes de codar (skill: creating-implementation-plan).
   - Aplique a regra do escoteiro em todo arquivo que tocar.
   - Se um indicador for novo, atualize o catalogo e o `02_metodologia.md` quando relevante.
