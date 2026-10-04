# Presentation observation protocol

The candidate `hypr-taskbar observe` (alias `watch`) requires its sibling
`taskbar_watch.py` and `taskbar_catalog.py` modules. It preserves the original
one-shot `snapshot` output and action commands; the observer invokes only the
original snapshot path. Existing preview identity cleanup and session-order file
writes retain their original behavior. No event or presentation cache authorizes
minimize, restore, capture, focus, pin or other compositor effects.

Host one tracked Quickshell `Process` in the plugin service, shared by all bar
instances. Enable stdin before starting. Write the exact string `refresh\n` to
request a fresh observation. Duplicate refreshes coalesce; unknown commands,
lines above 64 bytes and malformed framing terminate the helper nonzero. EOF on
stdin ends it normally. Stdout contains only complete JSON lines; diagnostics use
stderr. Do not treat successful writes or process disappearance as effect
acknowledgements.

Each line preserves `groups`, `focusedAddress`, `snapGroups`, `settings`,
`monitors` and `reducedMotion` and adds `protocolVersion: 1`, `epoch` (32 lowercase
hex characters, fixed for the process) and `sequence` (positive, strictly
increasing, including reconnects). These are presentation ordering fields. The
consumer binds the first epoch to the current tracked process, rejects
out-of-order lines, and clears observations when that process exits. Encoded JSON
is bounded to 4 MiB, forbids nonfinite numbers, and never publishes partial data
on a failed provider call.

One nonblocking subscriber connects to the exact startup
`$XDG_RUNTIME_DIR/hypr/$HYPRLAND_INSTANCE_SIGNATURE/.socket2.sock`; instance names
cannot contain path separators. The endpoint must be an owned socket with no
symlink traversal. Its device/inode and peer UID/PID/start time are checked before
and after connection and after each snapshot. Reconnects retain the same selected
compositor lifetime. A changed/dead peer terminates observation; unavailable
endpoints retry every second for at most ten seconds. A failed snapshot is
terminal so the consumer can clear stale presentation state. Event framing has
a 64 KiB bound.

The initial snapshot, complete compositor events and local file invalidations
request fresh independent legacy queries. Bursts coalesce over 75 ms without
waiting for the burst to finish. A 15-second reconciliation handles fields with
missing events. A single inotify descriptor watches desktop application trees,
pins/settings/order, recent files, reduced motion, attention/launcher data,
preview files and snap-group files. It handles close-write, attribute change,
rename into/out of watched directories, creation/removal and queue overflow;
missing and replaced directories rebuild the inventory. Session-order writes and
lock files are excluded from invalidation. The inventory is bounded to 4096
directories. Native query deadlines are unchanged.

SIGTERM/SIGINT closes observation and interrupts an in-flight `subprocess.run`
query through its cleanup path. The fake-command CLI test confirms the immediate
query child is killed and reaped; this is not proof about arbitrary descendants
or full native helper closure. Existing native Keeper/job/resource rules remain
required.

`WATCH_PROOF.json` records source hashes, the installed origin hash, 26 protected
fake-peer/inotify/CLI checks and all 15 unchanged installed backend tests. These
are CPU/kernel and mock-backend results, not real Quickshell/GUI acceptance.
