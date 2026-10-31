#!/usr/bin/python3
"""Development-only, one-shot partial-capture runner for the protected native loop.

Run only through docs/warlock-build-loop/v2/loop.py native, after source-bound
changed-condition review. This never accepts an original scenario or release.
The selection file is root's reviewed developer input, not a wire authority.
Trusted stable system paths and no hostile same-UID mutation remain premises.
"""
from __future__ import annotations

import hashlib
import fcntl
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import selectors
import signal
import socket
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
STATE = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild/elm-haskell-redesign-20261030')
SELECTION = ROOT / 'implementation/warlock/qa/first-elm-haskell-capture.selection.json'
RECORD = '.warlock-contributor/first-render-changed-composition.json'
OLD_STOP = ROOT / '.warlock-contributor/elm-haskell-host-feasibility-preparation.json'
PROOF_NAMES = {'parentCompile', 'parentControls', 'regularClosure', 'physicalAlias',
               'deviceCustody', 'deviceMetadata', 'formalContract'}
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope  # noqa: E402
from elm_haskell_frame_receiver import FrameError, archive_frame, _owned_fd  # noqa: E402


class Refused(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refused('duplicate metadata key')
        result[key] = value
    return result


def metadata(raw):
    def reject_constant(_value):
        raise Refused('nonfinite metadata')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Refused('invalid metadata') from error


def fingerprint(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns]


def verified_file(spec, limit, *, retain=True, _owned_selection=False):
    """Read a hash-selected regular file; never follow a final symlink."""
    if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
        raise Refused('artifact selection fields')
    if not isinstance(spec['path'], str):
        raise Refused('artifact path type')
    path = Path(spec['path'])
    digest = spec['sha256']
    if digest is None and (not _owned_selection or path != SELECTION):
        raise Refused('artifact digest required')
    if not path.is_absolute() or path.resolve() != path or (digest is not None and (not isinstance(digest, str) or re.fullmatch('[0-9a-f]{64}', digest) is None)):
        raise Refused('artifact path or digest')
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_uid not in (0, os.getuid()) or before.st_mode & 0o022 or not 0 <= before.st_size <= limit:
        raise Refused('artifact kind, owner, mode or bound')
    with _owned_fd(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)) as fd:
        if fingerprint(os.fstat(fd)) != fingerprint(before):
            raise Refused('artifact changed before read')
        chunks, count, hashed = [], 0, hashlib.sha256()
        while True:
            chunk = os.read(fd, min(65536, limit + 1 - count))
            if not chunk:
                break
            count += len(chunk)
            if count > limit:
                raise Refused('artifact exceeded read bound')
            hashed.update(chunk)
            if retain:
                chunks.append(chunk)
        if count != before.st_size or (digest is not None and hashed.hexdigest() != digest) or fingerprint(os.fstat(fd)) != fingerprint(before) or fingerprint(path.lstat()) != fingerprint(before):
            raise Refused('artifact hash or identity changed')
        return b''.join(chunks), fingerprint(before)


