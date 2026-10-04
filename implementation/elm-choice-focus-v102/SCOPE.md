# Bounded choice wait and picker-close focus

The primary Elm Desktop remains the only interaction controller. A picker choice
retires its popup, requests authoritative post-close facts, and arms an opaque
binding/request token. Main schedules a two-second Process.sleep; a matching
ChoiceDeadline cancels the unsubmitted choice and publishes an accessible status
and explicit Refresh windows control. A later projection cannot submit that old
choice. Refresh obtains facts only: a new explicit choice is required. Older or
completed choice timers cannot expire a later choice. This is a prototype wait
budget, not a revision of inherited native deadlines or a full latency acceptance.

Explicit picker close now requests fresh facts before restoring DOM focus to its
newly scoped group opener. The previous immediate restoration could be lost when
a subsequent native focus revision disabled the old group button. Matching fresh
facts restore once; disconnect, binding replacement, another interaction, or a
missing group cancel the return. It does not request native application focus.
Cross-output focus policy remains unqualified; this candidate is single-output.

V104 compiles the exact V102 production Elm modules (test-only SurfaceReplay
adds saved opaque token and emitted-focus observations): 64 controller/codec
checks and 12 presenter checks. V102 builds optimized Main and Popup, retained
20 effect/27 shell checks, six host and four surface test groups. V99 choice
model passes 13 named scenarios/1,000 samples; V105 return-focus model passes
eight named scenarios/1,000 samples. These abstract models are not automatic
native refinement proofs.

V103 native campaign passes 99 checks on qualified V89/core-V23 tuple: original
91 preserved, focused-grab refusal, four timer/recovery assertions and three
extra owned pointer exits. The stopped broker resumes and its late snapshot
cannot emit the expired choice. Actual timer observation is 2.202 seconds.
All native clients/helpers/host/backend exit normally with ordered cleanup.

V96/V97 parser failures and V100 native focus failure are retained. V98 timeout
behavior alone is not full native regression acceptance. Full desktop, canonical
scene/output roles, actual AT/IME, human usability, hardware/resource budgets,
WebGPU, C00 feasibility and release/deployment remain open.
