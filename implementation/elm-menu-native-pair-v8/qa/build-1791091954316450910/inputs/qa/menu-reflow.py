"""Serial native shell-owned window-row context-menu qualification only.

Real pointer/keyboard -> compiled Elm -> existing authenticated minimize/restore.
No full taskbar, application menus, transformed outputs, AT or release claim.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
CORE = REPO/'implementation/elm-buffer-authority-pair-v8'
spec = importlib.util.spec_from_file_location('context_menu_private_host', ROOT/'candidate_host.py')
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
FIXTURE = ROOT/'fixture.py'
report = {'passed': False, 'mainDesktopActions': False,
          'scope': 'Original menu scenario plus targeted menu resize/integer-scale/Escape; parent rotation campaign remains failed/open; no exhaustive cancellation/geometry, bar keyboard, AT or release acceptance',
          'checks': [], 'output': str(OUTPUT)}
apps = []
s = None
loaded = False
fixture = None
stopped_backend = None
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
    build_path = sorted((ROOT/'qa').glob('build-*/report.json'))[-1]
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
                          KEYBOARD.with_suffix('.c'), FIXTURE, ROOT/'qa/inspection.py', ROOT/'candidate_host.py')})
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
                    '--backend', str(backend_path), '--authority-config', str(config_path), '--surface-experiment',
                    '--qa-exit-after-render', '--qa-stay-open'], env=dict(env, WAYLAND_DEBUG='client'))
            apps.append(web)

            def frames(prefix):
                return [json.loads(line.split(prefix, 1)[1]) for line in
                        (OUTPUT/'elm-webview.log').read_text(errors='replace').splitlines()
                        if line.startswith(prefix)]

            sys.path.insert(0, str(ROOT/'qa'))
            from inspection import Collector
            collector = Collector()
            def projection():
                return collector.read((OUTPUT/'elm-webview.log').read_text(errors='replace'))
            def group():
                value=projection()
                return next((g for g in value['groups'] if g['key']=='application:GTK Application' and not g['disabled']),None) if value and value['phase']=='Coherent' else None
            def row(state):
                value=projection()
                return next((r for r in value['picker']['selections'] if r['title']=='ELM-AUTHORITY-FIXTURE' and r['state']==state and not r['disabled']),None) if value and value['phase']=='Coherent' and value['picker'] else None
            def target(state):
                if not projection() or not projection()['picker']:
                    pointer(wait(group))
                return wait(lambda:row(state))
            def menu():
                value=projection()
                return value.get('menu') if value else None

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

            def keyboard_target(state):
                item=target(state)
                for _ in range(3):
                    if projection().get('focus')==item['domId']:
                        check('physicalKeyboardFocusesExactFixtureRoot', True, incarnation=item['incarnation'], projection=projection())
                        return item
                    prior=projection().get('focus')
                    key(15)
                    wait(lambda:projection() if projection() and projection().get('focus')!=prior else None)
                raise AssertionError('Exact fixture root not focused within three physical Tab stops')

            def action(label):
                value = menu()
                return next((a for a in value['actions'] if a['label'] == label), None) if value else None

            identity = target('Open')['incarnation']
            def native_window(request):
                facts = client.scene_facts(str(request))
                return facts, next(w for w in facts['facts']['windows'] if w['incarnation'] == identity)

            pointer(target('Open'), 273)
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
            check('escapeClosesPopupWithoutNativeEffect', len(effects()) == 0,
                  projection=projection())
            # Popup keyboard only: bar keyboard focus remains a future gate.
            # evdev 127 + XKB offset 8 is <COMP>/<MENU>; KEY_MENU139 is XF86MenuKB.
            keyboard_target('Open')
            key(127)
            wait(menu)
            check('menuKeyUsesExactPhysicallyFocusedNativeRoot',menu()['incarnation']==identity,projection=projection())
            check('actualMenuKeyOpensWithoutEffect', len(effects()) == 0, projection=projection())
            key(1)
            wait(lambda:projection() if projection()['menu'] is None else None)
            keyboard_target('Open')
            keyboard('key 42 1\nkey 68 1\nsleep 40\nkey 68 0\nkey 42 0\n')
            wait(menu)
            check('shiftF10UsesExactPhysicallyFocusedNativeRoot',menu()['incarnation']==identity,projection=projection())
            check('actualShiftF10OpensWithoutEffect', len(effects()) == 0, projection=projection())
            key(15)
            wait(lambda:projection() if projection().get('focus') == menu()['closeId'] else None)
            key(28)
            wait(lambda:projection() if projection()['menu'] is None else None)
            check('enterOnDismissNeverActivatesWindowAction', len(effects()) == 0
                  and not native_window(2)[1]['minimized'], projection=projection())
            # Popup keyboard only: bar keyboard focus remains a future gate.
            # evdev 127 + XKB offset 8 is <COMP>/<MENU>; KEY_MENU139 is XF86MenuKB.
            keyboard_target('Open')
            key(127)
            wait(menu)
            check('pendingKeyboardMenuUsesExactNativeRoot',menu()['incarnation']==identity,projection=projection())
            backend_args = [b'/usr/bin/python3', b'-B', str(backend_path).encode()]
            def backend():
                for owned in s.host.descendants():
                    try:
                        args = Path(f"/proc/{owned['pid']}/cmdline").read_bytes().split(b'\0')
                    except FileNotFoundError:
                        continue
                    if args[:3] == backend_args:
                        return owned['pid']
                return None
            stopped_backend = wait(backend)
            os.kill(stopped_backend, signal.SIGSTOP)
            dispatched_lease = projection()['lease']
            pointer(action('Minimize'))
            pending = wait(lambda:projection() if projection() and projection()['transaction']=='Pending'
                           and projection()['menu'] is None else None)
            wait(lambda:f'surface-popup-closed: lease={dispatched_lease}' in (OUTPUT/'elm-webview.log').read_text())
            check('pendingCommandClosesActualNativePopupBeforeSend', pending['menu'] is None
                  and pending['outstanding']==1 and pending['registry']==1
                  and not native_window(8)[1]['minimized'], projection=pending)
            check('singleCorrelatedIntentWhileBrokerStopped', len(effects())==1,
                  projection=pending)
            os.kill(stopped_backend, signal.SIGCONT)
            stopped_backend = None
            wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['transaction']=='Committed' else None)
            facts, minimized = native_window(2)
            check('contextMinimizeNativeState', minimized['minimized']
                  and not minimized['acceptsInput'] and not minimized['shouldRenderAny'], window=minimized)
            check('minimizeHasOneCorrelatedIntentAndReceipt', len(effects()) == 1
                  and effects()[0]['intent']['operation'] == 'minimize'
                  and projection()['transaction'] == 'Committed', projection=projection(), request=effects()[0])
            pointer(target('Minimized'), 273)
            wait(menu)
            check('minimizedWindowMinimizeDisabledRestoreEnabled', action('Minimize')['disabled']
                  and not action('Restore')['disabled'], menu=menu())
            pointer(action('Minimize'))
            check('disabledMinimizeDispatchesNothing', len(effects()) == 1 and native_window(3)[1]['minimized'])
            pointer(action('Restore'))
            wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['transaction']=='Committed' else None)
            facts, restored = native_window(4)
            check('contextRestoreNativeStateAndFocus', not restored['minimized']
                  and restored['acceptsInput'] and facts['facts']['focused'] == identity, window=restored)
            check('restoreHasOneCorrelatedIntentAndReceipt', len(effects()) == 2
                  and effects()[-1]['intent']['operation'] == 'restore'
                  and projection()['transaction'] == 'Committed', projection=projection(), request=effects()[-1])
            # Targeted geometry retires old provider authority; reopening requires a new gesture.
            pointer(target('Open'),273)
            wait(menu)
            geometry_journal=effects()
            import re
            def latest_menu_popup():
                values=[tuple(map(int,match.groups())) for match in re.finditer(r'xdg_popup[#@]\d+\.configure\((\d+), (\d+), (\d+), (\d+)\)',(OUTPUT/'elm-webview.log').read_text(errors='replace'))]
                return values[-1] if values else None
            def geometry_authority():
                values=[frame['context'] for frame in frames('backend-frame: ') if frame.get('kind')=='action-projection']
                return values[-1] if values else None
            def geometry_keyboard_ready(lease):
                values=[state for token,state in re.findall(r'surface-native-keyboard-focus: lease=(\d+) in=(\d+)',(OUTPUT/'elm-webview.log').read_text(errors='replace')) if token==lease]
                return bool(values and values[-1]=='1')
            def geometry_pointer(item,button=272):
                monitors=s.data('monitors')
                assert len(monitors)==1 and monitors[0]['name']=='WAYLAND-1' and monitors[0]['x']==0 and monitors[0]['y']==0
                mon=monitors[0]
                width=round(mon['width']/mon['scale']);height=round(mon['height']/mon['scale'])
                x,y=(round(v) for v in item['point'])
                assert item['visible'] and 0<x<width and 0<y<height
                observed=projection()
                assert observed and observed['phase']=='Coherent'
                if observed.get('picker') or observed.get('menu'):
                    wait(lambda:geometry_keyboard_ready(projection()['lease']))
                result=subprocess.run([str(POINTER),str(width),str(height)],input=f'move {x} {y}\nsleep 100\nbutton {button} 1\nsleep 50\nbutton {button} 0\nsleep 100\n',text=True,capture_output=True,env=s.env,timeout=5)
                check('menuGeometryPointerNormalExit',result.returncode==0,point=[x,y],extent=[width,height],button=button,stderr=result.stderr)
            def geometry_target(state):
                if not projection() or not projection()['picker']:
                    geometry_pointer(wait(group))
                item=wait(lambda:row(state))
                wait(lambda:geometry_keyboard_ready(projection()['lease']))
                return item
            before_resize=geometry_authority()
            resize_receipt=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="640x480@60",position="0x0",scale=1})').strip()
            check('menuReflowResizeRequested',resize_receipt=='ok',receipt=resize_receipt)
            wait(lambda:any(m['name']=='WAYLAND-1' and m['width']==640 and m['height']==480 for m in s.data('monitors')))
            retired_resize=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['menu'] is None and geometry_authority()['output']!=before_resize['output'] else None)
            check('menuReflowResizedAuthorityRetiresProviderWithoutEffect',effects()==geometry_journal and retired_resize['registry']==0 and retired_resize['outstanding']==0,before=before_resize,after=geometry_authority(),projection=retired_resize)
            resized_authority=geometry_authority()
            geometry_pointer(geometry_target('Open'),273)
            fresh_resize=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['menu'] and projection()['menu']['incarnation']==identity else None)
            resized=wait(lambda:latest_menu_popup() if latest_menu_popup() and latest_menu_popup()[0]>=0 and latest_menu_popup()[1]>=48 and latest_menu_popup()[0]+latest_menu_popup()[2]<=640 and latest_menu_popup()[1]+latest_menu_popup()[3]<=480 else None)
            check('menuReflowExplicitResizedContextUsesCurrentAuthority',geometry_authority()['output']==resized_authority['output'] and effects()==geometry_journal,authority=geometry_authority(),projection=fresh_resize)
            check('menuReflowInsideResizedWorkarea',all(a['visible'] for a in fresh_resize['menu']['actions']) and fresh_resize['menu']['close']['visible'],configure=resized,projection=fresh_resize)
            before_scale=geometry_authority()
            scaled_receipt=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="960x640@60",position="0x0",scale=2,transform=0})').strip()
            check('menuReflowIntegerScaleRequested',scaled_receipt=='ok',receipt=scaled_receipt)
            scaled=wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1' and m['scale']==2 and m['width']==960 and m['height']==640),None))
            retired_scale=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['menu'] is None and geometry_authority()['output']!=before_scale['output'] else None)
            check('menuReflowScaledAuthorityRetiresProviderWithoutEffect',effects()==geometry_journal and retired_scale['registry']==0 and retired_scale['outstanding']==0,before=before_scale,after=geometry_authority(),projection=retired_scale)
            scaled_authority=geometry_authority()
            geometry_pointer(geometry_target('Open'),273)
            fresh_scale=wait(lambda:projection() if projection() and projection()['phase']=='Coherent' and projection()['menu'] and projection()['menu']['incarnation']==identity else None)
            scaled_popup=wait(lambda:latest_menu_popup() if latest_menu_popup() and latest_menu_popup()[0]>=0 and latest_menu_popup()[1]>=48 and latest_menu_popup()[0]+latest_menu_popup()[2]<=480 and latest_menu_popup()[1]+latest_menu_popup()[3]<=320 else None)
            wait(lambda:'set_buffer_scale(2)' in (OUTPUT/'elm-webview.log').read_text(errors='replace'))
            layers=[row for output in s.data('layers').values() for rows in output['levels'].values() for row in rows if row['pid']==web.pid]
            check('menuReflowExplicitScaledContextUsesCurrentAuthority',geometry_authority()['output']==scaled_authority['output'] and effects()==geometry_journal,authority=geometry_authority(),projection=fresh_scale)
            check('menuReflowScaledBarReservationAndBuffers',scaled['reserved'][1]==48 and len(layers)==1 and layers[0]['h']==48,monitor=scaled,layers=layers)
            check('menuReflowInsideScaledLogicalWorkarea',all(a['visible'] for a in fresh_scale['menu']['actions']) and fresh_scale['menu']['close']['visible'],configure=scaled_popup,projection=fresh_scale)
            wait(lambda:geometry_keyboard_ready(fresh_scale['lease']))
            check('menuReflowScaledEscapeHasCurrentNativeKeyboardReady',geometry_keyboard_ready(fresh_scale['lease']),lease=fresh_scale['lease'])
            key(1)
            wait(lambda:projection() if projection() and projection()['menu'] is None else None)
            check('menuReflowActualEscapeAfterScaleNoEffect',effects()==geometry_journal,projection=projection())
            restored_geometry=s.ctl('eval','hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1,transform=0})').strip()
            check('menuReflowRestoresOriginalFixtureGeometry',restored_geometry=='ok',receipt=restored_geometry)
            wait(lambda:any(m['name']=='WAYLAND-1' and m['scale']==1 and m['width']==800 and m['height']==600 for m in s.data('monitors')))
            wait(lambda:projection() if projection() and projection()['phase']=='Coherent' else None)

            screenshot = OUTPUT/'elm-context-menu-restored.png'
            subprocess.run(['grim', str(screenshot)], env=s.env, check=True, timeout=5)
            report['screenshotSHA256'] = host.digest(screenshot)
            pointer(target('Open'), 273)
            wait(menu)
            retired_menu = menu()
            effects_before_retire = len(effects())
            temp = control.with_suffix('.tmp')
            temp.write_text(json.dumps({'op': 'quit'}))
            temp.replace(control)
            fixture.wait(timeout=5)
            check('fixtureNormalExit', fixture.returncode == 0)
            wait(lambda:projection() if projection() and projection()['phase']=='Coherent'
                 and projection()['menu'] is None and all(g['title']!='ELM-AUTHORITY-FIXTURE' for g in projection()['groups']) else None)
            check('retiredWindowClosesMenuWithoutEffect', len(effects()) == effects_before_retire,
                  retiredMenu=retired_menu, projection=projection())

            for path,digest in report['inputs'].items():
                assert host.digest(Path(path))==digest,path
            report['passed'] = True
        finally:
            if stopped_backend is not None:
                try:
                    os.kill(stopped_backend, signal.SIGCONT)
                except ProcessLookupError:
                    pass
                stopped_backend = None
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
