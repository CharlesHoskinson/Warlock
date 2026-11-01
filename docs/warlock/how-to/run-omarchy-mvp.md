# Run the standalone Warlock UI MVP window on stock Omarchy

This how-to describes the Root-serialized procedure to build, stage, launch, and
collect external evidence for the single-window GTK4/WebKitGTK 6 Warlock beta UI
(`Warlock.Ui.Mvp` + `warlock-ui-owner` + `warlock-ui-backend` + Elm `HttpMain` /
`HttpBar` / `HttpPopup`) on the stock Omarchy Wayland guest (`Virtual-1`,
`1280x800`).

> [!IMPORTANT]
> **Honesty, `NOT-RUN` status, and gate boundaries**
> - **Source-only (`NOT-RUN` in worker wave)**: `Warlock/Ui/Mvp.hsc` and `tools/omarchy_ui_mvp.py` were authored and audited in source only without worker-side compiler, test, Quint, or VM execution. Every behavioral step below describes what the integrated source is **intended** to do once Root compiles and runs it.
> - **100% Elm GUI**: `Warlock.Ui.Mvp` creates an undecorated `GtkWindow` (`gtk_window_set_decorated 0`) with zero GTK headerbar, title label, or GTK buttons. Every visible GUI element and text node is rendered by Elm (`HttpBar.elm` and `HttpPopup.elm`). `tools/omarchy_ui_mvp.py` is a non-shipping QA/staging helper.
> - **Zero fabricated observations or bindings**: `Warlock.Ui.Mvp` emits nothing while unmapped, emits `viewProtocol: 1` (`views: [scope]`) when `GdkSurface` has positive mapped dimensions before GDK observes a valid `GdkMonitor`, upgrades to `viewProtocol: 2` (`locations: [{scope, box}]`) only when `gdk_display_get_monitor_at_surface` reports a valid non-overflowing positive `GdkMonitor` rectangle, observes physical `Escape` in `GTK_PHASE_CAPTURE` while returning `0` (`GDK_EVENT_PROPAGATE`) so normal typing/IME composition reaches WebKit untouched, and commits `MvpStepState` transactionally per accepted `Owner` event.
> - **Trusted standalone attachment (`applicationAttachment: true`)**: When `backend.json` carries `"applicationAttachment": true` (omitted defaults to `false`), the initial GDK topology is intended to cause `HttpMain` (`OutputController`) to POST a valid presentation-only `view-commit` (`requests: []`) to `Warlock.Backend`. `Warlock.Backend` is wired to reply once with `protocolVersion: 3`, `kind: "application-attached"`, `nativeOperations: []` over the existing `native-event` gateway, transitioning `Shell.elm` to `applicationOnly = True`, `phase = Reconciling` (`Shell.available == False`) so Applications catalog browsing, search filtering, pin toggling, and refresh can operate while compositor window/workspace controls stay explicitly disabled.
> - **Unqualified engine retirement & retained CPU runtime failures preserved**: `EngineResult` in `Warlock.Ui.WebKit` remains `EngineResult False False` (`CallbackPending`, `ProviderUnqualified`, and retained filter-store directories), and `HOSTSTOP2` / original failure records remain preserved. The previous native MVP remains unqualified, and the latest offline Haskell `--ui-origin` CPU run (`.warlock-contributor/haskell-cpu-1793524578237302360/report.json`) retains **two CPU runtime suite failures** (`warlock-runtime:test:ui-origin-controls` exit `1` on public-library frame/IO boundary & independent cleanup, and `warlock-runtime:test:ui-webkit-controls` exit `127` on host runtime `libjavascriptcoregtk-6.0.so.1` lookup) alongside five passing CPU suites (`ui-mvp-controls`, `ui-engine-controls`, `ui-private-network-controls`, `ui-display-controls`, `desktop-boundary-controls`). `warlock-ui-owner` and `warlock-ui-backend` are expected to exit non-zero with `"passed":false,"nativeAccepted":false,"releaseAccepted":false` even after serving live callbacks and catalog/pin operations.
> - **Not acceptance**: Native-on-VM execution is component/beta evidence only. It is neither a protected host QA campaign (`loop.py check` / `qa_run.py`) nor ARC024, DEL014, AT/IME, or original 242-requirement / 417-scenario release acceptance.