def verify_selection():
    raw, selection_info = verified_file({'path': str(SELECTION), 'sha256': None}, 1048576, _owned_selection=True)
    if selection_info[3] != os.getuid():
        raise Refused('selection must belong to this user')
    selected = metadata(raw)
    keys = {'kind', 'requirement', 'scenario', 'record', 'parent', 'manifest', 'proofs', 'review'}
    if not isinstance(selected, dict) or set(selected) != keys or (
        selected['kind'], selected['requirement'], selected['scenario'], selected['record']
    ) != ('one-bounded-elm-haskell-partial-capture-v1', 'ELM-ARC-002', 'ownership-presentation', RECORD):
        raise Refused('original scenario or selection schema')
    parent, parent_info = verified_file(selected['parent'], 16777216)
    parent_path = Path(selected['parent']['path'])
    if not parent_path.is_relative_to(STATE) or parent_path.name != 'parent' or not parent.startswith(b'\x7fELF\x02\x01\x01'):
        raise Refused('selected parent ELF')
    manifest_raw, _ = verified_file(selected['manifest'], 4194304)
    manifest = metadata(manifest_raw)
    if not isinstance(selected['proofs'], dict) or set(selected['proofs']) != PROOF_NAMES:
        raise Refused('missing source-bound preparation proof')
    proofs = {}
    for name, spec in selected['proofs'].items():
        body, _ = verified_file(spec, 8388608)
        proof = metadata(body)
        if not isinstance(proof, dict) or proof.get('passed') is not True:
            raise Refused('preparation proof is not qualified: ' + name)
        for path, digest in proof.get('inputs', {}).items():
            source_path = Path(path)
            if not source_path.is_absolute():
                raise Refused('relative proof source path')
            # Tool/source alias provenance remains with its original proof; this
            # checks current resolved bytes, never grants execution of that alias.
            verified_file({'path': str(source_path.resolve()), 'sha256': digest}, 268435456, retain=False)
        proofs[name] = proof
    compiled = proofs['parentCompile']
    if compiled.get('executables', {}).get(str(parent_path)) != selected['parent']['sha256'] or compiled.get('manifestSHA256') != selected['manifest']['sha256']:
        raise Refused('parent compilation/selection join')
    review_raw, _ = verified_file(selected['review'], 1048576)
    review = metadata(review_raw)
    if not isinstance(review, dict) or review.get('decision') != 'admit-one-bounded-partial-capture' or review.get('parentSHA256') != selected['parent']['sha256'] or review.get('manifestSHA256') != selected['manifest']['sha256'] or review.get('record') != RECORD or review.get('nativeAccepted') is not False:
        raise Refused('changed-condition review does not bind this tuple')
    if review.get('stoppedRecord', {}).get('path') != str(OLD_STOP):
        raise Refused('original HOST STOP2 reference missing')
    verified_file(review['stoppedRecord'], 4194304)
    rows = manifest.get('files', [])
    if len(rows) != 243 or len({row['namespacePath'] for row in rows}) != 243 or sum(row['role'] == 'data' for row in rows) != 30:
        raise Refused('full current regular role inventory')
    by_path = {row['namespacePath']: row for row in rows}
    alias, target = by_path['/usr/lib/libweston-15.so.0'], by_path['/usr/lib/libweston-15.so.0.0.1']
    if alias.get('declaredAliasTarget') != 'libweston-15.so.0.0.1' or any(alias[key] != target[key] for key in ('sourceResolvedPath', 'sourceBytes', 'sourceSHA256', 'capturePath', 'captureSHA256')):
        raise Refused('fixed direct alias identity')
    captures = 0
    for row in rows:
        _, stamp = verified_file({'path': row['sourceResolvedPath'], 'sha256': row['sourceSHA256']}, 268435456, retain=False)
        if stamp[4] != row['sourceBytes']:
            raise Refused('source size mismatch')
        if row['role'] == 'elf':
            captured, _ = verified_file({'path': row['capturePath'], 'sha256': row['captureSHA256']}, 1048576)
            captures += len(captured)
    total = sum(row['sourceBytes'] for row in rows) - target['sourceBytes'] + 21 + captures
    if total > 536870912 or len(rows) - 1 + 9 > 256:
        raise Refused('unchanged input/descriptor bound')
    devices = proofs['deviceMetadata']
    if len(devices.get('devices', [])) != 9:
        raise Refused('nine explicit device metadata rows required')
    for device in devices['devices']:
        fact = device['facts']
        current = Path(device['path']).lstat()
        if not stat.S_ISCHR(current.st_mode) or [current.st_dev, current.st_ino, current.st_mode, current.st_uid, current.st_rdev] != [fact['device'], fact['inode'], fact['mode'], fact['uid'], fact['rdev']]:
            raise Refused('device metadata changed')
        for ancestor in device['ancestors']:
            before = ancestor['facts']; current = Path(ancestor['path']).lstat()
            if not stat.S_ISDIR(current.st_mode) or [current.st_dev, current.st_ino, current.st_mode, current.st_uid] != [before['device'], before['inode'], before['mode'], before['uid']]:
                raise Refused('device ancestor changed')
    kernel = Path('/proc/driver/nvidia/version').open('rb')
    with kernel:
        kernel_version = kernel.read(4097)
    if len(kernel_version) > 4096 or hashlib.sha256(kernel_version).hexdigest() != devices.get('kernelNvidiaVersionSHA256') or os.uname().release != devices.get('kernelRelease'):
        raise Refused('kernel driver metadata changed')
    return selected, hashlib.sha256(raw).hexdigest(), parent_info, total


