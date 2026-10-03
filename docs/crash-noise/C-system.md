# Keeping QA-harness crashes out of the desktop "Process crashed" toast

Research only — nothing on the machine was changed. Scope: system/process-level ways to stop
`omarchy-crash-watch` from toasting crashes produced by another Claude Code session's QA harness
(nested Hyprland on :1, test quickshell, python Orca probes, a private-bus portal), without losing
real desktop crash toasts.

## 1. What's actually on this machine right now

`coredumpctl list --since 2026-09-30 --no-pager` shows 26 coredumps since boot. Cross-referencing
`coredumpctl info <pid>` "Command Line" and "User Unit" fields splits them cleanly into two groups:

**QA harness (all share `User Unit: app-Hyprland-xdg\x2dterminal\x2dexec-709acf58.scope` — i.e. they
were just launched from a terminal inside the real session, not isolated in any way):**
- 3x `Hyprland` SIGABRT/SIGSEGV — command line is literally
  `Hyprland --config /home/hoskinson/window-integration-qa/nested_pinned.lua` (the nested test
  compositor, not the real desktop Hyprland)
- 8x `Xwayland` SIGABRT — `Xwayland :1 -rootless -core -listenfd ... -wm 53`
- 1x `quickshell` SIGSEGV — `qs -p /home/hoskinson/.local/share/hypr-window-controls -d -n`
- 2x `python3.14`/`python3` SIGABRT/SIGSEGV — one is literally
  `python .../window-integration-qa/orca-reader/.../orca ...`, the other
  `python3 .../window-integration-qa/recovery-audit/keyboard-monitor/abi_client.py org.gnome.Orca orca`
- 1x `xdg-desktop-portal-hyprland` SIGSEGV

**Real desktop (different unit):**
- 4x `grim` SIGSEGV — `User Unit: wayland-wm@hyprland.desktop.service` (the actual session compositor
  unit, distinct from the harness's terminal-exec scope)
- node, gnome-keyring-daemon crashes — unrelated dev/session activity

`cat /etc/systemd/coredump.conf`: stock Arch defaults, everything commented out (`Storage=`,
`ProcessSizeMax=`, etc. all at compiled-in defaults: `Storage=external`, `ProcessSizeMax=32G` on
64-bit). No `/etc/systemd/coredump.conf.d/` drop-ins exist.

`ulimit -c` → `unlimited`. `sysctl kernel.core_pattern` →
`|/usr/lib/systemd/systemd-coredump %P %u %g %s %t %c %h %d %F %I` (a **pipe**, which matters — see §2).

`systemd --version` → systemd 261 (261.2-1-arch).

### How `omarchy-crash-watch` works (read from `/usr/bin/omarchy-crash-watch`)

It's a bash loop over `journalctl -f -o json "MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1"` (the
fixed systemd-coredump journal message ID). For each entry it pulls `._UID`, `.COREDUMP_COMM`,
`.COREDUMP_PID`, `.COREDUMP_EXE`, `.COREDUMP_SIGNAL_NAME` via `jq`, derives a basename from
`COREDUMP_EXE`, and the **only** suppression knob is:

```bash
readonly ignore_pattern=${OMARCHY_CRASH_IGNORE:-}
...
[[ -n $ignore_pattern && $name =~ $ignore_pattern ]] && continue
```

— an extended regex matched against the executable's basename only. It never looks at
`COREDUMP_UNIT`/`COREDUMP_USER_UNIT`/`COREDUMP_CGROUP`, even though those fields are present in
every coredump journal entry (confirmed below).

**Why `OMARCHY_CRASH_IGNORE` can't solve this alone:** the QA harness crashes as `Hyprland`,
`Xwayland`, `quickshell`, `python3.14` — the exact same basenames the real desktop uses for its
actual compositor, actual bar, and any python script the user runs. A basename regex broad enough
to swallow the harness's crashes (`^(Hyprland|Xwayland|quickshell|python3?.*)$`) would also swallow
a real crash of the real Hyprland, the real quickshell bar, or any of the user's own python
scripts — exactly the outcome the user wants to avoid. This is a structural limitation of the one
knob that exists today, not a configuration mistake.

### The journal already carries a distinguishing field — it's just unused

`journalctl -o json "MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1"` entries carry (confirmed via
`jq` on the quickshell coredump, PID 2387334):

