#!/usr/bin/env python3
"""Fixed offline delegated-user-namespace authentication CPU check.

Only qa_cpu's reviewed dispatch may run the outer entry point.  This is not a
native campaign or original-scenario acceptance.
"""
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base
from check_haskell_cpu import (CACHE, MANIFEST, artifacts, digest, directory,
                               regular, tree_hashes_without_receipt)

LOCK = ROOT / '.warlock-contributor/auth-namespace-helper-lock.json'
TOOLS = {name: Path('/usr/bin') / name for name in
         ('unshare', 'newuidmap', 'newgidmap', 'bwrap')}
EXPECTED_MAP = [[0, 1000, 1], [1, 100000, 65536]]
CAPS = (1 << 5) | (1 << 7)  # CAP_KILL and CAP_SETUID
ENV = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
       'PYTHONDONTWRITEBYTECODE': '1', 'GHC_ENVIRONMENT': '-', 'TMPDIR': '/tmp'}


def write(path, value):
    # Separate reports per process: the parent never overwrites child evidence.
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def snapshot():
    status = Path('/proc/self/status').read_text().splitlines()
    capabilities = {line.split(':', 1)[0]: line.split(':', 1)[1].strip()
                    for line in status if line.startswith(('CapInh:', 'CapPrm:', 'CapEff:', 'CapBnd:', 'CapAmb:'))}
    return {'namespaces': {name: os.readlink('/proc/self/ns/' + name) for name in ('user', 'net', 'pid')},
            'uidMap': [[int(x) for x in row.split()] for row in Path('/proc/self/uid_map').read_text().splitlines()],
            'gidMap': [[int(x) for x in row.split()] for row in Path('/proc/self/gid_map').read_text().splitlines()],
            'uid': os.getuid(), 'euid': os.geteuid(), 'gid': os.getgid(), 'egid': os.getegid(),
            'capabilities': capabilities}


def helper_inputs():
    result = {}
    for name, path in TOOLS.items():
        resolved = path.resolve(strict=True)
        if not resolved.is_file():
            raise RuntimeError('Helper is not a regular file: ' + str(path))
        info = resolved.stat()
        version = subprocess.run([str(resolved), '--version'], env=ENV, capture_output=True,
                                 text=True, timeout=10, check=True)
        result[name] = {'path': str(path), 'resolved': str(resolved), 'sha256': digest(resolved),
                        'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid,
                        'version': (version.stdout + version.stderr).strip()}
    return result


def check_output(output):
    if output.parent != ROOT / '.warlock-contributor' or not re.fullmatch(r'auth-cpu-[0-9]+', output.name):
        raise RuntimeError('Invalid private output path')
    directory(output)
    if stat.S_IMODE(output.stat().st_mode) != 0o700:
        raise RuntimeError('Private output must be mode 0700')


def sdk_state(packet):
    sdk = CACHE / packet['sdkDirectory']
    directory(sdk)
    receipt = sdk / 'sdk.json'
    regular(receipt)
    saved = json.loads(receipt.read_text())
    files = tree_hashes_without_receipt(sdk)
    if saved['manifestSHA256'] != digest(MANIFEST) or saved['files'] != files or len(files) != 11250:
        raise RuntimeError('SDK receipt or 11250-file inventory differs')
    artifacts(packet)
    return {'receiptSHA256': digest(receipt), 'manifestSHA256': digest(MANIFEST),
            'files': files}


def source_state():
    from qa_cpu import haskell_inputs
    names = haskell_inputs(ROOT, False) | {'tools/check_auth_cpu.py'}
    result = {}
    for name in sorted(names):
        path = ROOT / name
        regular(path)
        result[name] = digest(path)
    return result


def mapped(state):
    if (state['uidMap'] != EXPECTED_MAP or state['gidMap'] != EXPECTED_MAP or
            any(state[k] != 0 for k in ('uid', 'euid', 'gid', 'egid'))):
        raise RuntimeError('Unexpected delegated UID/GID mapping or identity')