def require_native_lock():
    """Require the live kernel lock held by this runner's coordinator ancestor."""
    adapter_path = ROOT / 'docs/warlock-build-loop/v2/loop.py'
    spec = importlib.util.spec_from_file_location('_first_render_native_adapter', adapter_path)
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    coordinator = adapter.portable_coordinator(ROOT)
    return held_lock_ancestor(coordinator.lock_path(ROOT))


def held_lock_ancestor(path):
    with _owned_fd(os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)) as fd:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise Refused('native coordinator lock metadata')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            pass
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
            raise Refused('native coordinator is not holding the lock')
        ancestors, pid = {}, os.getppid()
        for _ in range(128):
            if pid <= 1 or pid in ancestors:
                break
            body = Path('/proc', str(pid), 'stat').read_text()
            facts = body[body.rfind(')') + 2:].split()
            ancestors[pid] = facts[19]
            pid = int(facts[1])
        with open('/proc/locks', 'rb') as stream:
            raw = stream.read(4194305)
        if len(raw) > 4194304:
            raise Refused('kernel lock table bound')
        for line in raw.decode('ascii').splitlines():
            fields = line.split()
            if len(fields) < 8 or fields[1:4] != ['FLOCK', 'ADVISORY', 'WRITE']:
                continue
            identity = fields[5].split(':')
            # Btrfs reports a per-subvolume st_dev, while proc lock records use
            # the superblock device. Join the record to the ancestor's actual
            # descriptor identity AND its fdinfo lock; never accept inode alone.
            if len(identity) == 3 and int(identity[2]) == info.st_ino:
                owner = int(fields[4])
                if owner in ancestors and Path('/proc', str(owner)).stat().st_uid == os.getuid():
                    descriptors = list(itertools.islice(Path('/proc', str(owner), 'fd').iterdir(), 4097))
                    if len(descriptors) > 4096:
                        raise Refused('coordinator descriptor count bound')
                    for descriptor in descriptors:
                        try:
                            held = descriptor.stat()
                            if (held.st_dev, held.st_ino) != (info.st_dev, info.st_ino):
                                continue
                            fdinfo = Path('/proc', str(owner), 'fdinfo', descriptor.name)
                            with fdinfo.open('rb') as stream:
                                record = stream.read(4097)
                            if len(record) > 4096:
                                raise Refused('coordinator descriptor metadata bound')
                            for detail in record.decode('ascii').splitlines():
                                parts = detail.split()
                                if len(parts) == 9 and parts[0] == 'lock:' and parts[2:9] == fields[1:8] and fields[6:8] == ['0', 'EOF']:
                                    after = descriptor.stat()
                                    body = Path('/proc', str(owner), 'stat').read_text()
                                    start = body[body.rfind(')') + 2:].split()[19]
                                    if (after.st_dev, after.st_ino) == (info.st_dev, info.st_ino) and start == ancestors[owner]:
                                        return owner
                        except (FileNotFoundError, ProcessLookupError):
                            continue
        raise Refused('live native-lock owner is not a coordinator ancestor')


def parse_cgroup_events(raw):
    if len(raw) > 4096:
        raise Refused('cgroup event bound')
    try:
        lines = raw.decode('ascii').splitlines()
    except UnicodeError as error:
        raise Refused('non-ASCII cgroup events') from error
    values = {}
    for line in lines:
        fields = line.split()
        if len(fields) != 2 or fields[0] not in ('populated', 'frozen') or fields[0] in values or fields[1] not in ('0', '1'):
            raise Refused('malformed or duplicate cgroup event')
        values[fields[0]] = fields[1] == '1'
    if set(values) != {'populated', 'frozen'}:
        raise Refused('missing cgroup event')
    return values


def atomic_report(output, report):
    """Publish complete JSON without truncating the durable failed baseline."""
    body = (json.dumps(report, indent=2) + '\n').encode()
    if len(body) > 1048576:
        raise Refused('report metadata bound')
    temporary = output / ('report-' + uuid.uuid4().hex + '.tmp')
    with _owned_fd(os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)) as fd:
        remaining = memoryview(body)
        while remaining:
            written = os.write(fd, remaining)
            if written <= 0:
                raise OSError('report write made no progress')
            remaining = remaining[written:]
        os.fsync(fd)
    os.replace(temporary, output / 'report.json')
    with _owned_fd(os.open(output, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)) as fd:
        os.fsync(fd)