## Prerequisites

1. **Integrated source state & six-root Elm closure (`UI007` included)**:
   - **Six owning Elm roots** (`implementation/warlock/elm.json` + 73-module transitive import closure in `implementation/warlock/src/`): port-based `Main.elm`, `Bar.elm`, `Popup.elm` and HTTP-backed `HttpMain.elm`, `HttpBar.elm`, `HttpPopup.elm`. Product `UI007` adds mandatory `implementation/warlock/src/StatusScroll.elm` and updates `Bar.elm`, `HttpBar.elm`, and `SurfaceRenderer.elm` (transitively imported by `Bar`, `Popup`, `HttpBar`, and `HttpPopup`). Offline package closure is pinned by `implementation/warlock-preview-provider-v143/qa/toolchain.json` (`elmHome` 7 core/browser/html/json/time/url/virtual-dom packages) plus `tools/elm-http-dependencies.json` (`elm/http 2.0.0`, `elm/bytes 1.0.8`, `elm/file 1.0.5`).
   - `implementation/warlock/haskell/runtime/runtime.cabal`: `Warlock.Ui.Mvp` listed in `other-modules` for `warlock-ui-owner`, `ui-security-child`, and `ui-webkit-controls` (and exercised in `ui-mvp-controls`).
   - `Warlock.Backend`, `Warlock.Protocol.Desktop`, and `Shell.elm`: `applicationAttachment` (`Bool`, default `False`), `ApplicationAttached` (`protocolVersion: 3`, `nativeOperations: []`), and `Shell.applicationOnly` integrated.
   - `Warlock.Ui.Owner` & `Warlock.Ui.WebKit`: `UiEndpoints.uiLastProjection` wired into `stepMvpWindow mvp (readMvpLease (uiLastProjection endpoints)) ownerEvent` and `handleMvpDispatch` (dropping only `Left "stale native UI projection"` as non-fatal while escalating any other `Owner` error).
2. **Omarchy guest readiness** (`/home/charl/vm/omarchy/AGENTS.md`):
   - Stock Omarchy 4.0.6 (`Hyprland 0.56.2`, `wayland-1`, `/run/user/1000`). Note: the base guest image inventories `webkit2gtk-4.1` and `gtk3`; building and running `warlock-ui-owner` inside the guest additionally requires guest `ghc`, `cabal`, `gtk4`, and `webkitgtk-6.0` development packages matching the guest ABI (`pkg-config --exists gtk4 webkitgtk-6.0`).
   - Run all VM helper scripts from `/home/charl/vm/omarchy` (`./ssh.sh`, `./vm-wake.sh`, `./vm-unlock.sh`).
   - Never read or print `/home/charl/vm/omarchy/credentials.txt` or password helpers into stdout, logs, or artifacts.
   - Use Omarchy's builtin shell IPC (`OMARCHY_PATH=/usr/share/omarchy omarchy-shell ...`), never `hyprlock`, `hypridle`, or `makoctl`.

## Step 1: Run protected host build checks and record the source manifest

From the host workspace (Root only). Running `check_haskell_cpu.py --ui-origin`
inside `qa_run.py` compiles the offline Elm HTML documents (`HttpMain.html`,
`HttpBar.html`, `HttpPopup.html` via `tools/ui_backend_frontend.py:prepare`) and
runs the offline Haskell UI-origin build and control suites:

