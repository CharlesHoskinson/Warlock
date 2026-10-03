#!/usr/bin/env python3
"""Native Files launcher checks using a disposable copy of the actual app.

The installed launcher is copied with only its APP constant redirected to the
disposable QML tree. Original explorer process/window and data are preserved.
Run only in the coordinated GUI slot.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

H = Path.home()
REPORT = H / '.cache/window-files-summon-native.json'


def run(*args, timeout=10):
    return subprocess.check_output([str(a) for a in args], text=True, timeout=timeout).strip()


def data(name): return json.loads(run('hyprctl', name, '-j'))


def wait(predicate, label):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        value = predicate()
        if value: return value
        time.sleep(.08)
    raise AssertionError(label)


def main():
    original = data('clients')
    focus = data('activewindow')
    cursor = data('cursorpos')
    catalog = H / '.config/omarchy/virtual-desktops.json'
    saved_catalog = catalog.read_bytes() if catalog.exists() else None
    report = {'checks': {}, 'scope': 'Actual Files app copy, installed launcher with APP constant redirected'}
    process = None
    with tempfile.TemporaryDirectory(prefix='files-native-') as directory:
        root = Path(directory)
        app = root / 'app'
        shutil.copytree(H / '.local/share/omarchy-files', app,
                        ignore=shutil.ignore_patterns('spec', '__pycache__'))
        source = (H / '.local/bin/omarchy-files').read_text()
        old = 'APP="$HOME/.local/share/omarchy-files"'
        assert source.count(old) == 1
        launcher = root / 'omarchy-files'
        launcher.write_text(source.replace(old, 'APP=' + json.dumps(str(app))))
        env = dict(os.environ, FILES_STATE=str(root / 'state'), FILES_DRYRUN='1')
        payload = root / 'folder'
        payload.mkdir()
        (payload / 'sample.txt').write_text('Disposable explorer fixture\n')
        current = next(m for m in data('monitors') if m['focused'])['activeWorkspace']['name']
        def launch():
            subprocess.run(['bash', str(launcher), str(payload)], env=env, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=15)
        try:
            # Start in foreground so ownership and exact cleanup PID are known.
            process = subprocess.Popen(['qs', '-p', str(app)], env=env,
                                       stdout=subprocess.DEVNULL, stderr=(root / 'qml.log').open('w'))
            wait(lambda: subprocess.run(['qs', '-p', str(app), 'ipc', 'call', 'files', 'state'],
                                        capture_output=True).returncode == 0, 'copied app IPC ready')
            launch()
            def client(): return next((w for w in data('clients') if w['pid'] == process.pid and w['title'] == 'Files'), None)
            initial = wait(client, 'Files maps after launcher')
            address, stable, pid = initial['address'], initial['stableId'], initial['pid']
            def windowctl(command): return run(H / '.local/bin/hypr-windowctl', command, address, stable, pid)
            def rect(w): return w['at'] + w['size']
            run('hyprctl', 'dispatch', f'hl.dsp.window.move({{x=140,y=260,window="address:{address}"}})')
            run('hyprctl', 'dispatch', f'hl.dsp.window.resize({{x=900,y=560,window="address:{address}"}})')
            time.sleep(.3)
            saved = client()
            report['originalFixture'] = saved
            report['checks']['warmLaunchMapsAndFocuses'] = data('activewindow').get('address') == address
            windowctl('minimize')
            assert client()['workspace']['name'] == 'special:win-minimized'
            launch()
            restored = wait(lambda: client() if client()['workspace']['name'] == current else None, 'launcher restores on original current desktop')
            report['checks']['minimizedExactGeometry'] = rect(restored) == rect(saved)
            report['checks']['minimizedPinPreserved'] = restored['pinned'] == saved['pinned']
            state = Path(os.environ['XDG_RUNTIME_DIR']) / 'hypr-windowctl' / address
            report['checks']['minimizedStateConsumed'] = not state.exists() and not state.with_name(state.name + '.monitor.json').exists()
            run('hyprctl', 'dispatch', f'hl.dsp.window.pin({{window="address:{address}"}})')
            assert client()['pinned']
            windowctl('minimize')
            assert not client()['pinned']
            launch()
            restored = client()
            report['checks']['pinnedMinimizedRestore'] = restored['pinned'] and rect(restored) == rect(saved)
            report['checks']['restoredFocusExactIdentity'] = (
                data('activewindow').get('address') == address and restored['stableId'] == stable and restored['pid'] == pid)
            report['checks']['pinnedStateConsumed'] = not state.exists()
            report['checks']['noScratchpadEntry'] = restored['workspace']['name'] == current
        except Exception as error:
            report['error'] = repr(error)
        finally:
            # Hide only the copied explorer before normal process cleanup.
            if process and process.poll() is None:
                subprocess.run(['qs', '-p', str(app), 'ipc', 'call', 'files', 'toggle'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4)
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired: process.kill(); process.wait()
            if saved_catalog is None: catalog.unlink(missing_ok=True)
            else: catalog.write_bytes(saved_catalog)
            existing = {w['address']: w for w in data('clients')}
            report['checks']['originalWindowStatesPreserved'] = all(
                w['address'] in existing and all(existing[w['address']].get(k) == w.get(k)
                    for k in ('pid', 'stableId', 'workspace', 'at', 'size', 'pinned', 'fullscreen'))
                for w in original)
            if focus.get('address') in existing and existing[focus['address']].get('stableId') == focus.get('stableId'):
                run('hyprctl', 'dispatch', f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
            run('hyprctl', 'dispatch', f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
            report['checks']['fixtureProcessExited'] = process is None or process.poll() is not None
    report['result'] = 'pass' if not report.get('error') and all(report['checks'].values()) else 'fail'
    REPORT.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    assert report['result'] == 'pass'


if __name__ == '__main__': main()
