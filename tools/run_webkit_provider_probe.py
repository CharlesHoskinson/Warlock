#!/usr/bin/env python3
"""Fixed protected metadata probe. No arbitrary program, argv or provider grant."""
import argparse
import datetime as dt
import hashlib
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
EVIDENCE = ROOT / '.warlock-contributor/evidence/nextloop-20261106/native-provider-probe'
PACKET = EVIDENCE / 'probe-packet.json'
SYSTEM = Path('/home/hoskinson/.local/share/warlock-toolchain/system-build-inputs.json')
SYSTEM_SHA = '33b9ed73bd1d249225d228a35c8f40ae941f690bca8f3626fb2e6f5e267ac7b4'
RECORD = '.warlock-contributor/ux003-walking-skeleton-root.json'
IDENTITY = 'cd0fba4b68a96d3cfa8ea9986e2b836a6678a759e8e2db74b8ee824ecb236d0f'
EXPIRY = '2026-11-07T20:23:00Z'
SOURCE_HASHES = {'implementation/elm-build-loop-v1/loop.py': '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6', 'implementation/warlock/haskell/runtime/test-webkit-provider-probe/Controls.hs': 'be9885d27bade1400563310dc8e95078aad13d8c5227a4aaee500c576d3f7012', 'implementation/warlock/haskell/runtime/test-webkit-provider-probe/Main.hs': '17f47886bcc879a89856bdb773de0736392105a3112aa995199c91b396d63651', 'implementation/warlock/haskell/runtime/test-webkit-provider-probe/ProviderProbeContract.hs': 'da1387ddd63ca62a3998d817af2c04bfea25e9c5c9343e5e6e917a5a801b6414', 'implementation/warlock/haskell/runtime/test-webkit-provider-probe/ProviderProbeHeaders.hsc': 'bdb92d1317a30ddc62677938d232181e27a6de1f4f5b3461b5a84a0cd343ca9a', 'implementation/warlock/haskell/runtime/ui/Warlock/Ui/EngineCustody.hsc': '5028eed1eae2df6f066d3868777af686aa0ddb889a651159b26cb3369c4129de', 'implementation/warlock/haskell/runtime/ui/Warlock/Ui/WebKit.hs': 'b1f00b0db2370fee7442cbfa30ebfb6ed06911a704b4299a4f1f61f3650ea79a', 'implementation/warlock/haskell/runtime/ui/Warlock/Ui/WebKitABI.hsc': '8a016b2cfa837b1874019f376d7e4d1c333f3064ea48e62787565e4a616f40e8', 'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23', 'window-integration-qa/qa_run.py': '656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1'}
SHA = re.compile(r'[0-9a-f]{64}\Z')
LIMIT = 65536


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def regular(path, limit):
    path = Path(path)
    if path.resolve() != path:
        raise ValueError('Noncanonical or symlinked file')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        first = os.fstat(stream.fileno())
        if not stat.S_ISREG(first.st_mode) or first.st_size > limit:
            raise ValueError('Expected bounded regular file')
        data = stream.read(limit + 1)
        last = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(data) > limit or any(getattr(first, x) != getattr(last, x) for x in fields):
        raise ValueError('File changed while reading')
    return data


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def expected_observation():
    return {'schema': 1, 'kind': 'fixed-webkit-version-header-abi',
            'runtimeVersion': [2, 54, 2], 'headerVersion': [2, 54, 2],
            'headerLayout': [24, 8, 0], 'existingLayout': [24, 8, 0],
            'headerWidths': [4, 4, 8, 8], 'haskellWidths': [4, 4, 8, 8],
            'headerAarch64': True, 'passed': True, 'error': None,
            'providerQualified': False, 'cleanupQualified': False,
            'inputQualified': False, 'nativeAcceptance': False, 'originalAcceptance': False}


def validate_observation(value):
    if json.dumps(value, sort_keys=True, separators=(',', ':')) != json.dumps(
            expected_observation(), sort_keys=True, separators=(',', ':')):
        raise ValueError('Fixed metadata observation differs')
    return value


def verify_sources():
    for name, expected in SOURCE_HASHES.items():
        if hashlib.sha256(regular(ROOT / name, 16 * 1024 * 1024)).hexdigest() != expected:
            raise ValueError('Probe/source/guard drift: ' + name)


