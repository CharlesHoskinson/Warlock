# Crash-watcher noise: findings and proposed fix

Read-only research. Nothing on the machine was changed. Target: stop
window-integration-qa sandbox crash toasts without touching
`/usr/share/omarchy` or `/usr/bin`, while still notifying real desktop
crashes.

## 1. How `omarchy-crash-watch` actually filters today

`/usr/bin/omarchy-crash-watch` (Omarchy 4.0.4.legion-2):

- Tails `journalctl -f -n 0 -o json MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1`
  (the systemd-coredump message ID) and parses each entry with `jq`.
- Pulls exactly four fields out of each entry: `_UID`, `COREDUMP_COMM`,
  `COREDUMP_PID`, `COREDUMP_EXE`, `COREDUMP_SIGNAL_NAME`. Nothing else in the
  journal entry is ever looked at by the shipped script.
- Computes `name` = basename of `COREDUMP_EXE` if it's an absolute path,
  else falls back to the (15-char-truncated) `COREDUMP_COMM`.
- The **only** filter hook is `OMARCHY_CRASH_IGNORE`, an extended regex
  matched with `[[ $name =~ $ignore_pattern ]]` against that basename.
  Nothing else — no cgroup, no cwd, no cmdline, no environ — ever factors
  into the decision.
- Also hardcodes a self-exclusion: `name == omarchy-crash-*` or
  `omarchy-agent-*` is always skipped (string prefix, not regex).
- Per-name dedupe window (`OMARCHY_CRASH_DEDUPE_SECONDS`, default 60s),
  keyed on `name`, only armed after a toast is successfully delivered.
- On a pass, it shells out to `omarchy-notification-wait` (waits for the
  notification daemon to come back up, since the shell itself owns
  `org.freedesktop.Notifications` and a shell crash takes the daemon down
  with it) then `omarchy-notification-send ... --exec omarchy-agent-crash
  "$pid" "$comm" "$exe" "$signal"`.

`/usr/bin/omarchy-agent-crash` just re-looks-up `coredumpctl list $pid` for
a timestamp, builds a prompt, and `exec omarchy-agent --prompt "$prompt"`,
pointing the chosen agent at `$OMARCHY_PATH/default/agents/skills/diagnose-crash/SKILL.md`
for the actual triage method. It does not re-filter anything.

The user unit (`/usr/lib/systemd/user/omarchy-crash-watch.service`) is a
plain `Type=simple`, `Restart=always`, gated by
`ConditionEnvironment=WAYLAND_DISPLAY` and
`ConditionPathExists=!%h/.local/state/omarchy/toggles/crash-capture-off`
(the flag `omarchy-toggle-crash-capture` / the Trigger menu writes). The
existing user drop-in,
`~/.config/systemd/user/omarchy-crash-watch.service.d/ignore-dev.conf`, only
sets `Environment="OMARCHY_CRASH_IGNORE=^(node|npm|vitest|Hyprland)$"` — it
doesn't touch `ExecStart`.

**Key structural fact: `OMARCHY_CRASH_IGNORE` can only ever see a basename.**
It has no way to know *where* a process came from (sandbox terminal scope
vs. the real session), only *what it's called*. That's the whole problem.

## 2. What the overnight journal actually shows

`journalctl -o json MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1 --since
2026-09-30` returned **26 coredumps**. Full field set observed on these
entries (union across all 26):

