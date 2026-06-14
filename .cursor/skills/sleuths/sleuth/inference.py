from __future__ import annotations

import json
import threading
from dataclasses import dataclass

import requests
from langsmith import traceable

from sleuth.config import InferenceApi, OllamaConfig

_inference_calls = 0
_call_lock = threading.Lock()


def inference_call_count() -> int:
    with _call_lock:
        return _inference_calls


def reset_inference_call_count() -> None:
    global _inference_calls
    with _call_lock:
        _inference_calls = 0


def _increment_calls() -> None:
    global _inference_calls
    with _call_lock:
        _inference_calls += 1


@traceable(name="sleuth_inference_generate", run_type="llm")
def _generate_traced(config: OllamaConfig, prompt: str) -> str:
    _increment_calls()
    if config.api == InferenceApi.OLLAMA:
        return _generate_ollama(config, prompt)
    return _generate_openai_chat(config, prompt)


@dataclass
class InferenceClient:
    config: OllamaConfig

    def generate(self, prompt: str) -> str:
        return _generate_traced(self.config, prompt)


def _generate_ollama(config: OllamaConfig, prompt: str) -> str:
    base = config.base_url.rstrip("/")
    url = f"{base}/api/generate"
    body = {
        "model": config.model,
        "prompt": prompt,
        "stream": False,
    }
    resp = requests.post(url, json=body, timeout=600)
    if not resp.ok:
        raise RuntimeError(
            f"Ollama request failed ({resp.status_code}): {resp.text}"
        )
    parsed = resp.json()
    return str(parsed.get("response", "")).strip()


def _generate_openai_chat(config: OllamaConfig, prompt: str) -> str:
    base = config.base_url.rstrip("/")
    url = f"{base}/v1/chat/completions"
    body = {
        "model": config.model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
    }
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
