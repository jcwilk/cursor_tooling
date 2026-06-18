## Context

Sleuth refresh runs relevance filtering, batched summarization, and hierarchical merge as separate pipeline stages. Within each stage, batch groups are processed in strict serial `for group in groups:` loops that call `InferenceClient.generate()` one at a time (`run_relevance_pass`, `run_summarize_pass`, `recursive_reduce` in `.cursor/skills/sleuths/sleuth/pipeline.py`).

Relevance filtering currently asks the model for a JSON object (`{"relevant_ids": [0, 2]}`) via `relevance_prompt()` in `prompts.py` and parses it with `json.loads` in `parse_relevant_ids()` (`relevance.py`). That output format roughly doubles token generation for a short answer.

Local processing settings live in `ProcessingConfig` (`config.py`) and `.sleuths/config.yaml` under the `processing` section.

## Goals / Non-Goals

**Goals:**

- Run up to four summarization-service requests in parallel within a single pipeline stage when that stage has multiple batch groups.
- Expose `max_parallel_inference_requests` (default `4`) on `ProcessingConfig` and in `.sleuths/config.yaml` `processing` section.
- Replace JSON relevance output with comma-separated zero-based indices only (e.g. `0,2,5` or empty).
- Preserve existing batch sizing, checkpoint semantics, error handling, and stage ordering.

**Non-Goals:**

- Parallelism across different pipeline stages simultaneously.
- Changing input batch sizing budgets or stage-specific content targets.
- New retry or backoff logic for failed parallel calls beyond existing error handling.
- Backward compatibility with JSON relevance responses (prompt change only; old responses in flight are not a supported migration path).

## Decisions

### 1. Concurrency model: bounded pool within each stage loop

Use `concurrent.futures.ThreadPoolExecutor` with `max_workers = processing.max_parallel_inference_requests` to submit one future per batch group inside relevance, summarize, and merge-round loops. Collect results in submission order (or map futures back to groups by index) so downstream aggregation order matches today's serial semantics.

**Why threads:** `InferenceClient.generate()` is I/O-bound HTTP; threads avoid asyncio refactor of the LangGraph pipeline.

**Alternative considered:** `asyncio.gather` with async HTTP client — rejected as larger cross-cutting change for marginal gain.

### 2. Scope of parallelism

Parallelize only the inner batch loops within a stage:

| Stage | Parallel unit |
|---|---|
| Relevance | Each relevance batch group |
| Summarize | Each summarize batch group |
| Merge | Each merge group within one recursive round |

Do **not** overlap relevance with summarization, or merge rounds with the next stage. Each `while` iteration in `recursive_reduce` still completes before the next round begins.

### 3. Config field

Add to `ProcessingConfig`:

```python
max_parallel_inference_requests: int = 4
```

Load from `processing.max_parallel_inference_requests` in YAML. Values `< 1` should clamp to `1` at load or use site (design choice: clamp to 1 with optional stderr warning).

### 4. Relevance output format

**Prompt** (`relevance_prompt`): Instruct model to respond with ONLY comma-separated zero-based indices, no JSON, no prose, no markdown fences. Examples: `0,2,5` or empty string when nothing is relevant.

**Parser** (`parse_relevant_ids`): Strip whitespace and optional code fences; split on commas; parse integers; filter to `0..max_index`; dedupe and sort. Non-numeric tokens and out-of-range indices are skipped. Empty or whitespace-only response → `[]`. Any unparseable remainder → treat as unparseable (return `[]`, log to stderr) consistent with existing unparseable scenario.

**Completion limit:** Existing `relevance_max_completion_tokens` (default ~200) remains sufficient; CSV output is shorter than JSON.

### 5. Observability

LangSmith `@traceable` spans on stage functions remain; individual `client.generate()` calls keep existing per-call tracing. Parallel execution may interleave span timestamps — acceptable.

## Risks / Trade-offs

- **[Increased load on local inference server]** → Default concurrency 4; operator can lower via config; document for single-GPU setups.
- **[Non-deterministic span ordering in traces]** → Acceptable; functional order of merged results preserved.
- **[Model emits prose despite prompt]** → Parser returns `[]` for batch (existing unparseable behavior); no new retry path.
- **[Thread safety of shared client]** → Verify `InferenceClient` uses per-request HTTP calls without shared mutable state; use one client per worker task or confirm thread-safe session.

## Migration Plan

No checkpoint or summary migration. After deploy:

1. Operators with custom relevance prompts in forked code must align with CSV format.
2. Default config needs no change (new field optional, defaults to 4).
3. Rollback: revert code; concurrency falls back to serial; relevance prompt reverts to JSON if rolled back entirely.

## Open Questions

- None blocking apply — clamp vs reject for `max_parallel_inference_requests: 0` (recommend clamp to 1).
