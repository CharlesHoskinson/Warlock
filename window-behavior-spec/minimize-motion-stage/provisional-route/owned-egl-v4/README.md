# Owned GPU producer — staged, not installed

`Renderer.cpp` uses QtCore only for JSON/hash utilities; it never creates a Qt
GUI application or borrows QPA surfaces. Wayland, EGL and GLES are owned here.
Compositor scheduling remains untouched.

Build/offline checks:

```sh
make -C /home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/owned-egl -j2
./test-commit-ledger
quint typecheck owned_commit_test.qnt
quint test owned_commit_test.qnt
quint run owned_commit.qnt --invariant=allProps --max-samples=2000 --max-steps=100
./hypr-motion-renderer-staged --describe
```

The executable's default mode connects to the current display and is a GUI
operation. Run only under the root agent's explicitly coordinated private
fixture. `--describe` does not connect to a display.

## Producer interface

Newline-delimited JSON arrives through the private controller stdin pipe;
bounded JSON observations leave stdout. `outputs` reports observed logical
geometry, pixel mode, fractional scale, transform and a unique surface/output
generation. All required protocols and a monotonic presentation clock must be
available. No seat is bound. Every layer surface has an empty input region,
keyboard interactivity NONE, exclusive zone -1, transparent clear and namespace
`hoskinson-window-motion`.

`seed` requires stableId/PID, entire token, immutable file path/digest, exact
captured nativeRect/atlasRect/insets/pixels/scale, iconRect, operation,
from/target endpoints, durationMs and current named output generations.
Missing/drifting metadata, duplicate outputs and arbitrary endpoint rectangles
are rejected. The source file is privately owned and opened once with no symlink
following; the same bytes are hashed/decoded once, premultiplied once and uploaded
once. GPU draws do not reread/redecode/upload or resize the PNG on the CPU.

`validate` promotes only the exact current or pending new token. A promoted seed
emits `ready` only after every participating output presents that exact image.
The controller may then hide the native window and send `start`. `retarget`
accepts only newer tokens for the same retained identity/endpoints, immediately
retires prior native authority, drains one outstanding commit per output and
starts each fragment at its own actual presented rectangle. One progress sample
per render batch moves all outputs. Visual retargeting does not wait for native
metadata. A later exact promotion permits readiness/endpoint acknowledgements;
an old metadata callback cannot promote a superseded token.

`state` reports bounded actual accepted presentation records; `cancel` requires
exact identity/current token. `stop`, controller EOF, swap error, GL error,
feedback discard/timeout, output change/removal or layer destruction retire
authority and destroy surfaces. `prepareOutputs` reopens transparent output
surfaces after cancellation and publishes fresh generations before a new seed.
An unstarted/held endpoint has a two-second controller handshake deadline.

## Commit binding source evidence

Installed Mesa is 26.2.2. The exact primary source was extracted from
[Mesa's official 26.2.2 archive](https://archive.mesa3d.org/mesa-26.2.2.tar.xz)
into `primary-source/platform_wayland.c`. Direct DRI's
`dri2_wl_swap_buffers_with_damage` attaches its rendered buffer and calls
`wl_surface_commit` before returning EGL_TRUE (lines1830–1950). The producer
requests feedback on its own surface before that call and accepts it only after
the exact swap returns EGL_TRUE. It explicitly selects the Wayland EGL platform.
Mesa vendor/version, non-Zink and non-software runtime guards keep the source claim scoped:
the Kopper/Zink wrapper and software/swrast paths are unreviewed here and explicitly rejected.
Initial native probing must record actual GL/EGL strings and resulting cadence.

Feedback received before swap return is retained by the ledger. It first emits
`presentationObservedBeforeSwap`; successful return then emits the immutable
accepted original scene as `presented`. A failed return cancels instead. Registry
removal during a swap marks the output dead and defers surface destruction until
the swap returns; retired output proxies are retained until safe final teardown.

## Remaining integration

This prototype has **one window route**, explicit external promotion and no
native window authority. It has not connected to a native display in testing.
The service/family coordinator is not integrated. Required next gates are actual
GPU pixel provenance, presentation cadence (including240Hz), focus/input,
cross-output/mixed-scale/transform handover, rapid provisional reversal, native
failure/discard/removal cleanup and grouped family scene/acknowledgement support.
Only after these pass may fresh paired service/QML candidates replace the current
freeze implementation. Qt66 observations remain diagnostics.

Material claims retain the V18 boundaries: configured rounding/shadow/dim and
opaque client tested; exact installed theme/inactive colors and translucent
client backdrop equivalence are not claimed.

## Fresh v4 offline and native review packet

`checkpoint-v4.json` and `native-manifest-v4.json` supersede the retained v1
checkpoint; the v1 files and pre-repair source checkpoints remain evidence.
Current offline gates are 80 ledger, 28 actual command-consumer, 20 backend, 34 mapped material
checks, five observer tests and 13 formal scenarios / 2,000 traces of 100 steps.

The proposed private command (GUI slot required, not executed here) is:

```sh
python3 /home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/owned-egl-v4/nested_owned_egl_smoke.py --output /home/hoskinson/.cache/window-owned-egl-private-v4
```

The private fixture uses the frozen V18 atlas source in a separate compositor,
two observed outputs (1000×760/1 and 960×720/1.5), a synthetic second-output
icon, and one private window. It records static caption/client pixels only
before the uninstrumented motion run. During that run it requires active
interior presented origins, motion continuing while promotion is withheld,
stale-promotion rejection, one immutable upload, all-output latest endpoint
and actual monotonic presentation gaps no larger than two output refresh
intervals plus 0.5ms measurement tolerance (33.84ms at 60Hz). This is a first
producer smoothness gate, not a 240Hz performance claim. Output removal during
an additional active route must retire every owned surface. All original main
clients, geometry, focus/cursor, Files, reader/bus, outputs, plugins/config and
four catalog bytes are preserved using the existing exact private-fixture gates.

Remaining native gates include the entire transform/scale/pixel route matrix,
actual input delivery while layers are active, injected swap/discard failures,
missing protocols, and source close/reuse through the service. Service/family,
real taskbar endpoints and reduced-motion integration remain open. No fixture
telemetry is labeled proof of actual pixels without its independent screenshot.

The v2 native attempt is retained at `.cache/window-owned-egl-private-v2`: it
refused the backend before upload/readiness and preserved all12 main-state gates.
Actual runtime backend classification remains unobserved until v4 emits its
`backendObserved` event; the Arch build label is a source-backed compatibility
allowance, not a retrospective classification of that failed attempt.

V3 actual runtime classification is now retained: MesaProject / Intel Graphics
(ARL) / OpenGL ES3.2 Mesa26.2.2-arch1.1. It refused a device-domain mismatch
before source upload. V4 uses PROCMAP_QUERY for the existing mapping and the
already-hashed fd probe, with exact pinned ELF build IDs, bounded queries,
complete mapping revalidation and RAII. `MAPPED_MATERIAL_CONTRACT.md` records
the primary kernel source and preserves deleted/unmapped/replaced/wronghash
refusal. Actual tmpfs+Btrfs regressions print both stat and mapping devices.

Idle surfaces clear once; `state` exposes transparentCommitCount and observationId.
The private fixture requires that counter to remain stable across an idle interval
before the first seed. No active route/render cadence gates are weakened.
