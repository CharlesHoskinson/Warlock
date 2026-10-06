# Private session-lock qualification fixture

LOCK-FIXTURE01: The fixture SHALL connect only in the unchanged protected QA
scope, with core limit (1,1), an explicitly enabled private nonsymlink UID-owned
0700 runtime, its exact expected socket device/inode and authenticated server
PID. It SHALL never connect to the ordinary desktop by a default display.

LOCK-FIXTURE02: It SHALL use the real ext-session-lock-v1 protocol, create
bounded opaque SHM lock surfaces for advertised outputs, acknowledge actual
configure serials before exact-size commits, and log Locked only on the actual
server event. No fixture log qualifies hardware presentation of preview pixels.

LOCK-FIXTURE03: It SHALL retain owned buffers until release or connection
teardown. Explicit private control may request unlock only after Locked. Normal
exit requires actual unlock_and_destroy and a completed Wayland sync barrier;
signal cancellation, protocol failure or Finished is not normal qualification.

LOCK-FIXTURE04: Bounds are eight outputs/buffers and 128 MiB aggregate retained
SHM, at most 4096 per dimension, with no installed configuration or authentication
changes. Failure cleanup SHALL attempt protocol-correct unlock when Locked and
report failure without claiming successful native preview retirement. The native
campaign owns all launch/teardown and exact compositor/plugin ABI validation.