def verify_system():
    if hashlib.sha256(regular(Path('/etc/ld.so.cache'), 16 * 1024 * 1024)).hexdigest() != 'e26846bd2ef0d774afeb7f995b1dea790ca0037f13bb64df5694ee74b414d7b6':
        raise ValueError('Pinned loader cache changed')
    data = regular(SYSTEM, 16 * 1024 * 1024)
    if hashlib.sha256(data).hexdigest() != SYSTEM_SHA:
        raise ValueError('System inventory changed')
    files = json.loads(data, object_pairs_hook=unique)['files']
    for name, expected in files.items():
        if not name.startswith(('/usr/bin/', '/usr/lib/', '/usr/include/')):
            raise ValueError('Unexpected system inventory path')
        path = Path(name)
        if 'link' in expected:
            actual = {'link': os.readlink(path)} if path.is_symlink() else None
        else:
            actual = ({'mode': stat.S_IMODE(path.stat().st_mode), 'sha256': digest(path)}
                      if path.is_file() and not path.is_symlink() else None)
        if actual != expected:
            raise ValueError('System input differs: ' + name)
    return len(files)


def packet_input(expected):
    if not SHA.fullmatch(expected):
        raise ValueError('Expected packet SHA256')
    data = regular(PACKET, 1024 * 1024)
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Packet hash differs')
    packet = json.loads(data, object_pairs_hook=unique)
    fields = {'schema', 'kind', 'record', 'recordIdentitySha256', 'authorizationExpiresUTC',
              'systemInventorySha256', 'sourceHashes', 'image', 'buildReport'}
    if (not isinstance(packet, dict) or set(packet) != fields or type(packet['schema']) is not int
            or packet['schema'] != 1 or packet['kind'] != 'fixed-webkit-provider-probe'
            or packet['record'] != RECORD or packet['recordIdentitySha256'] != IDENTITY
            or packet['authorizationExpiresUTC'] != EXPIRY
            or packet['systemInventorySha256'] != SYSTEM_SHA or packet['sourceHashes'] != SOURCE_HASHES):
        raise ValueError('Fixed probe packet differs')
    image = packet['image']
    if (not isinstance(image, dict) or set(image) != {'path', 'size', 'sha256'}
            or type(image['size']) is not int or not 0 < image['size'] <= 512 * 1024 * 1024
            or not isinstance(image['sha256'], str) or not SHA.fullmatch(image['sha256'])):
        raise ValueError('Image binding malformed')
    path = Path(image['path'])
    if (not path.is_relative_to(ROOT / '.warlock-contributor') or path.name != 'webkit-provider-probe'
            or path.resolve() != path):
        raise ValueError('Expected exact built probe path')
    binary = regular(path, 512 * 1024 * 1024)
    if len(binary) != image['size'] or hashlib.sha256(binary).hexdigest() != image['sha256']:
        raise ValueError('Built probe differs')
    if (len(binary) < 64 or binary[:7] != b'\x7fELF\x02\x01\x01'
            or int.from_bytes(binary[18:20], 'little') != 183):
        raise ValueError('Expected AArch64 probe ELF')
    build = packet['buildReport']
    if not isinstance(build, dict) or set(build) != {'path', 'sha256'}:
        raise ValueError('Build report binding malformed')
    report_path = Path(build['path'])
    if not report_path.is_relative_to(ROOT / '.warlock-contributor'):
        raise ValueError('Build report must be retained repository evidence')
    if hashlib.sha256(regular(report_path, 16 * 1024 * 1024)).hexdigest() != build['sha256']:
        raise ValueError('Build report differs')
    return packet, binary


