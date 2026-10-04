# Held-key loss acceptance

AQ138 changes only Wayland.cpp relative to frozen AQ120. It records admitted
bounded key transitions in private event-loop state, refuses duplicate/unpaired
transitions, fences late events from failed or retired devices, and cancels held
keys before keyboard retirement. Cancellation clears records before callbacks,
retains a strong keyboard snapshot, and resets recorded modifiers after key
releases. Public headers and every prior exported symbol survive the complete
Release build. Existing pointer cancellation and transport/output/poll fences
remain. The owning native tuple is Core89/plugin90 where applicable/AQ138.

Actual C++ key admission/cancellation/destructor passed 2,735 checks and seven
compiled mutation controls, including all 768 slots, modifier-only cancellation,
callback reentry and multiple retained devices. Original pointer helper152/5 and
transport replay63/7 pass. The transport fixture uses typed no-op cancellation
stubs; actual helper and native wiring evidence are separate. Quint models one
keyboard and two abstract key identities: ten explicitly selected scenarios,
1,000 traces of at most40 steps and seven typechecked mutation controls pass.
It does not prove C++ callback lifetime, 768-slot refinement or modifier semantics.

The new private protocol6 fixture holds real keys and destroys only the exact
PID/start-identified focused child Wayland connection before balancing parent
keys. Observer132 reads owning public Core input/modifier getters and the public
shortcut ledger; it never mutates state. The exact GTK window independently
records physical key events and hardware code joins. Parent admission alone is
never a delivery receipt. A/Shift/both cancellation passes with the original
six-second deadlines, empty Core input/shortcut ledgers, zero modifiers, exact
single GTK releases, retired devices/output/kernel poll source, no stale later
delivery, and normal ordered shutdown. Pointer focus may remain on the live
GTK surface; no focus-clearing claim is made.

Native check executions: unchanged original held-key oracle147=37; three masks
148=114; input141=159; geometry142=96 (seven pixel stages); unheld-loss143=26;
all-three-pointer-buttons144=35. Total467 repeated check executions, not unique
scenarios or completed roadmap requirements. Regression runners retain old
baseline scope strings; frozen descriptors and actual mapped-library hashes
identify AQ138. Masks148 add the pre-fault Shift modifier assertion only.

Failure history remains:133 interactive whitelist refusal with cleanup;134
missing descriptor before private launch;135 actual AQ120 stale input/shortcut
failure with normal cleanup;136/137 mutant runner matching failures with passing
candidate bodies/model scenarios;139 verified cancellation but later parent key
admission refusal and failed normal-cleanup classification (all processes later
gone and runtime removed).145 compiled fixture correction is superseded by146,
which resets post-loss permission per exclusive controller.147 preserves135/139
native runner byte-for-byte and binds146.140 was prepared but never run.144
preparation error is recorded as an observed summary, not raw stderr.149's first
dispatch stopped on busy75 after mask1 passed; the later dispatch skipped that
completed case and passed the remaining cases. No native failure was retried
under the same frozen source root.

Next: qualify held-key keyboard-capability removal, ordinary keyboard focus
leave/enter and multiple-device ownership; review/adopt AQ138 in the shared GUI
integration lane. Full S01-S16/C00-C06, accessibility/IME, GPU/device/human and
resource gates, integrated user journeys, deployment and rollback remain open.
Nothing was installed or activated on the main desktop. Hosted automatic goal
still reports paused; `/goal resume` or the progress-row Resume control is needed
to enable later automatic turns. Session implementation has continued.
