# Reviewed source and role at the actual closed gate

This is a refinement of `ACTOR_LEDGER_CONTRACT.md`, before implementing its
source and role checks. The keeper observes the actual process image, sealed
handoff and producer descriptors, argv, environment and confinement. The sealed
handoff must have the exact reviewed source hash, and its real argument vector
must bind the declared target argv and descriptor numbers. A caller's digest of
an arbitrary confined script cannot substitute for reviewed handoff code.

An actual command recognized as a native effect or export cannot register as a
helper, renderer or CPU fixture. Conservative classification as native is allowed
for a CPU protocol refusal test: it grants no native result authority and cannot
attest until a separate durable semantic result exists. Registered renderer and
read-only helper roles still come from the authenticated service's known call
sites; this guard adds no general shell or IPC expression parser. It therefore
does not assert that every possible arbitrary command is read only. Cancellation
inspection will need a narrower explicit allowed argument vocabulary separately.

Malformed source, role or argument observation is refused before gate release.
The original strict Keeper cleanup remains; no selected actor or empty group
can turn that refusal into a native result. Current live API and restart handling
remain unimplemented. This protocol refinement makes no desktop acceptance claim.