def main_socket():
    runtime = Path(os.environ['XDG_RUNTIME_DIR'])
    display = Path(os.environ['WAYLAND_DISPLAY'])
    path = display if display.is_absolute() else runtime / display
    info = path.lstat()
    if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
        raise Refused('parent Wayland socket')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(1)
        connection.connect(str(path))
    return path, fingerprint(info)


def collect_bounded(process, result, seconds=45):
    # Caller owns buffers before any read so timeout/overflow never discards them.
    deadline = time.monotonic() + seconds
    with selectors.DefaultSelector() as selector:
        for name, stream in [('stdout', process.stdout), ('stderr', process.stderr)]:
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            left = deadline - time.monotonic()
            if left <= 0:
                raise TimeoutError('parent external containment bound')
            for key, _ in selector.select(min(left, 0.2)):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                result[key.data].extend(chunk)
                if len(result[key.data]) > 4194304:
                    raise Refused('parent output exceeded bound')
        process.wait(timeout=max(0.001, deadline - time.monotonic()))
    return {name: bytes(value) for name, value in result.items()}


def main():
    report = {'passed': False, 'nativeAccepted': False, 'releaseAccepted': False,
              'scope': require_qa_scope(), 'requirement': 'ELM-ARC-002',
              'scenario': 'ownership-presentation', 'record': RECORD,
              'renderObserved': False, 'forcedContainment': False,
              'limits': 'One changed-composition partial capture only; pixels/normal retirement/application effects/AT/IME/original acceptance require independent evidence.'}
    report['nativeCoordinatorPID'] = require_native_lock()
    selected, selection_hash, parent_info, total = verify_selection()
    host_socket, host_stamp = main_socket()
    output = STATE / ('native-partial-capture-' + uuid.uuid4().hex)
    output.mkdir(mode=0o700)
    report.update(selectionSHA256=selection_hash, parentFingerprint=parent_info,
                  declaredBytes=total, output=str(output))
    # One selection gets one attempt, even if launch or later collection fails.
    claim = STATE / ('native-partial-capture-' + selection_hash + '.claim')
    with claim.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write((str(output) + '\n').encode())
        stream.flush(); os.fsync(stream.fileno())
    with _owned_fd(os.open(STATE, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)) as state_fd:
        os.fsync(state_fd)
    parent_group = run_group = None
    parent_created = run_created = False
    ancestor_fd = group_fd = kill_fd = events_fd = qa_kill_fd = None
    phase = 'setup'
    launch_publication_uncertain = False
    prior_mask = signal.pthread_sigmask(signal.SIG_UNBLOCK, (signal.SIGALRM,))
    process = None
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    def populated():
        if events_fd is None:
            raise Refused('cgroup event descriptor unavailable')
        info = os.fstat(events_fd)
        if [info.st_dev, info.st_ino] != report['eventIdentity']:
            raise Refused('cgroup event identity changed')
        os.lseek(events_fd, 0, os.SEEK_SET)
        return parse_cgroup_events(os.read(events_fd, 4097))['populated']
    def drain(seconds):
        until = time.monotonic() + seconds
        while populated():
            if time.monotonic() >= until:
                return False
            time.sleep(0.02)
        return True
    def contain():
        try:
            occupied = populated()
        except (OSError, Refused) as error:
            report['eventReadError'] = repr(error)
            report['passed'] = False
            occupied = True  # Unknown is never evidence of emptiness.
        if occupied:
            if [os.fstat(group_fd).st_dev, os.fstat(group_fd).st_ino] != report['parentCgroupIdentity']:
                raise Refused('owned containment identity changed')
            if os.write(kill_fd, b'1') != 1:
                raise Refused('uncertain cgroup kill; no retry')
            report['forcedContainment'] = True
            report['passed'] = False
            if not drain(3):
                raise Refused('owned subtree did not drain')
    def interrupted(signum, _frame):
        if phase in ('pending', 'cleanup'):
            # The unique protected ancestor contains even a fork whose PID has
            # not yet been published by Popen. Its coordinator is outside it.
            info = os.fstat(ancestor_fd)
            if [info.st_dev, info.st_ino] != report['ancestorCgroupIdentity'] or qa_kill_fd is None:
                raise Refused('emergency scope identity unavailable')
            if os.write(qa_kill_fd, b'1') != 1:
                raise Refused('uncertain emergency scope kill; no retry')
            os._exit(124)
        if signum == signal.SIGALRM:
            raise TimeoutError('absolute parent supervision bound')
        raise InterruptedError('runner received signal ' + str(signum))
    previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)}
    try:
        membership = next(line[3:] for line in Path('/proc/self/cgroup').read_text().splitlines() if line.startswith('0::'))
        ancestor = Path('/sys/fs/cgroup') / membership.lstrip('/')
        if re.fullmatch(r'qa-harness-[A-Za-z0-9_-]+\.scope', ancestor.name) is None:
            raise Refused('protected ancestor scope')
        ancestor_fd = os.open(ancestor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        ancestor_info = os.fstat(ancestor_fd)
        report['ancestorCgroupIdentity'] = [ancestor_info.st_dev, ancestor_info.st_ino]
        qa_kill_fd = os.open('cgroup.kill', os.O_WRONLY | os.O_CLOEXEC, dir_fd=ancestor_fd)
        parent_group = ancestor / ('warlock-first-render-' + uuid.uuid4().hex)
        parent_group.mkdir(mode=0o700)
        parent_created = True
        group_fd = os.open(parent_group, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        parent_info_now = os.fstat(group_fd)
        report['parentCgroupIdentity'] = [parent_info_now.st_dev, parent_info_now.st_ino]
        kill_fd = os.open('cgroup.kill', os.O_WRONLY | os.O_CLOEXEC, dir_fd=group_fd)
        events_fd = os.open('cgroup.events', os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=group_fd)
        event_info = os.fstat(events_fd)
        report['eventIdentity'] = [event_info.st_dev, event_info.st_ino]
        initial_events = parse_cgroup_events(os.read(events_fd, 4097))
        if initial_events['populated'] or initial_events['frozen']:
            raise Refused('new P must be empty and unfrozen')
        run_group = parent_group / 'run'
        run_group.mkdir(mode=0o700)
        run_created = True
        a, p, r = os.fstat(ancestor_fd), os.fstat(group_fd), run_group.stat()
        report['ancestorCgroupIdentity'] = [a.st_dev, a.st_ino]
        report['parentCgroupIdentity'] = [p.st_dev, p.st_ino]
        report['runCgroupIdentity'] = [r.st_dev, r.st_ino]
        if (parent_group / 'cgroup.subtree_control').read_text().strip() or (parent_group / 'cgroup.type').read_text().strip() != 'domain' or (run_group / 'cgroup.type').read_text().strip() != 'domain':
            raise Refused('ordinary empty-controller domains required')
        def enter():
            fd = os.open(parent_group / 'cgroup.procs', os.O_WRONLY | os.O_CLOEXEC)
            try:
                value = str(os.getpid()).encode()
                if os.write(fd, value) != len(value):
                    raise Refused('uncertain parent migration; no retry')
            finally:
                os.close(fd)
        args = [selected['parent']['path'], *map(str, (ancestor_fd, a.st_dev, a.st_ino)), parent_group.name,
                *map(str, (p.st_dev, p.st_ino)), run_group.name, *map(str, (r.st_dev, r.st_ino))]
        report['argv'] = args
        report_path = output / 'report.json'
        pending_report = {**report, 'phase': 'before-spawn-publication', 'passed': False,
                          'forcedContainment': None, 'outcome': 'NotObserved',
                          'externalOperationSeconds': 45, 'cleanupSeconds': 10}
        atomic_report(output, pending_report)
        phase = 'pending'
        absolute_end = time.monotonic() + 45
        signal.setitimer(signal.ITIMER_REAL, 45)
        process = subprocess.Popen(args, cwd=output, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, close_fds=True, pass_fds=(ancestor_fd,),
                                   start_new_session=True, preexec_fn=enter,
                                   env={'PATH': '/usr/bin', 'LANG': 'C', 'LC_ALL': 'C'})
        phase = 'published'
        buffers = collect_bounded(process, buffers, seconds=max(0.001, absolute_end - time.monotonic()))
        report['parentExitCode'] = process.returncode
        if not drain(3):
            raise Refused('owned descendants remain after parent exit')
        report['privateCgroupEmpty'] = True
        # Failed/partial child exit is evidence, never a reason to discard its bytes.
        try:
            report['capture'] = archive_frame(buffers['stdout'], output, 'capture')
        except (FrameError, OSError, BaseExceptionGroup) as error:
            report['capture'] = {'refused': str(error), 'nativeAccepted': False}
        report['passed'] = not report['forcedContainment'] and bool(report['capture'].get('payloadSHA256Verified') and report['capture'].get('containerCRCVerified'))
    except BaseException as error:
        launch_publication_uncertain = phase == 'pending'
        report['passed'] = False
        report['error'] = repr(error)
    finally:
        phase = 'cleanup'
        cleanup_mask = signal.pthread_sigmask(signal.SIG_BLOCK, (signal.SIGINT, signal.SIGTERM))
        signal.setitimer(signal.ITIMER_REAL, 10)
        def cleanup_error(name, error):
            report.setdefault('cleanupErrors', []).append({'step': name, 'error': repr(error)})
            report['passed'] = False
        def attempt(name, action):
            try:
                action()
            except BaseException as error:
                cleanup_error(name, error)
        try:
            if launch_publication_uncertain:
                # Popen can raise after fork before publishing its child handle.
                # P being empty does not rule out a child still in the ancestor.
                report['launchPublicationUncertain'] = True
                report['forcedContainment'] = None
                report['containmentStatus'] = 'ancestor-attempt-pending'
                try:
                    atomic_report(output, report)
                finally:
                    interrupted(signal.SIGALRM, None)
            def terminate_parent():
                if process is not None and process.poll() is None:
                    process.terminate()
            attempt('terminate parent', terminate_parent)
            if group_fd is not None and kill_fd is not None:
                attempt('contain owned P subtree', contain)
            if process is not None:
                attempt('wait parent', lambda: process.wait(timeout=3))
            def remove_created(path, field):
                path.rmdir()
                report[field] = True
            if run_created:
                attempt('remove R', lambda: remove_created(run_group, 'runCgroupRemoved'))
            if group_fd is not None:
                for name, fd in [('events', events_fd), ('P kill', kill_fd), ('P directory', group_fd)]:
                    if fd is not None:
                        attempt('close ' + name, lambda fd=fd: os.close(fd))
            if parent_created:
                attempt('remove P', lambda: remove_created(parent_group, 'parentCgroupRemoved'))
            if 'capture' not in report and buffers['stdout']:
                try:
                    report['capture'] = archive_frame(bytes(buffers['stdout']), output, 'capture')
                except (FrameError, OSError, BaseExceptionGroup) as error:
                    report['capture'] = {'refused': str(error), 'nativeAccepted': False}
            if process is not None:
                for name, stream in [('stdout', process.stdout), ('stderr', process.stderr)]:
                    if stream is not None:
                        attempt('close ' + name, stream.close)
            for name, body in buffers.items():
                def write_artifact(name=name, body=body):
                    path = output / (name + '.bin')
                    path.write_bytes(body)
                    path.chmod(0o600)
                    report[name + 'SHA256'] = hashlib.sha256(body).hexdigest()
                attempt('archive ' + name, write_artifact)
            try:
                if fingerprint(host_socket.lstat()) != host_stamp:
                    raise Refused('main Wayland socket identity changed')
            except (OSError, Refused) as error:
                cleanup_error('main Wayland socket identity', error)
            # Preserve a failed baseline until final control-close outcomes are known.
            attempt('publish pending final controls', lambda: atomic_report(output,
                {**report, 'phase': 'final-controls-pending', 'passed': False,
                 'captureCollectionPassed': report['passed']}))
        finally:
            if parent_created and not report.get('parentCgroupRemoved'):
                # Also runs after artifact exceptions: never abandon an unknown
                # subtree when the independently held ancestor can contain it.
                attempt('emergency ancestor containment', lambda: interrupted(signal.SIGALRM, None))
            # All runtime/artifact work has finished or failed. Only final
            # control-close disposition remains; publish it atomically too.
            signal.setitimer(signal.ITIMER_REAL, 0)
            phase = 'final-report'
            for name, fd in [('QA kill', qa_kill_fd), ('QA ancestor', ancestor_fd)]:
                if fd is not None:
                    try:
                        os.close(fd)
                    except OSError as error:
                        cleanup_error('close ' + name, error)
            try:
                signal.setitimer(signal.ITIMER_REAL, 2)
                report['phase'] = 'finished'
                report_path = output / 'report.json'
                atomic_report(output, report)
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                for sig, handler in previous.items():
                    signal.signal(sig, handler)
                signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)
    print(json.dumps({'passed': report['passed'], 'nativeAccepted': False, 'report': str(report_path)}))
    # This is a partial capability observation, never original-scenario acceptance.
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
