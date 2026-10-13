"""ds-check: verificações de conformidade do projeto.

Verifica estrutura, dados no git, notebooks, dependências declaradas e o pipeline.

Uso:  uv run python .github/scripts/ds_check.py [caminho] [--skip "<nome da verificação>"]

Roda no CI (job `conformance`) e em `make check`. Cada problema vem com a forma de corrigir.
No GitHub Actions, os problemas também viram anotações e um quadro-resumo na página da execução.

Faz parte do padrão do template: não altere sem combinar com o time.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

REQUIRED_DIRS = [
    "data/raw",
    "data/interim",
    "data/processed",
    "data/external",
    "models",
    "notebooks",
    "reports/figures",
    "tests",
]
SAMPLE_FIXTURE = "tests/fixtures/sample_raw.csv"


@dataclass(frozen=True)
class Issue:
    """Um problema encontrado: o que é, como corrigir e (se houver) onde está."""

    message: str
    fix: str
    file: str | None = None
    line: int | None = None


def find_package(root: Path) -> Path | None:
    """Retorna o único pacote em src/ (o nome é livre, para permitir renomear)."""
    src = root / "src"
    if not src.is_dir():
        return None
    packages = [p for p in src.iterdir() if (p / "__init__.py").is_file()]
    return packages[0] if len(packages) == 1 else None


def _git_files(root: Path, *paths: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", *paths], cwd=root, capture_output=True, text=True, check=True
    )
    return [line for line in out.stdout.splitlines() if line]


def check_structure(root: Path) -> list[Issue]:
    issues = [
        Issue(
            f"pasta obrigatória ausente: {d}/",
            f"crie a pasta com um `.gitkeep`: `mkdir -p {d} && touch {d}/.gitkeep`",
        )
        for d in REQUIRED_DIRS
        if not (root / d).is_dir()
    ]
    if find_package(root) is None:
        issues.append(
            Issue(
                "src/ deve conter exatamente um pacote Python (pasta com __init__.py)",
                "mantenha um único pacote em `src/`; código novo vira módulo dentro dele",
            )
        )
    for f in ("pyproject.toml", "uv.lock", ".pre-commit-config.yaml"):
        if not (root / f).is_file():
            issues.append(
                Issue(f"arquivo obrigatório ausente: {f}", "restaure o arquivo do template")
            )
    return issues


def check_no_committed_data(root: Path) -> list[Issue]:
    return [
        Issue(
            f"arquivo de dados/modelo versionado no git: {f}",
            f"`git rm --cached {f}` e commite (o arquivo continua na sua máquina)",
            file=f,
        )
        for f in _git_files(root, "data", "models")
        if Path(f).name != ".gitkeep"
    ]


def check_notebooks(root: Path) -> list[Issue]:
    issues = []
    for nb in sorted((root / "notebooks").glob("**/*.ipynb")):
        if ".ipynb_checkpoints" in nb.parts:
            continue
        cells = json.loads(nb.read_text()).get("cells", [])
        if any(c.get("outputs") or c.get("execution_count") for c in cells):
            rel = str(nb.relative_to(root))
            issues.append(
                Issue(
                    f"{rel}: notebook commitado com outputs",
                    f"`uv run pre-commit run nbstripout --files {rel}` e commite "
                    "(rode `make setup` para o hook limpar sozinho nos próximos commits)",
                    file=rel,
                )
            )
    return issues


DEPTRY_FIXES = {
    "DEP001": "`uv add {module}` (use o nome do pacote no PyPI) ou remova o import",
    "DEP002": "`uv remove {module}`, ou `uv remove {module} && uv add --dev {module}` "
    "se for usado só em notebooks/testes",
    "DEP003": "`uv add {module}`: ele só está instalado por ser dependência de outro pacote",
    "DEP004": "`uv remove --dev {module} && uv add {module}`: é usado em `src/`, "
    "então precisa ser dependência da aplicação",
}


def check_dependencies(root: Path) -> list[Issue]:
    """deptry: imports de src/ x dependências declaradas no pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "deptry.json"
        result = subprocess.run(
            ["uv", "run", "--with", "deptry", "deptry", "src", "--json-output", str(report)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if not report.is_file():
            error = result.stderr.strip()[-1500:]
            return [Issue(f"deptry não rodou:\n{error}", "rode `make check`")]
        found = json.loads(report.read_text())

    issues = []
    for item in found:
        code, module, loc = item["error"]["code"], item["module"], item["location"]
        fix = DEPTRY_FIXES.get(code, "veja https://deptry.com/rules-violations/")
        issues.append(
            Issue(
                f"{code} {item['error']['message']}",
                fix.format(module=module),
                file=os.path.relpath(loc["file"], root) if loc["file"] else None,
                line=loc["line"],
            )
        )
    return issues


def _run_pipeline(root: Path, module: str, env: dict[str, str], *args: str) -> Issue | None:
    result = subprocess.run(
        ["uv", "run", "--no-sync", "python", "-m", module, *args],
        cwd=root,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        cause = stderr.splitlines()[-1] if stderr else f"código de saída {result.returncode}"
        return Issue(
            f"`python -m {module}` falhou: {cause}\n{stderr[-2000:]}",
            "rode `make demo` localmente para reproduzir o erro",
        )
    return None


def check_pipeline_contract(root: Path) -> list[Issue]:
    """Treina 2x e faz inferência sobre a amostra em tests/fixtures; valida artefatos e seed."""
    pkg = find_package(root)
    fixture = root / SAMPLE_FIXTURE
    if pkg is None:
        return []
    if not fixture.is_file():
        return [
            Issue(
                f"amostra ausente: {SAMPLE_FIXTURE}",
                "salve ali uma amostra pequena e anonimizada (centenas de linhas) dos dados reais",
            )
        ]

    metrics = []
    for _ in range(2):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            env = {
                "RAW_FILE": str(fixture),
                "DATA_DIR": str(out / "data"),
                "MODELS_DIR": str(out / "models"),
                "REPORTS_DIR": str(out / "reports"),
            }
            if issue := _run_pipeline(root, f"{pkg.name}.pipelines.train", env):
                return [issue]
            model, metrics_file = out / "models/model.joblib", out / "reports/metrics.json"
            missing = [str(p.relative_to(out)) for p in (model, metrics_file) if not p.is_file()]
            if missing:
                return [
                    Issue(
                        f"treino não gerou: {', '.join(missing)}",
                        "o treino precisa salvar em `paths.MODEL_FILE` e `paths.METRICS_FILE`",
                    )
                ]
            metrics.append(json.loads(metrics_file.read_text()))

            if issue := _run_pipeline(root, f"{pkg.name}.pipelines.predict", env, str(fixture)):
                return [issue]
            if not (out / "data/predictions/predictions.csv").is_file():
                return [
                    Issue(
                        "inferência não gerou data/predictions/predictions.csv",
                        "a inferência precisa salvar em `paths.PREDICTIONS_FILE`",
                    )
                ]

    if metrics[0] != metrics[1]:
        return [
            Issue(
                f"treino não é reprodutível com a mesma seed: {metrics[0]} != {metrics[1]}",
                "passe `random_state=CONFIG.seed` a tudo que é aleatório "
                "(split, modelo, amostragens)",
            )
        ]
    return []


CHECKS: dict[str, Callable[[Path], list[Issue]]] = {
    "estrutura de pastas": check_structure,
    "sem dados/modelos no git": check_no_committed_data,
    "notebooks sem outputs": check_notebooks,
    "dependências declaradas (deptry)": check_dependencies,
    "contrato do pipeline (treino + inferência + seed)": check_pipeline_contract,
}


def _escape(value: str, prop: bool = False) -> str:
    """Escapa texto para comandos de workflow do GitHub (::error ...::mensagem)."""
    value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return value.replace(":", "%3A").replace(",", "%2C") if prop else value


def _annotate(check: str, issue: Issue) -> None:
    props = [f"title={_escape(f'ds-check: {check}', prop=True)}"]
    if issue.file:
        props.append(f"file={_escape(issue.file, prop=True)}")
    if issue.line:
        props.append(f"line={issue.line}")
    print(f"::error {','.join(props)}::{_escape(f'{issue.message} → Como corrigir: {issue.fix}')}")


def _summary(results: dict[str, list[Issue] | None]) -> str:
    failed = {name: issues for name, issues in results.items() if issues}
    icon = "❌" if failed else "✅"
    lines = [f"## {icon} Verificações de conformidade", ""]
    lines += ["| Verificação | Resultado |", "|---|---|"]
    for name, issues in results.items():
        status = "⏭️ pulada" if issues is None else ("❌ falhou" if issues else "✅ ok")
        lines.append(f"| {name} | {status} |")
    for name, issues in failed.items():
        lines += ["", f"### {name}", "", "| Problema | Como corrigir |", "|---|---|"]
        for issue in issues:
            first_line = issue.message.splitlines()[0].replace("|", "\\|")
            lines.append(f"| {first_line} | {issue.fix.replace('|', '\\|')} |")
    if failed:
        lines += ["", "Reproduza localmente com `make check`."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="ds-check", description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="raiz do projeto")
    parser.add_argument("--skip", action="append", default=[], choices=list(CHECKS))
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    in_ci = os.getenv("GITHUB_ACTIONS") == "true"

    results: dict[str, list[Issue] | None] = {}
    for name, check in CHECKS.items():
        if name in args.skip:
            print(f"- {name} (pulado)")
            results[name] = None
            continue
        issues = results[name] = check(root)
        print(f"{'✗' if issues else '✓'} {name}")
        for issue in issues:
            print(f"    {issue.message}".replace("\n", "\n    "))
            print(f"    → como corrigir: {issue.fix}")
            if in_ci:
                _annotate(name, issue)

    if summary_file := os.getenv("GITHUB_STEP_SUMMARY"):
        with open(summary_file, "a") as fh:
            fh.write(_summary(results))

    failed = sum(bool(issues) for issues in results.values())
    if failed:
        print(f"\n{failed} verificação(ões) falharam.")
        sys.exit(1)
    print("\nTudo conforme.")


if __name__ == "__main__":
    main()
