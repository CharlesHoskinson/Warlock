"""Run one sealed native shell host; restart only on its native exit-3 request."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import resource
import selectors
import stat
import subprocess
import time


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate metadata member")
        result[key] = value
    return result


def metadata(path):
    if path.stat().st_size > 65536:
        raise ValueError("Metadata capacity exceeded")
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def regular(path):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise ValueError("Runtime file must be a regular owner-controlled file")
    # Reject symlink ancestors as well as the final entry.
    if any(parent.is_symlink() for parent in path.parents):
        raise ValueError("Runtime path has a symlink ancestor")
    return path.resolve()


def load_manifest(path, authority):
    manifest_path = regular(path)
    manifest = metadata(manifest_path)
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "scope", "host", "assets", "backend", "coreSHA256", "files"} or type(manifest["schema"]) is not int or manifest["schema"] != 1:
        raise ValueError("Unsupported runtime capsule")
    if not isinstance(manifest["files"], dict) or not 1 <= len(manifest["files"]) <= 512:
        raise ValueError("Missing runtime inventory")
    if any(not isinstance(manifest[key], str) for key in ["scope", "host", "assets", "backend", "coreSHA256"]):
        raise ValueError("Invalid capsule field type")
    for name, expected in manifest["files"].items():
        if not Path(name).is_absolute() or digest(regular(name)) != expected:
            raise ValueError("Runtime inventory mismatch")
    for key in ["host", "backend"]:
        if manifest[key] not in manifest["files"]:
            raise ValueError("Unsealed launch input")
    for directory in [Path(manifest["assets"]), Path(manifest["backend"]).parent]:
        if not directory.is_absolute() or directory.is_symlink() or not directory.is_dir():
            raise ValueError("Invalid runtime directory")
        actual_files = {str(regular(p)) for p in directory.iterdir()}
        sealed_files = {name for name in manifest["files"] if Path(name).parent == directory}
        if actual_files != sealed_files:
            raise ValueError("Unsealed runtime directory entry")
    authority_path = regular(authority)
    if authority_path.stat().st_mode & 0o077:
        raise ValueError("Authority configuration must be private")
    config = metadata(authority_path)
    if not isinstance(config, dict) or set(config) != {"runtime", "instance", "pid", "expected_start", "binary_sha256"} or config["binary_sha256"] != manifest["coreSHA256"]:
        raise ValueError("Authority configuration does not match the sealed core")
    return manifest, authority_path


def start_time(pid):
    raw = Path(f"/proc/{pid}/stat").read_text()
    return raw[raw.rindex(")") + 2:].split()[19]


def emit(kind, **values):
    print(kind + ": " + json.dumps(values, separators=(",", ":")), flush=True)


def run(manifest_path, authority_path, qa=False, qa_log_directory=None, qa_preview_subject=None):
    stopping = False
    child = None

    def stop(signum, _frame):
        nonlocal stopping
        stopping = True

    previous = {sig: signal.signal(sig, stop) for sig in [signal.SIGTERM, signal.SIGINT]}
    wake_read, wake_write = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
    previous_wakeup = signal.set_wakeup_fd(wake_write)
    generation = 0
    try:
        log_directory = None
        if qa_log_directory is not None:
            log_directory = Path(qa_log_directory)
            info = log_directory.lstat()
            if not qa or not log_directory.is_absolute() or log_directory.is_symlink() or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
                raise ValueError("Generation logging needs a private QA directory")
        if qa_preview_subject is not None:
            if not qa or log_directory is None or resource.getrlimit(resource.RLIMIT_CORE)!=(1,1) or type(qa_preview_subject) is not str or not qa_preview_subject.isascii() or not qa_preview_subject.isdigit() or qa_preview_subject.startswith('0') or not 0<int(qa_preview_subject)<=18446744073709551615:
                raise ValueError('Controlled preview needs exact protected QA subject and log directory')
            import sys
            sys.path.insert(0,'/home/hoskinson/window-integration-qa')
            from qa_launch import require_qa_scope
            require_qa_scope()
        while not stopping:
            # Recheck the entire sealed runtime before every generation.
            manifest, authority = load_manifest(manifest_path, authority_path)
            if stopping:
                break
            command = [manifest["host"], "--assets", manifest["assets"], "--backend", manifest["backend"],
                       "--authority-config", str(authority), "--surface-experiment"]
            if qa:
                command += ["--qa-exit-after-render", "--qa-stay-open"]
            generation += 1
            if qa_preview_subject is not None:
                reader=log_directory/('controlled-reader-generation-'+str(generation))
                fd=os.open(reader,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                with os.fdopen(fd,'wb') as stream:stream.write(b'hold\n');stream.flush();os.fsync(stream.fileno())
                snapshot=log_directory/('controlled-webkit-generation-'+str(generation)+'.png')
                command += ['--qa-preview-controlled',qa_preview_subject,'--qa-preview-snapshot',str(snapshot),'--qa-controlled-preview-reader',str(reader)]
            log_path = None
            if log_directory is None:
                child = subprocess.Popen(command, start_new_session=True)
            else:
                log_path = log_directory / ("generation-" + str(generation) + ".log")
                descriptor = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                with os.fdopen(descriptor, "wb") as stream:
                    child = subprocess.Popen(command, start_new_session=True, stdout=stream, stderr=subprocess.STDOUT)
            emit("supervisor-host-start", generation=generation, pid=child.pid, start=start_time(child.pid), log=str(log_path) if log_path else None)
            stop_deadline = None
            forced = False
            pidfd = os.pidfd_open(child.pid)
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(pidfd, selectors.EVENT_READ)
                    selector.register(wake_read, selectors.EVENT_READ)
                    while child.poll() is None:
                        if stopping and stop_deadline is None:
                            child.terminate()
                            stop_deadline = time.monotonic() + 5
                        if stop_deadline is not None and time.monotonic() >= stop_deadline:
                            child.kill()
                            forced = True
                            break
                        timeout = None if stop_deadline is None else max(0, stop_deadline - time.monotonic())
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
            emit("supervisor-host-exit", generation=generation, pid=child.pid, exitCode=code, stopping=stopping, forced=forced)
            child = None
            if stopping:
                return 1 if forced or code not in (0, 1, 3) else 0
            if code != 3:
                return code if code >= 0 else 128 - code
            # Code 3 is produced only by the trusted native recovery button.
            # A signal received after child exit also cancels this restart.
        return 0
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=2)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        signal.set_wakeup_fd(previous_wakeup)
        os.close(wake_read)
        os.close(wake_write)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--authority-config", required=True)
    parser.add_argument("--qa", action="store_true")
    parser.add_argument("--qa-log-directory")
    parser.add_argument('--qa-preview-subject')
    args = parser.parse_args()
    try:
        return run(args.manifest, args.authority_config, args.qa, args.qa_log_directory, args.qa_preview_subject)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print("Shell supervisor refused: " + type(error).__name__, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
