# Taskbar keyboard context entry

Current enabled taskbar groups and pins emit a keyboard context request for ContextMenu or Shift+F10.
The context request uses a separate opaque codec.
The display checks the current publication, lease and bar membership before dispatch.
Ordinary click actions keep their existing codec and behavior.

| Protected observation | Baseline | Fixed source |
| --- | --- | --- |
| Elm modules compiled | 3 | 3 |
| Context cases | 23 passed, 11 failed | 34 passed |
| Context assertions | 38 failed | 503 passed |
| Reproducible keyboard samples | 32 executed | 32 passed |
| Existing menu DOM cases | 18 passed | 18 passed |
| Existing DOM assertions | 86 passed | 86 passed |
| Existing Escape cases | 16 passed | 16 passed |

The seed inventory is 0 through 31. Five samples allow a context request and 27 refuse one.
The checks observe actual HTTP requests from compiled HttpBar callbacks with controlled DOM and HTTP inputs.
They cover current groups and pins, zero lease, full-width counters, detached stale callbacks, modifiers, IME, repeats and transport failure.
The two runs use byte-identical fixtures and 120 bound inputs.
Only CapturedAction, Presentation and SurfaceRenderer change between the runs.
The fixed harness also passes all 22 admission and result controls.
Independent source and result reviews bind the actual reports.

The compressed files retain the actual compiled images.
The reports retain source hashes, requests, seeded events and assertions.

This evidence establishes compiled component behavior.
It does not establish native keyboard delivery, backend menu opening or physical focus return.
Original ELM-UX-024 remains partial.
A genuine taskbar window producer and GTK menu focus integration remain required.
Original requirements, native timing bounds and release gates remain unchanged.
