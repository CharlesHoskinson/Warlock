# Native screen-coordinate shader capture

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

## Why
Native76 retains all1783 original controls,2216 total assertions and216 normal exits/clean teardown, then proves crop-local UV differs from actual output: preview21/28 vs compositor32/43 at the same root position. Identity/tint qualification cannot establish screen-coordinate fidelity.

## What Changes
Apply the actual static native shader in its output-sized texture/framebuffer coordinate domain, render only authorized family contributors, and export the exact independently owned crop after completion. Admit all nominal allocation phases under unchanged producer capacity before allocation; keep measured driver/GPU and full general shader release gates separate.

## Impact
Owning Renderer/OpenGL, matched native producer admission, real independent pixel qualification. No new Elm policy, GUI port/FD3 schema or public authority. Preserve failed derivatives and original clocks, source context, physical retirement and release requirements.
