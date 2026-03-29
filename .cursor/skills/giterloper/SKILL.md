---
name: giterloper
description: Reads, searches, queues, and reconciles version-pinned markdown knowledge via the giterloper MCP server (git-backed store, pins/SHAs, session and named pins). Use when the user mentions giterloper, knowledge pins, pending knowledge, reconciling knowledge, or comparing knowledge at different commits for epics and tickets.
---

# Giterloper (MCP)

## What it is

**Giterloper** is a **versioned knowledge store**: markdown lives in a Git remote (server-configured); each **pin** points at a **branch and/or resolved SHA**. You can **add** knowledge (queue → reconcile into `knowledge/`), **search** and **retrieve** at a pin (optionally a specific **40-char SHA**), and **name pins** so an epic or ticket set can target a **specific knowledge state** (e.g. “where we’re going” vs “baseline at an earlier juncture”).

Upstream product behavior and architecture for the server itself live in the giterloper repository; this skill covers **how to use the MCP tools** from an agent.

## MCP access (required)

1. **Read the tool schema first** — descriptors live under  
   `mcps/project-0-cursor_tooling-giterloper/tools/<tool-name>.json`  
   (project MCP folder; server name **`project-0-cursor_tooling-giterloper`** for `call_mcp_tool`).
2. **Call tools** with arguments exactly as schema specifies (required fields, patterns for `sha`, etc.).

Do **not** pass the literal pin name `_session`; it is reserved. **Omit** `pin` on tools that support it to use the **session pin**.

## Tools (summary)

| Tool | Role |
|------|------|
| `giterloper_pin_set` | View or set **session** pin (omit `pin`) or **named** pins: `ref` (SHA or branch/tag), `branch` for writes. Repository comes from server env—not from tool args. |
| `giterloper_state_inspect` | List pins; optional `verify` for clone health. Omit `pin` to list all (`_session` first). |
| `giterloper_search` | Search corpus at a pin; optional `sha`, `limit`. |
| `giterloper_retrieve` | Read a file by path (e.g. `knowledge/foo.md`) at a pin; optional `sha`. |
| `giterloper_insert_pending` | Queue UTF-8 **markdown** under `knowledge/_pending/` (`content` required). Use literal characters in markdown; do not HTML-encode placeholders. |
| `giterloper_reconcile_pending` | Integrate pending into `knowledge/**/*.md` via LLM-backed reconciliation (OpenAI; same idea as CLI `gl reconcile`). All-or-nothing semantics per product spec; needs API configuration when not using test fixtures. |
| `giterloper_merge` | Merge one pin’s branch into another via **GitHub API** (`sourcePin` / `targetPin`; omit one side to use session pin). |
| `giterloper_session_end` | End MCP session and clear session-local server state (e.g. free disk). |

**Writes** (pending insert, reconcile, merge, pin changes that affect branches) need a pin with a **branch** where the product requires it. **Reads** (`search`, `retrieve`) need no branch.

## Typical workflows

- **Consult current (session) knowledge:** `giterloper_search` / `giterloper_retrieve` with `pin` omitted (session pin).
- **Compare or freeze a state:** create or update a **named pin** with `giterloper_pin_set` (`ref` and optionally `branch`), then `search`/`retrieve` with that `pin` or a specific `sha`.
- **Epic / ticket alignment:** keep a **baseline** pin (e.g. SHA at kickoff) and a **target** pin (branch head or SHA the epic aims for); retrieve or search each to reason about **intent vs starting point**. Merge strategy across pins uses `giterloper_merge` when branches and GitHub are in play.
- **Intake new facts:** `giterloper_insert_pending` then `giterloper_reconcile_pending` when the user wants material merged into the main corpus (not left in `_pending`).

## Hierarchy and alignment

For how **giterloper knowledge** relates to root instructions, tests, code, and operational docs—and **precedence** when they conflict—see **[HIERARCHICAL_TRUTH_AND_ALIGNMENT_MANDATE.md](HIERARCHICAL_TRUTH_AND_ALIGNMENT_MANDATE.md)** in this skill directory.

## Reference implementation / docs

For server layout, env vars (`KNOWLEDGE_STORE_REMOTE`, test mode, memsearch), and CLI parity, the **giterloper** source tree (e.g. `/home/user/workspace/giterloper`) is authoritative: `README.md`, `specs/mcp.md`, `specs/pin-semantics.md`, `AGENTS.md`.