def internal(output, token, stage):
    check_output(output)
    marker = output / 'marker'
    regular(marker)
    if marker.stat().st_uid != os.getuid() or stat.S_IMODE(marker.stat().st_mode) != 0o600 or marker.read_text() != token:
        raise RuntimeError('Invalid internal marker')
    report = {'stage': stage, 'passed': False}
    path = output / (stage + '.json')
    try:
        before = snapshot()
        report['before'] = before
        mapped(before)
        if stage == 'delegated':
            write(output / 'delegated-before.json', before)
            cmd = ['/usr/bin/bwrap', '--die-with-parent', '--unshare-net', '--unshare-pid',
                   '--ro-bind', '/', '/', '--proc', '/proc', '--dev', '/dev',
                   '--tmpfs', '/tmp', '--tmpfs', '/run/user', '--tmpfs', '/home',
                   '--dir', '/home/charl', '--dir', '/home/charl/code',
                   '--dir', '/home/charl/.cache', '--ro-bind', str(ROOT), str(ROOT),
                   '--dir', '/home/charles',
                   '--ro-bind', str(ROOT), '/home/charles/Warlock',
                   '--ro-bind', str(CACHE), str(CACHE), '--bind', str(output), str(output),
                   '--cap-drop', 'ALL', '--cap-add', 'CAP_SETUID', '--cap-add', 'CAP_KILL',
                   '--clearenv', '--chdir', str(ROOT), '--', '/usr/bin/python3', '-B',
                   str(Path(__file__).resolve()), '--private', str(output), token]
            report['command'] = cmd[:-1] + ['<marker>']
            child = subprocess.run(cmd, env=ENV, cwd=ROOT)
            report['exit'] = child.returncode
            report['after'] = snapshot()
            if child.returncode != 0:
                raise RuntimeError('Private namespace failed; see private report and logs')
            report['passed'] = True
        else:
            parent = json.loads((output / 'outer.json').read_text())['before']
            delegated = json.loads((output / 'delegated-before.json').read_text())
            if before['namespaces']['user'] != delegated['namespaces']['user']:
                raise RuntimeError('bwrap changed the delegated user namespace')
            if any(before['namespaces'][n] == parent['namespaces'][n] for n in ('user', 'net', 'pid')):
                raise RuntimeError('A required namespace is not private')
            interfaces = {line.split(':', 1)[0].strip() for line in Path('/proc/net/dev').read_text().splitlines() if ':' in line}
            if interfaces != {'lo'}:
                raise RuntimeError('Network namespace is not loopback-only')
            caps = before['capabilities']
            if int(caps['CapEff'], 16) != CAPS or int(caps['CapPrm'], 16) != CAPS or int(caps['CapAmb'], 16):
                raise RuntimeError('Private capabilities differ from SETUID and KILL')
            packet = json.loads(MANIFEST.read_text())
            report['sdkBefore'] = sdk_state(packet)
            report['sourceBefore'] = source_state()
            from haskell_build import build
            report['build'] = build(CACHE / packet['sdkDirectory'], output, dict(ENV), profile='auth')
            report['sdkAfter'] = sdk_state(packet)
            report['sourceAfter'] = source_state()
            report['after'] = snapshot()
            if report['sdkBefore'] != report['sdkAfter'] or report['sourceBefore'] != report['sourceAfter']:
                raise RuntimeError('SDK or source changed during check')
            if report['before'] != report['after']:
                raise RuntimeError('Namespace, mapping or capabilities changed during check')
            evidence = report['build'].get('authEvidence', {})
            if (report['build'].get('passed') is not True or evidence.get('mode') != 'full' or
                    evidence.get('crossUidPassed') is not True or evidence.get('childUid') != 1 or
                    evidence.get('suite') != 'persistent-bootstrap-controls'):
                raise RuntimeError('Auth build or full cross-UID suite did not pass')
            report['passed'] = True
    except Exception:
        report['error'] = traceback.format_exc()
    finally:
        if stage == 'private' and 'after' not in report:
            try:
                report['after'] = snapshot()
                report['sourceAfter'] = source_state()
                report['sdkAfter'] = sdk_state(json.loads(MANIFEST.read_text()))
            except Exception:
                report['postcheckError'] = traceback.format_exc()
        write(path, report)
    return 0 if report['passed'] else 1


