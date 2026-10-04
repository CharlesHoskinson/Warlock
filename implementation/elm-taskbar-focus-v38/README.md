# Keyboard focus and bounded taskbar picker

Fresh V35 derivative fixes the grouped-render QA contract mismatch observed in V37:
the host now validates group counts rather than obsolete window-row counts. Picker
opening focuses the first available identity/revision/generation-bound control;
explicit dismissal restores the surviving scoped opener. Native selection and
scope changes do not restore the opener over application activation. Escape ignores
isComposing events. Compact layout exposes Close and two choices in the original
800x420 host; this is still an action-control prototype, not production bar geometry.

Optimized Main/native host build and host self-tests pass. Compiled replay passes
78 retained/scoped checks plus 20 picker controller checks. Quint executes eight
explicitly selected picker focus/lifetime scenarios and 1,000 invariant samples of
up to 40 steps. A Main precedence error and model reserved-name error are preserved
with frozen sources. The abstract model is not browser/native refinement proof.

Actual pointer/keyboard qualification is recorded separately in V39 (48 checks)
and V40 (61 checks), including normal host/backend exit and ordered cleanup. Full
IME/AT, native taskbar/popup/input lifetime, catalog/icons/pins/launcher, complete
scene, GPU/WebGPU, human UX, hardware/performance and release remain open. V40's
captured picker shows adjoining label/state text; spacing/reflow refinement is
pending. The live desktop is unchanged.
