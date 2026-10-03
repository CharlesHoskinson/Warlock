# Staged explicit native entrypoint

Not installed or natively tested. No invocation is authorized outside root's GUI
slot. Requires an already selected private runtime and live compositor sockets.
No fallback to the main compositor is allowed. Frozen source material and expected
producer/core SHA256 must be supplied explicitly.

Launch under the approved QA scope, using structured subprocess arguments:

```text
python3 native_runtime.py --root RUNTIME/hypr-window-motion/FRESH_PRIVATE_SERVICE
 --session EXACT_SIGNATURE --pid COMPOSITOR_PID --start PROC_START
 --display EXACT_PRIVATE_WAYLAND_DISPLAY --producer FROZEN_PRODUCER
 --producer-sha256 EXACT_PRODUCER_SHA --core FROZEN_CORE
 --core-sha256 EXACT_CORE_SHA
```

The private motion parent directory must already exist with mode 0700. The child
environment's XDG_RUNTIME_DIR, HYPRLAND_INSTANCE_SIGNATURE and WAYLAND_DISPLAY
must equal that selected compositor, with HOME retaining approved private QA
helper/catalog setup. The entrypoint strips all request-scoped HYPR_WINDOWCTL_*
flags. It does not install, discover another compositor, start automatically or
recover an unresolved durable journal.

Client: same --root/--session plus --request-stdin. A single JSON request on stdin
uses the existing explicit API fields command=request, operation, address,
stableId, pid, optional single. --stop sends only stop after exact runtime-owner
validation. Missing daemon is an error, with no startup/fallback. Lost response
is unknown acceptance and is never automatically repeated. accepted=true is a
durable receipt, completed=false remains asynchronous. state is read-only.

The renderer source is copied once per actor into a sealed executable memfd; each
core commit receives its own exact sealed script bytes and captured ID/PID.
Source pathname replacement and in-place modification cannot change those
executed copies. Imported modules create no actor/renderer/native effects.

Required native acceptance still includes real V18 family captures, complete
rasters, receipt-to-presented reversal latency, physical 240Hz/cross-output
cadence, reduced/interruption/reuse, exact geometry/native/input preservation and
normal daemon/renderer shutdown. Those are not implied by offline bootstrap tests.

## V12 private integration pairing

V12 requires toolkit-interruption-v4's reviewed immutable native/Snap/close-helper
pair. The API `retire_gesture_current(address, stableIdHex)` must exist and return
exact boolean success/retired for each selected member. A false result or absent
capability aborts the whole visual preparation before capture. The registry's
current complete-family reservation covers the batch and the subsequent full
native requery. Earlier V2/V3 native pairs are not this packet's launch material.

The packet pins the V4 manifest plus every one of its 936 input hashes. This is
private source review acceptance only; it is not main installation or native
gesture acceptance. Source draw order is ancestor first with native sibling
paint-vector witnesses, independently of deepest endpoint focus.

The durable journal exposes `liveActors`, `retiringActors`, `actorSerial`,
`actorLimit`, `resourceErrors`, `housekeepingErrors` and `managerClosed`. Actor
numbers increase and include failures/retirement. Normal retirement invokes
`NativeFactory.retired(number, desktop)` only after worker drain, normal renderer
close and exact private-directory disposal. A read-only observer must capture
controllers at the existing once-per-creation `transport.bind_controller` seam;
product actors are removed after retirement and cannot retain QA history.
Normal service stop performs the same closure/disposal and durable completion.

Offline replay from this directory: `python3 check_offline.py` requires fresh
log/report destinations and performs 165 Python checks, 90 named Quint scenarios
and 14 models at 2000 samples each. A frozen checkpoint already contains these
results. Replaying that packet should use a fresh copy/output path; never
rewrite its proof files. These counts do not imply native/physical acceptance.
