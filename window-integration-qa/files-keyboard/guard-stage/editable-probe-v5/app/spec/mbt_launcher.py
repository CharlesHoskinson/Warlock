#!/usr/bin/env python3
"""Model-based test: replay Quint traces of launcher.qnt against the LIVE app.

    python3 mbt_launcher.py [--traces N] [--steps N] [--seed S] [--main launcherFixed]

Drives the real `omarchy-files` launcher script, the real `qs` process and the
real Hyprland compositor (so a Files window flickers on your screen while it
runs), then compares what the compositor/app report with the model state:

    model action   real action
    Click t        omarchy-files <t>              (what the bar icon runs)
    UserClose      hyprctl close the Files window (same as the X button)
    MoveAway       hyprctl move it to workspace 8 (as if you switched workspace)
    Minimize       hyprctl move it to special:win-minimized
    Crash          kill -9 the qs process

    model var      observed as
    procUp         pgrep '^qs -p <app>'
    mapped         a Hyprland client titled "Files" owned by that pid
    place          Here / Elsewhere / Scratch from the client's workspace vs focus
    view           `qs ipc call files state`  ({view, coll})

`--main launcherBuggy` replays the pre-fix model; against the fixed app it is
expected to report divergences (proof the test has teeth).
The app is stopped at the end of the run.
"""
import argparse, glob, json, os, shutil, signal, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
SPEC = os.path.join(HERE, "launcher.qnt")
LAUNCH = os.path.expanduser("~/.local/bin/omarchy-files")
QS = ["qs", "-p", APP]
OTHER_WS = "8"
SCRATCH = "special:win-minimized"


def sh(*cmd, **kw):
    return subprocess.run(list(cmd), capture_output=True, text=True, **kw)


def dec(v):
    if isinstance(v, dict):
        if "#bigint" in v: return int(v["#bigint"])
        if "tag" in v and "value" in v: return v["tag"]
        return {k: dec(x) for k, x in v.items()}
    if isinstance(v, list): return [dec(x) for x in v]
    return v


# ---------------------------------------------------------------- real system
def app_pid():
    r = sh("pgrep", "-f", f"^qs -p {APP}( |$)")
    pids = r.stdout.split()
    return int(pids[0]) if pids else None


def client(pid):
    if pid is None: return None
    for c in json.loads(sh("hyprctl", "-j", "clients").stdout):
        if c["pid"] == pid and c["title"] == "Files":
            return c
    return None


def focused_ws():
    for m in json.loads(sh("hyprctl", "-j", "monitors").stdout):
        if m["focused"]: return m["activeWorkspace"]["name"]


def observe():
    pid = app_pid()
    c = client(pid)
    place = None
    if c:
        ws = c["workspace"]["name"]
        place = "Scratch" if ws.startswith("special:") else ("Here" if ws == focused_ws() else "Elsewhere")
    view = None
    if pid:
        r = sh(*QS, "ipc", "call", "files", "state")
        try:
            st = json.loads(r.stdout)
            view = st["coll"] and f"coll:{st['coll']}" or st["view"]
        except Exception:
            pass
    return {"procUp": pid is not None, "mapped": c is not None, "place": place, "view": view}


def settle(want_mapped, timeout=4.0):
    """Poll until the window's presence matches the model (or timeout)."""
    end = time.time() + timeout
    while time.time() < end:
        if (client(app_pid()) is not None) == want_mapped:
            break
        time.sleep(0.1)
    time.sleep(0.35)        # let summon / workspace moves finish


def stop_app():
    pid = app_pid()
    if pid:
        os.kill(pid, signal.SIGKILL)
        for _ in range(30):
            if app_pid() is None: break
            time.sleep(0.1)
    time.sleep(0.3)


def act(op, target, want):
    pid = app_pid()
    c = client(pid)
    if op == "Click":
        sh(LAUNCH, target)
        settle(want["mapped"])
    elif op == "UserClose":
        sh("hyprctl", "dispatch", f"hl.dsp.window.close({{ window = \"address:{c['address']}\" }})")
        settle(False)
    elif op in ("MoveAway", "Minimize"):
        ws = OTHER_WS if op == "MoveAway" else SCRATCH
        sh("hyprctl", "dispatch", f"hl.dsp.window.move({{ workspace = \"{ws}\", follow = false, window = \"address:{c['address']}\" }})")
        settle(True)
    elif op == "Crash":
        stop_app()
    else:
        raise SystemExit(f"unknown op {op}")


# ------------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", type=int, default=12)
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--seed")
    ap.add_argument("--main", default="launcherFixed")
    args = ap.parse_args()

    out = tempfile.mkdtemp(prefix="mbt-launcher-")
    cmd = ["quint", "run", SPEC, f"--main={args.main}", "--mbt", "--max-steps", str(args.steps),
           "--n-traces", str(args.traces), "--out-itf", os.path.join(out, "t{seq}.itf.json")]
    if args.seed: cmd += ["--seed", args.seed]
    r = sh(*cmd)
    traces = sorted(glob.glob(os.path.join(out, "*.itf.json")))
    if not traces:
        sys.exit("quint produced no traces:\n" + r.stdout + r.stderr)

    steps = failed_steps = failed_traces = 0
    for ti, tf in enumerate(traces):
        with open(tf) as f:
            states = [{k.split("::")[-1]: dec(v) for k, v in s.items() if k != "#meta"} for s in json.load(f)["states"]]
        stop_app()
        bad = []
        for si in range(1, len(states)):
            s = states[si]
            want = {"procUp": s["procUp"], "mapped": s["mapped"],
                    "place": s["place"] if s["mapped"] else None}
            op = s["lastOp"]
            if op in ("UserClose", "MoveAway", "Minimize") and client(app_pid()) is None:
                bad.append((si, op, "precondition: no window to act on", {}, want)); break
            act(op, s["lastTarget"], want)
            got = observe()
            steps += 1
            if s["mapped"] and op == "Click": want["view"] = s["lastTarget"]
            diff = {k: (want[k], got[k]) for k in want if want[k] != got[k]}
            if diff:
                failed_steps += 1
                bad.append((si, f"{op} {s['lastTarget'] if op == 'Click' else ''}".strip(), "diverged (model, real)", diff, want))
                break
        if bad:
            failed_traces += 1
            path = " -> ".join(f"{states[i]['lastOp']}" + (f"({states[i]['lastTarget']})" if states[i]['lastOp'] == 'Click' else "")
                               for i in range(1, bad[0][0] + 1))
            print(f"trace {ti}: FAIL at step {bad[0][0]}: {path}\n    {bad[0][2]}: {bad[0][3]}")
    stop_app()
    shutil.rmtree(out, ignore_errors=True)
    print(f"{len(traces)} traces · {steps} steps replayed against the live app · {failed_traces} failing trace(s)")
    sys.exit(1 if failed_traces else 0)


if __name__ == "__main__":
    main()
