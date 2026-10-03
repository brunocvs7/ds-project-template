#!/usr/bin/env bash
# Aplica o ruleset de proteção da branch padrão no repositório atual.
# Rulesets NÃO são copiados quando você cria um repo a partir de um template,
# então rode este script (ou `dskit protect`) em cada repo novo.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
RULESET=".github/rulesets/protect-main.json"

existing=$(gh api "repos/$REPO/rulesets" -q '.[] | select(.name=="protect-main") | .id' || true)
if [ -n "$existing" ]; then
  gh api -X PUT "repos/$REPO/rulesets/$existing" --input "$RULESET" >/dev/null
  echo "Ruleset atualizado em $REPO"
else
  gh api -X POST "repos/$REPO/rulesets" --input "$RULESET" >/dev/null
  echo "Ruleset criado em $REPO"
fi

# Configurações de merge: só squash, apaga a branch depois do merge
gh api -X PATCH "repos/$REPO" \
  -F allow_squash_merge=true -F allow_merge_commit=false -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true >/dev/null
echo "Configurações de merge aplicadas."
