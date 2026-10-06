# Explicit owned backdrop and native live blur

## Why

Native84 proves that copying blur configuration is insufficient: all76800 native body pixels change with blur brightness while isolated family pixels remain unchanged. Simply enabling snapshot blur could expose monitor cache pixels belonging to other windows.

## What Changes

- Add an explicit family-over-native-generated-color projection with owned full-output source and two private scratch buffers.
- Copy generated-color facts into the existing immutable source epoch and require exact source/clock/deadline/admission checks.
- Separate transport using authenticated typed scope/capture/state/retire kinds, FD4 plane256 and owning metadata/physical mapping.
- Preserve original transparent captures and bounded status; require original full GUI regression plus independent exact native pixel proof.

## Impact

Additive contract to original preview and resource/privacy requirements. Frozen242/417 and right-click24/48 remain unchanged. Arbitrary authorized backdrop dependencies, full renderer/color/hardware/resources and coherent release remain open.
