# Include actual background-effect protocol facts in family source identity

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

## Why

The owning ext-background-effect-v1 implementation sets a root wlSurface background-effect preference when get_background_effect is processed, before a buffer commit. Regions and removal are applied on later surface commits. Current source revisions account for buffers and native styling but omit that preference and exact regions. Snapshot family rendering explicitly disables background blur, so tracking facts alone cannot qualify complete background rendering.

## What Changes

Add value-owned native effect presence and exact normalized blur rectangles to content identity, including pending/applied protocol semantics, bounded storage and canonical unavailable recovery. Qualify creation, stable pending state, applied region/change/clear/removal on the exact owning tuple. Extend coverage to every participating root/subsurface/popup before production fidelity acceptance. Require real background-dependent blur evidence with exact source/privacy, clocks and physical ownership.

Preserve the one immutable Elm policy, frozen242/417, separate24/48, original preview13/restore38/recovery34/drag52, all identities/oracles/deadlines and conditionalC00–C06. No installed desktop configuration or session activation.

## Capabilities

### Modified Capabilities

- `elm-capture-motion`: additive renderer-input and actual background-effect fidelity refinements under the existing in-flight capability.

## Impact

Native collector, pure immutable C++ revision model and coupled selected Quint replay, actual protocol fixture, renderer/source qualification and typed capture contexts. Native facts are observations; they do not form another GUI policy.
