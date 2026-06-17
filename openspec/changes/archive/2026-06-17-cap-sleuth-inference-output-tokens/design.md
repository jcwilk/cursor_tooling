## Context

Sleuth refresh issues four kinds of inference calls through a shared `InferenceClient`: relevance filtering, pass summarization, intra-segment merge, and cross-segment merge. Today the client sends only model id and prompt text to either Ollama (`/api/generate`) or OpenAI-compatible chat (`/v1/chat/completions`). Output size is constrained only by prompt wording (`pass_summary_cap_tokens`, `final_summary_target_tokens`) and merge target instructions — not by a hard API parameter.

On Qwen3 via llama.cpp OpenAI chat, long runaway completions have been observed (especially on summarize/merge), increasing latency and occasionally breaking relevance JSON parsing.

The inference layer already tracks stage via `set_inference_stage` (`relevance`, `summarize`, `intra_merge`, `cross_merge`) before each `client.generate` call, so stage-appropriate limits can be selected without changing pipeline structure.

## Goals / Non-Goals

**Goals:**

- Pass a **hard completion token limit** on every inference request, chosen by pipeline stage.
- Defaults: **200** tokens for relevance; **1000** tokens for summarize and both merge stages.
- Expose both limits as optional `processing` config fields with the above defaults.
- Align prompt-level summary caps (`pass_summary_cap_tokens`, `final_summary_target_tokens`) with the new summarize/merge completion default (1000) so instructions and API limits agree.
- Support both configured API backends (Ollama `num_predict`, OpenAI chat `max_tokens`).

**Non-Goals:**

- Changing input-side batch sizing (relevance min/max, summarize/merge content targets).
- Retrying or truncating client-side when a model hits the limit mid-sentence (server-side cap is sufficient for v1).
- Per-model automatic tuning or dynamic limit adjustment.
- Changing checkpoint, session scope, or dry-run behavior.

## Decisions

### 1. Stage → limit mapping at the inference client

**Decision:** Extend `InferenceClient.generate` to accept an optional `max_completion_tokens` argument. `_generate_traced` passes it through to backend-specific request bodies. Pipeline stages set the limit immediately before calling `generate`, using values from `ProcessingConfig`.

**Rationale:** Centralizes API parameter spelling (`num_predict` vs `max_tokens`) in one module; pipeline already knows the stage.

**Alternatives considered:**

- *Separate client methods per stage* — rejected as unnecessary surface area.
- *Global single max_tokens for all stages* — rejected; relevance needs a much smaller cap than summarize.

### 2. Config field names and defaults

**Decision:** Add to `ProcessingConfig`:

| Field | Default | Used by stages |
|-------|---------|----------------|
| `relevance_max_completion_tokens` | 200 | relevance |
| `summary_max_completion_tokens` | 1000 | summarize, intra_merge, cross_merge |

Lower existing prompt defaults to match:

| Field | Old default | New default |
|-------|-------------|-------------|
| `pass_summary_cap_tokens` | 2000 | 1000 |
| `final_summary_target_tokens` | 2000 | 1000 |

**Rationale:** Matches operator request; keeps one knob for all summary-producing stages; relevance stays separate because output is a tiny JSON id list.

### 3. Backend parameter mapping

**Decision:**

- Ollama `/api/generate`: set `"options": {"num_predict": N}` (or top-level `num_predict` if the deployed Ollama version prefers it — verify against existing server; llama.cpp proxy may accept OpenAI path instead).
- OpenAI chat: set `"max_tokens": N`.

**Rationale:** Standard mappings for each configured `api` value; no new dependencies.

### 4. Truncated relevance responses

**Decision:** No new retry logic. Existing behavior applies: unparseable relevance response → no chunks from that batch proceed; refresh continues.

**Rationale:** 200 tokens is ample for index JSON; truncation at that limit likely indicates a model malfunction worth surfacing via existing parse-failure path rather than silent retry.

## Risks / Trade-offs

- **[Risk] Aggressive 1000-token cap truncates dense summarize output** → Mitigation: configurable; operator can raise `summary_max_completion_tokens` locally; prompt already asks for concise bullets.
- **[Risk] Backend ignores max_tokens** → Mitigation: documented as best-effort server contract; behavior unchanged from today for non-compliant servers except prompt alignment.
- **[Risk] Existing configs with explicit 2000 caps in yaml** → Mitigation: yaml overrides still win; only defaults change for fresh installs.

## Migration Plan

1. Ship code + config defaults + SKILL.md documentation.
2. Operators with custom `pass_summary_cap_tokens` / `final_summary_target_tokens` in `.sleuths/config.yaml` are unaffected until they remove overrides.
3. Rebuild local CLI (`scripts/build-local-tools.sh`) after apply.
4. No checkpoint or summary migration required.

## Open Questions

- None blocking apply — backend field names are known for both supported APIs.
