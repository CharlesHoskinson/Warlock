#!/usr/bin/env python3
"""Guarded native-only atlas deployment; requires accepted frozen private QA."""
from pathlib import Path
import argparse
import fcntl
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

USER_ROOT = Path.home()
STAGE = USER_ROOT / 'window-behavior-spec/minimize-motion-stage/cross-output-design'
sys.path.insert(0, str(STAGE))
from nested_preservation import CLIENT_FIELDS, project_outputs, files_state, reader_status, backup_catalogs, settle_catalogs

SIGNATURE = 'efb50993780079460b0cbed1363e2166a2de1d9f_1790777558_556595558'
MAIN_PID = 1468
CANDIDATE = STAGE / 'native-atlas-v18/hyprbars-v18-atlas-candidate.so'
TARGET = USER_ROOT / '.local/lib/libhyprbars-controls-v18.so'
OLD = USER_ROOT / '.local/lib/libhyprbars-controls-v14.so'
AUTOSTART = USER_ROOT / '.config/hypr/autostart.lua'
CANDIDATE_SHA = '908f134af0fc266d4b4e982c35b3cbd125659d1585584c23f31511b008282eba'
OLD_SHA = '6c9c346e9b7acb0951ee454ecfcf7dba295dfd0e4778d5dbdd883d96ca9c6274'
PRIVATE_QA = USER_ROOT / '.cache/window-atlas-v18-styled-v2-nested'
PRIVATE_REPORT_SHA = 'fc43088f5c643533346b01f4d3bdbf18c9aa7cf4629074c69993821338cb4883'
MANIFEST_SHA = '516aa454288c7c0c8dda3682befe8c59dbb1300cd34ac939801c2ccb9f87320f'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(*args):
    return subprocess.check_output(list(map(str, args)), text=True, timeout=15).strip()

def ctl(*args):
    return run('hyprctl', '-i', SIGNATURE, *args)

def data(*args):
    return json.loads(ctl(*args, '-j'))

def mapped(path):
    return str(path) in Path(f'/proc/{MAIN_PID}/maps').read_text()

def a11y_socket():
    path = Path(os.environ['XDG_RUNTIME_DIR']) / 'at-spi/bus_0'
    info = path.stat()
    with socket.socket(socket.AF_UNIX) as connection:
        connection.settimeout(.3)
        connection.connect(str(path))
    return [info.st_dev, info.st_ino]

def static_snapshot():
    keyboard_fields = ('address', 'name', 'layout', 'variant', 'options', 'capsLock', 'numLock', 'main')
    keyboards = [{k: d.get(k) for k in keyboard_fields} for d in data('devices')['keyboards']]
    client_fields = CLIENT_FIELDS + ('mapped', 'hidden', 'visible', 'acceptsInput', 'class',
        'initialClass', 'initialTitle', 'xwayland', 'pinFullscreened', 'fullscreenHandler',
        'allowedOverFullscreen', 'swallowing', 'inhibitingIdle', 'xdgTag', 'xdgDescription',
        'contentType', 'tearingHint')
    clients = sorted([{k: w.get(k) for k in client_fields} for w in data('clients')], key=lambda w: w['address'])
    focused = data('activewindow')
    return {
        'clients': clients,
        'outputs': project_outputs(data('monitors')),
        'files': files_state(USER_ROOT),
        'reader': reader_status(),
        'a11ySocket': a11y_socket(),
        'keyboards': sorted(keyboards, key=lambda d: (d['name'] or '', d['address'] or '')),
        'layers': data('layers'),
        'focus': {k: focused.get(k) for k in ('address', 'stableId', 'pid')},
        'cursor': data('cursorpos'),
        'configErrors': ctl('configerrors'),
        'accessibilityFlags': [run('gsettings', 'get', schema, key) for schema, key in (
            ('org.gnome.desktop.a11y.applications', 'screen-reader-enabled'),
            ('org.gnome.desktop.interface', 'toolkit-accessibility'))],
        'permissionEnforcement': data('getoption', 'ecosystem:enforce_permissions'),
    }

