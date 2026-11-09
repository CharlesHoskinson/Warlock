# Menu host focus intent parser

The host selects the current menu-close control as a Popup focus destination when keyboardParent is explicitly true.
The existing owner, lease, unique eligible target and no-repeat checks remain unchanged.
Pointer or missing keyboard-parent metadata does not activate this menu destination.

| Protected observation | Baseline | Fixed source |
| --- | --- | --- |
| Fixed targets compiled and linked | 2 | 2 |
| Builder controls | 11 passed | 11 passed |
| Allocation-only result | Fails first new menu assertion | PASS |
| Owner executable run | No | No |
| Forced cleanup | No | No |

The unchanged test source adds 13 menu parser checks and 32 literal-seed transition cases.
The baseline exits at the first new assertion, so it does not execute every later new check.
The fixed allocation-only branch reaches its final PASS after all controls.
This is one completed control-program execution, not per-control output telemetry.

Only Mvp changes among the 257 Haskell files and 11 support inputs.
Managed admission binds 270 inputs, including packet metadata.
Both runs use the same fixture, compiler, SDK, loader proof, runners, authorization and bounds.
The baseline build packet is preserved byte-for-byte before the fixed working packet binds the Mvp change.
Independent source and actual-result reviews bind these observations.

This evidence establishes parser and transition behavior in the compiled control program.
It does not establish physical GTK focus, DOM focus, a genuine window provider, native cleanup or original UX024 acceptance.
The raw cleanupQualified false field remains unchanged.
The GUI owner and native observer do not execute in this qualification.
