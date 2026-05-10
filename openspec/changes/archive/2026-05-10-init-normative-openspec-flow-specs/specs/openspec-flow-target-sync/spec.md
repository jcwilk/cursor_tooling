## ADDED Requirements

### Requirement: Version relationship assessment prior to propagation

OSF target synchronization tooling MUST summarize the ordering relationship between a chosen OSF reference Semantic Version and a consumer’s readable OSF Semantic Version marker when both are available.

#### Scenario: Known consumer baseline
- **WHEN** synchronization tooling parses both the reference OSF Semantic Version and a consumer OSF Semantic Version marker at the outset of a synchronization attempt
- **THEN** tooling reports parity, downgrade risk, advancement opportunity, or indeterminate parity in human-readable summaries before invoking destructive merges

### Requirement: Controlled replacement of OSF integration assets

OSF target synchronization MUST update integration assets attributable to OSF reference bundles using explicit propagation mechanics scoped to OSF bundle inventory without implying wholesale deletion of every file under broadened integration prefixes.

#### Scenario: Retaining coexistence companions
- **WHEN** the target retains additional operator-managed files neighboring OSF-managed integration artifacts under the same subtree
- **THEN** default OSF synchronization avoids deleting those coexistence companions unless synchronization documentation records an explicit destructive option selected by the operator

### Requirement: Semantic Version marker parity upon successful deliberate upgrade

When OSF target synchronization declares success aligning a consumer to reference version R absent reported blocking conflicts reported by tooling, OSF target synchronization MUST update or create consumer-readable OSF Semantic Version markers so they reflect reference version R consistently with OSF synchronization conventions.

#### Scenario: Successful parity upgrade completes
- **WHEN** an operator-directed synchronization concludes without conflict and aligns the consumer to reference Semantic Version `R`
- **THEN** consumer-maintained OSF Semantic Version markers authoritative for drift detection report `R` until superseded by a later synchronization invocation
