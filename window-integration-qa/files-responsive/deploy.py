#!/usr/bin/env python3
"""Root-coordinated, same-process migration of the idle hidden Files UI."""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

B = Path(__file__).resolve().parent
LIVE = Path.home() / '.local/share/omarchy-files'
BACKUP = B / 'deployment-backup'

def run(*args):
    return subprocess.check_output(list(map(str, args)), text=True, timeout=8).strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ipc(method, *args):
    return run('qs', '-p', LIVE, 'ipc', 'call', 'files', method, *args)

def clients():
    return json.loads(run('hyprctl', 'clients', '-j'))

def native_state(windows):
    fields = ('address','stableId','pid','at','size','workspace','pinned',
              'fullscreen','fullscreenClient','fullscreenHandler')
    return sorted([{k:w.get(k) for k in fields} for w in windows], key=lambda w:w['address'])

def clipboard(primary=False):
    flags = ['--primary'] if primary else []
    result = []
    for mode in ('--no-newline', '--list-types'):
        r = subprocess.run(['wl-paste', *flags, mode], capture_output=True, timeout=4)
        result.append([r.returncode, hashlib.sha256(r.stdout).hexdigest()])
    return result

def process_start(pid):
    return Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19]

def accessibility():
    path = Path(f'/run/user/{os.getuid()}/at-spi/bus_0')
    stat = path.stat()
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(1); connection.connect(str(path))
    return {'socket': [stat.st_dev, stat.st_ino],
            'flags': [run('gsettings','get',schema,key) for schema,key in
                      [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),
                       ('org.gnome.desktop.interface','toolkit-accessibility')]]}

def main():
    assert not BACKUP.exists(), 'Use a fresh backup directory for every deployment attempt'
    manifest = json.loads((B / 'source-hashes.json').read_text())
    for item in manifest['changedQml']:
        assert digest(LIVE / item['path']) == item['originalSha256'], item['path']
        assert digest(B / 'app' / item['path']) == item['candidateSha256'], item['path']
    for item in manifest['unchangedOperationsAndFileopsSpec']:
        assert digest(LIVE / item['path']) == item['sha256'], item['path']
    instances = json.loads(run('qs', '-p', LIVE, 'list', '-j'))
    assert len(instances) == 1, 'Require one exact original Files instance'
    instance = instances[0]; pid = instance['pid']; start = process_start(pid)
    assert pid == 667402 and instance['config_path'] == str(LIVE / 'shell.qml')
    state = json.loads(ipc('state')); prompt = ipc('act', 'promptinfo', '')
    original = clients()
    assert not any(w['pid'] == pid for w in original), 'Original must be hidden'
    assert state['view'] == 'home' and state['entries'] == state['count'] == 0
    assert not state['sel'] and not state['clip'] and not state['lb'] and prompt == 'none'
    focus = json.loads(run('hyprctl', 'activewindow', '-j'))
    cursor = json.loads(run('hyprctl', 'cursorpos', '-j'))
    layers = json.loads(run('hyprctl', 'layers', '-j'))
    clips = [clipboard(), clipboard(True)]
    a11y = accessibility()
    preserved_paths = [Path.home()/'.config/omarchy/virtual-desktops.json',
                       Path.home()/'.local/state/omarchy-files/dashboard.json']
    hashes = {str(p): digest(p) if p.exists() else None for p in preserved_paths}
    migration = {'targetPid': pid, 'targetInstance': instance['id'],
                 'legacyState': state, 'visible': False, 'promptInfo': prompt,
                 'windowWidth': 1320, 'windowHeight': 800}
    BACKUP.mkdir(mode=0o700)
    (BACKUP/'clients-before.json').write_text(json.dumps(original))
    (BACKUP / 'state.json').write_text(json.dumps(state)); (BACKUP / 'state.json').chmod(0o600)
    report = {'pid': pid, 'instance': instance['id'], 'checks': {}, 'result': 'pending'}
    for item in manifest['changedQml']:
        dest = BACKUP/item['path']; dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((LIVE/item['path']).read_bytes())
        staged = BACKUP/'staged'/item['path']; staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes((B/'app'/item['path']).read_bytes())
        rollback = BACKUP/'rollback'/item['path']; rollback.parent.mkdir(parents=True, exist_ok=True)
        rollback.write_bytes(dest.read_bytes())
    migration_path = LIVE/'ui-migration.json'
    assert not migration_path.exists(), 'Unexpected existing migration file'
    staged_migration = BACKUP/'migration.json'
    fd = os.open(staged_migration, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as stream: json.dump(migration, stream)
    assert process_start(pid) == start
    handle = os.pidfd_open(pid)
    try:
        signal.pidfd_send_signal(handle, signal.SIGSTOP)
        replaced = []
        try:
            os.replace(staged_migration, migration_path)
            for item in manifest['changedQml']:
                path = LIVE/item['path']
                os.replace(BACKUP/'staged'/item['path'], path)
                replaced.append(item['path'])
        except Exception:
            for rel in reversed(replaced): os.replace(BACKUP/'rollback'/rel, LIVE/rel)
            if migration_path.exists(): migration_path.unlink()
            raise
        finally:
            signal.pidfd_send_signal(handle, signal.SIGCONT)
        deadline = time.monotonic()+12
        while True:
            try:
                loaded = json.loads(ipc('migrationStatus'))
                if loaded.get('ready'): break
                if loaded.get('error'): raise RuntimeError(loaded['error'])
            except subprocess.CalledProcessError:
                pass
            if time.monotonic()>deadline: raise RuntimeError('Migration did not become ready')
            time.sleep(.08)
        time.sleep(.3)
        checks = report['checks']
        checks['sameProcessAndInstance'] = loaded['pid']==pid and loaded['instance']==instance['id'] and process_start(pid)==start
        checks['exactPublicState'] = json.loads(ipc('state'))==state
        ui = json.loads(ipc('uiState')); init = loaded['initialization']
        checks['hiddenBeforeNativeMap'] = init['resumed'] and not init['visible'] and not init['backingVisible'] and not ui['visible']
        after_clients = clients()
        (BACKUP/'clients-after.json').write_text(json.dumps(after_clients))
        checks['originalNativeWindowState'] = native_state(after_clients)==native_state(original)
        checks['originalFocus'] = json.loads(run('hyprctl','activewindow','-j'))==focus
        checks['originalCursor'] = json.loads(run('hyprctl','cursorpos','-j'))==cursor
        checks['originalLayers'] = json.loads(run('hyprctl','layers','-j'))==layers
        checks['clipboards'] = [clipboard(), clipboard(True)]==clips
        checks['accessibilitySocketAndFlags'] = accessibility()==a11y
        checks['catalogAndDashboardBytes'] = hashes=={str(p):digest(p) if p.exists() else None for p in preserved_paths}
        checks['fileOperationsAndSpecUnchanged'] = all(digest(LIVE/i['path'])==i['sha256'] for i in manifest['unchangedOperationsAndFileopsSpec'])
        checks['installedQmlHashes'] = all(digest(LIVE/i['path'])==i['candidateSha256'] for i in manifest['changedQml'])
        assert all(checks.values()), checks
        report['result'] = 'pass'
        migration_path.unlink()
    except Exception as error:
        report['error'] = repr(error); report['result'] = 'fail'
        # Keep the tested stateful host if it loaded successfully; reverting the
        # legacy host would reopen FILES_OPEN and lose the migrated history.
        raise
    finally:
        os.close(handle)
        (B/'deployment-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'result':report['result'], 'checks':report['checks']}, indent=2))

if __name__ == '__main__': main()
