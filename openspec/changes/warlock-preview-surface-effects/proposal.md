# Track every owned native surface background effect

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

## Why

The qualified root effect tracker cannot describe preferences/regions on a root's native subsurfaces and popups. The owning renderer reads each surface wrapper's effect facts. Copying only root facts can leave a capture context current across changes to another participating surface. Native tree identities must survive value copying without treating addresses as stable identities.

## What Changes

Extend immutable family style facts to all rows in the validated native root/subsurface/popup trees, using existing owner-scoped native incarnations and exact region values. Cap aggregate256 surfaces/4096 rectangles before copying. Add authenticated, bounded QA-only readonly fact projection for actual native qualification; normal typed GUI scope and FD3 wire shapes remain unchanged, one Elm policy remains authoritative and product diagnostic export015 stays deferred.

Preserve frozen242/417, separate24/48, original preview13/restore38/recovery34/drag52, all identities/oracles/deadlines and conditionalC00–C06. Native backdrop pixels/blur, output/hardware and full release acceptance require separate proof.

## Capabilities

### Modified Capabilities

- `elm-capture-motion`: additive full-tree renderer-fact identity and qualification refinements under the existing in-flight capability.

## Impact

Immutable C++ snapshots, explicitly selected Quint/implementation replay, native tree identity observer/collector, QA protocol fixture and readonly inspector. No installed desktop changes or new frontend/native GUI policy.
