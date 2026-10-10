# Single-family taskbar native accessibility

Actual private GTK/WebKit AT-SPI and Orca now qualify the focused single-family Activate/Minimize/Restore fixture. Five real AT-SPI press actions each commit once, with native focus, MRU/desktop succession, client keyboard recipients and painted/absent application frames preserved. A separate physical-Enter journey passes under actual AT observation. All current taskbar names, native active toggle states and focused controls agree with Orca; the real reader emits Activate/Minimize/Restore names. This verifies existing product behavior; no production code or ABI was changed.

[Manifest](manifest.json) preserves exact original UI-004 identities, frozen policy, source/toolchain/core/plugin tuple, native AT action vs physical Enter provenance, actual trees/Orca observations, frames, failed reports and historical runner bytes. Every AT action targets exactly one visible/enabled/focused current taskbar control from the actual host PID. Existing native effect receipts, application key recipients, membership and MRU/desktop succession assertions remain unchanged.

The fixture waits for the required actual current native AT tree before sampling the physical frame. An AT-SPI Action acknowledgement is not a native paint acknowledgement. The earlier frame is retained; no original deadline was extended. The reader uses the existing extracted real Orca with silent speech output and a read-only observation getter; audible speech/braille and broad AT acceptance are not claimed.

- Independent original-scenario review against the exact source/ABI/toolchain and frozen policy remains open.
- This fixture covers focused current AT-SPI press and physical Enter, with silent Orca speech transcript observation. Audible speech, braille, unfocused/cached AT actions, broader AT modes, grouped/zero/refusal taskbar scenarios and other GUI surfaces remain separate obligations.
- Physical hotplug/AT/IME breadth, resource/journey budgets, reproducible package and reversible deployment/rollback remain release obligations.
