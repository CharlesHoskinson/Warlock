# Parent cursor V15 native qualification

The protected native campaign passed 76 checks with normal ordered cleanup on the
frozen V8 core/plugin/Aquamarine tuple and V10 parent-input module, through the V13
reviewed host. No desktop activation or installed configuration change occurred.

A real GTK application provides a Cairo cursor of 24×20 logical pixels with a
(7,5) hotspot and distinct magenta/cyan colors. Scale-aware cursor surfaces are
observed in the actual parent Weston framebuffer through its capture protocol.
Private Weston alone uses `--debug` for capture authorization, inside the protected
UID-owned runtime. Capture-tool hashes and normal exits are retained. The main
compositor receives no capture/debug change.

All four modes passed actual parent cursor bounds, hotspot within two parent
pixels (including bilinear edge rounding), exact GTK press/release recipients,
and custom-to-transparent cursor removal. Observed bounds:

| Child mode | Scale | Parent cursor bounds (left, top, right, bottom) |
| --- | --- | --- |
| 800×600 | 1 | 267, 202, 291, 222 |
| 640×480 | 1 | 267, 203, 296, 227 |
| 960×640 | 2 | 267, 204, 306, 241 |
| 800×600 restored | 1 | 267, 202, 291, 222 |

The stretched cursor proves actual fallback pixels at each tested mode after an
application cursor replacement. It does not yet prove an existing cursor survives
geometry changes without replacement, rotation/multiple outputs, capability loss,
physical hardware, accessibility/IME, or the full release acceptance gate.

Source and evidence: `implementation/elm-parent-cursor-v15/qa/slice-manifest.json`.
Native report: `qa/native-1791095594826501191/report.json` under that slice.
