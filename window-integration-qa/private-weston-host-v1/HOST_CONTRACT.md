# Private signed Weston headless GL host (before launch)

No compositor launch occurred during package/source/dependency preparation.
No sudo/system installation/config/default/environment/main plugin changes.
The signed Arch Weston15.0.1-3 package is extracted solely to this QA prefix.
Installed Arch keyring was dearmored into private storage; GOODSIG/VALIDSIG
heftig83BC8889351B5DEBBB68416EB8AC08600F108CDF verified. Initial armored-keyring
failure is retained. Signed BUILDINFO pins the downloaded official Arch PKGBUILD;
its source tar/patch hashes match exact official15.0.1 release inputs. Licenses,
headers and exact source are retained. Required ELF ldd has no missing dependency.

API: PrivateWestonHost(output=<new QA host subdir>,main_env=<explicit original
copy>,width=1600,height=1000,dri_prime=None,mesa_vendor=False) context returns
host.env and host.evidence. Host creates owned0700 /run/user/$UID/wqa/qa-* BEFORE private
DBus; all HOME/config/data/cache/state reside beneath it. All inherited main
bus/display/socket/Hypr signature/activation and renderer override variables
are removed. Explicit headless backend/GL renderer/kiosk shell/fake seat,
private module map and LD paths, --no-config, socket weston-host and scale1
prevent main Wayland surface/input/config loading. No pixman/software fallback.
Optional reviewed DRI_PRIME or Mesa vendor selection is recorded and is NOT
runtime evidence. Intel real PCI0000:00:02.0 is renderD129; NVIDIA is renderD128.

Root owns first composite foundation launch and actual acceptance. Must retain
actual GL/Mesa vendor/renderer/render-node logs and live mapped ELF paths/hashes,
real default DMA-BUF feedback device/format table and O_RDWR render-node/driver
observation. Selection, source support or ldd is not runtime acceptance. Reviewed
producer hardware predicates remain unchanged; no forced success/software waiver.

Root's composite harness launches child Hypr AQ_BACKENDS=wayland against host
socket, discovers exact child signature/wl_socket, asserts actual output geometry,
and supplies that private env only to fixtures. Qt uses1600x1000 scale1; pointer
may use1280x800 scale1.25→logical1024x640. Root supplies compositorPID/start/config
for reader's private_session.run_session. Main snapshots enclose whole host,
use original explicit env, and are compared read-only; no main focus/cursor writes.
Own private AT-SPI launcher/Registry must use private bus/runtime/display.

Inner fixtures own normal EOF releases, quiescent plugin retirement/unload,
private daemon public stop, and private AX termination before context exit.
The composite context stops its own child Hypr before stopping Weston and DBus.
Host cleanup records unexpected surviving private descendants as a FAILURE,
uses UID/PID-start guards for scoped termination, then stops Weston/privateDBus,
archives inner Hypr logs/Weston log/configs before runtime removal and verifies
all descendants/runtime gone. Never raw-unload a false-quiescent plugin.
Main signatures/sockets/PIDs are never termination targets.

Composite API (fixed before implementation):
`with PrivateHyprSession(output=<fresh QA subdir>, main_env=<explicit original
environment>, width=1600, height=1000, nested_lua=<exact reviewed bytes>,
dri_prime=None, mesa_vendor=False) as session:` returns `session.env`,
`session.ctl(*args)` (text), `session.data(*args)` (JSON), and `session.evidence`.
Session first obtains actual host DMA-BUF feedback, then launches the exact
installed Hyprland with the supplied private Lua config. It removes the host's
EGL_PLATFORM=surfaceless before launching any nested Wayland EGL client. It
discovers only its own PID's instance in its private runtime, pins PID/start/PGID,
signature and socket UID/device/inode, and checks all before every explicit
`hyprctl -i <signature>` request. No main-instance fallback exists. Evidence
includes compositorPID/compositorStart/compositorConfig for the reader harness,
config hash and socket metadata, live maps, host/probe provenance and cleanup.
Output dimensions are physical host pixels; caller-provided Lua controls actual
Hyprland scale and must validate monitor geometry before fixture input.
Caller must stop its own fixtures normally before leaving the context; surviving
unknown descendants are a reported failure. Logs are archived even on setup
failure. Runtime removal follows verified descendant absence only. Context
performs no main reads/writes, plugin load/unload, reader launch or input.

## Crash-noise handoff (mandatory before native launch)

Exact `~/Documents/crash-noise/HANDOFF-codex-window-qa.md` was read. The complete
runner must run in `qa-harness.slice/qa-harness-*.scope` with exact soft/hard
RLIMIT_CORE=1 (explicit reviewed diagnostic infinity only). Require scope before
output/runtime/bus creation. Use shared qa_launch runtime and parent-socket
guards, pinned as external dependencies; current danger-full-access needs no
approval/escalation. Effective fresh Lua disables Xwayland because X11 is not
under test; preserve caller bytes/hash separately from effective config hash.
Weston parent socket is verified live, stable UID/inode and SO_PEERCRED matching
the recorded Weston process before explicit AQ_BACKENDS=wayland child launch.
Clients/AX first, nested Hypr second, Weston third, private bus last. Desktop
crash-watch override and existing frozen artifacts remain untouched. No DRM or
standalone headless Hypr fallback. Handoff's claimed sandbox cause is separate
from root's independently proved standalone-headless allocator limitation.