```
CODE_FILE, CODE_FUNC, CODE_LINE, COREDUMP_BY_PIDFD, COREDUMP_CGROUP,
COREDUMP_CMDLINE, COREDUMP_CODE, COREDUMP_COMM, COREDUMP_CWD,
COREDUMP_DUMPABLE, COREDUMP_ENVIRON, COREDUMP_EXE, COREDUMP_FILENAME,
COREDUMP_GID, COREDUMP_HOSTNAME, COREDUMP_OPEN_FDS, COREDUMP_OWNER_UID,
COREDUMP_PACKAGE_JSON, COREDUMP_PID, COREDUMP_PIDFDID, COREDUMP_PROC_AUXV,
COREDUMP_PROC_CGROUP, COREDUMP_PROC_LIMITS, COREDUMP_PROC_MAPS,
COREDUMP_PROC_MOUNTINFO, COREDUMP_PROC_STATUS, COREDUMP_RLIMIT,
COREDUMP_ROOT, COREDUMP_SIGNAL, COREDUMP_SIGNAL_NAME, COREDUMP_SLICE,
COREDUMP_THREAD_NAME, COREDUMP_TID, COREDUMP_TIMESTAMP, COREDUMP_UID,
COREDUMP_UNIT, COREDUMP_USER_UNIT, ...
```
(No `COREDUMP_CONTAINER_CMDLINE` or any explicit sandbox/namespace marker
field exists — systemd-coredump doesn't expose one on this kernel/systemd.)

Breakdown by `COREDUMP_COMM` and where it came from:

| comm | count | `COREDUMP_USER_UNIT` / cgroup tail | cwd / cmdline | real or QA? |
|---|---|---|---|---|
| Hyprland | 3 | `app-Hyprland-xdg\x2dterminal\x2dexec-709acf58.scope` | `--config ~/window-integration-qa/nested_*.lua` | QA (nested compositor) |
| Xwayland | 12 | same `709acf58` scope | `Xwayland :1 -rootless -core ...` (generic argv, one with cwd under `~/window-behavior-spec/...`) | QA (nested Xwayland, display `:1`) |
| qs (quickshell) | 1 | same `709acf58` scope | `qs -p ~/.local/share/hypr-window-controls -d -n` | QA |
| xdg-desktop-por(tal) | 1 | same `709acf58` scope | `/usr/lib/xdg-desktop-portal-hyprland` (no args) | QA (portal on the sandbox's private bus) |
| python / python3 | 2 | same `709acf58` scope | `~/window-integration-qa/orca-reader/...`, `~/window-integration-qa/recovery-audit/keyboard-monitor/abi_client.py` | QA (Orca probes) |
| node-MainThread | 1 | different scope `app-Hyprland-xdg\x2dterminal\x2dexec-2c9bf0d8.scope` | cwd `~/src/willweb-lanes/INT/web`, vitest run | separate dev-lane noise, not the QA sandbox |
| npm exec vitest | 1 | same `2c9bf0d8` scope | same willweb-lanes vitest invocation | separate dev-lane noise |
| grim | 4 | `wayland-wm@hyprland.desktop.service` (session.slice, **not** a terminal-exec scope) | `/run/user/1000/hypr-window-previews/.capture.*.png` | **real desktop** (window-preview grim calls, genuinely crashing) |
| gnome-keyring-d | 1 | `gnome-keyring-daemon.service` (app.slice, not terminal-exec) | normal keyring env | **real desktop** |

So: **22 of 26** overnight coredumps share one literal cgroup scope,
`app-Hyprland-xdg\x2dterminal\x2dexec-709acf58.scope` — one single terminal
window in which the QA sandbox spun up its own nested Hyprland, its own
nested Xwayland (`:1`), its own quickshell instance, its own portal, and
its own Orca/python probes. That one scope is the entire "test-harness
blast radius" the user described. 2 more (node/npm vitest) are a
*different* terminal scope (`2c9bf0d8`) and a different directory
(`~/src/willweb-lanes/INT/web`) — real dev-lane noise, not the QA sandbox,
but still not worth a toast. The remaining 5 (4× grim, 1× gnome-keyring)
are the real desktop crashing in its own service units
(`wayland-wm@hyprland.desktop.service`, `gnome-keyring-daemon.service`),
never under any terminal-exec scope — these absolutely should keep
notifying (the grim crashes in particular look like a real, recurring bug
in window-preview capture worth investigating separately).

Other things checked and ruled out as filter signals:
- `COREDUMP_ENVIRON` is **null** on most of these entries (present only for
  `gnome-keyring-d`) — it's not reliably captured (likely permission /
  timing dependent), so no sandbox marker can be read from it. Don't build
  a filter on environ.
- `COREDUMP_ROOT` is `/` and `COREDUMP_SLICE` is `user-1000.slice` on
  *every* entry, QA or real — the nested session isn't run inside a mount
  or PID namespace systemd-coredump can see, so there's no root/namespace
  tell either.
- `COREDUMP_OPEN_FDS` shows real DRM render-node fds for the QA portal
  (`/dev/dri/renderD129`) — the nested compositor stack genuinely opens
  GPU devices, so nothing there flags it as fake either.

**The important negative result: the current `ignore-dev.conf` drop-in
(`^(node|npm|vitest|Hyprland)$`) only actually matches 5 of the 26
overnight crashes** (the 3 Hyprland + the node/npm-derived pair — their
`COREDUMP_EXE` resolves to the `node` binary either way, so both match
`node`, not `npm`). It does **not** match Xwayland (12!), qs, the portal,
or python — i.e. it misses 17 of 26, including the bulk of the noise. That
matches the user's report that toasts kept firing overnight despite the
drop-in already being in place.

Also worth flagging as a latent risk in the *current* drop-in even where it
does match: `node`, `npm`, and (if ever added) `python`/`qs`/`Xwayland` are
extremely generic basenames. A blanket `OMARCHY_CRASH_IGNORE` entry for any
of them silences that binary **everywhere on the machine**, not just in the
sandbox — e.g. it would equally swallow a genuine crash of a real
Electron/node app, or (if someone added `qs`/`Xwayland` to the regex to
plug today's gap) a real quickshell segfault on the actual bar, or a real
Xwayland crash on `:0`. Name-only matching cannot express "ignore this
binary only when it's the sandbox's copy."

## 3. Upstream (basecamp/omarchy, now continued at `omacom/omarchy`)

Note: the repo appears to have been renamed/forked from `basecamp/omarchy`
to `omacom/omarchy` at some point; current issues/PRs live under
`omacom/omarchy`.

Relevant prior art found in open issues/PRs (none of this is in our
installed 4.0.4.legion-2):

- **PR #11569** ("Skip Electron utility subprocess crashes in crash-watch")
  — adds a *cmdline*-based filter (`COREDUMP_CMDLINE` contains
  `--type=utility`) alongside the name filter. Confirms the maintainers are
  willing to key filtering off fields beyond the basename, on a
  case-by-case basis, hardcoded rather than via a new env knob.
- **Issue #10662** ("self-exclusion guard matches process names, but its
  own health check crashes as `quickshell`") — the fix proposed *in the
  issue itself* is: "adding `COREDUMP_USER_UNIT` to that extraction and
  skipping any crash originating from its own unit would close the loop by
  provenance rather than by name." This is exactly the
  cgroup/unit-provenance approach this report recommends, already
  recognized upstream as the right fix for a closely analogous problem
  (self-notification loop vs. our sandbox-noise problem — same root cause:
  name-only filtering can't express "this instance, not that instance").
- **Issue #11992** ("announces the crash its own dispatched agent just
  reproduced") — proposes having `omarchy-agent-crash` export a marker into
  the agent's environment and having `omarchy-crash-watch` skip coredumps
  whose `COREDUMP_CGROUP` is that agent's scope. Again cgroup-based, not
  merged, no env var name settled.
- **PR #13835** ("Mute crash toasts while diagnosis is in flight") — ended
  up using a **session lock file** (held for the agent's lifetime) rather
  than cgroup or env markers — a different, narrower problem (same
  program's own re-crash during diagnosis) but shows the project has
  multiple provenance-filtering mechanisms in flight for different
  sub-problems.
- A newer `omarchy crash mute <name>` command exists in later
  branches/versions (`omarchy crash mute hyprland`, `... off`, bare to
  list) — but it's still explicitly **name-based** ("accepts the binary's
  path or name"), with the same generic-basename blast-radius problem as
  `OMARCHY_CRASH_IGNORE`, and it is not present in 4.0.4.legion-2
  (`omarchy crash` here reports no documented subcommands).

**Conclusion: nothing upstream, released or proposed, does cwd/cmdline or
durable cgroup-scope filtering today.** The maintainers have repeatedly
reached for cgroup/unit provenance as the right fix for "same binary name,
different instance" problems, but no `OMARCHY_CRASH_IGNORE_CGROUP` /
`OMARCHY_CRASH_IGNORE_CWD`-style knob exists yet. This is a legitimate
upstream feature request, not a one-off need — issue #10662 and #11992
already establish the precedent and vocabulary (`COREDUMP_USER_UNIT`,
`COREDUMP_CGROUP`) a new issue could point to directly.

## 4. Recommended design

### Why a user-level wrapper, not just a richer `OMARCHY_CRASH_IGNORE` value

`OMARCHY_CRASH_IGNORE` cannot express provenance at all — it only ever sees
a basename — so no regex value fixes this. The literal cgroup scope ID
(`709acf58`) is a dead end too: it's a random suffix systemd mints fresh
*per terminal window spawn* (`app-Hyprland-xdg\x2dterminal\x2dexec-<id>.scope`),
so hardcoding it would need updating every time the QA harness is relaunched
in a new terminal — not durable. The only way to get cgroup/cwd-aware
filtering without editing `/usr/bin/omarchy-crash-watch` is to replace what
`ExecStart` runs.

### Proposed filter logic (in priority order, inside a new local script)

1. Keep the existing self-exclusion (`omarchy-crash-*` / `omarchy-agent-*`).
2. Keep `OMARCHY_CRASH_IGNORE` (name-based) as-is for the already-accepted
   blunt cases — it's still useful as a cheap first filter and the user has
   already decided the collateral risk for `node`/`npm`/`vitest` is
   acceptable. Hyprland can stay in it too, belt-and-suspenders, now that
   rule 3 below also covers it more precisely.
3. **New: provenance rule.** If `COREDUMP_USER_UNIT` matches a terminal-exec
   app scope (`^app-.*-xdg\\x2dterminal\\x2dexec-.*\\.scope$`) **and** the
   basename is one of the nested-compositor-stack binaries that this
   desktop's real copies never run under a terminal scope — `Hyprland`,
   `Xwayland`, `qs`, `quickshell`, `xdg-desktop-portal-hyprland`,
   `xdg-desktop-portal` — ignore it. This is durable (no scope ID baked in)
   and covers the Hyprland/Xwayland/qs/portal noise (21 of the 22
   `709acf58` crashes) regardless of which terminal window or scope ID the
   sandbox uses next time. It's safe because the *real* versions of these
   binaries on this machine run under `wayland-wm@hyprland.desktop.service`
   or directly under `graphical-session.target`'s own app scopes for
   dbus-activated services, confirmed from the journal — never under an
   interactively-opened terminal's scope.
4. **New: path rule**, for the binaries rule 3 deliberately doesn't cover
   by name (`python`/`python3`, since Hermes itself is python and must keep
   notifying for real crashes). If `COREDUMP_CWD` or `COREDUMP_CMDLINE`
   contains a configurable sandbox-root pattern, ignore it. Default pattern
   covers `~/window-integration-qa` and the sibling `~/window-behavior-spec`
   seen in one stray Xwayland cwd; expose it as a new env var
   (`OMARCHY_CRASH_IGNORE_PATH`) so future QA repos can be added without
   editing the script again.
5. Anything else — including a real Xwayland/qs/portal/Hyprland/python
   crash in the user's actual session, and the `grim`/`gnome-keyring-d`
   crashes seen overnight — falls through unchanged and still gets the
   full `omarchy-notification-wait` → `omarchy-notification-send --exec
   omarchy-agent-crash` treatment, identical to stock behavior.

### Mechanics

- Put the script at `~/.local/bin/omarchy-crash-watch` (new file, not
  touching the system one).
- Override the unit's `ExecStart` via a drop-in at
  `~/.config/systemd/user/omarchy-crash-watch.service.d/override.conf`:
  ```ini
  [Service]
  ExecStart=
  ExecStart=%h/.local/bin/omarchy-crash-watch
  ```
  (empty `ExecStart=` first to clear the inherited one, per systemd
  drop-in semantics.) The existing `ignore-dev.conf` can stay as-is
  alongside it, or its `Environment=` line can be folded into the same
  drop-in — either works since systemd merges all `.d/*.conf` files.
- The wrapper reuses the existing small utilities
  (`omarchy-notification-wait`, `omarchy-notification-send`,
  `omarchy-default-agent`, `omarchy-agent-crash`) rather than
  reimplementing notification delivery — those are stable, separately
  invocable `/usr/bin/*` scripts, so only the filter predicate and the
  `journalctl -f` orchestration loop need to be forked.

### Trade-offs

- **Pro:** fully within `~/.config` and `~/.local` — no edits to
  `/usr/share/omarchy` or `/usr/bin`, survives `pacman -Syu` /
  `omarchy update` untouched (a package update can't overwrite a user
  drop-in or a file under `~/.local/bin`).
- **Con:** it's a fork of the orchestration loop, not a patch — an upstream
  bugfix to `/usr/bin/omarchy-crash-watch` (e.g. the dedupe/notification-wait
  fixes or the Electron `--type=utility` filter found in the issues above)
  won't automatically apply to the local copy. Mitigate by commenting the
  fork with the package version it was taken from
  (`omarchy 4.0.4.legion-2`) and diffing
  `/usr/bin/omarchy-crash-watch` against it after any `omarchy update`.
- **Con:** rule 3's binary allowlist (`Hyprland`, `Xwayland`, `qs`,
  `quickshell`, `xdg-desktop-portal*`) needs a manual add if the QA harness
  starts spawning some other compositor-stack component under the terminal
  scope (e.g. a second `wireplumber` or `pipewire` test instance) — it's
  not a fully general rule, just general enough to survive scope-ID churn
  for the binaries actually observed.
- **Also worth doing independently:** file the upstream feature request
  (`OMARCHY_CRASH_IGNORE_CGROUP` and/or `OMARCHY_CRASH_IGNORE_CWD`,
  ERE against `COREDUMP_USER_UNIT`/`COREDUMP_CGROUP` and
  `COREDUMP_CWD`/`COREDUMP_CMDLINE` respectively) against
  `omacom/omarchy`, citing issues #10662 and #11992 as precedent that the
  maintainers already consider cgroup-based filtering the correct fix for
  this class of problem. If it lands, the local wrapper can be retired in
  favor of two `Environment=` lines in a drop-in, which is strictly less
  to maintain.

## 5. Draft script

```bash
#!/bin/bash
# ~/.local/bin/omarchy-crash-watch
#
# Forked from /usr/bin/omarchy-crash-watch as shipped in
# omarchy 4.0.4.legion-2, 2026-10-01. Diff against the system copy after
# any `omarchy update` / `pacman -Syu` and re-port upstream fixes by hand.
#
# Adds two filter dimensions the stock script can't express (it only ever
# sees a basename via OMARCHY_CRASH_IGNORE): cgroup/unit provenance and
# cwd/cmdline path, so a sandboxed nested-compositor test harness (e.g.
# ~/window-integration-qa) can be silenced without also silencing real
# crashes of the same-named binaries in the actual desktop session.

set -uo pipefail

readonly COREDUMP_MESSAGE_ID=fc2e22bc6ee647b6b90729ab34a250b1
readonly CRASH_GLYPH=$'\U000f16a1'
readonly dedupe_seconds=${OMARCHY_CRASH_DEDUPE_SECONDS:-60}
readonly ignore_pattern=${OMARCHY_CRASH_IGNORE:-}

# New knobs, not present upstream.
# Basenames whose *real* copies on this machine never run as a child of an
# interactively-opened terminal scope — only a nested/test instance does.
readonly ignore_scope_names=${OMARCHY_CRASH_IGNORE_SCOPE_NAMES:-^(Hyprland|Xwayland|qs|quickshell|xdg-desktop-portal.*)$}
# A terminal-launched app scope, any id.
readonly terminal_scope_pattern='^app-.*-xdg\\x2dterminal\\x2dexec-.*\.scope$'
# cwd/cmdline substrings that mark a known QA/test sandbox tree.
readonly ignore_path_pattern=${OMARCHY_CRASH_IGNORE_PATH:-/window-integration-qa|/window-behavior-spec}

declare -A last_notified

announce() {
  local comm=$1 pid=$2 exe=$3 signal=$4
  omarchy-notification-wait || return 1
  omarchy-notification-send \
    --urgency critical \
    --glyph "$CRASH_GLYPH" \
    "Process crashed: $comm" \
    "Click to diagnose with AI" \
    --exec omarchy-agent-crash "$pid" "$comm" "$exe" "$signal"
}

journalctl -f -n 0 -o json "MESSAGE_ID=$COREDUMP_MESSAGE_ID" 2>/dev/null |
  while IFS= read -r entry; do
    IFS=$'\t' read -r uid comm pid exe signal user_unit cwd cmdline < <(
      jq -r '[(._UID // "-"),
              (.COREDUMP_COMM // "-"),
              (.COREDUMP_PID // "-"),
              (.COREDUMP_EXE // "-"),
              (.COREDUMP_SIGNAL_NAME // "-"),
              (.COREDUMP_USER_UNIT // "-"),
              (.COREDUMP_CWD // "-"),
              (.COREDUMP_CMDLINE // "-")] | @tsv' <<<"$entry" 2>/dev/null
    )

    [[ $pid =~ ^[0-9]+$ ]] || continue
    [[ -n $(omarchy-default-agent) ]] || continue
    [[ $uid =~ ^[0-9]+$ ]] || continue
    ((uid == UID)) || continue

    name=$comm
    [[ $exe == /* ]] && name=${exe##*/}

    [[ -n $ignore_pattern && $name =~ $ignore_pattern ]] && continue
    [[ $name == omarchy-crash-* || $name == omarchy-agent-* ]] && continue

    # Provenance: known compositor-stack binary, running as a child of a
    # terminal scope -> it's a nested/test instance, not the real one.
    if [[ $user_unit =~ $terminal_scope_pattern && $name =~ $ignore_scope_names ]]; then
      continue
    fi

    # Path: cwd or cmdline under a known sandbox tree.
    if [[ -n $ignore_path_pattern ]] &&
       { [[ $cwd =~ $ignore_path_pattern ]] || [[ $cmdline =~ $ignore_path_pattern ]]; }; then
      continue
    fi

    now=$EPOCHSECONDS
    (((now - ${last_notified[$name]:-0}) < dedupe_seconds)) && continue
    announce "$name" "$pid" "$exe" "$signal" && last_notified[$name]=$now
  done
```

Drop-in to install it (not applied — read-only task):

```ini
# ~/.config/systemd/user/omarchy-crash-watch.service.d/override.conf
[Service]
ExecStart=
ExecStart=%h/.local/bin/omarchy-crash-watch
```

then `chmod +x ~/.local/bin/omarchy-crash-watch && systemctl --user
daemon-reload && systemctl --user restart omarchy-crash-watch.service`.

## 6. Verification plan (for whoever applies this)

- Re-run last night's workload (or just `coredumpctl list` the same 22 QA
  PIDs) and confirm no toast fires for any of them, while deliberately
  crashing something real (e.g. `kill -SEGV` a throwaway real-session
  `qs`/foot window, or just wait for the next genuine `grim` crash) still
  produces a toast.
- `journalctl --user -u omarchy-crash-watch -f` while testing, to see the
  loop's own stderr/behavior live.
- Confirm `coredumpctl list` itself is untouched — this only changes
  whether a toast fires, never whether the crash is captured/inspectable.
