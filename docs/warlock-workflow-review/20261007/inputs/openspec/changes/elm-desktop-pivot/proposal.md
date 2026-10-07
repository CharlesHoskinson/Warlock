# Elm desktop pivot

## Why

The current desktop has unfinished Windows-style behavior and observed layering failures: maximized peers can disagree with visible stack order, and Heroic remains visibly covering the display after a minimize route while a terminal is active. The proposed Elm shell centralizes typed presentation/policy, but native window, capture and input authority still require explicit correction and acceptance.

## What Changes

- Draft a complete Elm shell roadmap, preserving existing native acceptance identities and deadlines.
- Define equivalent EARS and OpenSpec proposed behavior for host integration, event/intent/receipt authority, shell interaction, capture/motion, layering, GPU/WebGPU qualification, security, verification and delivery.
- Compare hardware-accelerated native webview hosts; qualify GPU execution in the actual host instead of assuming WebGPU from Vulkan availability.
- Study complete pinned Mutter/KWin source snapshots and scoped developer documentation to inform native architecture and layering.
- Include separately conditional feasibility and implementation for a native compositor with Elm policy. Retain Hyprland for mandatory initial shell delivery.
- Record model-specific independent audits and reconcile their findings before finalizing the plan.

No implementation or deployment is performed by this planning change. All implementation tasks remain unchecked.

## Capabilities

### New Capabilities

- `elm-accessibility`: Proposed acceptance contract for accessibility.
- `elm-capture-motion`: Proposed acceptance contract for capture motion.
- `elm-delivery`: Proposed acceptance contract for delivery.
- `elm-gpu`: Proposed acceptance contract for gpu.
- `elm-host`: Proposed acceptance contract for host.
- `elm-layering`: Proposed acceptance contract for layering.
- `elm-native-bridge`: Proposed acceptance contract for native bridge.
- `elm-native-compositor`: Proposed acceptance contract for native compositor.
- `elm-performance`: Proposed acceptance contract for performance.
- `elm-security`: Proposed acceptance contract for security.
- `elm-shell-experience`: Proposed acceptance contract for shell experience.
- `elm-switcher`: Proposed acceptance contract for switcher.
- `elm-taskbar`: Proposed acceptance contract for taskbar.
- `elm-verification`: Proposed acceptance contract for verification.
- `elm-window-policy`: Proposed acceptance contract for window policy.

### Modified Capabilities

None. There was no existing OpenSpec capability baseline. These draft additions are not archived into deployed truth before implementation acceptance.

## Impact

Planning artifacts and supporting offline research are added under `docs/elm-roadmap/`, `docs/research/elm-pivot/` and this change. Future implementation affects the native shell host, native authority, Elm assets and user-owned Omarchy integration. Full native compositor replacement is optional and separately scoped. The plan preserves archived proofs and excludes unrelated local native builds from the roadmap commit. No network publication is authorized.

## Verification

Run the local requirement/scenario/task/link verifier and pinned OpenSpec strict validation through protected QA orchestration. Four independent audits review a hashed draft packet; retain findings and dispositions. These checks qualify document structure and planning coherence, not GPU rendering, window behavior or implemented Windows parity.
