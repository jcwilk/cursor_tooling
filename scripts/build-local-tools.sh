#!/usr/bin/env bash
# Build local tools shipped under .cursor/skills/ (Python editable installs; Rust crates if any).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/.cursor/skills"
BUILT=0
PYTHON="${PYTHON:-python3}"
VENV="$REPO_ROOT/.venv"

if [[ ! -x "$VENV/bin/pip" ]]; then
  echo "==> creating $VENV"
  "$PYTHON" -m venv "$VENV"
fi
PIP="$VENV/bin/pip"

for pyproject in "$SKILLS_DIR"/*/pyproject.toml; do
  [[ -f "$pyproject" ]] || continue
  dir="$(dirname "$pyproject")"
  echo "==> pip install -e $dir"
  "$PIP" install -e "$dir"
  BUILT=$((BUILT + 1))
done

for manifest in "$SKILLS_DIR"/*/Cargo.toml; do
  [[ -f "$manifest" ]] || continue
  dir="$(dirname "$manifest")"
  echo "==> cargo build --release in $dir"
  (cd "$dir" && cargo build --release)
  BUILT=$((BUILT + 1))
done

if [[ "$BUILT" -eq 0 ]]; then
  echo "No Python or Rust skill packages found under $SKILLS_DIR"
  exit 1
fi

echo "Done. Activate with: source $VENV/bin/activate"
