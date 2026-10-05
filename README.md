# ds-project-template

Template para projetos de Data Science em Python. Todo projeto criado a partir dele já vem com:

- **ambiente reprodutível** com [uv](https://docs.astral.sh/uv/) (Python fixo + lockfile);
- **pipelines de treino e inferência prontos**: você só implementa carga, limpeza, features, modelo e métricas;
- **qualidade automática**: ruff e outros hooks rodando a cada commit (pre-commit);
- **testes** com pytest e uma amostra de dados versionada;
- **verificações de conformidade** que garantem o padrão do projeto;
- **CI no GitHub Actions** que roda tudo isso em cada Pull Request;
- **fluxo de branches padronizado**: a `main` só recebe código via PR, com CI verde.

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Criando um projeto novo](#2-criando-um-projeto-novo)
3. [Estrutura de pastas](#3-estrutura-de-pastas)
4. [Ambiente e dependências com uv](#4-ambiente-e-dependências-com-uv)
5. [Configuração: `.env`, `paths.py` e `config.py`](#5-configuração-env-pathspy-e-configpy)
6. [Pipelines de treino e inferência](#6-pipelines-de-treino-e-inferência)
7. [Notebooks](#7-notebooks)
8. [Testes](#8-testes)
9. [pre-commit](#9-pre-commit)
10. [Verificações de conformidade](#10-verificações-de-conformidade)
11. [Fluxo de desenvolvimento](#11-fluxo-de-desenvolvimento)
12. [CI no GitHub](#12-ci-no-github)
13. [Referência de comandos `make`](#13-referência-de-comandos-make)
14. [Claude Code: skills e agentes](#14-claude-code-skills-e-agentes)
15. [Desfazendo coisas](#15-desfazendo-coisas)
16. [Problemas comuns](#16-problemas-comuns)

---

## 1. Pré-requisitos

Instale uma vez por máquina:

| Ferramenta | Para quê | Instalação |
|---|---|---|
| **uv** | ambientes e pacotes Python | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **git** | versionamento | já vem no macOS (`git --version`) |
| **make** | atalhos do projeto | já vem no macOS com as Command Line Tools (`xcode-select --install`) |
| **GitHub CLI (`gh`)** | PRs e CI pelo terminal | `brew install gh` e depois `gh auth login -p https` |
| **dskit** *(opcional)* | skills do Claude Code | `uv tool install git+https://github.com/brunocvs7/ds-agent-kit` |

Você **não** precisa instalar Python: o uv baixa a versão definida no projeto.

---

## 2. Criando um projeto novo

### 2.1 Criar o repositório

No GitHub, abra este repositório e clique em **Use this template → Create a new repository**. Escolha o dono (a organização) e o nome do projeto.

Ou pelo terminal:

```bash
gh repo create <org>/<nome-do-projeto> --template brunocvs7/ds-project-template --private --clone
cd <nome-do-projeto>
```

### 2.2 Preparar o ambiente

```bash
make setup
```

O que isso faz:

1. `uv sync` cria a pasta `.venv/` com o Python do `.python-version` e instala todas as dependências na versão exata do `uv.lock`, incluindo o próprio projeto em modo editável;
2. `pre-commit install` ativa os hooks que rodam a cada `git commit`;
3. cria o `.env` a partir do `.env.example`, se ainda não existir.

> Rode `make setup` **em todo clone novo**. O hook do pre-commit fica em `.git/hooks/`, que não é versionado.

### 2.3 Ver tudo funcionando

```bash
make demo
```

Treina e gera predições usando os dados de exemplo (`tests/fixtures/sample_raw.csv`, um problema de churn sintético). Saída esperada:

```
{ "accuracy": 0.65, "f1": 0.3226, "roc_auc": 0.5906 }
Modelo salvo em .../models/model.joblib
300 predições salvas em .../data/predictions/predictions.csv
```

As métricas são baixas de propósito: os dados são quase aleatórios. O objetivo é só validar o fluxo.

### 2.4 Renomear o pacote (recomendado)

O pacote `ds_project` é um nome provisório. Para trocar, por exemplo para `churn`, faça numa branch (veja a [seção 11](#11-fluxo-de-desenvolvimento)):

```bash
git switch -c chore/renomeia-pacote
git mv src/ds_project src/churn
grep -rl ds_project src tests pyproject.toml | xargs sed -i '' 's/ds_project/churn/g'
sed -i '' 's/^name = "ds-project"/name = "churn"/' pyproject.toml
uv sync && make ci
```

O Makefile, o CI e as verificações de conformidade descobrem o nome do pacote sozinhos.

### 2.5 Skills do Claude Code (opcional)

```bash
dskit add --all
```

Veja a [seção 14](#14-claude-code-skills-e-agentes).

---

## 3. Estrutura de pastas

```
.
├── data/
│   ├── raw/              # dados originais, imutáveis (nunca edite à mão)
│   ├── external/         # dados de terceiros
│   ├── interim/          # resultados intermediários
│   ├── processed/        # dados prontos para modelagem
│   └── predictions/      # saída do pipeline de inferência (criada automaticamente)
├── models/               # modelos treinados (model.joblib)
├── notebooks/            # exploração e análises
├── reports/
│   ├── figures/          # gráficos gerados
│   └── metrics.json      # métricas do último treino (gerado)
├── src/ds_project/       # código do projeto: um pacote Python importável
│   ├── paths.py          # caminhos padrão
│   ├── config.py         # parâmetros do experimento
│   ├── data.py           # ✏️ carga e limpeza
│   ├── features.py       # ✏️ feature engineering
│   ├── model.py          # ✏️ definição do modelo
│   ├── evaluate.py       # ✏️ métricas
│   └── pipelines/
│       ├── train.py      # 🔒 pipeline de treino (pronto)
│       └── predict.py    # 🔒 pipeline de inferência (pronto)
├── tests/
│   ├── conftest.py       # fixtures compartilhadas (ex.: raw_df)
│   ├── fixtures/
│   │   └── sample_raw.csv   # amostra pequena dos dados (versionada)
│   └── test_*.py         # testes
├── .github/              # CI e template de Pull Request
├── .env.example          # modelo de variáveis de ambiente
├── .pre-commit-config.yaml
├── .python-version       # versão do Python (3.12)
├── Makefile              # atalhos (make help)
├── pyproject.toml        # dependências e configuração de ruff/pytest
└── uv.lock               # versões exatas de todas as dependências
```

### O que vai e o que não vai para o git

| Vai para o git | Não vai (ignorado) |
|---|---|
| código em `src/` e `tests/` | conteúdo de `data/` (só os `.gitkeep` são versionados) |
| `tests/fixtures/sample_raw.csv` | conteúdo de `models/` |
| notebooks **sem outputs** | `reports/metrics.json` e `data/predictions/` |
| `pyproject.toml` **e** `uv.lock` | `.venv/`, `.env`, caches |

Dados reais e modelos **nunca** são commitados. O pre-commit bloqueia arquivos acima de 1 MB e a verificação de conformidade bloqueia qualquer arquivo em `data/` e `models/`.

---

## 4. Ambiente e dependências com uv

O uv substitui `pip`, `venv`, `pyenv` e `pip-tools`. **Nunca use `pip install`** neste projeto: o pacote não fica registrado no `pyproject.toml` e o projeto quebra na máquina de outra pessoa e no CI.

### Comandos do dia a dia

```bash
uv sync                          # instala/atualiza o ambiente conforme o uv.lock
uv add lightgbm                  # dependência da aplicação (usada em src/)
uv add --dev seaborn             # dependência só de desenvolvimento (notebooks, testes, ferramentas)
uv remove lightgbm               # remove
uv lock --upgrade-package pandas # atualiza um pacote específico
uv lock --upgrade                # atualiza tudo
uv run <comando>                 # roda qualquer comando dentro do ambiente, sem precisar ativá-lo
```

### Aplicação ou desenvolvimento?

| Onde o pacote é usado | Comando | Grupo no `pyproject.toml` |
|---|---|---|
| em `src/` (roda em produção) | `uv add <pacote>` | `dependencies` |
| só em notebooks, testes ou ferramentas | `uv add --dev <pacote>` | `[dependency-groups] dev` |

A verificação de conformidade (deptry) acusa erro se um pacote importado em `src/` não estiver em `dependencies`. Detalhes na [seção 10](#10-verificações-de-conformidade).

### Regras

- Sempre commite `pyproject.toml` **e** `uv.lock` juntos. O pre-commit verifica se estão sincronizados.
- Para trocar a versão do Python, edite o `.python-version` e rode `uv sync`.
- Ativar a venv é opcional: `uv run` já usa o ambiente certo. Se preferir ativar, use `source .venv/bin/activate`.

---

## 5. Configuração: `.env`, `paths.py` e `config.py`

### `paths.py`: onde ficam as coisas

Todos os caminhos do projeto saem daqui. **Nunca escreva caminhos absolutos no código** (como `/Users/fulano/...`); use:

```python
from ds_project import paths

paths.RAW_FILE  # data/raw/dataset.csv (arquivo de entrada padrão do treino)
paths.RAW_DIR  # data/raw/
paths.INTERIM_DIR  # data/interim/
paths.PROCESSED_DIR  # data/processed/
paths.PREDICTIONS_FILE  # data/predictions/predictions.csv
paths.MODEL_FILE  # models/model.joblib
paths.METRICS_FILE  # reports/metrics.json
paths.REPORTS_DIR  # reports/
```

Os caminhos são calculados a partir da raiz do projeto, então funcionam de qualquer pasta, inclusive de dentro de `notebooks/`.

### `.env`: sobrescrever caminhos e configurar integrações

O `.env` é local e **não vai para o git**. O `make setup` cria o arquivo a partir do `.env.example`. Os comandos do Makefile carregam o `.env` automaticamente.

| Variável | Padrão | Uso |
|---|---|---|
| `RAW_FILE` | `data/raw/dataset.csv` | arquivo de entrada do treino |
| `DATA_DIR` | `data` | raiz dos dados |
| `MODELS_DIR` | `models` | onde salvar o modelo |
| `REPORTS_DIR` | `reports` | onde salvar métricas |
| `SEED` | `42` | semente de aleatoriedade |

Credenciais (`DATABASE_URL`, `AWS_PROFILE`, `MLFLOW_TRACKING_URI`...) também vão no `.env`, **nunca no código**.

### `config.py`: parâmetros do experimento

```python
from ds_project.config import CONFIG

CONFIG.target  # nome da coluna alvo ("target")
CONFIG.seed  # semente (vem do SEED do .env)
CONFIG.test_size  # fração de teste no split (0.2)
```

Ajuste os valores padrão no próprio `config.py` conforme o seu problema.

---

## 6. Pipelines de treino e inferência

O template separa **o que você implementa** (✏️) do **que já está pronto** (🔒).

### O que você implementa

| Arquivo | Função | Regra |
|---|---|---|
| `data.py` | `load_raw(path) -> DataFrame` | lê os dados brutos (CSV, parquet, SQL, API...) |
| `data.py` | `clean(df) -> DataFrame` | limpeza; **não pode depender da coluna target**, porque também roda na inferência |
| `features.py` | `build_features(df) -> DataFrame` | só transformações **linha a linha** (sem `fit`): razões, flags, datas... |
| `model.py` | `build_model(seed) -> sklearn.Pipeline` | pré-processamento que **aprende com os dados** (imputer, scaler, encoder) + algoritmo, tudo dentro de um `Pipeline` |
| `evaluate.py` | `compute_metrics(y_true, y_pred, y_score) -> dict` | métricas do problema |

### O que já está pronto

**Treino**: `make train` (ou `uv run python -m ds_project.pipelines.train`):

```
load_raw → clean → remove linhas sem target → build_features
        → train_test_split (seed fixa, estratificado)
        → build_model().fit() → compute_metrics() no conjunto de teste
        → salva models/model.joblib e reports/metrics.json
```

**Inferência**: `make predict INPUT=caminho/novos.csv`:

```
carrega models/model.joblib → load_raw → clean → build_features   (as MESMAS funções do treino)
        → predict + predict_proba → salva data/predictions/predictions.csv
```

### Por que essa divisão

- **Treino e inferência usam as mesmas funções** de limpeza e features. Isso evita *training-serving skew*: o modelo nunca recebe em produção dados processados de outro jeito.
- **Tudo que aprende com os dados fica dentro do `Pipeline` do sklearn.** O `fit` acontece só no treino, depois do split, o que evita *data leakage*. Exemplo: um `StandardScaler` aplicado antes do split "vê" a média do conjunto de teste.
- **O modelo salvo inclui o pré-processamento.** O `model.joblib` recebe o DataFrame de features e faz o resto sozinho.

### A amostra `tests/fixtures/sample_raw.csv`

É uma amostra **pequena** (algumas centenas de linhas), **anonimizada** e **no mesmo formato dos dados reais**. Ela é usada:

- pelos testes (`raw_df` no `conftest.py`);
- pelo `make demo`;
- pela verificação de conformidade, que treina e prediz em cima dela a cada PR.

**Ao trocar o exemplo pelo seu problema, substitua essa amostra.** Sem ela, o CI não consegue validar o pipeline.

### Do exemplo para o seu problema

1. Coloque os dados em `data/raw/dataset.csv` (ou aponte `RAW_FILE` no `.env`).
2. Ajuste `CONFIG.target` em `config.py`.
3. Reescreva `data.py`, `features.py`, `model.py` e `evaluate.py`.
4. Gere uma amostra anonimizada e salve em `tests/fixtures/sample_raw.csv`.
5. Atualize os testes.
6. `make train`, depois `make ci`.

---

## 7. Notebooks

Notebooks servem para **explorar**: EDA, testar hipóteses, prototipar features e analisar resultados. Código que vai para produção mora em `src/`.

### Como abrir

- **VS Code**: abra o `.ipynb` e selecione o kernel **`.venv` (Python 3.12)** no canto superior direito. O `ipykernel` já vem nas dependências de desenvolvimento.
- **Jupyter Lab no navegador**: `make notebook`.

### Usando o código do projeto

O pacote está instalado no ambiente, então qualquer notebook importa direto, sem mexer em `sys.path`:

```python
%load_ext autoreload
%autoreload 2          # ao editar src/, o notebook recarrega o código sozinho

from ds_project import paths
from ds_project.data import load_raw, clean
from ds_project.features import build_features

df = build_features(clean(load_raw(paths.RAW_FILE)))
```

### Boas práticas

- **Nome sugerido**: `NN-iniciais-descricao.ipynb` (ex.: `01-bcv-eda-clientes.ipynb`). Isso ordena e identifica o autor, mas não é obrigatório.
- **Lógica reutilizável vai para `src/`** com teste em `tests/`. Se você copiou uma célula para um segundo notebook, ela deveria ser uma função.
- **Figuras** vão em `reports/figures/`.
- **Outputs não são commitados.** O pre-commit (nbstripout) remove os outputs no commit automaticamente. Diffs ficam legíveis e nenhum dado vaza pelo notebook.
- Pacotes usados só em notebooks (`seaborn`, `plotly`...) entram com `uv add --dev`.

---

## 8. Testes

Os testes usam **pytest** e ficam em `tests/`.

```bash
make test                                   # todos os testes
uv run pytest tests/test_features.py        # um arquivo
uv run pytest -k is_senior                  # testes cujo nome contém "is_senior"
uv run pytest -x                            # para no primeiro erro
uv run pytest --cov=src                     # com relatório de cobertura
```

### Fixtures disponíveis

```python
def test_algo(raw_df):  # raw_df = DataFrame lido de tests/fixtures/sample_raw.csv
    ...
```

Crie novas fixtures em `tests/conftest.py`.

### O que testar em um projeto de DS

| O quê | Exemplo |
|---|---|
| funções de limpeza | remove duplicados, padroniza colunas, funciona **sem** a coluna target |
| features | valor calculado correto em casos conhecidos, bordas (divisão por zero, nulos) |
| imutabilidade | `build_features` não altera o DataFrame de entrada |
| modelo | treina e prediz em `raw_df`, lida com categoria nunca vista |
| métricas | resultado conhecido em um caso perfeito |

Exemplo:

```python
def test_is_senior():
    df = pd.DataFrame({"age": [59, 60], "income": [1.0, 1.0], "tenure_months": [1, 1]})
    assert build_features(df)["is_senior"].tolist() == [0, 1]
```

A cobertura aparece no CI, mas é **informativa**: não há percentual mínimo.

---

## 9. pre-commit

O pre-commit roda verificações **automaticamente a cada `git commit`**, só nos arquivos do commit. Ele é ativado pelo `make setup`.

| Hook | O que faz | Corrige sozinho? |
|---|---|---|
| `ruff-check` | lint: erros, imports não usados, más práticas | sim, quando possível |
| `ruff-format` | formatação do código | sim |
| `check-added-large-files` | bloqueia arquivos acima de 1 MB | não |
| `detect-private-key` | bloqueia chaves privadas | não |
| `check-yaml` / `check-toml` | sintaxe de YAML e TOML | não |
| `end-of-file-fixer` / `trailing-whitespace` | quebra de linha final e espaços sobrando | sim |
| `nbstripout` | remove outputs dos notebooks | sim |
| `uv-lock` | garante que o `uv.lock` acompanha o `pyproject.toml` | sim |

### Como funciona na prática

- **Na primeira vez** demora um pouco: o pre-commit baixa o ambiente de cada hook. Depois fica em cache.
- **Se um hook corrigir arquivos**, o commit é **abortado** com os arquivos já corrigidos. Revise e repita:
  ```bash
  git add -A && git commit -m "..."
  ```
- **Se um hook falhar sem conseguir corrigir**, corrija à mão e commite de novo.
- Para rodar em todos os arquivos, sem commitar: `make lint`.

`git commit --no-verify` pula o hook, mas **não adianta**: o CI roda o mesmo pre-commit em todos os arquivos e bloqueia o PR.

### Convenções do ruff

Configuradas no `pyproject.toml`: linhas de até 100 caracteres, Python 3.12, imports ordenados. Os nomes `X`, `X_train` e `X_test` são permitidos (convenção do sklearn).

---

## 10. Verificações de conformidade

`make check` roda duas ferramentas que garantem o padrão do projeto. As mesmas rodam no CI, no job `ci / conformance`.

### deptry: dependências declaradas

Compara os `import` de `src/` com o `pyproject.toml`:

| Problema | Exemplo | Por que importa |
|---|---|---|
| importado mas não declarado | `import lightgbm` sem `uv add lightgbm` | funciona na sua máquina e quebra em qualquer outra |
| declarado mas não usado | `xgboost` no `pyproject.toml` sem nenhum import | ambiente maior e mais conflitos de versão |
| dependência de dev usada em `src/` | `import matplotlib` em `src/` com o pacote só em `--dev` | quebra quando o pacote é instalado sem as dependências de dev |

Só `src/` é verificado. Notebooks e testes podem usar dependências de dev à vontade.

### ds-check: padrões do projeto

| Verificação | Falha quando |
|---|---|
| estrutura de pastas | falta alguma pasta padrão (`data/*`, `models/`, `notebooks/`, `reports/figures/`, `tests/`), o `pyproject.toml`, o `uv.lock` ou o `.pre-commit-config.yaml`, ou `src/` não tem exatamente um pacote |
| sem dados ou modelos no git | há arquivo versionado em `data/` ou `models/` além de `.gitkeep` |
| notebooks sem outputs | algum notebook foi commitado com outputs |
| contrato do pipeline | `train` ou `predict` falham sobre `tests/fixtures/sample_raw.csv`, não geram `model.joblib`, `metrics.json` e `predictions.csv`, ou **duas execuções com a mesma seed dão métricas diferentes** |

O ds-check é mantido centralmente em [`ds-workflows`](https://github.com/brunocvs7/ds-workflows). As regras são as mesmas para todos os projetos e não podem ser alteradas por projeto.

---

## 11. Fluxo de desenvolvimento

### Regras da `main`

- Não aceita push direto. Todo código entra por **Pull Request**.
- O PR só pode ser mergeado com **as 4 verificações do CI verdes**.
- A branch do PR precisa **seguir o padrão de nome** abaixo.
- O merge é sempre **squash**: o PR inteiro vira um único commit na `main`.
- A branch é **apagada automaticamente** no GitHub após o merge.

### Padrão de nome de branch

Formato: **`<tipo>/<descricao>`**, tudo minúsculo, com a descrição em kebab-case (palavras separadas por hífen, sem acentos nem espaços).

| Tipo | Quando usar | Exemplo |
|---|---|---|
| `feature/` | funcionalidade nova | `feature/modelo-churn` |
| `fix/` | correção de bug | `fix/nulos-em-income` |
| `hotfix/` | correção urgente em produção | `hotfix/predict-quebrado` |
| `refactor/` | reestruturar código sem mudar o comportamento | `refactor/separa-features-temporais` |
| `experiment/` | testar um modelo, feature ou hipótese | `experiment/lightgbm-vs-rf` |
| `docs/` | documentação | `docs/readme-pipeline` |
| `chore/` | dependências, configuração, manutenção | `chore/atualiza-pandas` |
| `test/` | só testes | `test/cobertura-features` |
| `ci/` | CI e automação | `ci/cache-uv` |

Branches como `minha-branch`, `Feature/X` ou `feature/Modelo Novo` são **rejeitadas** pela verificação `ci / branch-name`.

### Passo a passo

```bash
# 1. Comece sempre da main atualizada
git switch main
git pull

# 2. Crie a branch
git switch -c feature/is-senior

# 3. Desenvolva: edite o código e rode os testes com frequência
make test

# 4. Commite (o pre-commit roda sozinho)
git add -A
git commit -m "feat: adiciona feature is_senior"

# 5. Antes de enviar, rode localmente tudo que o CI vai rodar
make ci

# 6. Envie e abra o PR
git push -u origin feature/is-senior
gh pr create --fill

# 7. Acompanhe o CI
gh pr checks --watch

# 8. Com tudo verde, faça o merge (pelo botão no GitHub ou pelo terminal)
gh pr merge --squash

# 9. Volte para a main e limpe a branch local
git switch main
git pull
git branch -D feature/is-senior
```

O `-D` maiúsculo no passo 9 é necessário porque, com squash, o git não reconhece a branch como mergeada.

### Mensagens de commit

Use o mesmo vocabulário dos tipos de branch ([Conventional Commits](https://www.conventionalcommits.org/)):

```
feat: adiciona feature is_senior
fix: trata nulos em income
refactor: separa features temporais
docs: explica pipeline no README
chore: atualiza pandas para 2.3
test: cobre casos de borda em clean
```

Com squash, **o título do PR vira a mensagem do commit na `main`**. Capriche no título.

### Durante o PR

- **Mais commits** na mesma branch atualizam o PR e rodam o CI de novo.
- **A `main` avançou?** O PR precisa estar atualizado com ela antes do merge:
  ```bash
  gh pr update-branch          # ou: git pull origin main && git push
  ```
- **Errou o nome da branch?** Não dá para renomear um PR aberto. Crie a branch certa e abra outro PR:
  ```bash
  git branch -m feature/nome-certo
  git push -u origin feature/nome-certo
  gh pr create --fill
  # depois feche o PR antigo
  ```
- Use **`experiment/`** para hipóteses que talvez não sejam mergeadas. Se o experimento não der certo, feche o PR com `gh pr close --delete-branch`. O histórico da discussão fica no GitHub.

---

## 12. CI no GitHub

Em todo PR (e em todo push na `main`), o GitHub Actions roda 4 jobs:

| Check | O que roda | Equivalente local |
|---|---|---|
| `ci / lint` | `pre-commit run --all-files` | `make lint` |
| `ci / test` | `uv sync --locked` + `pytest --cov` | `make test` |
| `ci / conformance` | deptry + ds-check | `make check` |
| `ci / branch-name` | valida o padrão `<tipo>/<descricao>` (só em PRs) | — |

`make ci` roda os três primeiros. **Se passar localmente, passa no PR.**

A lógica do CI fica centralizada no repositório [`ds-workflows`](https://github.com/brunocvs7/ds-workflows); o `.github/workflows/ci.yml` deste projeto só aponta para ele. Melhorias no CI chegam a todos os projetos sem mudanças aqui.

### Quando o CI falha

```bash
gh pr checks                     # quais checks falharam
gh run view --log-failed         # log só das etapas que falharam
```

Corrija, commite e dê push: o CI roda de novo sozinho. Para disparar o CI manualmente na `main`: `gh workflow run CI`.

---

## 13. Referência de comandos `make`

`make` sem argumentos lista todos.

| Comando | O que faz |
|---|---|
| `make setup` | cria a `.venv`, instala os hooks do pre-commit e cria o `.env` |
| `make lint` | roda todos os hooks do pre-commit em todos os arquivos |
| `make format` | formata e corrige o código automaticamente (ruff) |
| `make test` | roda os testes |
| `make check` | verificações de conformidade (deptry + ds-check) |
| `make ci` | `lint` + `test` + `check`: tudo que o CI roda |
| `make demo` | treina e prediz com a amostra de `tests/fixtures` |
| `make train` | treina com `data/raw/dataset.csv` (ou `RAW_FILE` do `.env`) |
| `make predict INPUT=arquivo.csv` | gera predições para um arquivo |
| `make notebook` | abre o Jupyter Lab no ambiente do projeto |
| `make clean` | apaga caches, modelo, métricas e predições (não toca em `data/raw`) |

---

## 14. Claude Code: skills e agentes

Com a CLI `dskit`, o projeto ganha skills e agentes que ensinam o Claude Code a seguir este fluxo:

```bash
dskit list              # o que está disponível e o que já está instalado
dskit add --all         # instala tudo em .claude/
dskit add run-checks    # instala só um item
dskit remove ds-eda     # remove um item
```

Com o Claude Code aberto no projeto, peça em linguagem natural, por exemplo:

| Pedido | Skill acionada |
|---|---|
| "começa uma branch para a feature de região" | `new-branch`: cria `feature/...` a partir da `main` atualizada |
| "adiciona o lightgbm no projeto" | `add-dependency`: `uv add` no grupo certo |
| "isso vai passar no CI?" | `run-checks`: roda `make ci` e resume o resultado |
| "revisa meu PR" | `pr-review`: checks + revisão do diff pelo agente `code-reviewer` |

Commite a pasta `.claude/` para que todo o time use as mesmas skills.

---

## 15. Desfazendo coisas

| Situação | Comando |
|---|---|
| descartar alterações não commitadas de um arquivo | `git restore caminho/arquivo.py` |
| desfazer o último commit **local** (ainda sem push), mantendo as alterações | `git reset --soft HEAD~1` |
| desfazer algo **que já está na `main`** | `git revert <sha>`, numa branch `fix/...`, via PR |

**Regra:** `reset` reescreve o histórico e só deve ser usado em commits seus que ainda não foram enviados. Para o que já está na `main` ou em uma branch compartilhada, use sempre `revert`. Ele cria um commit novo que desfaz o anterior. Como cada PR vira um único commit (squash), desfazer um PR inteiro é um único `git revert`.

```bash
git switch main && git pull
git switch -c fix/reverte-is-senior
git revert <sha-do-commit>
git push -u origin fix/reverte-is-senior
gh pr create --fill
```

---

## 16. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| o commit foi abortado e os arquivos mudaram | um hook do pre-commit corrigiu algo | `git add -A && git commit` de novo |
| o pre-commit não roda no commit | o hook não foi instalado neste clone | `make setup` |
| `ci / lint` falha, mas o commit local passou | commit feito com `--no-verify` ou sem o hook instalado | `make lint`, commite as correções |
| `uv.lock` fora de sincronia / `uv sync --locked` falha no CI | o `pyproject.toml` foi editado sem atualizar o lock | `uv lock` e commite o `uv.lock` |
| deptry: `DEP001 'x' imported but missing` | import em `src/` sem declarar | `uv add x` (ou remova o import) |
| deptry: `DEP002 'x' defined but not used` | dependência sobrando | `uv remove x` (ou mova para `--dev`) |
| ds-check: "treino não é reprodutível" | algo aleatório sem seed | passe `random_state=seed`/`CONFIG.seed` a tudo que é aleatório |
| ds-check: "arquivo de dados versionado no git" | arquivo em `data/` ou `models/` commitado | `git rm --cached <arquivo>` e commite |
| `ci / branch-name` falha | branch fora do padrão | crie a branch com o nome certo e abra outro PR (seção 11) |
| o merge está bloqueado com tudo verde | a `main` avançou depois que o PR foi aberto | `gh pr update-branch` |
| `ModuleNotFoundError: ds_project` no notebook | kernel errado | selecione o kernel `.venv` (Python 3.12) |
| `make: *** No rule to make target` | comando rodado fora da raiz do projeto | `cd` para a pasta do projeto |
