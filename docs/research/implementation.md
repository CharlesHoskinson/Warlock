# Implementation simplification research — 2026-10-03

Research only. No desktop configuration, compositor, helpers, accepted evidence or historical sources changed. Primary sources were searched online and fetched with Scrapling `Fetcher.get`; responses, status codes and SHA-256 hashes are in `/home/hoskinson/.cache/windows-parity-research/implementation/sources.json`. One systemd HTML request returned 418; the upstream XML source was fetched successfully instead.

Installed versions observed read-only: Quickshell 0.3.1 and Hyprland 0.56.2, compositor commit `efb50993780079460b0cbed1363e2166a2de1d9f`. The proposals below refer to exact Quickshell 0.3.1 API docs. Omarchy upstream documentation is on the mutable `quattro` branch; installed `PluginShellApi.qml` and `shell.qml` were checked for own-service scope and keep-loaded service behavior. Every implementation would require a fresh derivative and the original acceptance campaign.

## Ranked proposals

### 1. Finish the existing bounded runtime manifest rather than widening Process limits

**Cost: low. Leverage: high, because it unblocks native evidence immediately.**

The local `pin-private-qs-native-v1/capture_source.py` already separates full campaign provenance from an explicitly selected Process runtime-source manifest and reserves 1 MiB inside the original 16 MiB bound. Finish source review, publish a fresh CPU report matching the materialization edits, then exercise real changed/same/cancelled/stale input routes before reliability. Consolidate future manifest materialization in one reusable, reviewed schema adapter so each new helper does not grow another complete campaign copy.

The official [Quickshell IpcHandler API](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/IpcHandler/) requires typed arguments and return values, supports only the documented scalar types, and limits function calls to ten arguments. Small typed commands carrying a receipt ID and a bounded payload fit that interface well. This is an architectural inference, not a documented 16 MiB limit: that limit is from the local Process provider and must remain unchanged.

**Tradeoff:** smaller manifests must still close over every actually mapped executable/module/source. Retain full campaign preflight and terminal verification and fail on unknown mappings. Runtime projection is already in progress; this proposal prioritizes and standardizes it rather than claiming it is new.

### 2. Make the taskbar a thin service-backed widget in the existing Omarchy shell

**Cost: low to medium. Leverage: high.**

Use one namespaced plugin with service and bar-widget entry points, place it at the left of the trusted built-in bar, and keep one owner of taskbar grouping, window identity and pending commands. Taskbar, previews, overview and shortcuts should consume the same service instead of starting separate shell instances or each owning mutable group state. Keep the existing native backend responsible for operations that require compositor authority.

