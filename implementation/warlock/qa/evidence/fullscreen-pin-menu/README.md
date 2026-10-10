# Explicit fullscreen menu exit

Original ELM-REN-017 / ren-017 remains partial. In the two-root Wayland fixture, true fullscreen fills the output, pinned ordinary windows retain their native paint/hit/focus priority, and the owned shell bar uses the overlay layer so its window menu remains reachable. Floating MAX still respects the bar's exclusive band. Opening a context menu or focusing a pinned window does not exit fullscreen.

The negotiated **Exit fullscreen** item issues one typed desired-state operation through Elm's prepared menu and receipt router, the existing host journal, and the native geometry authority. It requires current native/client fullscreen modes and an eligible unpinned singleton family. Session locks, exclusive layers, seat grabs, drags, stale dependencies and unresolved operations retain their existing refusal/barrier protections. Native readback must confirm ordinary modes, unchanged focus, scope and peer state before Committed; uncertainty stays Unknown without replay.

The protected native runner records independent RGB captures, real GTK button press/release and focus above and outside the pinned window, read-only menu opening, disabled MAX/pin actions, enabled exit, exactly one committed exit, restored ordinary geometry and retained peer pin. Original MAX/pin checks and the unchanged direct-owner modal regression pass, including normal owned exits and strict cleanup. The owning core/ABI is unchanged; the plugin and host are rebuilt. See [manifest](manifest.json), [native report](native-fullscreen.json), and [modal regression](native-modal-regression.json).

Retained failures explain the changes: the old top-layer bar was covered by fullscreen, and the first overlay build exposed an omitted ExitFullscreen protocol mapping in ReceiptRouter. The corrected prepared-menu replay exercises that actual mapping. Compiler/fixture failures remain referenced by immutable local report hashes; both native failures and complete compressed logs are retained here.

quint-llm-kit guided the behavioral model and implementation: typecheck, ten explicitly selected named tests, positive committed/Unknown/pinned-focus witnesses and sampled safety traces run before and after source changes. Thirteen compiled Elm checks cover capability negotiation, eligibility, blocked and Unknown boundaries, receipt correlation and the full prepared-menu transaction. These results abstract one target and effect; they do not prove native clocks, ABI, actual locks/grabs or pixels.

Replay through the protected launchers, using a current participant record and exact owning pair:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B /home/hoskinson/window-integration-qa/qa_run.py -- /usr/bin/python3 -B /home/hoskinson/omarchy-windows-parity/implementation/warlock/qa/check-search.py --fullscreen-pin
python3 -B docs/warlock-build-loop/v2/loop.py --record .warlock-contributor/fullscreen.json native --runner /home/hoskinson/omarchy-windows-parity/implementation/warlock/qa/native-fullscreen-pin.py
```

Still required: independent disposition, wider fullscreen/unpin/allowed-over cells and modal/tiled/Xwayland families, real protected-input races, transformed/multiple outputs, native AT/IME, and the release-wide hardware/resource/package/rollback obligations. Neither this bounded journey nor a sampled model accepts the full requirement or release.
