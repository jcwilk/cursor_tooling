#!/usr/bin/env bash
# Build release binaries for all Rust crates shipped under .cursor/skills/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILT=0

for manifest in "$ROOT"/skills/*/Cargo.toml; do
  [[ -f "$manifest" ]] || continue
  dir="$(dirname "$manifest")"
  echo "==> cargo build --release in $dir"
  (cd "$dir" && cargo build --release)
  BUILT=$((BUILT + 1))
done

if [[ "$BUILT" -eq 0 ]]; then
  echo "No Rust crates found under $ROOT/skills/"
  exit 1
fi

echo "Done. Binaries are under each crate's target/release/ (gitignored)."
