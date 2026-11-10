"""Unreviewed fixed daemon-only supervisor; called inside the protected ARM profile."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import time

DAEMON = Path('/usr/bin/dbus-daemon')
DAEMON_SHA = '7a3fc70805c2f7c2888839b4d62a23e84163a6bf8427f512756eaf8244c04790'
ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'tools/ux031-private-bus.conf'
CONFIG_SHA = '465f5056d58e3581d59654a4c33401114582b6c804eb1d9fee2692776f11cda6'
BASE = Path('/tmp/warlock-ux031')
CFG = BASE / 'private-bus.conf'
SOCKET = BASE / 'bus'
EXPIRY = datetime.datetime(2026, 11, 6, 19, 7, 31, 942628, tzinfo=datetime.timezone.utc)


def pin(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise RuntimeError('nonregular input')
        digest = hashlib.sha256()
        while True:
            part = os.read(fd, 65536)
            if not part:
                break
            digest.update(part)
        end = os.fstat(fd)
        if (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns) != (end.st_dev, end.st_ino, end.st_size, end.st_mtime_ns, end.st_ctime_ns):
            raise RuntimeError('input changed while hashing')
        return [st.st_dev, st.st_ino, st.st_size, digest.hexdigest()]
    finally:
        os.close(fd)


SYSTEM_MANIFEST = Path("/home/hoskinson/.local/share/warlock-toolchain/system-build-inputs.json")
SYSTEM_MANIFEST_SHA = '33b9ed73bd1d249225d228a35c8f40ae941f690bca8f3626fb2e6f5e267ac7b4'
ELF_PINS = {'/usr/lib/ld-linux-aarch64.so.1': 'b1f2738bdb51e6419d7062f96c8a44bd68853698dc5ac624fa6ca9f9b03d456d', '/usr/bin/dbus-daemon': '7a3fc70805c2f7c2888839b4d62a23e84163a6bf8427f512756eaf8244c04790', '/usr/lib/libc.so.6': '6ab264fb4e8df9942b0fb75b48fcd5c30b2f081d8dfaa6c25d7be1d3fce5b2ab', '/usr/lib/libsystemd.so.0.45.0': '82ffd5629ecf5d0d6f15928144d4f52dfceaf389150b526f748dd5d7d5e61ec5', '/usr/lib/libgcc_s.so.1': 'ac598673a4bf67c0295b6609e46b1fafd0d4adf3f80a513d61ac49ecff772e48', '/usr/lib/libcap-ng.so.0.0.0': 'c62b668a9810af6a194d5808e9498b5bb59f3d1f350d4ea66f0017a177b945f0', '/usr/lib/libaudit.so.1.0.0': 'cf41b23b9a259a5531f06fadb56e90b3011a301e0763830ef06d71d1e09c1e46', '/usr/lib/libexpat.so.1.13.1': '04755e5476227b0fab77e07f8b4c7542ef11111707738ccc47290066d6def6e7', '/usr/lib/libdbus-1.so.3.38.3': 'e23d65f51af54dd8822cb76ad11be11d38d51a9d55d59503d26016d1e178626a'}
STATIC_REVIEW_SHA = 'ef17a5671d46aac6870bf82a8c70c691f2824e2ed700f57a11606c7a9d1f5044'

def process_snapshot():
    rows = {}
    paths = list(Path("/proc").iterdir())
    numeric = [p for p in paths if p.name.isdecimal()]
    if len(numeric) > 128:
        raise RuntimeError("unexpected private PID namespace population")
    for path in numeric:
        try:
            fields = (path / "stat").read_text().rsplit(")", 1)[1].split()
        except FileNotFoundError:
            continue
        rows[path.name] = {"birth": fields[19], "ppid": fields[1]}
    if str(os.getpid()) not in rows or "1" not in rows:
        raise RuntimeError("incomplete private PID namespace snapshot")
    return rows

def closure_pins():
    manifest = pin(SYSTEM_MANIFEST)
    if manifest[3] != SYSTEM_MANIFEST_SHA:
        raise RuntimeError("system manifest differs from reviewed closure")
    rows = {name: pin(Path(name)) for name in ELF_PINS}
    if any(rows[name][3] != expected for name, expected in ELF_PINS.items()):
        raise RuntimeError("reviewed ELF dependency differs")
    return {"systemManifest": manifest, "elf": rows, "staticReviewSHA256": STATIC_REVIEW_SHA}

def run_daemon_only(output):
    start = time.monotonic()
    if datetime.datetime.now(datetime.timezone.utc) >= EXPIRY:
        raise RuntimeError('authorization expired')
    result = {'scope': 'daemon config/load/listen only', 'nativeAcceptance': False,
              'originalAcceptance': False, 'passed': False, 'forcedCleanup': False}
    owned = False
    proc = None
    selected = selectors.DefaultSelector()
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    eof = set()
    issues = []
    image_before = None
    config_before = None
    closure_before = None
    baseline = None
    handlers = {}
    signal_seen = []
    cleaning = False
    def interrupted(signum, _frame):
        signal_seen.append(signum)
    def pump(deadline):
        if not cleaning and signal_seen:
            raise RuntimeError('supervisor interrupted')
        if not cleaning and datetime.datetime.now(datetime.timezone.utc) >= EXPIRY:
            raise RuntimeError('authorization expired')
        remaining = min(deadline, start + 20) - time.monotonic()
        if remaining <= 0:
            return
        for key, _ in selected.select(min(remaining, 0.1)):
            name = key.data
            chunk = os.read(key.fd, 4096)
            if not chunk:
                selected.unregister(key.fileobj)
                eof.add(name)
                continue
            streams[name].extend(chunk)
            if len(streams[name]) > (1026 if name == 'stdout' else 16384):
                raise RuntimeError(name + ' exceeded bound')
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            handlers[sig] = signal.signal(sig, interrupted)
        closure_before = closure_pins()
        result["closureBefore"] = closure_before
        baseline = process_snapshot()
        result["namespaceBefore"] = baseline
        image_before = pin(DAEMON)
        config_before = pin(CONFIG)
        if image_before[3] != DAEMON_SHA or config_before[3] != CONFIG_SHA:
            raise RuntimeError('daemon/config hash differs')
        BASE.mkdir(mode=0o700)
        owned = True
        st = BASE.lstat()
        if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
            raise RuntimeError('private directory identity')
        data = CONFIG.read_bytes()
        fd = os.open(CFG, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o400)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        copied = pin(CFG)
        if copied[3] != CONFIG_SHA:
            raise RuntimeError('config copy differs')
        env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
               'HOME': str(output / 'home'), 'TMPDIR': '/tmp'}
        argv = [str(DAEMON), '--nofork', '--nosyslog', '--nopidfile',
                '--config-file=/tmp/warlock-ux031/private-bus.conf', '--print-address=1', '--print-pid=1']
        if (signal_seen or datetime.datetime.now(datetime.timezone.utc) >= EXPIRY
                or time.monotonic() >= start + 5):
            raise RuntimeError('authorization/startup budget expired or interrupted before spawn')
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                close_fds=True, start_new_session=True, env=env)
        for name, stream in (('stdout', proc.stdout), ('stderr', proc.stderr)):
            os.set_blocking(stream.fileno(), False)
            selected.register(stream, selectors.EVENT_READ, name)
        ready_until = min(start + 5, start + 20)
        while streams['stdout'].count(b'\n') < 2 and time.monotonic() < ready_until:
            if proc.poll() is not None:
                raise RuntimeError('daemon exited during readiness')
            pump(ready_until)
        lines = bytes(streams['stdout']).splitlines(keepends=True)
        if len(lines) != 2 or any(not x.endswith(b'\n') or len(x) > 513 for x in lines):
            raise RuntimeError('invalid readiness records')
        records = [x[:-1] for x in lines]
        address = rb'unix:path=/tmp/warlock-ux031/bus(?:,guid=[0-9a-f]{32})?'
        addresses = [x for x in records if re.fullmatch(address, x)]
        pids = [x for x in records if re.fullmatch(rb'[1-9][0-9]*', x)]
        if len(addresses) != 1 or len(pids) != 1 or int(pids[0]) != proc.pid:
            raise RuntimeError('readiness identity mismatch')
        st = SOCKET.lstat()
        if not stat.S_ISSOCK(st.st_mode) or st.st_uid != os.getuid():
            raise RuntimeError('socket identity')
        live_end = time.monotonic() + 0.1
        while time.monotonic() < live_end:
            if proc.poll() is not None:
                raise RuntimeError('daemon exited before live observation')
            pump(live_end)
        if bytes(streams['stdout']).count(b'\n') != 2 or not bytes(streams['stdout']).endswith(b'\n'):
            raise RuntimeError('extra stdout')
        active = process_snapshot()
        unexpected = {pid: row for pid, row in active.items()
                      if pid != str(proc.pid) and
                      (pid not in baseline or baseline[pid]["birth"] != row["birth"])}
        if unexpected:
            raise RuntimeError("unexpected daemon descendants in private PID namespace")
        result["namespaceDuring"] = active
        result.update(readinessRecords=[x.decode('ascii') for x in records], liveObservationMs=100)
    except Exception as error:
        issues.append(str(error))
    finally:
        cleaning = True
        if signal_seen:
            issues.append('supervisor interrupted')
        if proc is not None:
            try:
                if proc.poll() is None:
                    proc.terminate()  # retained child handle only
                    result['terminationRequested'] = 'SIGTERM'
                    until = min(time.monotonic() + 2, start + 20)
                    while proc.poll() is None and time.monotonic() < until:
                        try:
                            pump(until)
                        except Exception as error:
                            issues.append("termination drain: " + str(error))
                            break
                if proc.poll() is None:
                    result['forcedCleanup'] = True
                    proc.kill()  # retained child handle only
                    try:
                        proc.wait(timeout=min(2, max(0, start + 20 - time.monotonic())))
                    except subprocess.TimeoutExpired:
                        issues.append('child not reaped after SIGKILL')
                result['exit'] = proc.poll()
                if result.get('terminationRequested') != 'SIGTERM':
                    issues.append('daemon exited before requested termination')
                if result['exit'] != 0:
                    issues.append('daemon did not exit normally with status zero')
                end = min(start + 20, time.monotonic() + 2)
                while selected.get_map() and time.monotonic() < end:
                    pump(end)
                if eof != {'stdout', 'stderr'}:
                    issues.append('missing pipe EOF')
                try:
                    os.killpg(proc.pid, 0)  # observation only, never signal parsed PID
                except ProcessLookupError:
                    pass
                else:
                    issues.append('child process group still exists')
                if bytes(streams['stdout']).count(b'\n') != 2 or not bytes(streams['stdout']).endswith(b'\n'):
                    issues.append('extra or incomplete stdout')
            except Exception as error:
                issues.append('cleanup: ' + str(error))
            finally:
                for stream in (proc.stdout, proc.stderr):
                    if stream is not None:
                        stream.close()
        selected.close()
        try:
            if closure_before is not None:
                after = closure_pins()
                result["closureAfter"] = after
                if after != closure_before:
                    issues.append("reviewed ELF/manifest closure changed")
            if baseline is not None:
                retired = process_snapshot()
                result["namespaceAfter"] = retired
                survivors = {pid: row for pid, row in retired.items()
                             if pid not in baseline or baseline[pid]["birth"] != row["birth"]}
                if survivors:
                    issues.append("new live private namespace processes after cleanup")
            if image_before is not None and pin(DAEMON) != image_before:
                issues.append('daemon image changed')
            if config_before is not None and pin(CONFIG) != config_before:
                issues.append('source config changed')
            if owned:
                if CFG.exists() and (pin(CFG)[3] != CONFIG_SHA or CFG.is_symlink()):
                    raise RuntimeError('config copy changed')
                if SOCKET.exists():
                    st = SOCKET.lstat()
                    if not stat.S_ISSOCK(st.st_mode) or st.st_uid != os.getuid():
                        raise RuntimeError('socket replaced')
                    SOCKET.unlink()
                if CFG.exists():
                    CFG.unlink()
                BASE.rmdir()  # rejects any unexpected file
        except Exception as error:
            issues.append('filesystem cleanup: ' + str(error))
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
        if signal_seen and 'supervisor interrupted' not in issues:
            issues.append('supervisor interrupted')
        result.update(stdout=bytes(streams['stdout']).decode('ascii', 'backslashreplace'),
                      stderr=bytes(streams['stderr']).decode('utf-8', 'backslashreplace'),
                      pipeEOF=sorted(eof), errors=issues, elapsedSeconds=time.monotonic() - start)
        if result['elapsedSeconds'] > 20 or datetime.datetime.now(datetime.timezone.utc) >= EXPIRY:
            issues.append('deadline exceeded')
        result['passed'] = not issues and not result['forcedCleanup'] and proc is not None
        (output / 'ux031-daemon-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    if not result['passed']:
        raise RuntimeError('fixed daemon-only probe failed; retained receipt')
    return result