def immutable_paths():
    paths = [USER_ROOT / '.local/bin' / n for n in ('hypr-window-motion', 'hypr-windowctl', 'hypr-windowctl-core')]
    widget = USER_ROOT / '.config/omarchy/plugins/hoskinson.windows'
    paths += [widget / 'manifest.json'] + sorted((widget / 'widget_v65').rglob('*.qml'))
    paths += [USER_ROOT / '.config/hypr' / n for n in ('snap.lua', 'pin.lua', 'looknfeel.lua', 'hyprland.lua')]
    paths += sorted((USER_ROOT / '.local/share/omarchy-files').rglob('*.qml'))
    paths += sorted((USER_ROOT / '.local/share/omarchy-files/scripts').glob('*'))
    paths += [USER_ROOT / '.local/share/omarchy-files/spec/fileops.qnt', OLD]
    return {str(p): sha(p) for p in paths if p.is_file()}

def atomic_bytes(path, content, mode):
    temporary = path.with_name(path.name + '.atlas-v18.tmp')
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists(): temporary.unlink()

def restore_focus(snapshot):
    selected = snapshot['focus']
    clients = data('clients')
    assert any(all(w.get(k) == v for k, v in selected.items()) for w in clients)
    ctl('dispatch', 'hl.dsp.focus({window=' + json.dumps('address:' + selected['address']) + '})')
    cursor = snapshot['cursor']
    ctl('dispatch', f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert os.environ.get('HYPRLAND_INSTANCE_SIGNATURE') == SIGNATURE
    assert any(i['pid'] == MAIN_PID and i['instance'] == SIGNATURE for i in json.loads(run('hyprctl', 'instances', '-j')))
    assert sha(CANDIDATE) == CANDIDATE_SHA and sha(OLD) == OLD_SHA
    assert not TARGET.exists(), 'A fresh library URL is required'
    assert mapped(OLD) and not mapped(TARGET)
    assert data('getoption', 'ecosystem:enforce_permissions').get('bool') is False, 'Do not trigger a permission popup during this unattended migration'
    assert sha(PRIVATE_QA / 'snapshot-smoke.json') == PRIVATE_REPORT_SHA
    qa = json.loads((PRIVATE_QA / 'snapshot-smoke.json').read_text())
    assert qa['result'] == 'pass' and len(qa['checks']) == 59 and all(qa['checks'].values())
    manifest = PRIVATE_QA / 'executed-manifest.json'
    assert sha(manifest) == MANIFEST_SHA
    for path, expected in json.loads(manifest.read_text())['files'].items():
        assert sha(Path(path)) == expected, path
    assert json.loads(run('omarchy-shell', 'hoskinson.windows', 'motionVisualState')) == []
    root = Path(os.environ['XDG_RUNTIME_DIR']) / 'hypr-window-motion' / hashlib.sha256(SIGNATURE.encode()).hexdigest()[:20]
    if (root / 'pending.json').exists():
        assert json.loads((root / 'pending.json').read_text()) == [], 'Do not settle an active operation for deployment'
    args.output.mkdir(mode=0o700)
    os.umask(0o077)
    source_bytes = AUTOSTART.read_bytes()
    source_mode = AUTOSTART.stat().st_mode & 0o777
    assert source_mode == 0o644, 'Preserve the observed autostart permissions'
    assert source_bytes.count(b'libhyprbars-controls-v14.so') == 1
    changed_bytes = source_bytes.replace(b'libhyprbars-controls-v14.so', b'libhyprbars-controls-v18.so')
    before = static_snapshot()
    assert not before['files']['visible'] and 'false' in before['reader'] and before['configErrors'] == ''
    immutables = immutable_paths()
    others = [p for p in data('plugin', 'list') if p['name'] != 'hyprbars']
    catalogs = backup_catalogs(args.output, USER_ROOT)
    (args.output / 'autostart.lua.before').write_bytes(source_bytes)
    title_hashes = lambda: {w['address']: hashlib.sha256(w.get('title', '').encode()).hexdigest() for w in data('clients')}
    report = {'candidateSHA256': CANDIDATE_SHA, 'rollbackSHA256': OLD_SHA, 'before': before,
              'immutableBefore': immutables, 'privateQAReportSHA256': PRIVATE_REPORT_SHA,
              'scope': 'Native plugin and autostart path only; full Windows parity remains incomplete',
              'clientComparison': 'All captured stable compositor fields; app-owned current title hashes are observed separately because the original Codex terminal animates its title.',
              'titleHashesBefore': title_hashes(), 'checks': {}}
    changed = False
    try:
        stopped = json.loads(run(USER_ROOT / '.local/bin/hypr-window-motion', 'stop'))
        assert stopped.get('ok'), stopped
        assert static_snapshot() == before, 'Idle stop must not change original desktop state'
        with TARGET.open('xb') as destination:
            destination.write(CANDIDATE.read_bytes())
        TARGET.chmod(0o755)
        assert sha(TARGET) == CANDIDATE_SHA
        assert AUTOSTART.read_bytes() == source_bytes
        atomic_bytes(AUTOSTART, changed_bytes, source_mode)
        changed = True
        assert ctl('plugin', 'unload', OLD) == 'ok'
        assert ctl('plugin', 'load', TARGET) == 'ok'
        assert ctl('reload') == 'ok'
        time.sleep(.4)
        restore_focus(before)
        time.sleep(.1)
        for name in ('window_snapshot', 'window_atlas', 'window_families', 'file_drag_active'):
            assert ctl('repl', f'print(type(hl.plugin.hyprbars.{name}))') == 'function', name
        assert ctl('repl', 'print(hl.plugin.hyprbars.drag_bridge(),hl.plugin.hyprbars.modal_focus_bridge())').split() == ['true', 'true']
        report['catalogComparison'] = settle_catalogs(catalogs, seconds=4)
        after = static_snapshot()
        report['after'] = after
        report['titleHashesAfter'] = title_hashes()
        report['checks'].update({name: after[name] == value for name, value in before.items()})
        report['checks']['allCatalogBytes'] = all(v['exactBytes'] for v in report['catalogComparison'].values())
        report['checks']['immutableCodeBytes'] = immutable_paths() == immutables
        report['checks']['freshNativeMapping'] = mapped(TARGET) and not mapped(OLD)
        report['checks']['otherPlugins'] = [p for p in data('plugin', 'list') if p['name'] != 'hyprbars'] == others
        report['checks']['autostartExactPathOnly'] = AUTOSTART.read_bytes() == changed_bytes
        report['checks']['autostartModePreserved'] = AUTOSTART.stat().st_mode & 0o777 == source_mode
        assert all(report['checks'].values()), {k: v for k, v in report['checks'].items() if not v}
        report['result'] = 'deployed; integrated installed QA pending'
    except Exception as error:
        report['error'] = repr(error)
        if changed:
            report['rollbackSteps'] = []
            def attempt(name, operation):
                try:
                    operation()
                    report['rollbackSteps'].append({'name': name, 'ok': True})
                except Exception as recovery_error:
                    report['rollbackSteps'].append({'name': name, 'ok': False, 'error': repr(recovery_error)})
            def unload_candidate():
                if mapped(TARGET): assert ctl('plugin', 'unload', TARGET) == 'ok'
            def load_old():
                assert not mapped(TARGET), 'Do not install overlapping native hooks after a refused unload'
                if not mapped(OLD): assert ctl('plugin', 'load', OLD) == 'ok'
            def reload_config():
                assert ctl('reload') == 'ok'
            def observe_rollback():
                time.sleep(.2)
                report['rollbackAfter'] = static_snapshot()
                report['rollbackPreserved'] = report['rollbackAfter'] == before
                report['rollbackNativeMapping'] = mapped(OLD) and not mapped(TARGET)
            attempt('restore autostart bytes and mode', lambda: atomic_bytes(AUTOSTART, source_bytes, source_mode))
            attempt('unload candidate if mapped', unload_candidate)
            attempt('load original plugin if absent', load_old)
            attempt('reload original config', reload_config)
            attempt('restore original focus and cursor', lambda: restore_focus(before))
            attempt('observe original desktop and native mapping', observe_rollback)
        report['result'] = ('rolled back' if report.get('rollbackPreserved') and report.get('rollbackNativeMapping')
                            and all(s['ok'] for s in report.get('rollbackSteps', []))
                            else 'rollback incomplete; retained recovery evidence') if changed else 'stopped before compositor mutation'
        raise
    finally:
        (args.output / 'deployment.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('before', 'after', 'immutableBefore')}, indent=2))

if __name__ == '__main__':
    with (USER_ROOT / 'window-integration-qa/atlas-deployment.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        main()
