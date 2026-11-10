#!/usr/bin/env python3
"""One protected cold GObject fixture; no arbitrary native command interface."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

ROOT = Path('/home/hoskinson/Projects/Warlock')
PACKET_REL = '.warlock-contributor/evidence/nextloop-20261106/callback-disconnect-api/cold-signal-packet.json'
RECORD = '.warlock-contributor/ux003-walking-skeleton-root.json'
IDENTITY = 'cd0fba4b68a96d3cfa8ea9986e2b836a6678a759e8e2db74b8ee824ecb236d0f'
GENERATION = 10
EXPIRY = '2026-11-07T20:23:00Z'
EXPIRY_NS = int(dt.datetime.fromisoformat(EXPIRY.replace('Z', '+00:00')).timestamp()) * 1_000_000_000
METADATA_SHA = '49cce4b4e0a427473ced4357367d766d964454d0de08329a5608d919ae3c8a60'
SOURCE_MAP_SHA = '62358a1f1ea653f692d9052ca8229f8e52ea1f1f17cc5a1c837a6c4ed70c8a0d'
BUILD_MAP_SHA = '83ba6f30f0d6ea029245f4ee22bc2662e25f6787c9b7c1de533e3ffef0b6b409'
IMAGE_NAME = 'owned-signal-lifecycle-controls'
CAP_NS = 5_000_000_000
CLEANUP_NS = 2_000_000_000
LIMIT = 65536
SHA = re.compile(r'[0-9a-f]{64}\Z')
NORMAL = re.compile(rb'callback-thread=ThreadId [0-9]+\nowned-signal-lifecycle: complete\n\Z')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def map_digest(value):
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def metadata_helpers():
    path = ROOT / 'tools/run_webkit_provider_probe.py'
    if path.is_symlink() or path.resolve() != path or digest(path.read_bytes()) != METADATA_SHA:
        raise ValueError('Immutable metadata helper changed')
    spec = importlib.util.spec_from_file_location('fixed_metadata_read_helpers', path)
    if spec is None or spec.loader is None:
        raise ValueError('Metadata helper loader unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if digest(path.read_bytes()) != METADATA_SHA:
        raise ValueError('Metadata helper changed during import')
    return module


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def sample_budget():
    boot = boot_id()
    origin = time.monotonic_ns()
    utc = time.time_ns()
    cap = min(CAP_NS, EXPIRY_NS - utc - CLEANUP_NS)
    if origin < 0 or cap <= 0:
        raise ValueError('Insufficient original human window or invalid clock')
    return {'boot': boot, 'originNs': origin, 'originUTCNs': utc,
            'deadlineNs': origin + cap, 'cleanupLimitNs': origin + cap + CLEANUP_NS,
            'lastNs': origin, 'lastUTCNs': utc, 'authorizationExpiresUTC': EXPIRY}


def checked_now(budget):
    now = time.monotonic_ns()
    utc = time.time_ns()
    if (boot_id() != budget['boot'] or now < budget['lastNs']
            or utc < budget['lastUTCNs'] or utc >= EXPIRY_NS):
        raise ValueError('Boot/clock regression or human expiry')
    budget['lastNs'] = now
    budget['lastUTCNs'] = utc
    return now


def remaining_ns(budget):
    remaining = budget['deadlineNs'] - checked_now(budget)
    if remaining <= 0:
        raise TimeoutError('Original absolute fixture deadline exhausted')
    return remaining


def fixed_command(copied, budget):
    if (copied.name != IMAGE_NAME or copied.resolve() != copied
            or not copied.is_relative_to(ROOT / '.warlock-contributor')):
        raise ValueError('Expected fixed owned copied image')
    return ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
            '--unshare-ipc', '--unshare-uts', '--new-session', '--ro-bind', '/usr', '/usr',
            '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/bin', '/bin',
            '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/run', '--tmpfs', '/tmp',
            '--dir', '/etc', '--ro-bind', '/etc/ld.so.cache', '/etc/ld.so.cache',
            '--ro-bind', str(copied), '/probe', '--clearenv', '--setenv', 'LANG', 'C.UTF-8',
            '--setenv', 'LC_ALL', 'C.UTF-8', '--chdir', '/', '--', '/probe', str(budget['deadlineNs'])]


def validate_output(stdout, stderr):
    if stderr or NORMAL.fullmatch(stdout) is None:
        raise ValueError('Fixed cold-signal output differs')


def collect(copied, output, budget):
    """One INTERNAL D for argv, reads and wait. Never samples a new run cap."""
    outcome = {'passed': False, 'timeout': False, 'forcedCleanup': False,
               'cleanupUnknown': False, 'reaped': False, 'deadlineNs': budget['deadlineNs']}
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    selector = selectors.DefaultSelector()
    child = None
    try:
        command = fixed_command(copied, budget)
        remaining_ns(budget)
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, env={'PATH': '/usr/bin:/bin',
                                 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'},
                                 start_new_session=True, close_fds=True)
        outcome.update(pid=child.pid, argv=command)
        if child.stdout is None or child.stderr is None:
            raise ValueError('Missing owned pipes')
        selector.register(child.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(child.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            left = remaining_ns(budget)
            for key, _ in selector.select(min(left / 1_000_000_000, 0.1)):
                remaining_ns(budget)
                data = os.read(key.fd, 4096)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                if sum(map(len, streams.values())) + len(data) > LIMIT:
                    raise ValueError('Combined output exceeds 64KiB')
                streams[key.data].extend(data)
        outcome['exit'] = child.wait(timeout=remaining_ns(budget) / 1_000_000_000)
        outcome['reaped'] = True
        remaining_ns(budget)
        if outcome['exit'] != 0:
            raise ValueError('Cold fixture exit was not zero')
        validate_output(bytes(streams['stdout']), bytes(streams['stderr']))
        outcome['passed'] = True
    except BaseException as problem:
        outcome['error'] = str(problem)
        outcome['timeout'] = isinstance(problem, (TimeoutError, subprocess.TimeoutExpired))
        if child is not None and not outcome['reaped']:
            # Popen remains our unreaped child: its PID cannot be reused. Never
            # kill a reaped PID, foreign boot or an unrelated process group.
            if boot_id() != budget['boot']:
                outcome['cleanupUnknown'] = True
            else:
                outcome['forcedCleanup'] = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                except OSError as kill_problem:
                    outcome['cleanupUnknown'] = True
                    outcome['killError'] = str(kill_problem)
                try:
                    cleanup_start = checked_now(budget)
                    cleanup_end = min(budget['cleanupLimitNs'], cleanup_start + CLEANUP_NS)
                    outcome.update(cleanupStartNs=cleanup_start, cleanupDeadlineNs=cleanup_end)
                    left = cleanup_end - checked_now(budget)
                    if left <= 0:
                        raise TimeoutError('Original cleanup reserve exhausted')
                    outcome['exit'] = child.wait(timeout=left / 1_000_000_000)
                    outcome['reaped'] = True
                    end = checked_now(budget)
                    outcome['cleanupElapsedNs'] = end - cleanup_start
                    if end > cleanup_end:
                        raise TimeoutError('Cleanup returned after its bound')
                except (OSError, ValueError, TimeoutError, subprocess.TimeoutExpired) as cleanup_problem:
                    outcome['cleanupUnknown'] = True
                    outcome['cleanupError'] = str(cleanup_problem)
        if isinstance(problem, (KeyboardInterrupt, SystemExit)):
            outcome['interrupted'] = True
    finally:
        selector.close()
        if child is not None:
            if child.stdout is not None:
                child.stdout.close()
            if child.stderr is not None:
                child.stderr.close()
        for name, data in streams.items():
            with (output / (name + '.bin')).open('xb') as stream:
                stream.write(data)
    return outcome, bytes(streams['stdout']), bytes(streams['stderr'])


def image_binding(path):
    if (path.name != IMAGE_NAME or path.resolve() != path
            or not path.is_relative_to(ROOT / '.warlock-contributor')):
        raise ValueError('Expected canonical fixed image path')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        first = os.fstat(stream.fileno())
        if (not stat.S_ISREG(first.st_mode) or first.st_uid != os.getuid()
                or not first.st_mode & stat.S_IXUSR or first.st_mode & 0o6022
                or not 64 <= first.st_size <= 512 * 1024 * 1024):
            raise ValueError('Image ownership/type/size/mode differs')
        data = stream.read(512 * 1024 * 1024 + 1)
        last = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_uid', 'st_mode', 'st_mtime_ns', 'st_ctime_ns')
    current = path.lstat()
    if any(getattr(first, key) != getattr(last, key) or getattr(first, key) != getattr(current, key) for key in fields):
        raise ValueError('Image changed while reading')
    if len(data) != first.st_size or data[:7] != b'\x7fELF\x02\x01\x01' or int.from_bytes(data[18:20], 'little') != 183:
        raise ValueError('Expected exact AArch64 ELF')
    return {'path': str(path), 'device': first.st_dev, 'inode': first.st_ino,
            'size': first.st_size, 'uid': first.st_uid, 'mode': stat.S_IMODE(first.st_mode),
            'sha256': digest(data)}, data


def check_image(path, expected):
    observed, data = image_binding(path)
    if observed != expected:
        raise ValueError('Frozen image binding differs')
    return data


def verify_sources(helper, sources):
    if not isinstance(sources, dict) or map_digest(sources) != SOURCE_MAP_SHA:
        raise ValueError('Exact reviewed source map differs')
    for name, expected in sources.items():
        if digest(helper.regular(ROOT / name, 16 * 1024 * 1024)) != expected:
            raise ValueError('Current source/guard drift: ' + name)


def read_packet(helper, expected):
    if not SHA.fullmatch(expected):
        raise ValueError('Expected exact packet SHA')
    raw = helper.regular(ROOT / PACKET_REL, 1024 * 1024)
    if digest(raw) != expected:
        raise ValueError('Packet hash differs')
    packet = json.loads(raw, object_pairs_hook=helper.unique)
    fields = {'schema', 'kind', 'record', 'recordIdentitySha256', 'selectionGeneration',
              'authorizationExpiresUTC', 'systemInventorySha256', 'sourceHashes', 'image', 'buildReport'}
    if (not isinstance(packet, dict) or set(packet) != fields or type(packet['schema']) is not int
            or packet['schema'] != 1 or packet['kind'] != 'fixed-cold-owned-signal'
            or packet['record'] != RECORD or packet['recordIdentitySha256'] != IDENTITY
            or type(packet['selectionGeneration']) is not int or packet['selectionGeneration'] != GENERATION
            or packet['authorizationExpiresUTC'] != EXPIRY
            or packet['systemInventorySha256'] != helper.SYSTEM_SHA):
        raise ValueError('Fixed cold-signal packet differs')
    verify_sources(helper, packet['sourceHashes'])
    image = packet['image']
    if not isinstance(image, dict) or set(image) != {'path', 'device', 'inode', 'size', 'uid', 'mode', 'sha256'}:
        raise ValueError('Actual GREEN image binding missing')
    if any(type(image[key]) is not int for key in ('device', 'inode', 'size', 'uid', 'mode')):
        raise ValueError('Image integer metadata malformed')
    binary = check_image(Path(image['path']), image)
    build = packet['buildReport']
    if not isinstance(build, dict) or set(build) != {'path', 'sha256'}:
        raise ValueError('Actual GREEN report binding missing')
    report_path = Path(build['path'])
    if not report_path.is_relative_to(ROOT / '.warlock-contributor'):
        raise ValueError('Expected retained repository build report')
    report_raw = helper.regular(report_path, 16 * 1024 * 1024)
    if digest(report_raw) != build['sha256']:
        raise ValueError('Build report hash differs')
    report = json.loads(report_raw, object_pairs_hook=helper.unique)
    expected_names = ['provider-callback-profile-controls', 'provider-callback-build',
                      'list-webkit-callback-capi-controls', 'list-owned-signal-lifecycle-controls']
    if (report.get('passed') is not True or report.get('mode') != '--provider-callback-build'
            or map_digest(report.get('sourceHashes')) != BUILD_MAP_SHA
            or [entry.get('name') for entry in report.get('commands', [])] != expected_names
            or any(entry.get('exit') != 0 for entry in report['commands'])):
        raise ValueError('Actual successful reviewed GREEN source/build missing')
    built = report['providerCallbackBuild']['compiledImages'][IMAGE_NAME]
    if (built.get('executed') is not False or any(built.get(key) != image[key] for key in ('path', 'sha256'))
            or any(str(built.get(key)) != str(image[key]) for key in ('device', 'inode', 'size'))):
        raise ValueError('GREEN report-to-image binding differs')
    return packet, binary


def current_selection(helper):
    state = json.loads(helper.regular(ROOT / 'docs/warlock-build-loop/v2/STATE.json', 1024 * 1024), object_pairs_hook=helper.unique)
    selected = state.get('activeSelection', {})
    if (state.get('activeContributorRecord') != RECORD or selected.get('generation') != GENERATION
            or selected.get('recordIdentitySha256') != IDENTITY):
        raise ValueError('Selected record/generation differs')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    helper = metadata_helpers()
    packet, binary = read_packet(helper, args.sha256)
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    current_selection(helper)
    system_count = helper.verify_system()
    output = ROOT / '.warlock-contributor' / ('owned-signal-probe-' + str(time.time_ns()))
    output.mkdir(mode=0o700)
    copied = output / IMAGE_NAME
    with copied.open('xb') as stream:
        stream.write(binary)
    copied.chmod(0o500)
    copied_binding, _ = image_binding(copied)
    if copied_binding['sha256'] != packet['image']['sha256']:
        raise ValueError('Copied fixture differs')
    # All expensive staging/validation precedes this one execution origin.
    # Nothing below starts another execution cap or passes a replacement D.
    budget = sample_budget()
    receipt = {'schema': 1, 'kind': 'fixed-cold-owned-signal-result', 'passed': False,
               'packetSha256': args.sha256, 'protectedScope': scope, 'clock': dict(budget),
               'sourceHashes': packet['sourceHashes'], 'image': packet['image'],
               'copiedImage': copied_binding, 'systemInputsVerified': system_count,
               'providerQualified': False, 'cleanupQualified': False, 'inputQualified': False,
               'nativeAcceptance': False, 'originalAcceptance': False}
    try:
        execution, _, _ = collect(copied, output, budget)
        receipt['execution'] = execution
        if not execution['passed']:
            raise ValueError('Cold signal observation failed; retain actual execution evidence')
        current_selection(helper)
        read_packet(helper, args.sha256)
        helper.verify_system()
        check_image(copied, copied_binding)
        receipt['passed'] = True
    except Exception as problem:
        receipt['error'] = str(problem)
    with (output / 'report.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': receipt['passed'], 'report': str(output / 'report.json')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
