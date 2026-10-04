# Persistent build loop

The active automatic goal builds and qualifies the replacement Elm desktop through
the existing S01–S16 work packages and the additive right-click contract. Optional
C00–C06 compositor work retains its feasibility and go/no-go gates. The frozen
242 baseline requirements and 417 scenarios stay unchanged; component passes do
not imply a completed work package.

Automatic continuation is supplied by the active goal in the current AI session.
The repository coordinator records durable checkpoints and serializes native QA.
It does not start another AI process, call a model API, or run a timed daemon.
Closing the client or disabling its goal can stop hosted continuation. A new
session resumes from the roadmap, checkpoints, and current source/evidence.

## Every iteration

1. Read `AGENTS.md`, this document, the primary delivery loop state, and the latest
   checkpoints. Inspect current branch, working tree and concurrent work before
   choosing a source directory. Preserve other workers' files and frozen evidence.
2. Select the smallest unblocked feature with a concrete behavioral oracle and
   its original scenario identities. Acceptance prerequisites constrain completion;
   independent prototypes may proceed while other gates remain open.
3. Record the chosen slice and next work. Use a fresh derivative and stable
   interfaces. Parallelize independent implementation, fixtures and review;
   assign one owner to each source path. Keep native GUI campaigns serial.
4. Implement and review. Compile the actual changed program. Run applicable
   typed decoder/replay/fuzz tests and explicitly selected Quint scenarios. Get
   any model review required by an invoked skill before changing its logic.
5. Run required native tests on the owning source/ABI tuple, through the native
   lock wrapper and unchanged protected launcher. Preserve deadlines, input
   recipients, pixels, receipts, normal exits and ordered cleanup. A busy native
   slot is a scheduling conflict; continue independent CPU work.
6. Fix failures in a fresh, reviewable derivative. Retain every failed attempt.
   When checks pass, freeze source/build/evidence, update the checkpoint and
   commit only owned paths. Record bounded acceptance and remaining gaps.
7. Advance immediately to the next unmet slice. A status request receives a
   brief answer while work continues. Stop only for explicit pause/cancellation,
   a required external approval/input, a budget limit, or an actually exhausted
   blocking condition under the active goal's rules.

## Persistent state and coordination

`delivery/loop-state.json` is the existing primary integration lane. Preserve its
owner's updates. Each thread appends immutable checkpoints under
`delivery/build-loop-events/`; do not replace another thread's checkpoint or
infer current execution from an old `active` label. The coordinator's `status`
command prints the integration state and each thread's latest checkpoint.

The current additional goal is identified by thread
`01a101d3-cde7-7370-83b1-3170bdd0c9d1`. Its first independent feature lane follows
the tested `elm-context-menu-v1` into menu gesture/dismissal/delegation and
resource-bound work. The other integration lane is building the shared bar/popup
controller. Integrate their interfaces only after reviewed native source closure;
avoid a second authoritative desktop policy model.

Native campaigns use:

```bash
/usr/bin/python3 -B implementation/elm-build-loop-v1/loop.py native \
  --runner /absolute/path/to/reviewed/qa/native.py
```

The wrapper holds a shared per-user kernel lock across repositories and worktrees while the unchanged
`qa_run.py` launcher and its child finish. A second wrapper refuses immediately.
An already running protected campaign also prevents a new launch. All workers
must adopt the wrapper: scanning existing processes cannot prevent a new direct
launcher from racing after that scan. Do not edit the protected launcher or
replace its scope, core limit, parent-display, private-runtime and teardown rules.

For continuation:

```bash
/usr/bin/python3 -B implementation/elm-build-loop-v1/loop.py status
```

Checkpoint examples and verified command interfaces are in
`implementation/elm-build-loop-v1/README.md`.

## Completion gate

Review all mandatory baseline scenarios and the right-click amendment with their
applicable evidence. Close original restore, input, popup, renderer, hardware,
output, accessibility/IME and representative user-journey obligations on one
coherent release tuple. Include measured resource/performance budgets,
failure/recovery, reversible deployment and integrated user-flow verification.
Human/device-dependent gates remain explicit until actually performed.

Prepare deployment and rollback artifacts before any required session-activation
approval. Never restart the main compositor or close the user's drafts incidentally.
Only then mark the automatic goal complete. Component/test counts alone cannot
complete the goal.
