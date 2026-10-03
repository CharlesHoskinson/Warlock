#!/usr/bin/env python3
"""Paired user-local snapshot plugin/helpers/widget deployment with rollback."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

H = Path.home()
STAGE = H / 'window-behavior-spec/minimize-motion-stage/whole-window'
BACKUP = H / 'window-integration-qa/minimize-motion-deployment-v14'
PLUGIN = H / '.local/lib/libhyprbars-controls-v14.so'
OLD_PLUGIN = H / '.local/lib/libhyprbars-controls-v13.so'
AUTOSTART = H / '.config/hypr/autostart.lua'
MANIFEST = H / '.config/omarchy/plugins/hoskinson.windows/manifest.json'
WIDGET = MANIFEST.parent / 'widget_v64'


def run(*args):
    return subprocess.check_output([str(a) for a in args], text=True, timeout=15).strip()


def atomic_copy(source, destination):
    temporary = destination.with_name(destination.name + '.motion-deployment.tmp')
    shutil.copy2(source, temporary)
    os.replace(temporary, destination)


def main():
    candidate = STAGE / 'native/hyprbars-v14-snapshot-candidate.so'
    expected = '6c9c346e9b7acb0951ee454ecfcf7dba295dfd0e4778d5dbdd883d96ca9c6274'
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == expected
    assert not PLUGIN.exists(), 'Use a fresh native library filename'
    assert not WIDGET.exists(), 'Use a fresh QML URL'
    assert not BACKUP.exists(), 'Preserve previous backup artifacts'
    assert run('hyprctl', 'configerrors') == ''
    assert json.loads(run('omarchy-shell', 'hoskinson.windows', 'motionVisualState')) == []
    original = json.loads(run('hyprctl', 'clients', '-j'))
    BACKUP.mkdir(parents=True)
    shutil.copy2(AUTOSTART, BACKUP / 'autostart.lua.before')
    shutil.copy2(MANIFEST, BACKUP / 'manifest.before.json')
    helpers = ['hypr-windowctl-core', 'hypr-window-motion', 'hypr-windowctl']
    for name in helpers: shutil.copy2(H / '.local/bin' / name, BACKUP / (name + '.before'))
    report = dict(original=original, librarySHA256=expected, checks={}, testsPending=True)
    old_unloaded = False
    new_loaded = False
    try:
        run(H / '.local/bin/hypr-window-motion', 'stop')
        shutil.copy2(candidate, PLUGIN)
        text = AUTOSTART.read_text()
        assert text.count('libhyprbars-controls-v13.so') == 1
        AUTOSTART.write_text(text.replace('libhyprbars-controls-v13.so', 'libhyprbars-controls-v14.so'))
        assert run('hyprctl', 'plugin', 'unload', OLD_PLUGIN) == 'ok'
        old_unloaded = True
        assert run('hyprctl', 'plugin', 'load', PLUGIN) == 'ok'
        new_loaded = True
        assert run('hyprctl', 'reload') == 'ok'
        assert run('hyprctl', 'configerrors') == ''
        assert run('hyprctl', 'repl', 'print(type(hl.plugin.hyprbars.window_snapshot))') == 'function'
        for name in helpers: atomic_copy(STAGE / name, H / '.local/bin' / name)
        shutil.copytree(STAGE / 'widget_v64', WIDGET)
        manifest = json.loads(MANIFEST.read_text())
        manifest['entryPoints']['barWidget'] = 'widget_v64/Windows.qml'
        MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
        run('omarchy-shell', 'shell', 'rescanPlugins')
        time.sleep(.6)
        assert isinstance(json.loads(run('omarchy-shell', 'hoskinson.windows', 'stateAll')), list)
        current = {w['address']: w for w in json.loads(run('hyprctl', 'clients', '-j'))}
        assert all(w['address'] in current and all(current[w['address']].get(field) == w.get(field)
            for field in ('pid', 'stableId', 'at', 'size', 'workspace', 'pinned', 'fullscreen')) for w in original)
        report['checks']['pairedDeployment'] = True
        report['checks']['originalClientStatesPreserved'] = True
        report['checks']['noConfigurationErrors'] = True
        report['checks']['nativeSnapshotFunctionRegistered'] = True
        report['helpers'] = {name: hashlib.sha256((H / '.local/bin' / name).read_bytes()).hexdigest() for name in helpers}
        report['widget'] = str(WIDGET)
        report['library'] = str(PLUGIN)
        report['result'] = 'deployed; native animation acceptance pending'
    except Exception as error:
        report['error'] = repr(error)
        for name in helpers: atomic_copy(BACKUP / (name + '.before'), H / '.local/bin' / name)
        shutil.copy2(BACKUP / 'manifest.before.json', MANIFEST)
        shutil.copy2(BACKUP / 'autostart.lua.before', AUTOSTART)
        if new_loaded: run('hyprctl', 'plugin', 'unload', PLUGIN)
        if old_unloaded: run('hyprctl', 'plugin', 'load', OLD_PLUGIN)
        run('hyprctl', 'reload')
        run('omarchy-shell', 'shell', 'rescanPlugins')
        report['result'] = 'rolled back'
        raise
    finally:
        (BACKUP / 'deployment.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'original'}, indent=2))


if __name__ == '__main__': main()