```
COREDUMP_UNIT:      "user@1000.service"
COREDUMP_USER_UNIT:  "app-Hyprland-xdg\\x2dterminal\\x2dexec-709acf58.scope"
COREDUMP_CGROUP:     "/user.slice/user-1000.slice/user@1000.service/app.slice/app-graphical.slice/app-Hyprland-xdg\\x2dterminal\\x2dexec-709acf58.scope"
COREDUMP_SLICE:      (present)
```

Every process in a systemd user session inherits a `COREDUMP_USER_UNIT` from whatever scope/service
it was forked under. Right now the harness has no scope of its own, so it inherits the terminal
app's scope — same as any other app the user runs from a terminal, hence no reliable signal today.
**If the harness is launched under its own named `systemd-run --user --scope`, every descendant
(nested Hyprland, the Xwayland it spawns, the test quickshell, the python Orca probes, the portal)
inherits that scope's name in `COREDUMP_USER_UNIT`/`COREDUMP_CGROUP`, regardless of which binary
actually crashes.** This is documented systemd behavior (journald's `--user-unit=`/`_SYSTEMD_UNIT`
filtering: https://man7.org/linux/man-pages/man1/journalctl.1.html) and verified directly on this
machine above. It's the only field that would let a filter distinguish "test quickshell crashed"
from "real quickshell bar crashed" — basename alone cannot.

Caveat: using *only* this (tagging + extending `omarchy-crash-watch` to also regex
`COREDUMP_USER_UNIT`) requires a code change to `omarchy-crash-watch` itself, which this machine's
owner doesn't control from the QA harness side. See §3 for the recommendation that avoids needing
that change.

## 2. Does `RLIMIT_CORE=0` / `ulimit -c 0` stop the journal entry? — No, confirmed from source

This was the central question to verify, and the docs are genuinely ambiguous/contradictory on
their own, so I went to kernel source to settle it.

- `core(5)` (man7.org): *"RLIMIT_CORE ... will be ignored if the system is configured to pipe core
  dumps to a program."* [man7.org/linux/man-pages/man5/core.5.html](https://man7.org/linux/man-pages/man5/core.5.html)
- Confirmed in multiple independent sources: when `kernel.core_pattern` begins with `|` (it does on
  this machine — `|/usr/lib/systemd/systemd-coredump ...`), **the kernel ignores `RLIMIT_CORE` for
  the purpose of deciding whether to invoke the pipe helper**, specifically so a helper like
  systemd-coredump can still log/triage a crash even from a process that has disabled core files.
- `coredump.conf(5)` (Arch manpages): `Storage=none` + `ProcessSizeMax=0` *"disables all coredump
  handling **except for a log entry**"* — i.e. even the most aggressive coredump.conf settings
  still produce the journal entry `omarchy-crash-watch` watches for.
  [man.archlinux.org/man/coredump.conf.5.en](https://man.archlinux.org/man/coredump.conf.5.en)

**So: `ulimit -c 0` before launching the harness, or setting `Storage=none`/`ProcessSizeMax=0` in
coredump.conf, will NOT stop the toast.** The core *file* may not be saved, but systemd-coredump
still runs, still writes the `MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1` journal entry with
`COREDUMP_COMM`/`COREDUMP_EXE`/etc., and `omarchy-crash-watch` still fires on it.

### The one RLIMIT_CORE value that *does* work: exactly `1`

`core(5)`'s "ignored" rule has one documented exception, confirmed directly in current kernel
source (`fs/coredump.c`, `torvalds/linux` master,
https://github.com/torvalds/linux/blob/master/fs/coredump.c), function `coredump_pipe()`:

```c
if (cprm->limit == 1) {
        coredump_report_failure("RLIMIT_CORE is set to 1, aborting core");
        return false;
}
```

This check runs **before** the kernel ever calls `call_usermodehelper()` to spawn
`/usr/lib/systemd/systemd-coredump`. If a crashing process's `RLIMIT_CORE` is exactly `1` (one
byte — not 0, not unlimited), the kernel refuses to invoke the pipe helper at all:
systemd-coredump never runs, so it can never write the journal entry `omarchy-crash-watch` is
watching for. `coredump_report_failure()` only emits a kernel log line (visible in `dmesg`/
`journalctl -k`), which carries no `MESSAGE_ID` and is invisible to `coredumpctl`/the watcher.

(This sentinel exists in the kernel specifically so systemd-coredump's own usermode-helper
invocation of itself — which it sets to `RLIMIT_CORE=1` internally — can't recursively core-dump
if the helper itself crashes; the kernel can't distinguish "this is the real helper" from "this is
some other process that happens to have RLIMIT_CORE=1", so any process with that exact limit gets
the same protection.)

**RLIMIT_CORE survives `execve()`** (unlike `PR_SET_DUMPABLE`, see below), so setting it once on
the harness's launcher process means every forked/exec'd descendant — nested Hyprland, the Xwayland
it starts, quickshell, the python Orca probes, the portal — inherits it automatically, with no need
to inject anything into each binary.

## 3. Recommended mechanism

```bash
systemd-run --user --scope \
  --unit=qa-harness \
  --slice=qa-harness.slice \
  -p LimitCORE=1 \
  -- <the harness's actual launch command>
```

- `-p LimitCORE=1` sets `RLIMIT_CORE` to the kernel's sentinel value for the scope and everything
  forked under it (systemd's `Limit*=` unit properties map directly to the `setrlimit()` value in
  bytes, so `1` here is the one-byte sentinel, not "1 KB" or similar). Every crash anywhere in the
  harness's process tree — nested Hyprland, its Xwayland, the test quickshell, the Orca python
  probes, the sandboxed portal — hits `coredump_pipe()`'s early return and never reaches
  systemd-coredump. No journal entry, no `MESSAGE_ID` match, no toast. Nothing about
  `omarchy-crash-watch` or coredump.conf needs to change, and the real desktop (different
  scope/unit, default `RLIMIT_CORE=unlimited` on this machine) is completely unaffected.
- `--scope --unit=qa-harness --slice=qa-harness.slice` is not strictly required for the suppression
  itself, but it's cheap insurance and useful independent of it:
  - `systemd-run --scope` gives the whole harness tree one cgroup that can be torn down atomically
    (`systemctl --user stop qa-harness.scope` kills everything under it, no orphaned nested
    Hyprland/Xwayland processes left behind for `grim`/other real-desktop tools to trip over).
  - If `-p LimitCORE=1` is ever relaxed for a one-off debugging session (see below), the scope name
    still shows up in `COREDUMP_USER_UNIT` on any coredump that does get through, so
    `coordumpctl list` / a future unit-aware filter can tell harness crashes apart from real ones
    by cgroup rather than by binary name — the one thing `OMARCHY_CRASH_IGNORE` structurally can't
    do (§1).

**Trade-off to flag explicitly:** this is a full opt-out. No core file, no `coredumpctl` entry, no
backtrace — the crash becomes invisible to systemd's coredump tooling entirely, visible only as a
one-line kernel message (`RLIMIT_CORE is set to 1, aborting core`) in `dmesg`/`journalctl -k -g
RLIMIT_CORE`, and whatever the QA harness's own process supervision already captures (exit codes,
stdout/stderr). For normal flaky-sandbox-crash QA runs that's the right trade — the whole point is
these aren't supposed to be investigated as desktop incidents. If a specific crash ever needs a
real backtrace, rerun that one case with `-p LimitCORE=infinity` (or no `LimitCORE` override) so
`coordumpctl`/`diagnose-crash` can see it normally.

### Alternative considered and not recommended: `PR_SET_DUMPABLE(0)`

Community-confirmed effective — `prctl(PR_SET_DUMPABLE, 0)` from inside a process makes
`coredumpctl` see nothing for it and suppresses the crash handler entirely (per
https://groups.google.com/g/afl-users/c/ivDT0SZTriM, and documented as a valid opt-out alongside
`RLIMIT_CORE` by https://github.com/systemd/systemd/blob/main/docs/COREDUMP.md: *"Individual
services, processes or users can opt-out of coredump collection, by setting `RLIMIT_CORE` to 0 (or
alternatively invoke `PR_SET_DUMPABLE`)"* — note systemd's own doc conflates "RLIMIT_CORE to 0" and
"PR_SET_DUMPABLE" as equivalent opt-outs, which §2's kernel-source check shows is **not quite
right** for RLIMIT_CORE=0 specifically when core_pattern is a pipe; PR_SET_DUMPABLE is the one of
the two that actually works at 0/false).

The problem is **not whether it works, but how to apply it to binaries you don't control**:
`PR_SET_DUMPABLE` does not survive `execve()` of a new program the way rlimits do — the dumpable
flag is recomputed fresh at each exec (`man 2 prctl`). So it would have to be set by each target
binary itself, after its own exec, meaning you'd need an `LD_PRELOAD`'d shared library with a
`__attribute__((constructor))` calling `prctl(PR_SET_DUMPABLE, 0)` injected into every process in
the tree (Hyprland, Xwayland, quickshell, python), propagated through however the nested compositor
launches each one. That's strictly more moving parts than a single `-p LimitCORE=1` that
automatically inherits through every fork+exec for free. Not recommended as primary; mentioned here
in case `LimitCORE=1` ever turns out to be blocked by something specific to this environment.

### Why not just extend `OMARCHY_CRASH_IGNORE`

Covered in §1: the regex only sees the executable basename, and the harness's crashing binaries
(`Hyprland`, `Xwayland`, `quickshell`, `python3.14`) are identical names to the real desktop's. Any
pattern broad enough to catch the harness catches the real thing too. This is a dead end without a
code change to `omarchy-crash-watch` to also match `COREDUMP_USER_UNIT`/`COREDUMP_CGROUP` — which
is a reasonable thing to propose upstream to Omarchy separately, but isn't something the QA harness
can fix on its own, whereas `-p LimitCORE=1` is entirely within the harness's control.

## 4. The crashes themselves — which are real bugs worth reporting

### Xwayland: `FatalError` in `InitOutput()` when `wl_display_connect()` fails — known, already tracked upstream

All 8 Xwayland coredumps here are SIGABRT with the same shape (`abort()` called via `raise()` from
inside the Xwayland binary, no further useful symbols since Xwayland isn't built with
`-fno-omit-frame-pointer`/debug symbols on Arch) — consistent with the classic
`OsAbort() ← AbortServer() ← FatalError("Couldn't add screen") ← InitOutput()` path that fires when
Xwayland can't connect to its backing Wayland compositor (`wl_display_connect()` returns NULL). This
is a well-known, already-filed class of upstream bug in `xorg/xserver`:
- https://gitlab.freedesktop.org/xorg/xserver/-/issues/1239 (the specific
  FatalError/InitOutput/wl_display_connect pattern)