```bash
cd /home/charl/code/Warlock
python3 -B docs/warlock-build-loop/v2/loop.py check
python3 -B window-integration-qa/qa_run.py -- python3 -B tools/check_haskell_cpu.py --ui-origin

EVIDENCE_DIR=/home/charl/vm/omarchy/evidence/warlock-ui-mvp-20261101
mkdir -p "$EVIDENCE_DIR"
chmod 0700 "$EVIDENCE_DIR"
python3 -B /home/charl/code/Warlock/tools/omarchy_ui_mvp.py source-manifest \
  --repo-root /home/charl/code/Warlock \
  --output "$EVIDENCE_DIR/source-manifest.json"
```

## Step 2: Verify `UI007` `StatusScroll.elm` freshness and stage Elm HTML + 6-package Haskell workspace to the guest

Verify that the latest `haskell-cpu-*` frontend directory includes `UI007`
`StatusScroll.elm` and matches all current `.elm` source digests and `elm.json`
(refusing stale pre-UI007 artifacts such as `haskell-cpu-1793524578237302360`),
then stage `HttpMain.html`, `HttpBar.html`, `HttpPopup.html` plus the complete
6-package Cabal workspace listed in `implementation/warlock/haskell/cabal.project`:

```bash
EVIDENCE_DIR=/home/charl/vm/omarchy/evidence/warlock-ui-mvp-20261101
CPU_REPORT_DIR="$(ls -1dt /home/charl/code/Warlock/.warlock-contributor/haskell-cpu-* | head -n 1)"
FRONTEND_DIR="$CPU_REPORT_DIR/haskell-build/frontend"

python3 -B - "$CPU_REPORT_DIR/report.json" "$FRONTEND_DIR" <<'PY'
import hashlib, json, pathlib, sys
repo = pathlib.Path("/home/charl/code/Warlock")
report = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
frontend = pathlib.Path(sys.argv[2])
ui_fe = report["build"]["uiFrontend"]
recorded_src = ui_fe["sourceHashes"]
if "StatusScroll.elm" not in recorded_src:
    raise SystemExit("Refusing stale FRONTEND_DIR missing UI007 StatusScroll.elm; rerun check_haskell_cpu.py --ui-origin first")
for elm_file in sorted((repo / "implementation/warlock/src").rglob("*.elm")):
    rel = str(elm_file.relative_to(repo / "implementation/warlock/src"))
    actual = hashlib.sha256(elm_file.read_bytes()).hexdigest()
    if recorded_src.get(rel) != actual:
        raise SystemExit("Refusing stale FRONTEND_DIR: " + rel + " hash mismatch")
elm_json_sha = hashlib.sha256((repo / "implementation/warlock/elm.json").read_bytes()).hexdigest()
if ui_fe["fileHashes"].get("implementation/warlock/elm.json") != elm_json_sha:
    raise SystemExit("Refusing stale FRONTEND_DIR: elm.json hash mismatch")
for role, doc in (("controller", "HttpMain.html"), ("bar", "HttpBar.html"), ("popup", "HttpPopup.html")):
    doc_sha = hashlib.sha256((frontend / doc).read_bytes()).hexdigest()
    if ui_fe["documents"][role]["sha256"] != doc_sha:
        raise SystemExit("Frontend artifact digest mismatch for " + doc)
PY

tar -C /home/charl/code/Warlock -czf "$EVIDENCE_DIR/warlock-mvp-stage.tar.gz" \
  implementation/warlock/haskell/cabal.project \
  implementation/warlock/haskell/held-document \
  implementation/warlock/haskell/process-custody \
  implementation/warlock/haskell/protocol \
  implementation/warlock/haskell/elf-observation \
  implementation/warlock/haskell/runtime \
  implementation/warlock/haskell/native-authority \
  tools/omarchy_ui_mvp.py

(cd /home/charl/vm/omarchy && ./ssh.sh 'mkdir -p /tmp/warlock-mvp-src /tmp/warlock-mvp-assets && rm -rf /tmp/warlock-mvp-src/* /tmp/warlock-mvp-assets/*')
(cd /home/charl/vm/omarchy && ./ssh.sh \
  'cat > /tmp/warlock-mvp-stage.tar.gz && tar -xzf /tmp/warlock-mvp-stage.tar.gz -C /tmp/warlock-mvp-src') \
  < "$EVIDENCE_DIR/warlock-mvp-stage.tar.gz"

for DOC in HttpMain.html HttpBar.html HttpPopup.html; do
  (cd /home/charl/vm/omarchy && ./ssh.sh "cat > /tmp/warlock-mvp-assets/$DOC") < "$FRONTEND_DIR/$DOC"
done
```

