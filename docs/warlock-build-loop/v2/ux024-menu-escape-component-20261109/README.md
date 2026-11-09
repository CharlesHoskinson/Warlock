# Menu Escape component

Trusted Escape selects the enabled menu dismiss control when the current surface is a menu.
Other surfaces retain the existing close control.
The owner, publication and lease checks remain unchanged.
Keyboard dismissal uses the existing eligible-target return after a fresh observation.

| Protected observation | Baseline | Fixed source |
| --- | --- | --- |
| Elm modules compiled | 2 | 2 |
| Public setup checks | 5 passed | 5 passed |
| Escape cases | 9 passed, 7 failed | 16 passed |
| Existing menu DOM cases | 18 passed | 18 passed |
| Existing DOM assertions | 86 passed | 86 passed |

Both runs use the same fixtures and 119 recorded inputs.
Only `SurfaceController.elm` changes between the runs.
The source and actual results have independent reviews.
The fixed CPU route also passes 16 admission and result controls.
The baseline route passes 10 controls and fails six controls for the missing Escape API.

The compressed JavaScript files retain the actual compiled reducer images.
The raw reports retain commands, source hashes and observed effects.

This evidence establishes compiled component behavior.
It does not establish physical keyboard delivery, visible menu behavior or native focus return.
Original ELM-UX-024 remains partial.
The native preparation records the additional producer, keyboard emitter and focus integration work.
Original requirements, timing bounds and release gates remain unchanged.
