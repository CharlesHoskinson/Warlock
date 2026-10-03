Authenticated native scene diagnostics

This derivative extends the V3 read-only plugin with `scene-facts-request`.
Requests use the same authenticated kernel-peer/session/frontend binding and
bounded JSON parser. Replies use `kind: scene-facts`, request correlation and
their own sequence/revision counters. They cannot be mistaken for observer
snapshots. Stable facts keep their revision while each request advances sequence.
Counter namespaces are distinct; diagnostic requests do not introduce gaps into
the original observer stream. The V3 hello capability object remains unchanged;
the frozen plugin tuple identifies this experimental diagnostic extension.

One synchronous compositor event-thread callback reads focused incarnation,
transient parent, raw window-vector position, workspace/monitor IDs, current
workspace visibility, hidden/pinned state, native fullscreen permissions,
input acceptance and both native renderer visibility decisions. Placement IDs
are signed decimal strings, separate from authority-bearing uint64 identities.
Minimized state remains explicitly unavailable. Native parent lookup failure
refuses the entire diagnostic rather than inventing independent ancestry.

Raw vector position is not final canonical paint order. `acceptsInput` is a
window predicate, not an actual coordinate hit result. These fields describe
current native behavior; they cannot bypass Elm V6 admission or qualify a native
scene. An inactive window retaining a permissive fullscreen flag is deliberately
preserved as a regression input. There are no native effects in this plugin.

Protected build and serialized native qualification:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-facts-v7/qa/build.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-facts-v7/qa/scene_native.py
```

`qa/native-1791053243616778513/report.json` passes 32 diagnostic/observer checks
with the exact compiled plugin loaded in its owning private compositor. The
original nullable-state Elm replay and observer model checks reran on this tuple.
Fixture remap creates a fresh incarnation; session and malformed-peer refusals
remain enforced. Fixture/helper retirement and clients-before-plugin-before-
compositor teardown pass. Main desktop actions are false.

The experiment also **finds a native eligibility failure**: after a genuine raise
and silent move to an inactive special workspace, `workspaceVisible=false` and
`shouldRenderAny=false` but `shouldRenderOwnMonitor=true`, while the original
fullscreen permissions remain true. The exact receipt is frozen in
`diagnosis.json`. Passing diagnostic collection does not accept that behavior.
Renderer exclusions across ordinary, fullscreen and effect paths remain a
blocking implementation/acceptance gate. No pixel exclusion, actual hit target,
modal family qualification or Brave/Heroic acceptance is inferred from these
read-only predicates. The next derivative must repair and exercise that native
behavior, then admit coherent complete-scene observations into Elm.