## Step 3: Build `warlock-ui-owner` and `warlock-ui-backend` offline against the guest ABI

Never copy host-linked GTK/WebKit ELF binaries across incompatible system ABIs;
build `warlock-ui-owner` and `warlock-ui-backend` offline (`--offline`,
`active-repositories: :none`) inside the guest against its installed `gtk4` and
`webkitgtk-6.0` libraries using the three staged local dependency directories in
`~/warlock-mvp-dependencies-20261101` (`network-3.2.0.0`,
`cryptohash-sha256-0.11.102.1`, `hsc2hs-0.68.10`):

```bash
(cd /home/charl/vm/omarchy && ./ssh.sh 'set -euo pipefail
  command -v ghc cabal pkg-config >/dev/null
  pkg-config --exists gtk4 webkitgtk-6.0
  DEPS_ROOT="$HOME/warlock-mvp-dependencies-20261101"
  CABAL_WORK="/tmp/warlock-mvp-cabal"
  rm -rf "$CABAL_WORK"
  mkdir -m 0700 "$CABAL_WORK" "$CABAL_WORK/cabal-home" "$CABAL_WORK/repo-cache"
  cat > "$CABAL_WORK/cabal.config" <<EOF
remote-repo-cache: $CABAL_WORK/repo-cache
store-dir: $CABAL_WORK/store
active-repositories: :none
EOF
  HS_SRC="/tmp/warlock-mvp-src/implementation/warlock/haskell"
  cp -f "$HS_SRC/cabal.project" "$HS_SRC/mvp.project"
  FOUND_DEPS=0
  for CABAL_FILE in "$DEPS_ROOT"/*/*.cabal; do
    if [ ! -f "$CABAL_FILE" ]; then
      echo "No staged .cabal packages found under $DEPS_ROOT" >&2
      exit 2
    fi
    printf "packages: %s\n" "$(dirname "$CABAL_FILE")" >> "$HS_SRC/mvp.project"
    FOUND_DEPS=$((FOUND_DEPS + 1))
  done
  if [ "$FOUND_DEPS" -lt 3 ]; then
    echo "Expected 3 staged local dependency packages under $DEPS_ROOT, found $FOUND_DEPS" >&2
    exit 2
  fi
  cat >> "$HS_SRC/mvp.project" <<EOF
active-repositories: :none
package network
  tests: False
  benchmarks: False
package cryptohash-sha256
  tests: False
  benchmarks: False
package hsc2hs
  tests: False
  benchmarks: False
EOF
  export GHC_ENVIRONMENT=- CABAL_DIR="$CABAL_WORK/cabal-home"
  cd "$HS_SRC"
  if command -v hsc2hs >/dev/null 2>&1; then
    HSC2HS_BIN="$(command -v hsc2hs)"
  else
    cabal --config-file="$CABAL_WORK/cabal.config" build --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist-tools" hsc2hs:exe:hsc2hs
    HSC2HS_BIN="$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist-tools" hsc2hs:exe:hsc2hs)"
  fi
  cabal --config-file="$CABAL_WORK/cabal.config" build --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" --with-hsc2hs="$HSC2HS_BIN" warlock-runtime:exe:warlock-ui-owner warlock-runtime:exe:warlock-ui-backend
  cp -f "$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" warlock-runtime:exe:warlock-ui-owner)" /tmp/warlock-mvp-assets/warlock-ui-owner
  cp -f "$(cabal --config-file="$CABAL_WORK/cabal.config" list-bin --offline --project-file="$HS_SRC/mvp.project" --builddir="$CABAL_WORK/dist" warlock-runtime:exe:warlock-ui-backend)" /tmp/warlock-mvp-assets/warlock-ui-backend
  chmod 0755 /tmp/warlock-mvp-assets/warlock-ui-owner /tmp/warlock-mvp-assets/warlock-ui-backend')
```

