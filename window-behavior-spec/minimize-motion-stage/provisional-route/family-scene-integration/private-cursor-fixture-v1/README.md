# Private cursor fixture proposal

Use this exact private-nested.lua in a fresh root-owned private raster fixture.
Before producer launch, call require_invisible_private_cursor(session) and retain
the returned actual getoption record. After its backendObserved/outputs events,
call require_deterministic_owned_raster(observer.rows) and retain the actual
rasterState event. Use the paired fresh producer-checkpoint-v2.json launch.
All V3 image comparisons, complete output fields, source hashes, normal exit,
clients-first private cleanup and15 main read-only preservation gates remain.
No pixel region, alpha component or tolerance is excluded/changed. This module
never establishes a private session or talks to the main compositor on import.
The coordinating root owns the runnable host/config/manifest integration; this
is a source-reviewed fixture component, not a self-contained native test runner.

Source: exact Hypr commit efb50993780079460b0cbed1363e2166a2de1d9f,
ConfigValues.cpp588; Renderer.cpp2914–2964 including resetCursorImage.
Hyprland's official variables documentation describes cursor.invisible as no
cursor rendering: https://wiki.hypr.land/Configuring/Basics/Variables/ .
Actual native option and full raster remain untested for this fresh candidate.
