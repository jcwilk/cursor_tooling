#!/usr/bin/env bash
set -euo pipefail

root="${ROOT_WORKTREE_PATH:?ROOT_WORKTREE_PATH must be set}"

if [[ -f "$root/.env" ]]; then
  cp "$root/.env" .env
fi

if [[ -d "$root/.sleuths" ]]; then
  cp -r "$root/.sleuths" .
fi

if [[ -d "$root/.venv" ]]; then
  cp -r "$root/.venv" .
fi
