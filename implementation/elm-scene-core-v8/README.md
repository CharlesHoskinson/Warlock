Native inactive-special-workspace renderer exclusion

V7 captured an inactive special-workspace window with permissive fullscreen
flags: native general visibility returned false but owning-monitor visibility
returned true. This derivative repairs that predicate disagreement before any
pin/fullscreen/animation precedence. One helper checks that a special workspace
is currently active on the window's owning monitor. Both `shouldRenderWindow`
overloads use it, and the live `renderWindow` entry point applies it as well so
specialized passes cannot skip the exclusion. Ordinary workspace behavior and
the previous floating-MAX stack correction remain unchanged.

Standalone captures retain their separate existing route. They are not live
application rendering. Complete preview authorization, retained-family motion,
first-class minimization and native canonical scene transactions remain open
requirements; this guard does not replace them.

The fresh core recompiles only the renderer and replaces its object in a copy of
the previously accepted archive, then links a new executable. Previous binaries,
archives and owning ABI headers are preserved. The new read-only diagnostic
plugin is compiled against those exact headers and paired with this actual core
binary. Renderer compiler dependencies and plugin compiler dependencies are
rechecked at packet freeze. The QA builder now excludes receipt JSON from source
inputs so writing the final receipt cannot invalidate its own input closure.

`build-1791053548003608844/report.json` records successful compile/archive/link
with 870 compiler dependencies. `qa/build-1791053748917182207/report.json` records
the fresh plugin/Elm build and observer/model replay checks.
`qa/native-1791053782972224071/report.json` passes 33 private diagnostic/observer
checks. The genuine silent move to an inactive special workspace retains
`allowedOverFullscreen=true` and `renderOverFullscreen=true`, while **both**
renderer predicates now return false. Return to original workspace membership,
fresh remap incarnation, peer/binding refusal and clean clients-first teardown
pass. The first failed preflight ran before any private compositor was launched;
its report is retained.

This establishes an actual repaired native predicate on an exact compiled tuple.
It does not prove all displayed pixels, actual pointer targets, modal redirection,
effect paths or Brave/Heroic release behavior. The next native fixtures must
exercise those behaviors, rerun original MAX/family regressions and integrate
complete authenticated native scene observations with Elm admission. The live
desktop and staged deployment wiring have not been changed.

Protected commands, in order:

```
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-core-v8/build.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-core-v8/qa/build.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-core-v8/qa/scene_native.py
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/elm-scene-core-v8/qa/freeze_core.py
```

The core package selector is pinned to this particular build; use a fresh
derivative for subsequent source/build changes. Freeze verifies that selected
core, source and diagnostic receipts describe this same tuple.
