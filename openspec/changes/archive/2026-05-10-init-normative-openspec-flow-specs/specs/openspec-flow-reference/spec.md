## ADDED Requirements

### Requirement: Cohesive Semantic Version identity

OSF reference bundles MUST expose exactly one Semantic Version identifying the interoperability level of every OSF integration component intentionally distributed as a singular upgrade atom.

#### Scenario: Precedence-ready identification
- **WHEN** a consumer inspects OSF reference distribution metadata declaring release identity
- **THEN** exactly one Semantic Version suitable for pairwise ordering is plainly discoverable without reconciling contradictory version claims across OSF integration components bundled for that release

### Requirement: Isolation between proposal shaping and archival reconciliation

OSF workflows MUST distinguish behavioral-intent shaping from reconciling authoritative behavioral specification content unless the initiating human expressly combines those scopes in the same directive.

#### Scenario: Proposal shaping without silent reconciliation
- **WHEN** a worker is tasked solely with shaping or validating OSF behavioral intent artifacts that precede archival
- **THEN** reconciling deltas into OSF authoritative behavioral specifications MUST NOT occur without an explicit archival or finishing directive attributable to OSF apply lifecycle guidance

### Requirement: Dedicated execution modality for OSF apply lifecycle

OSF MUST designate a delegated execution pathway for OSF apply-related lifecycle roles so high-impact repository operations prescribed by OSF are not satisfied by conversational replay alone.

#### Scenario: Mandatory delegation documentation
- **WHEN** OSF documentation assigns apply, reconciliation, finish, or abort responsibilities that may alter repository-wide state
- **THEN** those responsibilities MUST mandate execution through OSF’s delegated Task-compatible pathway rather than direct conversational emulation of OSF agent-definition narratives

### Requirement: Behavioral specification supremacy post-archival

When OSF authoritative behavioral specifications have been reconciled through archival for a merged change, OSF MUST treat reconciled authoritative behavioral specification statements as authoritative over OSF narrative prose when enforcing behaviors they both describe.

#### Scenario: Narrative divergence after archival
- **WHEN** reconciled OSF authoritative behavioral specification content conflicts with OSF narrative descriptions covering the same responsibility
- **THEN** reconciled OSF authoritative behavioral specification content governs conformance until superseded via a subsequent OSF change that archives replacements
