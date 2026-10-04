# Output configuration and opener focus

A pending explicit picker-close focus return now captures the authoritative
output-configuration generation. It restores DOM focus only after matching
fresh facts on the same binding and generation, with an available opener group.
A generation change retires the return once, so later restoration of the old
configuration cannot revive it. The context.output field is a generation counter,
not a display identity. This is conservative topology invalidation; per-output
identity, surface roles, filtering, scale/transform and workarea remain open.

V107 compiles exact V106 production Elm (test-only SurfaceReplay observes saved
opaque timer tokens and focus effects). It preserves the 64 controller tests and
adds changed configuration, unavailable group and retired-focus revival cases.
67 controller/codec plus 12 presenter tests pass. V108 executes nine explicitly
selected Quint scenarios and 1,000 invariant samples. The abstract model and
compiled tests are distinct from native evidence.

Native campaigns retain the original 91 window checks, focused-grab refusal,
and bounded timeout/recovery prelude. An additive topology case stops only the
owned private broker after opening the picker, closes with real Escape, creates
a second actual nested Wayland output, verifies native generation change, resumes
the broker and checks the exact-publication DOM for cancelled opener focus. It
then explicitly removes the output. This tests real output lifetime and focus
invalidation; it does not qualify two physical displays or per-output desktop UX.

V109 created the second output and then failed a QA field lookup: outputGeneration
is on the authenticated response envelope, not its facts body. That packet and
normal cleanup remain preserved. V110 corrects only the lookup and strengthens
the DOM/publication correlation check. It retains the original helper deadlines.

No installed desktop or drafts changed. Full desktop, AT/IME/human UX, hardware
performance, WebGPU, compositor feasibility and coherent release remain open.
