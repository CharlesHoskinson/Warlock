"""Protected offline namespace and two-build reproducibility observations."""
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa/runs' / ('offline-reproducibility-' + str(time.time_ns()))
OUT.mkdir(parents=True)
sys.path.insert(0, str(ROOT / 'adapter'))
import release_builder as builder
import release_repro as repro
builder.require_scope()

listener = socket.socket()
listener.bind(('127.0.0.1', 0)); listener.listen()
port = listener.getsockname()[1]
with socket.create_connection(('127.0.0.1', port), timeout=1):
    accepted, _ = listener.accept(); accepted.close()
parent = {name: os.readlink('/proc/self/ns/' + name) for name in ('net', 'mnt', 'pid')}
program = '''import errno,json,os,pathlib,resource,socket,sys
connection=socket.socket();connection.settimeout(1)
try:connection.connect(('127.0.0.1',int(sys.argv[1])));blocked=False
except OSError as error:blocked=True;reason=error.errno
connection.close()
try:fd=os.open('/usr/bin/python3',os.O_WRONLY);os.close(fd);read_only=False
except OSError as error:read_only=error.errno in (errno.EROFS,errno.EACCES)
print(json.dumps({'namespaces':{n:os.readlink('/proc/self/ns/'+n) for n in ('net','mnt','pid')},
 'networkBlocked':blocked,'readOnlyInputs':read_only,'coreLimit':list(resource.getrlimit(resource.RLIMIT_CORE)),
 'cgroup':pathlib.Path('/proc/self/cgroup').read_text(),'hiddenHostSource':not pathlib.Path(sys.argv[2]).exists()}))
'''
command = ['/usr/bin/bwrap', '--unshare-user', '--unshare-pid', '--unshare-net',
    '--unshare-ipc', '--unshare-uts', '--die-with-parent', '--new-session',
    '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib',
    '--symlink', 'usr/lib', '/lib64', '--symlink', 'usr/bin', '/bin',
    '--dir', '/etc', '--ro-bind', '/etc/ld.so.cache', '/etc/ld.so.cache',
    '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp',
    '--', '/usr/bin/python3', '-B', '-c', program, str(port), str(ROOT)]
result = subprocess.run(command, text=True, capture_output=True, timeout=20)
listener.close()
(OUT / 'probe.stdout').write_text(result.stdout)
(OUT / 'probe.stderr').write_text(result.stderr)
report = {'passed': False, 'command': command, 'exitCode': result.returncode,
    'parentNamespaces': parent, 'nativeAcceptance': False, 'fullReleaseAccepted': False}
if result.returncode == 0:
    observed = json.loads(result.stdout)
    report.update(observed=observed, passed=all(observed['namespaces'][name] != parent[name]
        for name in parent) and observed['networkBlocked'] and observed['readOnlyInputs']
        and observed['hiddenHostSource'] and observed['coreLimit'] == [1, 1]
        and 'qa-harness.slice/qa-harness-' in observed['cgroup'])
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
if '--probe' in sys.argv or not report['passed']:
    print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json')}))
    raise SystemExit(not report['passed'])

full = {'passed': False, 'probe': report, 'nativeAcceptance': False,
        'fullReleaseAccepted': False}
try:
    manifest = builder.capture(ROOT.parents[1])
    lock = OUT / 'build-lock.json'
    lock.write_text(json.dumps(manifest, indent=2) + '\n')
    full['lockSHA256'] = builder.sha(lock)
    full['inputCount'] = builder.verify(manifest)
    print(json.dumps({'phase': 'locked-inputs', 'inputs': full['inputCount'],
                      'report': str(OUT / 'report.json')}), flush=True)
    pair = repro.run_pair(manifest, lock, OUT / 'pair')
    full['pair'] = pair
    if not pair['matched'] or pair['releaseBlocked']:
        raise builder.ChangedInput('Two offline builds did not match; see pair logs')
    left, right = OUT / 'pair/A/artifacts', OUT / 'pair/B/artifacts'
    archive = right / 'warlock-candidate.tar'
    length, original = archive.stat().st_size, builder.sha(archive)
    try:
        with archive.open('ab') as stream:
            stream.write(b'Intentional QA archive mismatch\n')
        negative = repro.compare(left, right)
        full['archiveMismatch'] = negative
        if not negative['releaseBlocked'] or negative['matched']:
            raise builder.ChangedInput('Different actual archive did not block release')
    finally:
        with archive.open('r+b') as stream:
            stream.truncate(length)
    if builder.sha(archive) != original:
        raise builder.ChangedInput('QA failed to restore original archive')
    asset = right / 'package/assets/bar.js'
    original_bytes = asset.read_bytes()
    try:
        asset.write_bytes(original_bytes + b'\n/* Intentional QA payload mismatch */\n')
        negative = repro.compare(left, right)
        full['payloadMismatch'] = negative
        if (not negative['releaseBlocked'] or negative['matched'] or
                not any(row.get('path') == 'assets/bar.js'
                        for row in negative['distributableDifferences'])):
            raise builder.ChangedInput('Different actual payload did not block release')
    finally:
        asset.write_bytes(original_bytes)
    alias = right / 'package/native/libaquamarine.so.14'
    target = os.readlink(alias)
    try:
        alias.unlink(); alias.symlink_to('./' + target)
        negative = repro.compare(left, right)
        full['aliasMismatch'] = negative
        if (not negative['releaseBlocked'] or negative['matched'] or
                not any(row.get('kind') == 'payload-link'
                        for row in negative['distributableDifferences'])):
            raise builder.ChangedInput('Changed loader alias did not block release')
    finally:
        alias.unlink(); alias.symlink_to(target)
    full['restoredComparison'] = repro.compare(left, right)
    full['passed'] = full['restoredComparison']['matched']
except (builder.ChangedInput, OSError, ValueError, subprocess.TimeoutExpired) as error:
    full['error'] = str(error)
finally:
    (OUT / 'report.json').write_text(json.dumps(full, indent=2) + '\n')
print(json.dumps({'passed': full['passed'], 'report': str(OUT / 'report.json')}), flush=True)
raise SystemExit(not full['passed'])
