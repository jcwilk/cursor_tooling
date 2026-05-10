## 1. Review

- [ ] 1.1 Review `proposal.md`, `design.md`, and both delta specs for behavioral cohesion and omission of OSF bundle path catalogs from normative language
- [ ] 1.2 Confirm OSF narrative docs (`README.md`, `OPENSPEC_FLOW.md`, `AGENTS.md`) remain materially consistent once authoritative specs reconcile (adjust prose only via follow-up OSF changes if divergence is unavoidable)

## 2. Publish reconciled behavioral specifications

- [ ] 2.1 Re-run validation: `npx @fission-ai/openspec@latest validate "init-normative-openspec-flow-specs" --type change`
- [ ] 2.2 Archive the approved change through OpenSpec (`npx @fission-ai/openspec@latest archive "init-normative-openspec-flow-specs"` or OSF `apply-finish` equivalent) so `openspec/specs/openspec-flow-reference/spec.md` and `openspec/specs/openspec-flow-target-sync/spec.md` reconcile from the deltas in this folder
