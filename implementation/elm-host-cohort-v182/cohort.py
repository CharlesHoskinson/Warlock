"""Own only the shell cohort in a fresh user scope, including detached helpers."""
import argparse
import json
import os
from pathlib import Path
import resource
import selectors
import signal
import subprocess
import time
from supervisor import emit, load_manifest, regular, start_time


def properties(unit):
    result = subprocess.run(["systemctl", "--user", "show", unit,
                             "--property=Id,ControlGroup,KillMode,TimeoutStopUSec,ActiveState"],
                            capture_output=True, text=True, timeout=3)
    return {line.split("=", 1)[0]: line.split("=", 1)[1] for line in result.stdout.splitlines() if "=" in line}


def members(group):
    root = Path("/sys/fs/cgroup") / group.lstrip("/")
    if not root.exists():
        return []
    return sorted({int(pid) for file in root.rglob("cgroup.procs") for pid in file.read_text().split()})


def run(args):
    load_manifest(args.manifest, args.authority_config)
    if args.qa and resource.getrlimit(resource.RLIMIT_CORE) != (1, 1):
        raise ValueError("QA must inherit exact core limit")
    program = regular(Path(__file__).parent / "supervisor.py")
    unit = ("qa-harness-shell-" if args.qa else "elm-shell-") + str(time.time_ns()) + ".scope"
    command = ["systemd-run", "--user", "--scope", "--quiet", "--expand-environment=no",
               "--slice=" + ("qa-harness.slice" if args.qa else "session.slice"), "--unit=" + unit,
               "--property=KillMode=control-group", "--property=TimeoutStopSec=5s",
               "/usr/bin/python3", "-B", str(program), "--manifest", args.manifest,
               "--authority-config", args.authority_config]
    if args.qa:
        command += ["--qa"]
    if args.qa_log_directory:
        command += ["--qa-log-directory", args.qa_log_directory]
    stopping = False
    child = None
    owned = False
    group = None
    cleanup = None
    wake_read, wake_write = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
    old_wakeup = signal.set_wakeup_fd(wake_write)

    def stop(_signum, _frame):
        nonlocal stopping
        stopping = True

    old_handlers = {sig: signal.signal(sig, stop) for sig in [signal.SIGTERM, signal.SIGINT]}

    def close_scope():
        nonlocal cleanup
        if not owned:
            return
        before = members(group)
        if before:
            # This is the exact scope proved to contain our unreaped direct child.
            result = subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, timeout=9)
            cleanup = {"stopExitCode": result.returncode, "before": before, "remaining": members(group)}
        else:
            cleanup = {"stopExitCode": None, "before": [], "remaining": []}
        emit("cohort-cleanup", unit=unit, **cleanup)

    try:
        if stopping:
            return 0
        child = subprocess.Popen(command, start_new_session=True)
        child_start = start_time(child.pid)
        until = time.monotonic() + 3
        while time.monotonic() < until:
            info = properties(unit)
            candidate = info.get("ControlGroup", "")
            # Do not reap the child before establishing ownership; its PID cannot
            # be reused while its exit status is still ours to wait for.
            if candidate.endswith("/" + unit) and info.get("Id") == unit:
                cgroup = Path(f"/proc/{child.pid}/cgroup").read_text()
                if "0::" + candidate + "\n" in cgroup and start_time(child.pid) == child_start:
                    if info.get("KillMode") != "control-group" or info.get("TimeoutStopUSec") != "5s":
                        raise ValueError("Scope stop policy mismatch")
                    owned = True
                    group = candidate
                    emit("cohort-ready", unit=unit, pid=child.pid, start=child_start, controlGroup=group)
                    break
            if stopping:
                child.terminate()
            time.sleep(.02)
        if not owned:
            raise ValueError("Scope ownership was not established")
        pidfd = os.pidfd_open(child.pid)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(pidfd, selectors.EVENT_READ)
                selector.register(wake_read, selectors.EVENT_READ)
                deadline = None
                while child.poll() is None:
                    if stopping and deadline is None:
                        child.terminate()
                        deadline = time.monotonic() + 7
                    if deadline is not None and time.monotonic() >= deadline:
                        close_scope()
                        break
                    timeout = None if deadline is None else max(0, deadline - time.monotonic())
                    for key, _mask in selector.select(timeout):
                        if key.fd == wake_read:
                            try:
                                while os.read(wake_read, 4096):
                                    pass
                            except BlockingIOError:
                                pass
        finally:
            os.close(pidfd)
        code = child.wait(timeout=2)
        close_scope()
        emit("cohort-exit", unit=unit, mainExitCode=code, stopping=stopping, remaining=cleanup["remaining"])
        return (code if code >= 0 else 128 - code) if not cleanup["remaining"] else 1
    finally:
        if cleanup is None and owned:
            close_scope()
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if owned:
                    close_scope()
                else:
                    child.kill()
                child.wait(timeout=2)
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
        signal.set_wakeup_fd(old_wakeup)
        os.close(wake_read)
        os.close(wake_write)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--authority-config", required=True)
    parser.add_argument("--qa", action="store_true")
    parser.add_argument("--qa-log-directory")
    args = parser.parse_args()
    try:
        return run(args)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Shell cohort refused: " + type(error).__name__, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
