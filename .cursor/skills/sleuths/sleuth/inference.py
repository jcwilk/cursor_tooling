from __future__ import annotations

import json
import threading
from contextvars import ContextVar
from dataclasses import dataclass

import requests
from langsmith import traceable

from sleuth.config import InferenceApi, OllamaConfig

STAGE_RELEVANCE = "relevance"
STAGE_SUMMARIZE = "summarize"
STAGE_INTRA_MERGE = "intra_merge"
STAGE_CROSS_MERGE = "cross_merge"

_inference_calls = 0
_stage_counts: dict[str, int] = {
    STAGE_RELEVANCE: 0,
    STAGE_SUMMARIZE: 0,
    STAGE_INTRA_MERGE: 0,
    STAGE_CROSS_MERGE: 0,
}
_call_lock = threading.Lock()
_inference_stage: ContextVar[str | None] = ContextVar("inference_stage", default=None)


def inference_call_count() -> int:
    with _call_lock:
        return _inference_calls


def inference_stage_counts() -> dict[str, int]:
    with _call_lock:
        return dict(_stage_counts)


def reset_inference_call_count() -> None:
    global _inference_calls
    with _call_lock:
        _inference_calls = 0
        for key in _stage_counts:
            _stage_counts[key] = 0


def set_inference_stage(stage: str | None) -> None:
    _inference_stage.set(stage)


def _increment_calls() -> None:
    global _inference_calls
    with _call_lock:
        _inference_calls += 1
        stage = _inference_stage.get()
        if stage in _stage_counts:
            _stage_counts[stage] += 1


@traceable(name="sleuth inference generate call", run_type="llm")
def _generate_traced(
    config: OllamaConfig, prompt: str, max_completion_tokens: int | None = None
) -> str:
    _increment_calls()
    if config.api == InferenceApi.OLLAMA:
        return _generate_ollama(config, prompt, max_completion_tokens)
    return _generate_openai_chat(config, prompt, max_completion_tokens)


@dataclass
class InferenceClient:
    config: OllamaConfig

    def generate(self, prompt: str, *, max_completion_tokens: int | None = None) -> str:
        return _generate_traced(self.config, prompt, max_completion_tokens)


def _generate_ollama(
    config: OllamaConfig, prompt: str, max_completion_tokens: int | None = None
) -> str:
    base = config.base_url.rstrip("/")
    url = f"{base}/api/generate"
    body: dict[str, object] = {
        "model": config.model,
        "prompt": prompt,
        "stream": False,
    }
    if max_completion_tokens is not None:
        body["options"] = {"num_predict": max_completion_tokens}
    resp = requests.post(url, json=body, timeout=600)
    if not resp.ok:
        raise RuntimeError(
            f"Ollama request failed ({resp.status_code}): {resp.text}"
        )
    parsed = resp.json()
    return str(parsed.get("response", "")).strip()


def _generate_openai_chat(
    config: OllamaConfig, prompt: str, max_completion_tokens: int | None = None
) -> str:
    base = config.base_url.rstrip("/")
    url = f"{base}/v1/chat/completions"
    body: dict[str, object] = {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
    if max_completion_tokens is not None:
        body["max_tokens"] = max_completion_tokens
    resp = requests.post(url, json=body, timeout=600)
    body_text = resp.text
    if not resp.ok:
        raise RuntimeError(
            f"OpenAI chat request failed ({resp.status_code}) at {url}: {body_text}"
        )
    return _parse_openai_chat_response(body_text)


def _parse_openai_chat_response(body: str) -> str:
    parsed = json.loads(body)
    choices = parsed.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if content is None:
        return ""
    return str(content).strip()
