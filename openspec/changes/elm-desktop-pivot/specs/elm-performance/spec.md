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

The graphics verifier SHALL record actual hardware adapter, driver, backend, capabilities and displayed acceleration for the selected shell webview; WebGPU availability and execution SHALL be reported separately.

#### Scenario: ELM-QA-024 qa-024

- GIVEN a host exposes WebGPU
- WHEN a preview workload runs
- THEN the actual hardware adapter and executed backend are evidenced

### Requirement: ELM-QA-025

WHEN a selected host GPU path suffers device loss or allocation failure, the native host SHALL invalidate rendering generations, retire invalid owned resources and reconcile current leases without presenting stale frames.

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

### Requirement: ELM-REV-020

The performance owner SHALL freeze a workload budget matrix covering cold startup, idle, catalog refresh, switcher open/navigation, minimized preview, first capture frame, reversible motion, output transfer and whole-process-tree soak.

#### Scenario: ELM-REV-020 revision-020

- GIVEN required workloads are inventoried
- WHEN P0 budget freeze runs
- THEN every listed workload has a measured baseline and missing rows block host selection

### Requirement: ELM-REV-021

The budget matrix SHALL record units, sample counts, device/output metadata, latency distributions, CPU, wakeups, memory, frame misses, power and copy/transfer costs, with numeric absolute and regression thresholds for applicable metrics and explicit justified exclusions.

#### Scenario: ELM-REV-021 revision-021

- GIVEN all workload rows exist but memory/copy/power thresholds are missing
- WHEN host selection reviews the matrix
- THEN incomplete applicable fields block admission; unsupported measurements need explicit scope justification

