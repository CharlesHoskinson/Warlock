# elm-performance

## ADDED Requirements

### Requirement: ELM-QA-021

The performance owner SHALL freeze measured current-shell workload baselines and numeric absolute and regression budgets before host selection or release evaluation.

#### Scenario: ELM-QA-021 qa-021

- GIVEN a budget lacks a measured baseline
- WHEN host selection is evaluated
- THEN selection is blocked

### Requirement: ELM-QA-022

The performance verifier SHALL compare host candidates and the current shell using identical workloads and report p50, p95, p99, sample counts, cold/warm state and instrumentation overhead.

#### Scenario: ELM-QA-022 qa-022

- GIVEN the same hardware and workload
- WHEN two hosts are measured
- THEN comparable distribution data and overhead are retained

### Requirement: ELM-QA-023

The performance verifier SHALL measure CPU, wakeups, resident/private memory, resource growth, uploads and missed frames across the complete host process group including renderer children and helpers.

#### Scenario: ELM-QA-023 qa-023

- GIVEN renderer children allocate preview buffers
- WHEN a soak completes
- THEN their memory and resource growth are included

### Requirement: ELM-QA-024

WHERE GPU acceleration or a WebGPU renderer is proposed, the graphics verifier SHALL record the actual adapter, driver, backend, device capabilities and accelerated execution on the selected host and display.

#### Scenario: ELM-QA-024 qa-024

- GIVEN a host exposes WebGPU
- WHEN a preview workload runs
- THEN the actual hardware adapter and executed backend are evidenced

### Requirement: ELM-QA-025

WHERE a GPU renderer is selected, IF device loss or allocation failure occurs, THEN the native host SHALL cancel invalid work, retire owned resources and reconcile state without presenting stale frames.

#### Scenario: ELM-QA-025 qa-025

- GIVEN live GPU frame leases
- WHEN the device is lost
- THEN invalid frames retire and recovery uses reconciled native truth

### Requirement: ELM-QA-026

IF a proposed GPU path uses a software adapter or CPU fallback, THEN the qualification report SHALL label that execution as software and exclude it from GPU acceptance.

#### Scenario: ELM-QA-026 qa-026

- GIVEN software fallback after initialization
- WHEN performance is reported
- THEN the software run cannot claim GPU qualification

