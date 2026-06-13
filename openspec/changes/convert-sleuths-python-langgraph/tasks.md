## 1. Python package scaffold

- [x] 1.1 Create `.cursor/skills/sleuths/pyproject.toml` with pinned `langgraph`, `langchain` (or split packages), `langsmith`, `python-dotenv`, `pyyaml`, `click`/`typer`, and `sleuth` console script entry point
- [x] 1.2 Add package layout under `.cursor/skills/sleuths/sleuth/` (`cli.py`, `config.py`, `discover.py`, `checkpoint.py`, `jsonl_extract.py`, `prompts.py`, `relevance.py`, `context_budget.py`, `token.py`, `slug.py`, `reset.py`, `refresh.py`)
- [x] 1.3 Add committed `secrets.example.env` stub documenting LangSmith and tracing variables; document copy target `.sleuths/secrets.env` in skill (gitignored)

## 2. Port core logic from Rust

- [x] 2.1 Port config loading (`SleuthsConfig`, `ProcessingConfig`, inference API selection) with parity for existing YAML keys
- [x] 2.2 Port slug derivation, transcript discovery (primary slug + git worktree expansion + `extra_transcript_slugs`), and segment ordering by mtime
- [x] 2.3 Port checkpoint read/write with `(transcript_id, relative_path, line_count)` granularity and per-segment persistence during refresh
- [x] 2.4 Port JSONL text extraction, chunk streaming, token estimation, and context-budget batching helpers
- [x] 2.5 Port prompt templates (relevance, summarize, merge) verbatim from Rust `prompts.rs`
- [x] 2.6 Port relevance JSON parsing, summarize pass, hierarchical reduce, and prior-summary seed merge semantics
- [x] 2.7 Implement `reset` command clearing summary + checkpoint without inference calls

## 3. LangGraph pipeline

- [x] 3.1 Define typed graph state for per-segment processing (`chunks`, `relevant_chunks`, `pass_summaries`, `segment_summary`, segment metadata)
- [x] 3.2 Build per-segment `StateGraph` with nodes: `load_chunks` → `relevance_pass` → `summarize_pass` → `hierarchical_reduce`
- [x] 3.3 Wire outer refresh orchestration (discover pending segments, invoke graph per segment, merge segment outputs, final reduce with prior summary, write artifacts)
- [x] 3.4 Integrate LangChain chat model adapters for Ollama and OpenAI-compatible HTTP backends per `config.yaml` `api` field

## 4. LangSmith observability

- [x] 4.1 Load `.sleuths/secrets.env` when present via `python-dotenv`; no error when absent
- [x] 4.2 Enable LangSmith tracing env vars before graph invoke when credentials are present
- [x] 4.3 Ensure graph nodes and LLM calls appear as trace spans in LangSmith; use configurable `LANGSMITH_PROJECT` (default `sleuths` in stub)
- [x] 4.4 On tracing export failure, emit explicit warning and continue refresh when inference succeeds (non-fatal tracing)

## 5. Remove Rust implementation

- [x] 5.1 Delete `.cursor/skills/sleuths/sleuth/` Rust crate sources and skill-root `Cargo.toml` workspace
- [x] 5.2 Update `.gitignore` to drop Rust `target/` paths for sleuths if no longer applicable

## 6. Bundle install and documentation

- [x] 6.1 Update `scripts/build-local-tools.sh` to `pip install -e` Python skill packages when `pyproject.toml` is present (retain Rust loop only for remaining crates)
- [x] 6.2 Update `.cursor/skills/sleuths/SKILL.md`: Python 3.11+ prerequisite, install command, optional LangSmith setup from `secrets.example.env`, same refresh/reset flows
- [x] 6.3 Update `AGENTS.md` sleuths section for Python entrypoint and optional tracing privacy note
- [x] 6.4 Update `.cursor/skills/openspec-flow-install/SKILL.md` inventory and `OPENSPEC_FLOW.md` / `README.md` capability table if they reference Rust build paths

## 7. Tests and verification

- [x] 7.1 Add `pytest` unit tests for slug derivation, token budget grouping, relevance JSON parsing, and checkpoint round-trip
- [x] 7.2 Smoke test: `pip install -e`, create sleuth, refresh twice — second run reports nothing new; checkpoint advances correctly
- [x] 7.3 Smoke test: reset clears summary/checkpoint; subsequent refresh rebuilds from scratch
- [x] 7.4 Smoke test: refresh fails cleanly when inference endpoint unreachable (no checkpoint advance on failed segment)
- [ ] 7.5 Smoke test (operator environment): with `.sleuths/secrets.env` filled, confirm a refresh run appears in LangSmith project dashboard

## 8. Archive (apply finish)

- [ ] 8.1 Run `/osf-apply-finish` to archive this change and merge `conversation-sleuths` delta into living specs

## Explicitly deferred

- [ ] D.1 Dual-shipping Rust and Python sleuth CLIs during a transition period (Rust removed in this change)
- [ ] D.2 Automatic per-batch LangGraph nodes (finer traces) — revisit if LangSmith noise becomes a problem
- [ ] D.3 `uv` lockfile / mandatory `uv` install path — pip editable install is sufficient for v1
