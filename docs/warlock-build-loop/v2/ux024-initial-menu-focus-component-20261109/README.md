# Initial keyboard menu focus

A successful new keyboard menu opening emits one typed Focus for its current close control.
The request travels with the same current projection commit.
Pointer openings, refused openings and duplicate openings do not emit this focus.
The deferred eligible taskbar return remains unchanged.

| Protected observation | Baseline | Fixed source |
| --- | --- | --- |
| Elm roots compiled | 4 | 4 |
| Initial-focus checks | 13 passed, 4 failed | 17 passed |
| Public setup checks | 5 passed | 5 passed |
| Public event sequences | 32 executed, 4 failed | 32 passed |
| Existing DOM cases and assertions | 18 and 86 passed | 18 and 86 passed |
| Existing Escape cases | 16 passed | 16 passed |
| Existing context cases and assertions | 34 and 503 passed | 34 and 503 passed |

The 32 literal seeds cover eight public sequence classes.
The same fixture checks exact current menu identity, effects and registered commit focus.
Only Desktop changes among 122 bound inputs between the two runs.
The fixed harness also passes all 28 admission and result controls.
Independent source and execution reviews bind the raw reports and compiled images.

This is compiled Elm component evidence.
It does not establish GTK handoff, physical DOM focus or original UX024 acceptance.
The Haskell menu parser remains unchanged during this phase.
The genuine taskbar observation producer and original native journey remain required.
