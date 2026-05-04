O trabalho na tarefa atual foi finalizado. Execute o fluxo de finalizacao:

1. **Format**: rode `cd code && ruff format .` para garantir formatacao consistente
2. **Lint**: rode `cd code && ruff check .` para validar o codigo
3. **Type check** (opcional, se `pyright` estiver disponivel): `cd code && pyright`
4. **Testes**: rode `cd code && pytest` se houver testes relevantes para os arquivos alterados

Se algum passo falhar:

- Corrija o problema automaticamente
- Rode o passo novamente ate passar

Quando tudo estiver verde:

5. **Stage**: adicione apenas os arquivos relevantes (nunca `.venv/`, `__pycache__/`, `*.egg-info`, `data/raw/` se for csv pesado, ou credentials)
6. **Commit**: crie um commit com mensagem convencional:
   - Formato: `{tipo}(escopo): descricao curta`
   - Exemplos: `feat(collectors): add HDI 2025 collector`, `fix(normalizers): handle NaN in zscore_clip`
   - Se houver uma issue relacionada na branch atual, adicione `closes #N` no body
7. **Push**: faca push da branch para o remote (`git push -u origin <branch>` se for o primeiro push)

Ao finalizar, mostre:

- Resumo das mudancas
- Resultado de cada validacao (format, lint, types, test)
- Hash e mensagem do commit
- Comando sugerido para abrir o PR: `gh pr create --base main`
