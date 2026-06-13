from __future__ import annotations

from pathlib import Path


def slug_from_path(path: Path) -> str:
    """Derive Cursor's ~/.cursor/projects/<slug>/ identifier from a workspace path."""
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path

    s = str(resolved)
    worktree_prefix = str(Path.home() / ".cursor" / "worktrees") + "/"
    if s.startswith(worktree_prefix):
        rest = s[len(worktree_prefix) :]
        parts = rest.split("/")
        if len(parts) >= 2:
            repo = parts[0].replace("_", "-")
            wid = parts[1]
            return f"home-user-cursor-worktrees-{repo}-{wid}"

    home_prefix = str(Path.home()) + "/"
    if s.startswith(home_prefix):
        rest = s[len(home_prefix) :]
    else:
        rest = s.lstrip("/")

    normalized = rest.replace("_", "-").replace("/", "-")
    return f"home-user-{normalized}"