- https://gitlab.freedesktop.org/xorg/xserver/-/issues/884 and
  https://gitlab.freedesktop.org/xorg/xserver/-/issues/1574 (related Xwayland abort-on-startup
  crashes)

Given every Xwayland crash here is `Xwayland :1 -rootless ... -wm 53` from inside a nested Hyprland
that is itself crashing/restarting in the same test windows, this is almost certainly the same race:
the nested compositor tears down (or never fully comes up) while Xwayland is mid-connect. **Not
worth filing as a new bug** — it's an existing, already-tracked upstream issue. If anything, the
actionable fix is on the harness side: sequence nested-Hyprland teardown so Xwayland is killed
before (or well after) the compositor socket disappears, rather than racing it.

### quickshell: SIGSEGV in `QInputMethod::commit()` called from a `QQuickItem` destructor chain — plausibly a real, not-yet-filed bug

Full backtrace (quickshell PID 2387334, `qs -p .../hypr-window-controls -d -n`):

```
#2  quickshell + 0x124389
#4  QInputMethod::commit()                                  (libQt6Gui)
#5  QQuickDeliveryAgentPrivate::clearFocusInScope(...)       (libQt6Quick)
#6  QQuickItem::setParentItem(...)                           (libQt6Quick)
#7  QQuickItem::~QQuickItem()                                (libQt6Quick)
#8  quickshell + 0x13d90a
#9  QObjectPrivate::deleteChildren()                          (libQt6Core)
#10 QObject::~QObject()
... (repeats through several more quickshell/QObject destructor frames) ...
```

