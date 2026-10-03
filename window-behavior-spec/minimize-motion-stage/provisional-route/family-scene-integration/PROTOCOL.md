# Composite owned-renderer protocol, implementation candidate 1

This producer is staged only. V4 remains the frozen single-window native candidate.
All commands are bounded JSON lines over one persistent private pipe. The service
owns the connection; it reads events continuously and never blocks rendering on
native metadata. No command can directly operate a native window.

`seed`: scene `token`, `operation` (`minimize`/`restore`), `durationMs`, output
`[{name,generation}]`, and ordered `members[]` (1–64). Each member carries
`stableId`, integer `pid`, immutable SHA256 `digest`, private PNG `path`,
`nativeRect`, decorated `atlasRect`, retained `iconRect`, nonnegative `insets`,
`pixels:[width,height]`, and `captureScale`. Rectangle fields are numeric
`x,y,width,height`. Duplicate stable IDs are rejected even with different PIDs.
Total decoded RGBA is at most 256 MiB. Sources are decoded/uploaded once per seed.
The ordered immutable source vector is part of every submitted scene record.

`retarget`: greater same-session scene `token`, exact ordered `identities[]`
`[{stableId,pid}]`, `operation`, and `durationMs`. It immediately retires prior
native authority, drains outstanding own presentation feedback, then reverses
from each output's *actually presented complete scene*. Sources and latched icon/
atlas endpoints are reused. No family query, screenshot, texture upload or Qt IPC
runs in this path. Latest accepted retarget owns cancellation and validation,
including while prior feedback is pending. Shared progress is sampled once per
render batch; origins may differ by output because presentation is asynchronous.

`validate` and `start`: exact scene `token` and ordered `identities[]`. Validation
is a service assertion that fresh exact client/native coverage, selected family
edges, geometry, output generations and policy passed. The renderer accepts only
the complete current source vector, and cannot grant authority to a partial or
reused identity. `start` additionally requires actual current complete readiness
on all required outputs. Provisional retarget motion begins before validation;
unvalidated endpoint feedback remains visual evidence only.

`cancel`: latest accepted scene `token` and ordered `identities[]`; stale cancels
cannot destroy a newer scene. `stop`, `state`, and `prepareOutputs` retain V4
lifecycle semantics. Output removal, failed swap, discard, deadline, EOF or policy
cancellation destroys the entire scene's surfaces and retires authority.

Events `seeded`, `retargetAccepted`, `retargeted`, `ready`, `endpoint`, `swap`,
`presented`, `cancelled`, `state` carry scene token and the exact identity vector.
Every swap/presentation record carries complete ordered `members[]` with each
`stableId,pid,digest,rectangle`; one output/generation/local sequence/submission
and actual presentation timestamp belongs to that immutable composite record.
Ready/endpoint require promotion plus complete scene feedback on every output.
No assigned digest alone proves pixels; full-raster native evidence is separate.

Current staged restriction: fresh attachment/detachment or geometry drift cancels
and settles safely rather than silently changing membership. Atomic replacement
scene preparation while old pixels continue moving is a following integration
step. Native controller acceptance, callback locking, per-member commits,
reduced-motion settlement and journal recovery remain service responsibilities.

## Independent native raster fixture

Launch the same binary with `--raster-fixture` only for pixel inspection. `seed`
uses the identical decoder/texture/draw path. `sample` requires exact current
`token`, complete `identities[]`, and finite numeric `progress` in [0,1], and
holds that progress across subsequent complete commits. `presented`/`state`
identify the exact ordered member rectangles rendered on each output. The mode
rejects `validate`/`start` and suppresses all native readiness/endpoint authority.
This permits an independent full-raster oracle to observe a stable interior
scene; it proves pixels only. Continuous production cadence is measured separately.

For each member, PNG RGBA8 c,a becomes premultiplied integer `(c*a+127)/255`.
Textures use GLES2 `GL_RGBA, GL_UNSIGNED_BYTE`, linear min/mag filters and clamp
to edge. Quad vertices map the requested global rectangle into output NDC using
logical output extents; UV (0,0) is its top-left, (1,1) bottom-right. The fragment
shader uses mediump interpolation and `texture2D`. Members are drawn in array
order onto transparent clear with `GL_ONE, GL_ONE_MINUS_SRC_ALPHA`. EGL requests
8 bits for all RGBA components; no sRGB conversion is requested. Fractional
buffer size is `ceil(logical extent * preferredScale)` and viewporter destination
is exact logical extent. Output transform is applied by the compositor. An
independent reference must account for hardware bilinear/UNORM quantization; the
producer does not claim a CPU reference is universally bit-identical on every GPU.
There are no excluded pixel regions in the proposed oracle.

Every existing `swap` event adds batch/draw-start/draw-done/swap-entry/swap-return
and last frame-callback monotonic clocks. `presented` adds callback delivery time
separately from actual wp_presentation timestamp. These clocks attribute delay;
they never replace actual presentation timestamps as cadence authority.

### Held-frame observation sequence

1. Launch `producer/hypr-motion-renderer-staged --raster-fixture` with the exact
   private compositor's WAYLAND_DISPLAY, XDG_RUNTIME_DIR and instance environment.
2. Await `outputs` (same own hardware/material proof must pass first). Use those
   exact output names/generations for `seed`; no output commit hook is installed.
3. Send `seed`, then `sample` with the same token, complete identity vector and
   desired interior progress, e.g. 0.35. Each member starts atlas→icon for minimize
   or icon→atlas for restore, with retained atlas/icon coordinates from seed.
4. Await `presented` with `accepted:true`, exact token, exact desired progress and
   complete members on *each* required output. `sequence` is an own local commit
   number, `timestampNs` actual wp_presentation time. Diagnostic mode cannot emit
   ready/endpoint or acquire native authority even if the headless backend uses
   raw refresh counter zero. Inspect `state` to confirm nativeReady/nativeEndpoint
   both false. `state.outputs[]` includes actual logical geometry, preferred
   scale/transform and EGL `bufferWidth/bufferHeight`; each swap/presentation
   record also carries the immutable buffer extent for that submitted frame.
5. Capture stable output PNGs and compare their whole raster against the retained
   native source exports and these exact per-member submitted rectangles. Keep
   main/window-source placement and known background as independent fixture data.
   Then exact latest cancel and normal stop. This experiment proves raster output
   only, and supplies no cadence/physical output or production-service claim.

After cancel, surfaces are disabled. To seed another scene on the same process,
first send `prepareOutputs`, await a fresh `outputs` event with new generations,
then seed with those generations. Never recycle the earlier output snapshot.