## Step 4: Prepare Omarchy desktop state, generate `0600` pins (`D <= 28s`), and launch

`Warlock.Capture.Process.Internal` enforces a non-renewable `CLOCK_MONOTONIC`
admission deadline `D <= 30.0s` (`30_000_000_000` ns). Always create a fresh
`0700` `$RUN_DIR` (`mkdir -m 0700 "$RUN_DIR"`, without `-p`, so collisions fail
closed before shell stdout redirection) and run `omarchy_ui_mvp.py guest-config`
inside the guest immediately before invoking `warlock-ui-backend`. `guest-config`
opens the existing `0700` `$RUN_DIR` via `O_DIRECTORY | O_NOFOLLOW` (`fstat`
uid/mode verified), verifies `fstat` fingerprints before and after reads, writes
`"applicationAttachment": true` into `backend.json` (with no browser marker in
`ui.json`), and mirrors non-symlink `.desktop` files via held descriptors only
if a catalog root contains symlinks that `Warlock.Backend.Store` would refuse.

Do **not** set `WEBKIT_*` or proxy environment variables; `Warlock.Ui.WebKit`
explicitly rejects them.

```bash
(cd /home/charl/vm/omarchy && ./vm-wake.sh)
(cd /home/charl/vm/omarchy && ./ssh.sh 'set -euo pipefail
  export OMARCHY_PATH=/usr/share/omarchy LANG=C.UTF-8 LC_ALL=C.UTF-8
  export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1

  if [ "$(omarchy-shell lock isLocked)" != "false" ]; then
    echo "Omarchy desktop is locked; unlock before running headed UI" >&2
    exit 2
  fi

  ORIG_IDLE="$(omarchy-shell idle status || true)"
  restore_idle() {
    if echo "$ORIG_IDLE" | grep -qi "enabled"; then
      omarchy-shell idle enable >/dev/null 2>&1 || true
    fi
  }
  trap restore_idle EXIT
  omarchy-shell idle disable >/dev/null 2>&1 || true
  omarchy-shell notifications dismissAll >/dev/null 2>&1 || true

  RUN_DIR="/tmp/warlock-mvp-run-$(date +%s)-$$"
  mkdir -m 0700 "$RUN_DIR"
  python3 -B /tmp/warlock-mvp-src/tools/omarchy_ui_mvp.py guest-config \
    --run-dir "$RUN_DIR" \
    --duration-seconds 25 \
    --controller-html /tmp/warlock-mvp-assets/HttpMain.html \
    --bar-html /tmp/warlock-mvp-assets/HttpBar.html \
    --popup-html /tmp/warlock-mvp-assets/HttpPopup.html \
    --ui-owner-bin /tmp/warlock-mvp-assets/warlock-ui-owner \
    --ui-backend-bin /tmp/warlock-mvp-assets/warlock-ui-backend \
    --catalog-root /usr/share/applications \
    > "$RUN_DIR/guest-config.stdout"

  hyprctl clients -j > "$RUN_DIR/hyprctl-clients-before.json" 2>/dev/null || true

  set +e
  /tmp/warlock-mvp-assets/warlock-ui-backend "$RUN_DIR/backend.json" \
    > "$RUN_DIR/backend.stdout" 2> "$RUN_DIR/backend.stderr" &
  BACKEND_PID=$!

  sleep 4
  hyprctl clients -j > "$RUN_DIR/hyprctl-clients-live.json" 2>/dev/null || true
  grim "$RUN_DIR/01-window-initial.png" 2>/dev/null || true

  wait "$BACKEND_PID"
  BACKEND_RC=$?
  set -e

  pgrep -af "warlock-ui-(backend|owner)" > "$RUN_DIR/lingering-procs.txt" || true
  python3 -B /tmp/warlock-mvp-src/tools/omarchy_ui_mvp.py evaluate-run \
    --run-dir "$RUN_DIR" \
    --backend-stdout "$RUN_DIR/backend.stdout" \
    --backend-exit-code "$BACKEND_RC" \
    --output "$RUN_DIR/mvp-run-receipt.json"
  printf "%s\n" "$RUN_DIR"')
```

