"""Serial native shell-owned window-row context-menu qualification only.

Real pointer/keyboard -> compiled Elm -> existing authenticated minimize/restore.
No full taskbar, application menus, transformed outputs, AT or release claim.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
CORE = REPO/'implementation/elm-input-region-fix-v23'
spec = importlib.util.spec_from_file_location('context_menu_private_host', CORE/'candidate_host.py')
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
sys.path.insert(0, str(CORE/'adapter'))
from endpoint import start_time
from effect_endpoint import Endpoint

OUT = ROOT/'qa'/('native-'+str(time.time_ns()))
OUT.mkdir()
OUTPUT = Path('/home/hoskinson/window-integration-qa')/('elm-context-menu-'+str(time.time_ns()))
POINTER = Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD = Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
FIXTURE = REPO/'implementation/elm-authority-v3/qa/fixture.py'
report = {'passed': False, 'mainDesktopActions': False,
          'scope': 'Real secondary-click and keyboard shell-owned row menu with disabled actions, Escape DOM focus and authenticated minimize/restore; no full taskbar, stale-target native, output, accessibility or release acceptance',
          'checks': [], 'output': str(OUTPUT)}
apps = []
s = None
loaded = False
fixture = None
LUA = b'''hl.config({xwayland={enabled=false},animations={enabled=false}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
'''

def check(name, value, **evidence):
    report['checks'].append({'name': name, 'passed': bool(value), **evidence})
    assert value, name

def wait(function, seconds=6):
    until = time.monotonic()+seconds
    while time.monotonic() < until:
        s.guard()
        value = function()
        if value:
            return value
        time.sleep(.04)
    raise RuntimeError('Unchanged six-second observation deadline')

try:
    build_path = sorted((ROOT/'qa').glob('host-build-*/report.json'))[-1]
    build = json.loads(build_path.read_text())
    assert build['passed']
    for relative, digest in build['inputs'].items():
        assert host.digest(ROOT/relative) == digest, relative
    binary = build_path.parent/'elm-host'
    assert host.digest(binary) == build['binarySHA256']
    manifest_path = CORE/'qa/build-pair-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['passed']
    for relative, digest in manifest['files'].items():
        assert host.digest(CORE/relative) == digest, relative
    pair = manifest['nativePair']
    plugin = pair['plugin']['path']
    assert host.digest(plugin) == pair['plugin']['sha256']
    assert host.digest(pair['core']['path']) == pair['core']['sha256']
    backend_path = build_path.parent/'inputs/adapter/daemon.py'
    assert backend_path.is_file(), 'Frozen backend is required'
    report.update(buildReport=str(build_path), buildReportSHA256=host.digest(build_path),
                  pair=pair, sourceManifestSHA256=host.digest(manifest_path),
                  inputs={str(p):host.digest(p) for p in (Path(__file__), POINTER, KEYBOARD,
                          KEYBOARD.with_suffix('.c'), FIXTURE, CORE/'candidate_host.py')})
    shutil.copy2(__file__, OUT/'native.py')
    with host.PrivateHyprSession(OUTPUT, dict(os.environ), 800, 600, LUA, mesa_vendor=True) as s:
        try:
            assert s.ctl('plugin', 'load', plugin).strip() == 'ok'
            loaded = True
            native = next(row for _, row in s.host.processes if row['name'] == 'hyprland')
            config = {'runtime': str(s.host.runtime), 'instance': s.env['HYPRLAND_INSTANCE_SIGNATURE'],
                      'pid': native['pid'], 'expected_start': start_time(native['pid']),
                      'binary_sha256': pair['core']['sha256']}
            config_path = OUTPUT/'authority-config.json'
            config_path.write_text(json.dumps(config))
            config_path.chmod(0o600)
            client = Endpoint(**config)
            client.hello()
            env = dict(s.env, GTK_A11Y='none', NO_AT_BRIDGE='1', GSETTINGS_BACKEND='memory', GTK_USE_PORTAL='0')
            control = OUTPUT/'fixture-control.json'
            fixture = s.host.launch('fixture', ['/usr/bin/python3', '-B', str(FIXTURE), str(control)], env=env)
            apps.append(fixture)
            wait(lambda:any(w['title'] == 'ELM-AUTHORITY-FIXTURE' for w in s.data('clients')))
            web = s.host.launch('elm-webview', [str(binary), '--assets', str(build_path.parent/'inputs/assets'),
                    '--backend', str(backend_path), '--authority-config', str(config_path), '--layer',
                    '--qa-exit-after-render', '--qa-stay-open'], env=env)
            apps.append(web)

            def frames(prefix):
                return [json.loads(line.split(prefix, 1)[1]) for line in
                        (OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines()
                        if line.startswith(prefix)]

            def projection():
                values = frames('projection-report: ')
                return values[-1]['body'] if values else None

            def row(state):
                value = projection()
                if not value or value['phase'] != 'Coherent':
                    return None
                return next((r for r in value['rows'] if r['label'] == 'ELM-AUTHORITY-FIXTURE'
                             and r['state'] == state), None)

            def menu():
                value = projection()
                return value.get('menu') if value and value['phase'] == 'Coherent' else None

            def effects():
                return [f for f in frames('frontend-request: ') if f['kind'] == 'window-effect']

            def pointer(item, button=272):
                x, y = (round(v) for v in item['point'])
                assert 0 < x < 800 and 0 < y < 420
                result = subprocess.run([str(POINTER), '800', '600'],
                    input=f'move {x} {y}\nsleep 100\nbutton {button} 1\nsleep 50\nbutton {button} 0\nsleep 100\n',
                    text=True, capture_output=True, env=s.env, timeout=5)
                check('ownedPointerNormalExit', result.returncode == 0,
                      point=[x,y], button=button, stderr=result.stderr)

            def keyboard(commands):
                result = subprocess.run([str(KEYBOARD)], input=commands+'sleep 100\nsync\n',
                    text=True, capture_output=True, env=s.env, timeout=5)
                check('ownedKeyboardNormalExit', result.returncode == 0, stderr=result.stderr)

            def key(code):
                keyboard(f'key {code} 1\nsleep 40\nkey {code} 0\n')

            def action(label):
                value = menu()
                return next((a for a in value['actions'] if a['label'] == label), None) if value else None

            identity = wait(lambda:row('Open'))['incarnation']
            def native_window(request):
                facts = client.scene_facts(str(request))
                return facts, next(w for w in facts['facts']['windows'] if w['incarnation'] == identity)

            pointer(row('Open'), 273)
            opened = wait(menu)
            check('actualSecondaryReleaseOpensWithoutEffect', len(effects()) == 0,
                  projection=projection())
            check('openWindowRestoreDisabledMinimizeEnabled', action('Restore')['disabled']
                  and not action('Minimize')['disabled'], menu=opened)
            pointer(action('Restore'))
            check('disabledRestoreDispatchesNothing', len(effects()) == 0
                  and not native_window(1)[1]['minimized'])
            key(1)
            wait(lambda:projection() if projection() and projection()['menu'] is None else None)
            wait(lambda:projection() if projection().get('focused') == 'window-'+identity else None)
            check('escapeReturnsDOMOpenerWithoutEffect', len(effects()) == 0,
                  projection=projection())
            key(139)
            wait(menu)
            check('actualMenuKeyOpensWithoutEffect', len(effects()) == 0, projection=projection())
            key(1)
            wait(lambda:projection() if projection()['menu'] is None else None)
            keyboard('key 42 1\nkey 68 1\nsleep 40\nkey 68 0\nkey 42 0\n')
            wait(menu)
            check('actualShiftF10OpensWithoutEffect', len(effects()) == 0, projection=projection())
            key(15)
            wait(lambda:projection() if projection().get('focused') == 'context-dismiss' else None)
            key(28)
            wait(lambda:projection() if projection()['menu'] is None else None)
            check('enterOnDismissNeverActivatesWindowAction', len(effects()) == 0
                  and not native_window(2)[1]['minimized'], projection=projection())
            key(139)
            wait(menu)
            pointer(action('Minimize'))
            wait(lambda:row('Minimized'))
            facts, minimized = native_window(2)
            check('contextMinimizeNativeState', minimized['minimized']
                  and not minimized['acceptsInput'] and not minimized['shouldRenderAny'], window=minimized)
            check('minimizeHasOneCorrelatedIntentAndReceipt', len(effects()) == 1
                  and effects()[0]['intent']['operation'] == 'minimize'
                  and projection()['transaction'] == 'Committed', projection=projection(), request=effects()[0])
            pointer(row('Minimized'), 273)
            wait(menu)
            check('minimizedWindowMinimizeDisabledRestoreEnabled', action('Minimize')['disabled']
                  and not action('Restore')['disabled'], menu=menu())
            pointer(action('Minimize'))
            check('disabledMinimizeDispatchesNothing', len(effects()) == 1 and native_window(3)[1]['minimized'])
            pointer(action('Restore'))
            wait(lambda:row('Open'))
            facts, restored = native_window(4)
            check('contextRestoreNativeStateAndFocus', not restored['minimized']
                  and restored['acceptsInput'] and facts['facts']['focused'] == identity, window=restored)
            check('restoreHasOneCorrelatedIntentAndReceipt', len(effects()) == 2
                  and effects()[-1]['intent']['operation'] == 'restore'
                  and projection()['transaction'] == 'Committed', projection=projection(), request=effects()[-1])
            screenshot = OUTPUT/'elm-context-menu-restored.png'
            subprocess.run(['grim', str(screenshot)], env=s.env, check=True, timeout=5)
            report['screenshotSHA256'] = host.digest(screenshot)
            temp = control.with_suffix('.tmp')
            temp.write_text(json.dumps({'op': 'quit'}))
            temp.replace(control)
            fixture.wait(timeout=5)
            check('fixtureNormalExit', fixture.returncode == 0)
            report['passed'] = True
        finally:
            for process in reversed(apps):
                if process.poll() is None:
                    owned = next(row for p, row in s.host.processes if p is process)
                    s.host.stop(owned, process)
                    process.wait(timeout=5)
                if process is not fixture:
                    report['checks'].append({'name': 'webviewAndBackendNormalExit',
                                            'passed': process.returncode == 0, 'exitCode': process.returncode})
                    report['passed'] = report['passed'] and process.returncode == 0
            if loaded:
                s.guard()
                assert s.ctl('plugin', 'unload', plugin).strip() == 'ok'
                loaded = False
            registered = {row['pid'] for _, row in s.host.processes}
            for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):
                s.host.stop(descendant)
except Exception as error:
    report.update(passed=False, error=repr(error), traceback=traceback.format_exc())
report['privateHost'] = s.evidence if s else None
report['cleanupPassed'] = bool(s and not s.evidence.get('cleanupErrors')
    and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants')
    and s.evidence.get('runtimeGone'))
report['passed'] = report['passed'] and report['cleanupPassed']
if OUTPUT.exists():
    shutil.copytree(OUTPUT, OUT/'native-evidence', symlinks=True)
report['artifacts'] = {str(p.relative_to(OUT)):host.digest(p) for p in OUT.rglob('*')
                       if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT/'report.json'), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
