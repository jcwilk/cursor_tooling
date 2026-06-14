## ADDED Requirements

### Requirement: Optional cloud run observability

When the operator configures cloud tracing credentials on the local workstation, sleuth refresh runs SHALL export run and step metadata for the refresh pipeline to the configured cloud observability service. When tracing credentials are not configured, refresh SHALL complete without requiring cloud connectivity and SHALL NOT export run metadata externally.

#### Scenario: Operator enables cloud tracing

- **GIVEN** valid cloud tracing credentials are configured locally for the workstation
- **WHEN** a human requests sleuth refresh
- **THEN** the refresh run exports observability metadata for the pipeline and its steps to the configured cloud service

#### Scenario: Operator has not configured tracing

- **GIVEN** no cloud tracing credentials are configured
- **WHEN** a human requests sleuth refresh
- **THEN** processing remains local to the workstation
- **AND** refresh does not require connectivity to a cloud observability service

#### Scenario: Tracing export fails during refresh

- **GIVEN** cloud tracing credentials are configured
- **AND** the cloud observability service is unreachable or rejects the export
- **WHEN** a human requests sleuth refresh
- **AND** the configured summarization service is available
- **THEN** refresh completes local summarization and artifact updates
- **AND** the operator receives an explicit warning that tracing export failed
