# Context-menu CPU replay

`fixtures.json` specifies externally authored lifecycle traces and expected
observable states/effects. `replay.cjs` drives a compiled Elm worker, with no
JavaScript reimplementation of the state machine. The worker invokes actual
`Menu.update`, records snapshots and emitted effects, and retains earlier menu
and intent identities so stale messages are genuinely replayed.

The fixture transport uses canonical decimal uint64 strings for external
identities. Counter/binding tests exercise the actual `UInt64` and `Binding`
decoders, including values above JavaScript's exact numeric range. Typed menu
construction is trusted adapter input; passing these tests does not certify a
native transport, provider authorization, identity acquisition, focus restoration,
geometry, accessibility, or right-click integration.

Run each script using the protected launcher:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  /home/hoskinson/window-integration-qa/qa_run.py -- \
  /usr/bin/python3 -B /absolute/path/to/qa/replay.py
```

The runner copies the exact input closure before compiling, records stdout,
stderr, command exits and hashes, and verifies that source stayed unchanged.
Failed runs remain intact. After a successful final source run, invoke
`qa/freeze.py` through the same launcher to freeze its report. The manifest
explicitly does not assert native GUI or complete feature acceptance.

`host_build.py` compiles the real `Main.elm`, bundled adapter, and native host,
then runs the host's asset and request-schema self-tests. `native.py` uses that
frozen build and the exact v23 compositor/plugin pair in a private session.
Run native campaigns serially. It checks actual pointer and keyboard input,
receipted minimize/restore, target retirement, and normal client/host teardown.

`model.py` typechecks and samples the approved Quint model; its named witnesses
are separate from the Elm fixtures and native evidence. `freeze_all.py` checks
all successful current source closures and records a combined immutable manifest
with separate scope statements. It never marks the whole feature accepted.
