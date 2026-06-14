from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

from dotenv import load_dotenv

from sleuth.config import secrets_path

_tracing_enabled = False


def load_secrets(project_root: Path) -> None:
    """Load .sleuths/secrets.env when present; no error when absent."""
    path = secrets_path(project_root)
    if path.exists():
        load_dotenv(path, override=False)


def configure_langsmith(project_root: Path) -> bool:
    """Enable LangSmith tracing env vars when credentials are present."""
    global _tracing_enabled
    load_secrets(project_root)
    api_key = os.environ.get("LANGSMITH_API_KEY", "").strip()
    if not api_key or api_key.startswith("<"):
        _tracing_enabled = False
        return False

    os.environ.setdefault("LANGSMITH_TRACING", "true")
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )
    os.environ.setdefault("LANGSMITH_PROJECT", "sleuths")
    # Short-lived CLI: must block on trace export, not LangChain's server default (background=true).
    os.environ["LANGCHAIN_CALLBACKS_BACKGROUND"] = "false"
    _tracing_enabled = True
    return True


def tracing_enabled() -> bool:
    return _tracing_enabled


def flush_tracing() -> None:
    """Wait for LangSmith to receive run completion updates before process exit."""
    if not _tracing_enabled:
        return
    try:
        from langsmith import Client

        Client().flush()
    except Exception as exc:
        warn_tracing_failure(exc)


def warn_tracing_failure(exc: BaseException) -> None:
    """Emit explicit warning when tracing export fails; refresh may still succeed."""
    msg = f"sleuth: LangSmith tracing export failed (refresh may still succeed): {exc}"
    print(msg, file=sys.stderr)
    warnings.warn(msg, stacklevel=2)
