## Context

The sleuth CLI currently exposes only `refresh`, which is checkpoint-aware and merges new output into an existing summary. Humans who want a clean slate today must manually delete files under `.sleuths/<id>/`. That works but is undocumented, easy to get wrong (e.g. deleting the query definition), and not discoverable from `--help`.

Reset is a narrow, local-only operation: delete summary and checkpoint artifacts, validate the sleuth id against an existing query definition, emit a short status message. It must not call the inference endpoint.

## Goals / Non-Goals

**Goals:**

- Mirror the `refresh` selection model: `--sleuth <id>` or `--all`.
- Remove only `.sleuths/<id>/summary.md` and `.sleuths/<id>/checkpoint.yaml`.
- Leave `.sleuths/queries/<id>.yaml` untouched.
- Be idempotent when artifacts are already absent.
- Add unit tests for single-sleuth and all-sleuths reset paths.

**Non-Goals:**

- Auto-refresh after reset (human runs refresh separately).
- Resetting config, query definitions, or transcript discovery settings.
- A `clear` alias (one name: `reset`).
- Agents invoking reset without explicit human request (same human-only policy as refresh).

## Decisions

**1. Subcommand name: `reset` (not `clear`)**

- `reset` signals "start processing from scratch" (checkpoint + summary).
- `clear` reads as summary-only and is ambiguous with filesystem "clear directory."

**2. Artifact scope**

- Delete summary and checkpoint only. Empty `.sleuths/<id>/` directory may remain.
- Validate sleuth id by loading the query file (same guard as refresh) so typos fail fast.

**3. CLI shape**

- `reset --sleuth <id>` and `reset --all`, matching refresh flags for consistency.
- Require exactly one of `--sleuth` or `--all` (same error as refresh when neither is given).

**4. Module layout**

- New `reset.rs` with `reset_sleuth`, `reset_all`, and shared artifact removal helper; wire from `main.rs` alongside existing `refresh` match arm.

## Risks / Trade-offs

- **[Risk] Human resets then forgets to refresh** → Mitigation: skill doc shows reset immediately followed by refresh; status message says artifacts were removed, not that summarization ran.
- **[Risk] Partial delete if process crashes mid-reset** → Mitigation: two small file deletes; idempotent re-run completes cleanup; refresh treats missing checkpoint as fresh start anyway.
- **[Risk] `--all` resets every sleuth without confirmation** → Mitigation: same pattern as `refresh --all`; human-only invocation; document in skill.

## Migration Plan

- Ship in bundle; consumers rebuild local binary via `scripts/build-local-tools.sh`.
- No migration of on-disk formats; existing manual deletion remains equivalent behavior.

## Open Questions

- (none)
