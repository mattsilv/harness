#!/usr/bin/env bash
# Project checks run by the required `checks` CI job (docs/CI.md); also run locally.
# Docs-only repos get the link check; add the stack's lint and test commands from
# PROJECT_CONFIG.md Stack below. Seeded by the harness only when absent; the project owns it after.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "== Relative Markdown links resolve"
git ls-files -z '*.md' | python3 -c '
import re, sys
from pathlib import Path
bad = []
for name in filter(None, sys.stdin.read().split("\0")):
    text = re.sub(r"```.*?```|`[^`\n]*`", "", Path(name).read_text(errors="ignore"), flags=re.S)
    for target in re.findall(r"\]\(([^)\s]+)", text):
        path = target.split("#")[0]
        if path and not re.match(r"[a-z][a-z0-9+.-]*:|/", path) and not (Path(name).parent / path).exists():
            bad.append(f"{name}: {target}")
print("\n".join(bad) or "ok")
sys.exit(bool(bad))
'

echo "== Stack checks"
if [ -f package.json ]; then
  command -v pnpm >/dev/null || { echo "::error::package.json found: add a pinned pnpm and Node setup step to .github/workflows/checks.yml"; exit 1; }
  pnpm install --frozen-lockfile
  for script in lint typecheck test; do pnpm run --if-present "$script"; done
fi
if [ -f pyproject.toml ]; then
  command -v uv >/dev/null || { echo "::error::pyproject.toml found: add a pinned uv setup step to .github/workflows/checks.yml"; exit 1; }
  uv sync --frozen
  if [ -d tests ]; then uv run --with pytest pytest -q; fi
fi
echo "ok"
