from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml


class InferenceApi(str, Enum):
    OLLAMA = "ollama"
    OPENAI_CHAT = "openai-chat"


_API_ALIASES = {
    "ollama": InferenceApi.OLLAMA,
    "llama-cpp": InferenceApi.OPENAI_CHAT,
    "llama.cpp": InferenceApi.OPENAI_CHAT,
    "openai": InferenceApi.OPENAI_CHAT,
    "chat-completions": InferenceApi.OPENAI_CHAT,
    "openai-chat": InferenceApi.OPENAI_CHAT,
}


@dataclass
class ProcessingConfig:
    context_budget_tokens: int = 16384
    response_headroom_tokens: int = 1000
    pass_summary_cap_tokens: int = 1000
    final_summary_target_tokens: int = 1000
    relevance_max_completion_tokens: int = 200
    summary_max_completion_tokens: int = 1000
    chunk_lines: int = 1
    max_chunks_per_batch: int = 20
    relevance_min_content_tokens: int = 2000
    relevance_max_content_tokens: int = 14000
    summarize_target_content_tokens: int = 8000
    merge_target_content_tokens: int = 8000
    merge_max_items_per_batch: int = 2
    max_parallel_inference_requests: int = 4


@dataclass
class OllamaConfig:
    base_url: str
    model: str
    api: InferenceApi = InferenceApi.OLLAMA


@dataclass
class TranscriptsConfig:
    extra_transcript_slugs: list[str] = field(default_factory=list)


@dataclass
class SleuthsConfig:
    ollama: OllamaConfig
    transcripts: TranscriptsConfig = field(default_factory=TranscriptsConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)


def sleuths_dir(project_root: Path) -> Path:
    return project_root / ".sleuths"


def config_path(project_root: Path) -> Path:
    return sleuths_dir(project_root) / "config.yaml"


def secrets_path(project_root: Path) -> Path:
    return sleuths_dir(project_root) / "secrets.env"


def ensure_sleuths_dirs(project_root: Path) -> None:
    (sleuths_dir(project_root) / "queries").mkdir(parents=True, exist_ok=True)


def _parse_inference_api(value: str | None) -> InferenceApi:
    if value is None:
        return InferenceApi.OLLAMA
    key = value.strip().lower()
    if key in _API_ALIASES:
        return _API_ALIASES[key]
    return InferenceApi.OLLAMA


def load_config(project_root: Path) -> SleuthsConfig:
    ensure_sleuths_dirs(project_root)
    path = config_path(project_root)
    if not path.exists():
        raise FileNotFoundError(
            f"missing {path} — create it with ollama.base_url and ollama.model "
            "pointing at your inference endpoint (Ollama or llama.cpp OpenAI chat). "
            "Sleuth does not start a local daemon; refresh only HTTP-calls the URL "
            "you configure (file is gitignored)"
        )

    with path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    ollama_raw = raw.get("ollama") or {}
    if not ollama_raw.get("base_url", "").strip() or not ollama_raw.get("model", "").strip():
        raise ValueError(f"{path} must set non-empty ollama.base_url and ollama.model")

    transcripts_raw = raw.get("transcripts") or {}
    processing_raw = raw.get("processing") or {}

    return SleuthsConfig(
        ollama=OllamaConfig(
            base_url=str(ollama_raw["base_url"]).strip(),
            model=str(ollama_raw["model"]).strip(),
            api=_parse_inference_api(ollama_raw.get("api")),
        ),
        transcripts=TranscriptsConfig(
            extra_transcript_slugs=list(transcripts_raw.get("extra_transcript_slugs") or []),
        ),
        processing=ProcessingConfig(
            context_budget_tokens=int(
                processing_raw.get("context_budget_tokens", ProcessingConfig.context_budget_tokens)
            ),
            response_headroom_tokens=int(
                processing_raw.get("response_headroom_tokens", ProcessingConfig.response_headroom_tokens)
            ),
            pass_summary_cap_tokens=int(
                processing_raw.get("pass_summary_cap_tokens", ProcessingConfig.pass_summary_cap_tokens)
            ),
            final_summary_target_tokens=int(
                processing_raw.get(
                    "final_summary_target_tokens", ProcessingConfig.final_summary_target_tokens
                )
            ),
            relevance_max_completion_tokens=int(
                processing_raw.get(
                    "relevance_max_completion_tokens",
                    ProcessingConfig.relevance_max_completion_tokens,
                )
            ),
            summary_max_completion_tokens=int(
                processing_raw.get(
                    "summary_max_completion_tokens",
                    ProcessingConfig.summary_max_completion_tokens,
                )
            ),
            chunk_lines=int(processing_raw.get("chunk_lines", ProcessingConfig.chunk_lines)),
            max_chunks_per_batch=int(
                processing_raw.get("max_chunks_per_batch", ProcessingConfig.max_chunks_per_batch)
            ),
            relevance_min_content_tokens=int(
                processing_raw.get(
                    "relevance_min_content_tokens",
                    ProcessingConfig.relevance_min_content_tokens,
                )
            ),
            relevance_max_content_tokens=int(
                processing_raw.get(
                    "relevance_max_content_tokens",
                    ProcessingConfig.relevance_max_content_tokens,
                )
            ),
            summarize_target_content_tokens=int(
                processing_raw.get(
                    "summarize_target_content_tokens",
                    ProcessingConfig.summarize_target_content_tokens,
                )
            ),
            merge_target_content_tokens=int(
                processing_raw.get(
                    "merge_target_content_tokens",
                    ProcessingConfig.merge_target_content_tokens,
                )
            ),
            merge_max_items_per_batch=int(
                processing_raw.get(
                    "merge_max_items_per_batch",
                    ProcessingConfig.merge_max_items_per_batch,
                )
            ),
            max_parallel_inference_requests=_clamp_parallel_inference_requests(
                processing_raw.get(
                    "max_parallel_inference_requests",
                    ProcessingConfig.max_parallel_inference_requests,
                )
            ),
        ),
    )


def _clamp_parallel_inference_requests(value: object) -> int:
    n = int(value)  # type: ignore[arg-type]
    return max(1, n)


def cursor_projects_dir() -> Path:
    home = Path.home()
    return home / ".cursor" / "projects"
