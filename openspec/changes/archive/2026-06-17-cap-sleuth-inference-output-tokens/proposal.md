## Why

Sleuth refresh inference calls currently rely on prompt instructions alone to bound output size. Some locally configured models (notably Qwen3) can ignore those instructions and generate excessively long completions — wasting latency, risking context overflow, and producing unparseable relevance responses. Hard completion limits at the inference API boundary prevent runaway generation without changing the refresh pipeline structure.

## What Changes

- Add **stage-specific completion length limits** on every summarization service call during sleuth refresh.
- **Relevance filtering** calls SHALL cap completion length at roughly two hundred tokens — sufficient for a small structured index list.
- **Summarization and merge** calls (pass summarize, intra-segment merge, cross-segment merge) SHALL cap completion length at roughly one thousand tokens.
- Defaults SHALL be configurable on the local workstation; when not configured, the tighter caps above apply.
- Align prompt-level summary size guidance with the new completion caps so instructions and API limits are consistent.

## Capabilities

### New Capabilities

_(none — behavior extends existing conversation-sleuths capability)_

### Modified Capabilities

- `conversation-sleuths`: Add observable completion-length limits on inference calls by pipeline stage; tighten default summary sizing to match.

## Impact

- Sleuth inference client and processing configuration (local `.sleuths/config.yaml` processing section).
- Relevance, summarize, and merge pipeline stages — all share the inference client.
- Operator documentation for sleuth refresh tuning.
- No change to checkpoint semantics, session scope, dry-run, or transcript discovery.
