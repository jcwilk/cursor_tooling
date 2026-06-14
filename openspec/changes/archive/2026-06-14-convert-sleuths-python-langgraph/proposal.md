## Why

The sleuths summarization runner is implemented today as a hand-rolled Rust map-reduce pipeline. That works, but it is harder to evolve, inspect, and debug than a graph-native workflow with first-class tracing. Rebuilding sleuths in Python on LangGraph preserves existing behavioral contracts while making the pipeline explicit, composable, and observable through LangSmith when the operator opts in.

## What Changes

- **Replace** the bundled Rust `sleuth` CLI with a Python package that exposes the same human-facing commands (`refresh`, `reset`) and the same `.sleuths/` on-disk layout.
- **Rebuild** the chunk → relevance → batched summarize → hierarchical reduce pipeline as a LangGraph `StateGraph` instead of imperative Rust functions.
- **Add** optional LangSmith cloud tracing for refresh runs when the operator supplies credentials (runs, spans, and node boundaries visible in LangSmith).
- **Add** committed secret stubs (example env file and/or example secrets file) documenting which values the operator must fill in for LangSmith and inference — no real secrets in git.
- **Update** the sleuths skill, build script, `AGENTS.md`, and bundle inventory to reflect Python install/build instead of Rust `cargo build`.
- **Remove** the Rust crate and its gitignored `target/` build artifacts from the bundle.

**BREAKING (operator-facing):** Consumers must install Python dependencies and invoke the new entrypoint instead of building the Rust binary. Existing `.sleuths/` config, queries, checkpoints, and summaries remain compatible; no forced re-summarization.

## Capabilities

### New Capabilities

- (none)

### Modified Capabilities

- `conversation-sleuths`: Add optional cloud run observability when the operator configures tracing credentials; clarify that refresh orchestration is graph-based while preserving all existing incremental summarization, checkpoint, reset, and privacy behaviors.

## Impact

- **Bundle**: `.cursor/skills/sleuths/` becomes a Python project (LangGraph + LangChain inference adapters); Rust `sleuth/` crate removed; `scripts/build-local-tools.sh` updated or superseded by a Python install path.
- **Consumer projects**: unchanged `.sleuths/` artifact layout; operators add optional LangSmith credentials via local secret files; Python 3.11+ (or bundle-pinned version) required on the workstation.
- **Dependencies**: `langgraph`, `langchain` (or compatible inference client), `langsmith` tracing SDK; HTTP inference backends (Ollama / OpenAI-chat) unchanged at the behavioral level.
- **Privacy**: LangSmith export is opt-in; transcript-derived content may leave the machine only when the operator explicitly configures cloud tracing — default remains local-only processing with local artifacts.
