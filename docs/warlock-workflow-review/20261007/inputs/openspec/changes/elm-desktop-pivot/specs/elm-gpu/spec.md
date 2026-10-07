# elm-gpu

## ADDED Requirements

### Requirement: ELM-GPU-001

The host selector SHALL require hardware-accelerated rendering by the shell webview’s own nonsoftware backend before host selection and accelerated release admission, separately from native preview or WebGPU execution.

#### Scenario: ELM-GPU-001 gpu-001

- GIVEN a candidate pinned host on the target machine
- WHEN host selection evaluates rendering
- THEN software-only execution cannot pass the GPU gate

#### Scenario: ELM-GPU-001 software-webview-native-gpu

- GIVEN webview uses software while a native Vulkan preview uses NVIDIA
- WHEN accelerated host admission runs
- THEN the webview acceleration gate fails despite a GPU-accelerated preview

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

WHEN a WebGPU adapter or device is unavailable, the host SHALL record WebGPU as unqualified and continue evaluation of alternative hardware paths; host selection SHALL remain blocked until at least one complete webview hardware path qualifies.

#### Scenario: ELM-GPU-004 gpu-004

- GIVEN an accepted native GPU path and a WebGPU probe
- WHEN requestAdapter returns null
- THEN WebGPU is unqualified while the native GPU path remains usable

#### Scenario: ELM-GPU-004 first-webgpu-evaluation

- GIVEN no path has qualified yet and WebGPU returns no device
- WHEN host comparison continues
- THEN WebGPU is unqualified, alternative probes continue, and no accelerated host claim is made prematurely

### Requirement: ELM-GPU-005

WHEN WebGPU evaluation obtains a nonsoftware adapter and device, the host SHALL verify deterministic render and compute results against supported limits and features and independently observe the native displayed frame.

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

WHEN any GPU device used by shell composition or preview import is lost, the host SHALL invalidate its dependent objects and rendering generation and revalidate current lease identity, output and scene state before new presentation, without replaying stale window effects.

#### Scenario: ELM-GPU-007 gpu-007

- GIVEN GPU resources and an old pending window intent
- WHEN device loss occurs
- THEN old resources become unusable and the old intent is not automatically committed

#### Scenario: ELM-GPU-007 gpu-loss-stale-lease

- GIVEN a retained historical frame belongs to an earlier application state
- WHEN the GPU device is lost and resources are rebuilt
- THEN the old image is not labeled current live content; publication requires a revalidated lease or explicit unavailable state

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

### Requirement: ELM-REV-019

IF device loss invalidates the only accepted storage for a retained frame, THEN the broker SHALL atomically revoke and retire that lease and publish an explicit unavailable-preview state rather than reuse invalid objects or label historical pixels as current.

#### Scenario: ELM-REV-019 revision-019

- GIVEN a source-stop frame has only storage on the lost device
- WHEN device loss invalidates storage
- THEN the lease is retired with unavailable outcome; valid independent copies may be revalidated under fresh publication authority

### Requirement: ELM-REV-022

IF preview copy volume, acquire-fence wait or cross-GPU transfer exceeds its frozen budget, THEN the preview qualification SHALL reject that import route and preserve a qualified native route or an explicit unavailable state.

#### Scenario: ELM-REV-022 revision-022

- GIVEN DOM hardware qualifies but full-frame cross-GPU imports exceed budget
- WHEN preview qualification runs
- THEN the expensive route is refused; merely recording copies cannot qualify it

### Requirement: ELM-REV-025

WHEN the active adapter, driver or engine differs from its qualified tuple, the host SHALL invalidate that acceleration verdict and require matching qualification before presenting the configuration as an accelerated release.

#### Scenario: ELM-REV-025 revision-025

- GIVEN NVIDIA profile is qualified but a later launch chooses Intel
- WHEN runtime tuple is compared
- THEN only a matching qualified Intel tuple can receive an accelerated verdict

