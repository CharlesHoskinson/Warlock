# Applied shader inputs

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

## Why
Configured screen-shader paths cannot identify the successfully linked program: a disk edit without reload leaves old code active, and a same-path reload can apply different bytes. Source contexts must follow the actual owner program rather than filesystem reads.

## What Changes
Add bounded exact applied vertex/fragment facts from the owning renderer; immutable equality, canonical unavailable for unsupported contextual uniforms and coherent recovery. Qualify actual reload/disable/failure without buffer commits and refuse stale contexts before allocation. Retain every original scenario, deadline, physical ownership and the single Elm policy.

## Impact
Additive WRLK-SHADER001-004 contracts and private owning renderer/plugin/model qualification. Full shader pixels, background blur/privacy, transforms/output/hardware and all original GUI release gates remain open.
