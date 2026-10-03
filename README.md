# ds-project-template

Template para projetos de Data Science com **uv**, pipelines de treino/inferência prontos,
**pre-commit**, **pytest** e CI centralizado em [`ds-workflows`](https://github.com/brunocvs7/ds-workflows).

## Começando

```bash
# 1. Crie o repo: botão "Use this template" no GitHub (ou: gh repo create meu-projeto --template brunocvs7/ds-project-template --public --clone)
# 2. Proteja a main (uma vez por repo):
../ds-workflows/scripts/protect-repo.sh brunocvs7/meu-projeto
# 3. Ambiente + hooks:
make setup
# 4. Veja tudo funcionando com os dados de exemplo:
make demo
```

`make` sem argumentos lista todos os comandos.

## Estrutura

```
.
├── data/
│   ├── raw/              # dados originais, imutáveis           ┐
│   ├── external/         # dados de terceiros                   │ fora do git
│   ├── interim/          # etapas intermediárias                │ (só .gitkeep)
│   ├── processed/        # dados prontos para modelagem         │
│   └── predictions/      # saída do pipeline de inferência      ┘
├── models/               # model.joblib gerado pelo treino (fora do git)
├── notebooks/            # exploração: NN-iniciais-descricao.ipynb (ex.: 01-bcv-eda.ipynb)
├── reports/figures/      # gráficos; reports/metrics.json é gerado pelo treino
├── src/ds_project/
│   ├── paths.py          # caminhos padrão (sobrescrevíveis via .env)
│   ├── config.py         # target, seed, test_size
│   ├── data.py           # ✏️ load_raw() e clean()
│   ├── features.py       # ✏️ build_features()
│   ├── model.py          # ✏️ build_model()  (pré-processamento + algoritmo)
│   ├── evaluate.py       # ✏️ compute_metrics()
│   └── pipelines/
│       ├── train.py      # 🔒 pronto: raw → clean → features → split → fit → métricas → salva
│       └── predict.py    # 🔒 pronto: carrega modelo → MESMA clean/features → predições
├── tests/
│   ├── fixtures/sample_raw.csv   # amostra pequena dos dados (versionada!)
│   └── test_<módulo>.py          # um arquivo de teste por módulo de src/
├── Makefile · .env.example · .pre-commit-config.yaml · pyproject.toml · uv.lock
```

## Os pipelines

Você implementa os arquivos marcados com ✏️; os pipelines 🔒 já orquestram tudo:

| Etapa | Função | Regra |
|---|---|---|
| Carga | `data.load_raw(path)` | lê de onde for (csv, parquet, SQL...) |
| Limpeza | `data.clean(df)` | **não pode usar o target** — roda também na inferência |
| Features | `features.build_features(df)` | só transformações linha a linha, sem `fit` |
| Modelo | `model.build_model(seed)` | retorna um `sklearn.Pipeline`; scaler/encoder/imputer ficam **aqui dentro** (evita data leakage) |
| Avaliação | `evaluate.compute_metrics(...)` | retorna um `dict` de métricas |

```bash
make train                      # usa data/raw/dataset.csv (ou RAW_FILE do .env)
make predict INPUT=novos.csv    # escreve data/predictions/predictions.csv
```

O exemplo incluído é uma classificação de churn sobre dados sintéticos — substitua pelo seu problema.

**Mantenha `tests/fixtures/sample_raw.csv` atualizado** com uma amostra pequena (algumas centenas de
linhas, anonimizadas) no formato dos seus dados reais: o CI treina e prediz em cima dela.

## Ambiente com uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # instala o uv (uma vez por máquina)

uv sync                          # cria .venv (Python do .python-version) e instala o uv.lock
uv add lightgbm                  # dependência da aplicação
uv add --dev matplotlib          # dependência só de desenvolvimento
uv remove lightgbm
uv lock --upgrade                # atualiza versões
uv run python -m ds_project.pipelines.train   # roda qualquer coisa no ambiente, sem ativar a venv
```

Sempre faça commit de `pyproject.toml` **e** `uv.lock` juntos (o pre-commit confere).

Variáveis de ambiente: `cp .env.example .env` (feito pelo `make setup`). O Makefile carrega o `.env`
automaticamente; o `.env` nunca vai para o git.

## Renomeando o pacote

O nome `ds_project` é só um placeholder. Para trocar (ex.: `churn`):

1. `git mv src/ds_project src/churn`
2. Em `pyproject.toml`: `name = "churn"` e `packages = ["src/churn"]`
3. Substitua os imports: `grep -rl ds_project src tests | xargs sed -i '' 's/ds_project/churn/g'`
4. `uv sync && make test`

O Makefile e o CI descobrem o nome do pacote sozinhos.

## Qualidade: três camadas

| Camada | Quando roda | O quê |
|---|---|---|
| **pre-commit** | a cada `git commit` (e no CI) | ruff (lint + format), nbstripout, bloqueio de arquivos >1 MB, chaves privadas, uv.lock sincronizado |
| **testes** (`tests/`) | `make test` e CI | testes unitários escritos por você |
| **conformidade** (`ds-check`) | `make check` e CI | estrutura de pastas, nada de dados no git, notebooks limpos e bem nomeados, um teste por módulo, sem caminhos absolutos, dependências declaradas (deptry), pipeline treina + prediz na amostra e é reprodutível com a mesma seed |

`make ci` roda as três — se passar local, passa no PR.

## Fluxo de branches

A `main` só recebe código por Pull Request, com CI verde, vindo de uma branch `<tipo>/<descricao>`:

| Tipo | Uso |
|---|---|
| `feature/` | funcionalidade nova |
| `fix/` | correção de bug |
| `hotfix/` | correção urgente em produção |
| `refactor/` | reestruturação sem mudar comportamento |
| `experiment/` | testar um modelo, feature ou hipótese |
| `docs/` | documentação |
| `chore/` | dependências, configuração, manutenção |
| `test/` | só testes |
| `ci/` | workflows e automação |

```bash
git switch -c feature/modelo-churn
# ... commits ...
git push -u origin feature/modelo-churn
gh pr create --fill
```

Checks obrigatórios: `ci / lint`, `ci / test`, `ci / conformance`, `ci / branch-name`.
Merge apenas por squash; a branch é apagada após o merge. Push direto e force-push na `main` são bloqueados.

As regras (lista de prefixos, checks, proteção) são mantidas em
[`ds-workflows`](https://github.com/brunocvs7/ds-workflows) — mudanças lá valem para todos os projetos.