def outer():
    if os.getuid() != 1000 or os.geteuid() != 1000 or os.getgid() != 1000:
        raise RuntimeError('Expected ordinary host UID/GID 1000')
    scope = require_qa_scope()
    runtime_base()
    output = ROOT / '.warlock-contributor' / ('auth-cpu-' + str(time.time_ns()))
    output.mkdir(mode=0o700)
    check_output(output)
    report = {'schema': 1, 'passed': False, 'scope': scope, 'nativeAccepted': False,
              'originalScenariosAccepted': False, 'releaseAccepted': False, 'before': snapshot()}
    child = None
    forced = False
    def interrupted(signum, _frame):
        raise InterruptedError('Received signal ' + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        regular(LOCK)
        reviewed = json.loads(LOCK.read_text())
        helpers = helper_inputs()
        if reviewed != {'schema': 1, 'helpers': helpers}:
            raise RuntimeError('Installed namespace helpers differ from root-reviewed lock')
        report['helperLockSHA256'] = digest(LOCK)
        report['helpersBefore'] = helpers
        report['sourceBefore'] = source_state()
        packet = json.loads(MANIFEST.read_text())
        report['sdkBefore'] = sdk_state(packet)
        token = os.urandom(32).hex()
        marker = output / 'marker'
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(token)
        write(output / 'outer.json', report)
        cmd = ['/usr/bin/unshare', '--user', '--map-user=0', '--map-group=0',
               '--map-users=1:100000:65536', '--map-groups=1:100000:65536', '--keep-caps',
               '--fork', '--kill-child=KILL', '--', '/usr/bin/python3', '-B',
               str(Path(__file__).resolve()), '--delegated', str(output), token]
        report['command'] = cmd[:-1] + ['<marker>']
        with (output / 'namespace.stdout').open('wb') as stdout, (output / 'namespace.stderr').open('wb') as stderr:
            child = subprocess.Popen(cmd, env=ENV, cwd=ROOT, stdout=stdout, stderr=stderr, start_new_session=True)
            report['childPid'] = child.pid
            try:
                report['exit'] = child.wait(timeout=1140)
            except BaseException:
                forced = True
                raise
        if report['exit'] != 0:
            raise RuntimeError('Delegated namespace failed; see retained reports and logs')
        private = json.loads((output / 'private.json').read_text())
        delegated = json.loads((output / 'delegated.json').read_text())
        if private.get('passed') is not True or delegated.get('passed') is not True:
            raise RuntimeError('Required full cross-UID check did not complete')
        report['passed'] = True
    except BaseException:
        report['error'] = traceback.format_exc()
    finally:
        if child is not None and child.poll() is None:
            forced = True
            try:
                os.killpg(child.pid, signal.SIGTERM)
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            except ProcessLookupError:
                child.wait()
        if child is not None:
            try:
                os.killpg(child.pid, 0)
            except ProcessLookupError:
                pass
            else:
                forced = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        report['cleanup'] = 'forced' if forced else 'normal'
        try:
            report['after'] = snapshot()
            report['helpersAfter'] = helper_inputs()
            report['sourceAfter'] = source_state()
            report['sdkAfter'] = sdk_state(json.loads(MANIFEST.read_text()))
            if (report['before'] != report['after'] or report.get('helpersBefore') != report['helpersAfter'] or
                report.get('sourceBefore') != report['sourceAfter'] or report.get('sdkBefore') != report['sdkAfter'] or forced):
                raise RuntimeError('Pre/post verification failed or cleanup was forced')
        except BaseException:
            report['passed'] = False
            report['postcheckError'] = traceback.format_exc()
        write(output / 'outer.json', report)
        print(json.dumps({'passed': report['passed'], 'report': str(output / 'outer.json')}), flush=True)
    return 0 if report['passed'] else 1


def main():
    if len(sys.argv) == 1:
        return outer()
    if (len(sys.argv) == 4 and sys.argv[1] in ('--delegated', '--private') and
            re.fullmatch(r'[0-9a-f]{64}', sys.argv[3])):
        return internal(Path(sys.argv[2]), sys.argv[3], sys.argv[1][2:])
    raise RuntimeError('Only the fixed outer entry or internal marker is supported')


if __name__ == '__main__':
    raise SystemExit(main())
