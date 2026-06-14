#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
worktree_root="$(cd "$script_dir/.." && pwd)"

if [[ -n "${ROOT_WORKTREE_PATH:-}" ]]; then
  primary_root="$(cd "$ROOT_WORKTREE_PATH" && pwd)"
elif git -C "$worktree_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  common_git_dir="$(git -C "$worktree_root" rev-parse --path-format=absolute --git-common-dir)"
  primary_root="$(cd "$(dirname "$common_git_dir")" && pwd)"
else
  echo "error: cannot determine primary checkout (set ROOT_WORKTREE_PATH or run from a git worktree)" >&2
  exit 1
fi

if [[ "$worktree_root" == "$primary_root" ]]; then
  exit 0
fi

copy_paths=(
  ".env"
  ".sleuths"
  ".venv"
)

copy_one() {
  local rel="$1"
  local src="$primary_root/$rel"
  local dst="$worktree_root/$rel"

  if [[ ! -e "$src" ]]; then
    echo "skip copy: $rel (missing)"
    return 0
  fi

  mkdir -p "$(dirname "$dst")"
  rm -rf "$dst"

  if [[ -d "$src" ]]; then
    mkdir -p "$dst"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a "$src"/ "$dst"/
    else
      cp -a "$src"/. "$dst"/
    fi
  else
    cp -a "$src" "$dst"
  fi

  echo "copied: $rel"
}

for rel in "${copy_paths[@]}"; do
  copy_one "$rel"
done
