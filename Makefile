.DEFAULT_GOAL := help
.PHONY: help setup lint format test check ci demo train predict notebook clean

ENV_FILE := $(if $(wildcard .env),--env-file .env,)
RUN      := uv run $(ENV_FILE)
PKG      := $(notdir $(wildcard src/*))
DS_CHECK ?= uvx --no-cache --from git+https://github.com/brunocvs7/ds-workflows@v1 ds-check
SAMPLE   := tests/fixtures/sample_raw.csv

help: ## Lista os comandos
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

setup: ## Cria a .venv e instala os hooks do pre-commit
	uv sync
	uv run pre-commit install
	@test -f .env || cp .env.example .env

lint: ## Roda todos os hooks do pre-commit (igual ao CI)
	uv run pre-commit run --all-files

format: ## Formata e corrige o que der automaticamente
	uv run ruff format .
	uv run ruff check . --fix

test: ## Testes unitários (pytest)
	$(RUN) pytest

check: ## Verificações de conformidade (igual ao CI)
	uv run --with deptry deptry src
	$(DS_CHECK)

ci: lint test check ## Tudo que o CI roda — "vai passar no PR?"

demo: ## Treina e prediz usando a amostra em tests/fixtures
	RAW_FILE=$(SAMPLE) $(RUN) python -m $(PKG).pipelines.train
	RAW_FILE=$(SAMPLE) $(RUN) python -m $(PKG).pipelines.predict $(SAMPLE)

train: ## Treina com data/raw/dataset.csv (ou RAW_FILE do .env)
	$(RUN) python -m $(PKG).pipelines.train

predict: ## Gera predições (make predict INPUT=caminho.csv)
	$(RUN) python -m $(PKG).pipelines.predict $(INPUT)

notebook: ## Abre o Jupyter Lab no ambiente do projeto
	$(RUN) --with jupyterlab jupyter lab

clean: ## Remove caches e artefatos gerados (não toca em data/raw)
	rm -rf .pytest_cache .ruff_cache .coverage htmlcov dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf data/predictions reports/metrics.json
	find models -type f ! -name .gitkeep -delete