The [official shell contract](https://github.com/omacom/omarchy/blob/quattro/docs/omarchy-shell.md) documents the long-lived host, multi-kind manifests and own-service lookup. It also says replacement third-party bars provide their hosted widgets a service-less facade: replacing the whole bar adds an integration constraint that a widget under the built-in bar avoids. The [official plugin development guide](https://plugins.omarchy.org/develop.html) recommends working in user-owned plugin directories and forbids starting a second Quickshell instance for a plugin.

**Tradeoff:** a shared QML host means plugin crashes can affect the desktop shell. Bound decoding and transport work, keep expensive capture outside the GUI thread, and preserve native backend isolation. Private Quickshell instances remain appropriate for QA; this recommendation concerns production processes.

### 3. Separate UI reload state from native ownership, and replace detached control helpers with acknowledged transport

**Cost: medium. Leverage: high for cancellation and process lifetime.**

`WindowMotion.qml` in the private wrapper still sends control signals through `Quickshell.execDetached([helper, method, token])`. Prefer a persistent backend command channel, with typed receipts and an epoch tied to the backend's lifetime; reject callbacks whose epoch/window/action no longer matches. `Socket` plus `SplitParser` can carry a bounded protocol without spawning one control helper per ready/close/cancel signal. Explicitly flush writes and treat disconnection as loss of authority.

[Quickshell Process](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/Process/) states that `running=false` sends SIGTERM and that detached processes are neither tracked nor killed with Quickshell. This does not establish descendant process-tree closure; retain the existing Keeper/job/resource ownership proof. [Socket](https://quickshell.org/docs/v0.3.1/types/Quickshell.Io/Socket/) documents asynchronous connection state and explicit flushing. [PersistentProperties](https://quickshell.org/docs/v0.3.1/types/Quickshell/PersistentProperties/) preserves properties across QML reload, which is useful for panel presentation but is not durable crash recovery or backend ownership.

Use `keepLoaded` only where continuity is essential: [Omarchy's contract](https://github.com/omacom/omarchy/blob/quattro/docs/omarchy-shell.md) says kept service code changes require a shell restart. Continue the locally mandated new-entry-directory/manifest/rescan procedure; do not assume upstream hot reload cures the installed QML URL cache problem.

**Tradeoff:** a persistent connection introduces reconnection and framing cases. Keep the current stale/cancelled receipt checks and absolute deadlines; do not replace acknowledgement with successful write or process disappearance.

### 4. Share event-driven display state, while retaining fresh observations before native effects

**Cost: medium. Leverage: medium to high for taskbar and overview scale.**

Use one presentation model sourced from `Hyprland.toplevels`, monitor/workspace models and `rawEvent`; coalesce UI updates into a single refresh and avoid every hover/delegate launching a full inventory query. Copy event strings inside the signal handler before queuing work, because event objects may be reused. Track freshness explicitly and query again at operation boundaries or after reconnect.

The [Hyprland singleton API](https://quickshell.org/docs/v0.3.1/types/Quickshell.Hyprland/Hyprland/) exposes all these models and refresh methods; it explicitly warns some state-invalidating actions do not emit events. A cache therefore cannot be the final authority for pin, minimize, restore, family geometry or capture. The local V29 `READONLY_IPC_CONTRACT.md` already provides direct read-only IPC, and explicitly requires a fresh complete reply; do not redesign it into an event-cache shortcut. The event model is for presentation and reducing duplicate non-authoritative work.

**Tradeoff:** state gaps and Lua dispatcher differences need explicit handling. Check `usingLua`, do not hard-code a dispatcher syntax from an older wiki example, and preserve the existing exact allowed requests at authoritative call sites.

### 5. Profile journal publication, then evaluate an append-only durable store

**Cost: high. Leverage: potentially high, unproven until measured natively.**

The V29 contract preserves an earlier CPU replay result: 24 trivial queries plus 98 fsynced journal snapshots cost 1777.233 ms. This is evidence of source overhead, not proof of the current native bottleneck or a promised speedup. Local `service_runtime.py:201–209` holds `manager.lock` across snapshot serialization and durable store publication, including nested ownership histories. Add separate measurements for lock wait, serialization, ownership checks, fsync, capture, renderer seeding and upload in a fresh derivative; retain the original two-second deadline. If full-snapshot rewrites dominate, prototype append-only transition records with sequence numbers and checksums, or SQLite WAL with equivalent transactional invariants.

[SQLite WAL documentation](https://www.sqlite.org/wal.html) explains append-based commits and checkpoint scheduling. [SQLite synchronous documentation](https://www.sqlite.org/pragma.html#pragma_synchronous) distinguishes durability modes: do not select NORMAL merely for speed when power-loss durability at each authority publication is required. A FULL transaction may reduce rewrite work but still needs its commit synchronization; do not promise fewer mandatory durability boundaries.

The local contract requires durable registration before connection, durable completion/refusal before exposing bytes, complete nontruncated retained history, capacity refusal, quarantine on durability fault and restart reconstruction. Checkpoints must preserve that complete history and cannot drop refused or unfinished records to admit more work. Keep the old journal parser for historical packets and use a versioned new format with equivalence and crash-point tests.

**Tradeoff:** this is a storage/recovery redesign, and may cost more validation than it saves. First finish the already tested V29 capture fusion and measure its native baseline; use the WAL option only when the measured budget warrants it.

## Suggested sequence

Finish the existing runtime-source projection and real popup routes first; establish the V29 native baseline separately. Then consolidate the production UI around a single service-backed widget and receipt transport. Measure the coherent integration before undertaking journal replacement. Preserve all original scenario identities, assertion counts, deadlines, failed packets, ABI pairs and serial native QA ownership. Upstream API availability and a simpler architecture are not native acceptance.
