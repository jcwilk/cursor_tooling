## 1. Propose lane lock

- [x] 1.1 Add **Lane lock** section to `.cursor/skills/osf-propose/SKILL.md` immediately after the opening paragraph (before Required reading): writable scope is only `openspec/changes/<name>/`; everything else read-only for orientation; healthy end state is validated change folder + `/osf-explain` debrief—not edited skills, agents, or bundle docs; if first planned edit is outside the change folder, stop.

## 2. Simplify apply orchestration

- [x] 2.1 Rewrite `.cursor/skills/osf-apply-changes/SKILL.md`: current-branch assumption; remove branch/worktree setup, parallel multi-change section, and duplicated worker-owns list; keep Task-only + wait-for-subagent + task prompt contract + single-change procedure + finish/abort outcomes; target ~50 lines.
- [x] 2.2 Rewrite `.cursor/agents/osf-apply-start.md`: current-branch worker; remove Step 1 isolation and worktree/branch inputs; reference parent task prompt contract instead of duplicating full forbidden/allowed table; keep orient, task classes, loop, finish/abort delegation; target ~110 lines.
- [x] 2.3 Align `.cursor/agents/osf-apply-finish.md`: **working branch** terminology; remove worktree-path inputs; simplify merge step to use repository root from inputs.
- [x] 2.4 Align `.cursor/agents/osf-apply-abort.md`: **working branch** terminology; remove worktree-path inputs; consistent with finish agent.

## 3. Flow narrative

- [x] 3.1 Update `OPENSPEC_FLOW.md`: add **Forbidden lane transitions** subsection (`/osf-propose` must not jump to direct bundle/integration edits; apply paths only after approved tasks); update capability table and standard-flow step 3 for current-branch apply; replace remaining “execution branch” / “isolated branch” wording with **working branch** / **current branch** where apply context is described; prerequisites line should not imply apply owns isolation setup.

## 4. Bundle version and validation

- [x] 4.1 Bump `OPENSPEC_FLOW_VERSION` in `OPENSPEC_FLOW.md` front matter and add `CHANGELOG.md` entry summarizing apply simplification and propose lane lock.
- [x] 4.2 Run `npx @fission-ai/openspec@latest validate simplify-apply-propose-lane-guards --type change` and `npx @fission-ai/openspec@latest validate --specs` after archive (finish step).

## Explicitly deferred

- Expanded `osf-propose` do-not-implement path lists, not-a-bypass table, combined propose+apply clarification, turn success criterion, `AGENTS.md` slash-command section, `osf-apply-changes` anti-propose guard, `osf-propose` frontmatter description — out of scope per human decision; revisit in a follow-on change if needed.