This is a genuine use-after-free/teardown-ordering crash class, not a sandbox artifact — a
`QQuickItem` destructor reparenting itself out of its scene triggers focus-scope cleanup, which
calls into the input method, which touches something already torn down. I did **not** find an
existing quickshell issue with this exact signature (`QInputMethod::commit` specifically), but
quickshell's own tracker has several *very* similar, currently-open issues describing the same
general bug class — SIGSEGV during `QQuickItem` teardown/destructor chains on Qt 6.11.x:
- https://github.com/quickshell-mirror/quickshell/issues/1228 (`~QuickshellScreenInfo` notifies a
  QML binding writing to an already-freed item, Qt 6.11.2)
- https://github.com/quickshell-mirror/quickshell/issues/1165 (`QQmlData::destroyed` during
  `QQuickItem` teardown after monitor removal)
- https://github.com/quickshell-mirror/quickshell/issues/1169 (SIGSEGV in `__dynamic_cast` during
  QML `createObject`)
- https://github.com/quickshell-mirror/quickshell/issues/986, #1157

**Recommendation: worth reporting**, but as a new issue cross-referencing the above (same bug
family — Qt Quick item-teardown ordering — different trigger path through the input-method/focus
code rather than QML Repeater/monitor-removal code), not a duplicate. Caveat for whoever files it:
this specific instance fired during an automated test harness doing synthetic input injection
(Orca probe), so it'd be worth first checking whether it reproduces outside that harness (e.g. a
real focus change during a real window close) before assuming it's generally user-triggerable —
but the crash itself is a legitimate Qt/quickshell defect, not an environment-configuration issue
like the other two.

