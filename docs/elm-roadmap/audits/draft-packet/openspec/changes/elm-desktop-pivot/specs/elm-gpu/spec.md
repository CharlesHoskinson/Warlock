# elm-gpu

## ADDED Requirements

### Requirement: ELM-GPU-001

The Elm desktop SHALL require measured hardware-accelerated rendering in the selected native host before host selection and accelerated release admission.

#### Scenario: ELM-GPU-001 gpu-001

- GIVEN a candidate pinned host on the target machine
- WHEN host selection evaluates rendering
- THEN software-only execution cannot pass the GPU gate

### Requirement: ELM-GPU-002

The graphics qualification SHALL distinguish hardware discovery, native GPU rendering, accelerated webview composition and WebGPU adapter/device execution as separate evidence claims.

#### Scenario: ELM-GPU-002 gpu-002

- GIVEN Vulkan enumerates physical devices
- WHEN the inventory is recorded
- THEN WebGPU and displayed-render verdicts remain unproven until their probes pass

### Requirement: ELM-GPU-003

WHEN WebGPU is evaluated, the native host SHALL expose bundled assets through a qualified secure local origin without disabling renderer sandboxing.

#### Scenario: ELM-GPU-003 gpu-003

- GIVEN a local shell asset bundle
- WHEN the host loads its GPU probe
- THEN the probe uses the approved secure origin and the renderer sandbox remains enabled

### Requirement: ELM-GPU-004

WHEN a WebGPU adapter or device is unavailable, the host SHALL reject WebGPU qualification and preserve an accepted alternative hardware-rendering route.

#### Scenario: ELM-GPU-004 gpu-004

- GIVEN an accepted native GPU path and a WebGPU probe
- WHEN requestAdapter returns null
- THEN WebGPU is unqualified while the native GPU path remains usable

### Requirement: ELM-GPU-005

The WebGPU qualification SHALL verify a deterministic render and compute result using supported adapter limits and features and independently observe the native displayed frame.

#### Scenario: ELM-GPU-005 gpu-005

- GIVEN a nonsoftware adapter and accepted device
- WHEN the deterministic workload completes
- THEN known results match and the rendered native frame is independently observed

### Requirement: ELM-GPU-006

WHILE GPU effects are active, the renderer SHALL own GPU objects locally and keep per-frame pixel buffers outside Elm port messages.

#### Scenario: ELM-GPU-006 gpu-006

- GIVEN an Elm view with a GPU effect
- WHEN motion is sampled for successive frames
- THEN ports carry bounded control metadata and GPU objects remain renderer-owned

### Requirement: ELM-GPU-007

WHEN the GPU device is lost, the host SHALL invalidate dependent resources and the rendering generation before rebuilding them without replaying stale application-window effects.

#### Scenario: ELM-GPU-007 gpu-007

- GIVEN GPU resources and an old pending window intent
- WHEN device loss occurs
- THEN old resources become unusable and the old intent is not automatically committed

### Requirement: ELM-GPU-008

The preview qualification SHALL measure actual native-buffer import, synchronization and copy volume instead of inferring zero-copy support from WebGPU availability.

#### Scenario: ELM-GPU-008 gpu-008

- GIVEN a native frame lease and a WebGPU-capable host
- WHEN a preview is rendered
- THEN the report records actual copies and fences without claiming an untested DMA-BUF import

### Requirement: ELM-GPU-009

IF every qualified GPU path becomes unavailable, THEN the host SHALL expose essential recovery controls in a disclosed degraded mode and block accelerated release admission.

#### Scenario: ELM-GPU-009 gpu-009

- GIVEN all GPU backends unavailable
- WHEN recovery mode starts
- THEN essential controls remain accessible and the report identifies software/degraded execution

### Requirement: ELM-GPU-010

The GPU qualification SHALL compare integrated and discrete execution, where selectable, against frozen latency, memory, power and transfer budgets on the actual output configuration.

#### Scenario: ELM-GPU-010 gpu-010

- GIVEN Intel and NVIDIA devices in the inventory
- WHEN qualified selectable profiles are compared
- THEN each profile identifies the actual device and measured workload verdict