## Step 5: Drive pointer/keyboard interactions and collect external evidence

1. Diff `hyprctl-clients-before.json` and `hyprctl-clients-live.json` (matching the
   child `warlock-ui-owner` PID) to read actual compositor geometry
   `(at: [x, y], size: [w, h])`. Because the window is undecorated (`decorated = 0`),
   the top `72px` of the client surface is intended to display the Elm `HttpBar`
   strip and the remainder the Elm `HttpPopup` workspace.
2. Send QMP pointer motion, button-down, and button-up in **separate**
   `python3 -I qmp.py cmd ...` invocations from `/home/charl/vm/omarchy` with a
   short pause (`0.08s`), always releasing buttons in a `finally` block.
3. Capture Wayland `grim` PNGs and host QMP `shot` frames into
   `/home/charl/vm/omarchy/evidence/warlock-ui-mvp-20261101/` covering:
   - Initial mapped Elm bar + disabled window-effect controls.
   - Opened Applications catalog populated from stock Omarchy `.desktop` entries.
   - Live query filtering, pin toggle (`pins/taskbar.json`), physical `Escape` popup dismiss, and explicit refresh.
   - `UI007` bar status scrollport (`StatusScroll.elm` / `HttpBar.elm` / `SurfaceRenderer.elm`): verify the inner status scrollport (`id="warlock-bar-status-scroll-<epoch>"`, `tabindex="0"` when status is non-idle) at default `1120x680` on `1280x800` and under narrow width reflow (e.g. `621px` width via compositor tile/resize), confirming full long-status reachability via horizontal keyboard/pointer scroll without overlapping bar action buttons, scroll-offset retention across unchanged status publications, and monotonic `<epoch>` advance + `(0, 0)` viewport reset when status text changes.
4. Copy `mvp-guest-manifest.json`, `mvp-run-receipt.json`, `backend.stdout`,
   `backend.stderr`, `hyprctl-clients-before.json`, `hyprctl-clients-live.json`,
   `lingering-procs.txt`, and `pins/taskbar.json` from `$RUN_DIR` into
   `/home/charl/vm/omarchy/evidence/warlock-ui-mvp-20261101/`.

## Intended outcomes to verify (unrun; awaiting Root execution)

- `hyprctl-clients-live.json` is intended to record the mapped undecorated `warlock-ui-owner` client on `Virtual-1`.
- `backend.stdout` (`backendResultJson`) is intended to record `callbacks >= 1` (initial topology presentation-only commit triggering `application-attached` once, followed by user commits) and `operations >= 1` (`CatalogRead` / `PinsWrite`), with `"nativeAccepted":false,"releaseAccepted":false`.
- `backendExitCode` is expected to remain `1` (`"passed":false`) because `Warlock.Ui.WebKit` honestly reports `EngineResult False False` until WebKit filter-store callback retirement and provider confinement are independently qualified.
- `lingering-procs.txt` should be empty after `warlock-ui-backend` exits, and `omarchy-shell idle status` must match its pre-run state.


### Dynamic-only GHC guest

The verified Omarchy GHC9.6.7 package provides dynamic Prelude interfaces. Build its pinned local dependency closure and runtime with `--enable-shared --disable-library-vanilla --enable-executable-dynamic`; retain the offline project, build tree and store. Record resolved Haskell DSO hashes as well as executable hashes: repairing Native changed the shared library while both executable hashes stayed identical. No system upgrade is needed. The current owner refuses the incompatible PID-for-children namespace before GTK; preserve that refusal and the original deadline while preparing the separate owned engine process.
