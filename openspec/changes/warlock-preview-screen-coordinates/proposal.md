# Native screen-coordinate shader capture

## Why
Native76 retains all1783 original controls,2216 total assertions and216 normal exits/clean teardown, then proves crop-local UV differs from actual output: preview21/28 vs compositor32/43 at the same root position. Identity/tint qualification cannot establish screen-coordinate fidelity.

## What Changes
Apply the actual static native shader in its output-sized texture/framebuffer coordinate domain, render only authorized family contributors, and export the exact independently owned crop after completion. Admit all nominal allocation phases under unchanged producer capacity before allocation; keep measured driver/GPU and full general shader release gates separate.

## Impact
Owning Renderer/OpenGL, matched native producer admission, real independent pixel qualification. No new Elm policy, GUI port/FD3 schema or public authority. Preserve failed derivatives and original clocks, source context, physical retirement and release requirements.
