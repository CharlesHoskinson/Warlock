#!/usr/bin/python3
"""Cabal test wrapper: dispatch only the exact executables in the build receipt."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys

MODES = ('positive', 'busy', 'inventory', 'malformed', 'stale', 'stale-claim',
         'view-fields', 'foreign', 'wrong-thread', 'expiry', 'reserved-cut',
         'pending-sync-cut', 'submitted-cut')
CHILD = {'internal-controls': 'custody-child', 'selected-fd-controls': 'selected-fd-child',
         'deadline-stop-controls': 'graceful-stop-child', 'current-session-oracles': 'credential-peer-child',
         'persistent-bootstrap-controls': 'credential-peer-child'}
COPY = {'held-executable-controls': 'custody-child', 'bootstrap-facade-controls': 'bootstrap-facade-child'}
FIXTURES = {'ingress-controls', 'credential-guard-controls'}
ROOTS = {'durable-storage-controls', 'selection-admission-controls', 'host-guard-controls',
         'slot-store-controls', 'pair-store-smoke', 'child-directory-controls',
         'independent-admission-shape', 'pair-store-sequences', 'independent-lifetime-owner'}
NOARGS = {'held-document-controls', 'public-controls', 'boundary-controls', 'owner-sequences',
          'elf-cases', 'native-cancellation-controls', 'desktop-boundary-controls'}


def pin(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise RuntimeError('fixture is not a regular nonsymlink: ' + str(path))
    st = path.stat()
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    return [str(st.st_dev), str(st.st_ino), str(st.st_size), digest]


def main():
    if len(sys.argv) != 2:
        raise RuntimeError('unexpected Cabal wrapper argv')
    requested = Path(sys.argv[1])
    all_suites = json.loads(Path(os.environ['WARLOCK_HASKELL_DISPATCH']).read_text())['suites']
    if str(requested) not in all_suites:
        raise RuntimeError('test path is outside the fixed build manifest')
    manifest = all_suites[str(requested)]
    suite = manifest['suite']
    if str(requested) != manifest['test']['path'] or requested.name != suite:
        raise RuntimeError('unexpected test executable path or name')
    if pin(requested) != manifest['test']['pin']:
        raise RuntimeError('test executable pin changed')
    base = Path(manifest['runRoot'])
    base.mkdir(mode=0o700)  # fails closed on reuse
    os.chmod(base, 0o700)
    def fresh(label):
        directory = base / label
        directory.mkdir(mode=0o700)
        return directory
    def fixture(name):
        item = manifest['fixtures'][name]
        path = Path(item['path'])
        if path.name != name or pin(path) != item['pin']:
            raise RuntimeError('fixture executable pin changed: ' + name)
        return path
    calls = []
    child_env = dict(os.environ)
    if suite in NOARGS:
        calls = [('default', [])]
    elif suite in CHILD:
        child = fixture(CHILD[suite])
        if suite == 'current-session-oracles':
            historical = Path('/home/charles/Warlock/implementation/warlock/haskell/protocol/test/fixtures/valid-prepare.bin')
            expected = '0d3341e70d17fbe5967dc898efcc978ff05b9029e80d60aee971ca9cfb8f2ed1'
            copied = Path(manifest['protocolFixtures']) / 'valid-prepare.bin'
            if pin(historical)[3] != expected or pin(copied)[3] != expected:
                raise RuntimeError('historical prepare fixture mapping differs')
        values = pin(child)
        args = [str(child)] + (values if suite in ('current-session-oracles', 'persistent-bootstrap-controls') else [])
        if suite == 'persistent-bootstrap-controls':
            args += ['full', '1'] if manifest.get('authProfile') == 'auth' else ['common']
        calls = [('default', args)]
    elif suite in COPY:
        original = fixture(COPY[suite])
        target_dir = fresh('image')
        image = target_dir / original.name
        shutil.copy2(original, image)
        values = pin(image)
        if values[2:] != pin(original)[2:]:
            raise RuntimeError('fixture copy differs')
        calls = [('default', [str(target_dir), image.name, values[2], values[3]])]
    elif suite in FIXTURES:
        calls = [('default', [manifest['protocolFixtures']])]
    elif suite in ROOTS:
        calls = [('default', [str(fresh('storage'))])]
    elif suite == 'independent-pairstore':
        calls = [(mode, [mode, str(fresh(mode))]) for mode in MODES]
    elif suite == 'ui-backend-controls':
        backend, child = fixture('warlock-ui-backend'), fixture('ui-stream-child')
        frontend = manifest['frontend']
        if set(frontend) != {'node', 'main', 'harness'}:
            raise RuntimeError('Unexpected fixed frontend manifest')
        for name, item in frontend.items():
            path = Path(item['path'])
            if set(item) != {'path', 'sha'} or not path.is_absolute() or pin(path)[3] != item['sha']:
                raise RuntimeError('UI frontend pin differs: ' + name)
        frontend_path = base / 'frontend.json'
        frontend_path.write_text(json.dumps(frontend, indent=2) + '\n')
        os.chmod(frontend_path, 0o600)
        child_env['WARLOCK_UI_FRONTEND_MANIFEST'] = str(frontend_path)
        calls = [('default', [str(backend), *pin(backend), str(child), *pin(child), str(fresh('storage'))])]
    else:
        raise RuntimeError('suite is not in fixed whitelist: ' + suite)
    results = []
    for label, args in calls:
        log = base / (label + '.log')
        with log.open('wb') as stream:
            proc = subprocess.Popen([str(requested), *args], stdout=stream, stderr=subprocess.STDOUT,
                                    start_new_session=True, env=child_env)
            timed_out = False
            def terminate_child(signum, frame):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                raise SystemExit(128 + signum)
            old_term = signal.signal(signal.SIGTERM, terminate_child)
            old_int = signal.signal(signal.SIGINT, terminate_child)
            try:
                try:
                    code = proc.wait(timeout=180)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    os.killpg(proc.pid, signal.SIGKILL)
                    code = proc.wait()
            finally:
                signal.signal(signal.SIGTERM, old_term)
                signal.signal(signal.SIGINT, old_int)
            # A surviving member is a cleanup failure, even when the leader exited normally.
            forced = False
            try:
                os.killpg(proc.pid, 0)
            except ProcessLookupError:
                pass
            else:
                forced = True
                os.killpg(proc.pid, signal.SIGKILL)
            results.append({'mode': label, 'argv': args, 'exit': code, 'timeout': timed_out,
                            'forcedCleanup': forced or timed_out, 'log': str(log)})
        (base / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
    if suite == 'ui-backend-controls':
        for name, item in manifest['frontend'].items():
            if pin(item['path'])[3] != item['sha']:
                raise RuntimeError('UI frontend changed during execution: ' + name)
    return 0 if len(results) == len(calls) and all(r['exit'] == 0 and not r['forcedCleanup'] for r in results) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('test wrapper failure:', error, file=sys.stderr, flush=True)
        sys.exit(1)