### libatspi: SIGSEGV in `XKeysymToKeycode()` with no/dead X display — plausibly a real, long-standing gap

Backtrace (python3.14 PID 2915296, `python3 .../keyboard-monitor/abi_client.py org.gnome.Orca
orca`):

```
#0  XKeysymToKeycode          (libX11.so.6)     <- fault here, SEGV_MAPERR
#1  libatspi.so.0 + 0x1c6d3                      (spi_dec_x11_get_keycode, per at-spi2-core source)
#2  libffi ... -> _gi (PyGObject) -> libpython3.14 -> Py_RunMain
```

`XKeysymToKeycode()` is being called with a stale or NULL `Display*`, classic for an X11-era code
path running in an environment without a live X connection (here: a Wayland/nested-Wayland session
where the backing Xwayland is itself crashing — see above — in the same time window). Research:
- libatspi's keycode-generation path (`spi_dec_x11_get_keycode` in
  `deviceeventcontroller-x11.c`) calls `XKeysymToKeycode()` as a direct, apparently unguarded Xlib
  call.
- at-spi2-core *has* previously fixed a related-but-distinct problem: in 2012,
  `at-spi2-registryd`'s own "can't open the X display" path was changed from `g_error()` (SIGABRT)
  to `g_warning()` + `exit(1)` (graceful) — but that fix was in the registry daemon's display-open
  code, not in libatspi's client-side `XKeysymToKeycode` call used for synthetic key generation,
  which is a different code path and still appears to assume a live X display unconditionally.
- I did not find an existing at-spi2-core issue tracking this specific `XKeysymToKeycode`
  NULL/stale-display segfault.

**Recommendation: worth reporting** against https://gitlab.gnome.org/GNOME/at-spi2-core — this is a
crash (SIGSEGV), not a graceful error, triggered by a now-common scenario (pure-Wayland or
nested-Wayland sessions where no X11 display is guaranteed to exist, which is exactly Omarchy's
default setup). It's the same class of robustness gap the registryd fix addressed 14 years ago, just
in a sibling code path that evidently never got the same treatment. The immediate trigger here is
specific to this sandbox (Xwayland dying mid-session), but the underlying defect — an unguarded
Xlib call with no check that a display connection still exists — is general and would reproduce any
time libatspi's key-generation path runs while its X connection is gone.

## Summary

- `OMARCHY_CRASH_IGNORE` alone cannot safely silence the QA harness: it matches executable basename
  only, and the harness crashes under the exact same binary names the real desktop uses.
- `ulimit -c 0` / `RLIMIT_CORE=0`, and `coredump.conf`'s `Storage=none`/`ProcessSizeMax=0`, do
  **not** stop the toast — confirmed from `core(5)`, `coredump.conf(5)`, and kernel source: when
  `core_pattern` is a pipe (it is, here), the kernel ignores `RLIMIT_CORE` except for the sentinel
  value `1`, and systemd-coredump still writes its journal entry regardless of storage settings.
- **Recommended:** launch the harness via
  `systemd-run --user --scope --unit=qa-harness --slice=qa-harness.slice -p LimitCORE=1 -- <cmd>`.
  `LimitCORE=1` hits a kernel-source-confirmed early return in `coredump_pipe()` that skips
  invoking systemd-coredump entirely — no journal entry, no toast, for anything in that process
  tree — while leaving the real desktop's crash reporting completely untouched. The
  scope/slice wrapping is free insurance for clean teardown and future unit-based filtering, even
  though it's not required for the suppression itself.
- Of the three crash signatures investigated: the Xwayland `FatalError`/`InitOutput` abort is a
  known, already-filed upstream xserver issue (not worth re-reporting); the quickshell
  `QInputMethod::commit` SIGSEGV and the libatspi `XKeysymToKeycode` SIGSEGV both look like genuine,
  not-yet-filed upstream bugs worth reporting (to quickshell-mirror/quickshell and
  gitlab.gnome.org/GNOME/at-spi2-core respectively), with the caveat that a minimal repro outside
  this specific sandbox would strengthen either report.