def execute_fixed(command, output):
    """Five seconds from spawn; combined output is bounded before storage."""
    started = time.monotonic()
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                             'LC_ALL': 'C.UTF-8'}, start_new_session=True, close_fds=True)
    streams = {'stdout': bytearray(), 'stderr': bytearray()}
    outcome = {'pid': child.pid, 'timeout': False, 'forcedCleanup': False, 'reaped': False}
    selector = selectors.DefaultSelector()
    try:
        if child.stdout is None or child.stderr is None:
            raise RuntimeError('Missing owned capture pipes')
        selector.register(child.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(child.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            remaining = 5.0 - (time.monotonic() - started)
            if remaining <= 0:
                outcome['timeout'] = True
                raise TimeoutError('Five-second probe deadline')
            for key, _ in selector.select(min(remaining, 0.1)):
                data = os.read(key.fd, 4096)
                if not data:
                    selector.unregister(key.fileobj)
                    continue
                if sum(len(v) for v in streams.values()) + len(data) > LIMIT:
                    raise ValueError('Combined probe output exceeds64KiB')
                streams[key.data].extend(data)
        remaining = 5.0 - (time.monotonic() - started)
        if remaining <= 0:
            outcome['timeout'] = True
            raise TimeoutError('Five-second probe deadline')
        outcome['exit'] = child.wait(timeout=remaining)
        outcome['reaped'] = True
    except BaseException as error:
        outcome['error'] = str(error)
        outcome['forcedCleanup'] = True
        if isinstance(error, (TimeoutError, subprocess.TimeoutExpired)):
            outcome['timeout'] = True
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            outcome['exit'] = child.wait(timeout=2)
            outcome['reaped'] = True
        except subprocess.TimeoutExpired:
            outcome['cleanupUnknown'] = True
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            outcome['interrupted'] = True
    finally:
        selector.close()
        if child.stdout is not None:
            child.stdout.close()
        if child.stderr is not None:
            child.stderr.close()
        for name, data in streams.items():
            with (output / (name + '.bin')).open('xb') as stream:
                stream.write(data)
    outcome['elapsedSeconds'] = time.monotonic() - started
    return outcome, bytes(streams['stdout']), bytes(streams['stderr'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    # Source-pinned existing protection, not a bypass flag or fabricated scope.
    verify_sources()
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    packet, binary = packet_input(args.sha256)
    count = verify_system()
    cutoff = dt.datetime.fromisoformat(EXPIRY.replace('Z', '+00:00'))
    if (cutoff - dt.datetime.now(dt.timezone.utc)).total_seconds() <= 5:
        raise ValueError('Fixed authorization window cannot contain the probe')
    output = ROOT / '.warlock-contributor' / ('webkit-provider-probe-' + str(time.time_ns()))
    output.mkdir(mode=0o700)
    copied = output / 'webkit-provider-probe'
    with copied.open('xb') as stream:
        stream.write(binary)
    copied.chmod(0o500)
    if digest(copied) != packet['image']['sha256']:
        raise ValueError('Copied probe differs')
    command = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
               '--unshare-ipc', '--unshare-uts', '--new-session', '--ro-bind', '/usr', '/usr',
               '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/bin', '/bin',
               '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/run', '--tmpfs', '/tmp',
               '--dir', '/etc', '--ro-bind', '/etc/ld.so.cache', '/etc/ld.so.cache',
               '--ro-bind', str(copied), '/probe', '--clearenv', '--setenv', 'LANG', 'C.UTF-8',
               '--setenv', 'LC_ALL', 'C.UTF-8', '--chdir', '/', '--', '/probe']
    receipt = {'schema': 1, 'kind': 'fixed-webkit-provider-probe-result', 'passed': False,
               'packetSha256': args.sha256, 'protectedScope': scope, 'argv': command,
               'sourceHashes': SOURCE_HASHES, 'systemInventorySha256': SYSTEM_SHA,
               'systemInputsVerified': count, 'image': packet['image'],
               'copiedImage': {'path': str(copied), 'sha256': digest(copied)},
               'providerQualified': False, 'cleanupQualified': False, 'inputQualified': False,
               'nativeAcceptance': False, 'originalAcceptance': False}
    try:
        result, stdout, stderr = execute_fixed(command, output)
        receipt['execution'] = result
        if result.get('exit') != 0 or result['timeout'] or result['forcedCleanup'] or not result['reaped']:
            raise ValueError('Probe did not exit normally within its bound')
        if stderr:
            raise ValueError('Unexpected probe diagnostics')
        receipt['observation'] = validate_observation(json.loads(stdout, object_pairs_hook=unique))
        verify_sources()
        verify_system()
        if digest(copied) != packet['image']['sha256']:
            raise ValueError('Copied image changed')
        receipt['passed'] = True
    except Exception as error:
        receipt['error'] = str(error)
    with (output / 'report.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'passed': receipt['passed'], 'report': str(output / 'report.json')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
