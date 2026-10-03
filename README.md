# ds-project-template

Template para projetos de Data Science com **uv**, **ruff**, **pytest** e CI no GitHub Actions.
Merges na `main` só acontecem via Pull Request vindo de uma branch `feature/*`, com CI verde.

## Estrutura

```
.
├── configs/              # parâmetros (yaml) do projeto
├── data/
│   ├── raw/              # dados originais, imutáveis (não versionados)
│   ├── external/         # dados de terceiros
│   ├── interim/          # dados intermediários
│   └── processed/        # dados finais para modelagem
├── models/               # modelos treinados / serializados (não versionados)
├── notebooks/            # exploração (nomeie como 01-bcv-eda.ipynb)
├── reports/figures/      # gráficos e relatórios gerados
├── scripts/              # utilitários (ex.: setup-branch-protection.sh)
├── src/ds_project/       # código do projeto (pacote importável)
├── tests/                # testes com pytest
├── pyproject.toml        # dependências e config de ruff/pytest
└── uv.lock               # lockfile (sempre versionado)
```

> Ao criar um projeto novo, renomeie `src/ds_project` e o campo `name` do `pyproject.toml`.

## Ambiente com uv

Instale o uv (uma vez por máquina):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Crie o ambiente e instale tudo (inclusive as dependências de dev):

```bash
uv sync                 # cria .venv com a versão do .python-version e instala o uv.lock
```

Gerenciar pacotes:

```bash
uv add pandas scikit-learn          # dependência da aplicação
uv add --dev ipykernel matplotlib   # dependência só de desenvolvimento
uv remove pandas                    # remove
uv lock --upgrade                   # atualiza versões no lockfile
uv python install 3.12              # instala outra versão de Python, se precisar
```

Rodar coisas dentro do ambiente (sem precisar ativar a venv):

```bash
uv run python -m ds_project
uv run jupyter lab                  # depois de `uv add --dev jupyterlab`
```

Sempre faça commit de `pyproject.toml` **e** `uv.lock` juntos.

## Qualidade de código

```bash
uv run ruff check .          # lint
uv run ruff check . --fix    # corrige o que der automaticamente
uv run ruff format .         # formata
uv run pytest                # testes
```

O CI (`.github/workflows/ci.yml`) roda exatamente esses comandos em todo PR.

## Fluxo de branches

1. `git switch -c feature/minha-feature`
2. Commits + `git push -u origin feature/minha-feature`
3. Abra um PR para `main`
4. Os checks obrigatórios precisam passar:
   - `lint` — ruff check + ruff format --check
   - `test` — pytest
   - `branch-name` — a branch de origem precisa começar com `feature/`
5. Merge (squash). A branch é apagada automaticamente.

Push direto, force-push e deleção da `main` são bloqueados pelo ruleset
`.github/rulesets/protect-main.json`.

### Aplicando a proteção em um repo novo

Rulesets **não** são copiados quando se usa "Use this template". Depois de criar o repo:

```bash
./scripts/setup-branch-protection.sh            # usa o repo do diretório atual
# ou, com a CLI ds-agent-kit:
dskit protect
```

> Rulesets em repositórios **privados** exigem GitHub Pro/Team. Em repos públicos são gratuitos.
