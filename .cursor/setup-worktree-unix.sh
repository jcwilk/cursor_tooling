#!/usr/bin/env bash
set -euo pipefail

worktree_root="$(git rev-parse --show-toplevel)"
common_git_dir="$(git rev-parse --path-format=absolute --git-common-dir)"
primary_root="$(dirname "$common_git_dir")"

if [[ -n "${ROOT_WORKTREE_PATH:-}" ]]; then
  primary_root="$ROOT_WORKTREE_PATH"
fi

if [[ "$worktree_root" == "$primary_root" ]]; then
  exit 0
fi

copy_one() {
  local rel="$1"
  local src="$primary_root/$rel"
  local dst="$worktree_root/$rel"

  if [[ ! -e "$src" ]]; then
    return 0
  fi

  if [[ -d "$src" ]]; then
    rm -rf "$dst"
    cp -a "$src" "$dst"
  else
    cp -a "$src" "$dst"
  fi
}

copy_one ".env"
copy_one ".sleuths"
copy_one ".venv"
