#!/usr/bin/env python3
"""Real Orca event/focus/navigation/action QA with silent output, no direct AT-SPI actions."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from atspi_qa import assistive_session
import gi
from gi.repository import Gio, GLib

OUTPUT = Path(__file__).resolve().parent
QA = OUTPUT.parent
H = Path.home()
SHELL = '/usr/share/omarchy/shell'
CONTROLS = str(H / '.local/share/hypr-window-controls')
report = {'reader': 'Official Arch Orca 50.2', 'input': 'physical Wayland virtual keyboard, standard evdev keycodes', 'output': 'silent QA factory', 'checks': [], 'physical_commands': [], 'legacy_keygrab_fix':os.environ.get('ORCA_QA_LEGACY_GRAB_FIX') == '1', 'failures': []}
processes = []
reader = None
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

def run(*args):
    return subprocess.check_output([str(x) for x in args], text=True).strip()

def data(name):
    return json.loads(run('hyprctl', name, '-j'))

def grab_surfaces():
    return [surface for monitor in data('layers').values()
        for surfaces in monitor.get('levels', {}).values() for surface in surfaces
        if surface.get('alpha', 1) > 0 and
        ('sudo-askpass' in surface.get('namespace', '') or
         'hyprlock' in surface.get('namespace', ''))]

def ensure_input_available():
    grabs = grab_surfaces()
    if grabs:
        raise RuntimeError('foreign input grab: ' + json.dumps(grabs))

def ipc(target, method, *args, config=SHELL):
    return run('qs', '-p', config, 'ipc', 'call', target, method, *args)

def dbus(module, method, args):
    return bus.call_sync('org.gnome.Orca.Service', '/org/gnome/Orca/Service/' + module,
        'org.gnome.Orca.Module', method, args, None, Gio.DBusCallFlags.NONE, 5000, None).unpack()[0]

def state():
    return json.loads(dbus('QAObservation', 'ExecuteRuntimeGetter', GLib.Variant('(s)', ('State',))))

def container_selection():
    controls = json.loads(ipc('controls', 'state', config=CONTROLS))
    if controls['opened']:
        return {'kind':'controls', 'selected':controls['selected']}
    view = json.loads(ipc('hoskinson.taskview', 'state'))
    if view['opened']:
        return {'kind':'taskview','selected':view['selectedWindow'], 'desktopKeys':view['desktopKeys']}
    bar = json.loads(ipc('hoskinson.windows', 'state'))
    if bar['popupOpen']:
        return {'kind':'taskbar','selected':bar['selectedWindowIndex']}
    return None

def command(module, name):
    # Execute no Orca command RPC: keys pass through the compositor/Qt/AT-SPI.
    ensure_input_available()
    keys = {'MoveToParent':103,'MoveToFirstChild':108,'MoveToNextSibling':106,
            'MoveToPreviousSibling':105,'PerformAction':28}
    held = [110,29,keys[name]] if module == 'ObjectNavigator' else [96]
    before = container_selection()
    sequence = ''.join(f'key {code} 1\nsleep 90\n' for code in held)
    sequence += ''.join(f'key {code} 0\nsleep 90\n' for code in reversed(held))
    subprocess.run([str(OUTPUT/'evdev-keyboard')], input=sequence, text=True, check=True, timeout=5)
    time.sleep(.4)
    after = container_selection()
    record = dict(module=module, command=name, before=before, after=after,
                  reader_state=state())
    report['physical_commands'].append(record)
    if name != 'PerformAction':
        assert before == after, ('Orca command leaked into native keyboard container', record)


def wait(fn, label, seconds=8):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try:
            value = fn()
            if value:
                return value
        except GLib.Error:
            pass
        time.sleep(.1)
    raise AssertionError('timeout: ' + label)

def check(name, passed, **details):
    report['checks'].append(dict(name=name, passed=bool(passed), **details))
    if not passed:
        report['failures'].append(name)

def focus_name(name):
    return wait(lambda: state() if (state().get('focus') or {}).get('name') == name else None,
                'Orca focus ' + name)

def speech_since(start, expected):
    records = [json.loads(x) for x in (OUTPUT / 'utterances.jsonl').read_text().splitlines()]
    texts = [x['text'] for x in records if x['time'] >= start and x['kind'] == 'speech']
    return any(expected in x for x in texts), texts

def key(name):
    ensure_input_available()
    run('wtype', '-k', name)
    time.sleep(.3)

def window(p):
    return next((x for x in data('clients') if x['pid'] == p.pid), None)

def scenario(name, fn):
    try:
        fn()
    except Exception as error:
        grabs = grab_surfaces()
        check(name, False, error=repr(error), reader_state=state(), foreign_grabs=grabs, backend_activewindow=data('activewindow'))
        if grabs:
            report['input_blocked'] = True
    finally:
        ipc('controls', 'hide', config=CONTROLS)
        ipc('hoskinson.windows', 'dismiss')
        ipc('hoskinson.taskview', 'close')
        time.sleep(.3)

# Check before flags, reader startup, or disposable app creation.
ensure_input_available()
initial = data('activewindow')
cursor = data('cursorpos')
initial_clients = {(x['address'], x.get('stableId'), x['pid']) for x in data('clients')}
with assistive_session():
    try:
        (OUTPUT / 'utterances.jsonl').write_text('')
        reader_output = (OUTPUT / 'reader.stdout').open('w')
        reader_env = {**os.environ, 'ORCA_QA_UTTERANCES':str(OUTPUT/'utterances.jsonl'),
                      'ORCA_QA_LEGACY_GRAB_FIX':os.environ.get('ORCA_QA_LEGACY_GRAB_FIX','0')}
        if os.environ.get('ORCA_QA_NATIVE_WAYLAND_MODIFIERS') == '1':
            reader_env.pop('DISPLAY', None)
            reader_env['GDK_BACKEND'] = 'wayland'
        report['native_wayland_modifiers'] = os.environ.get('ORCA_QA_NATIVE_WAYLAND_MODIFIERS') == '1'
        launcher = QA / ('run-orca-native-wayland' if report['native_wayland_modifiers'] else 'run-orca')
        reader = subprocess.Popen([str(launcher), '--debug-file', str(OUTPUT / 'reader.debug')],
            stdout=reader_output, stderr=subprocess.STDOUT, env=reader_env)
        wait(state, 'Orca DBus and native event loop ready', 15)
        for title in ['Orca reader QA one', 'Orca reader QA two']:
            p = subprocess.Popen(['foot', '--app-id=org.omarchy.orcareaderqa', '--title=' + title,
                'sleep', '300'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append(p)
            wait(lambda: window(p), title)
        first, second = processes
        address = window(first)['address']
        identity = window(first)['stableId']

        def controls():
            start = time.monotonic()
            run(H / '.local/bin/hypr-window-menu', 'system', address)
            wait(lambda: (state().get('focus') or {}).get('name') in ('Restore', 'Window controls'), 'controls reader focus')
            wait(lambda: speech_since(start, 'Restore')[0], 'reader initial Restore announcement')
            heard, texts = speech_since(start, 'Restore')
            check('Orca announces native window menu initial focus', heard, utterances=texts)
            check('native controls retain selected item as Orca focus', (state().get('focus') or {}).get('name') == 'Restore', reader_state=state())
            if state()['focus']['name'] == 'Restore':
                command('ObjectNavigator', 'MoveToParent')
            command('ObjectNavigator', 'MoveToFirstChild')
            command('ObjectNavigator', 'MoveToNextSibling')
            navigation = state().get('navigator') or {}
            check('Orca ObjectNavigator traverses native menu siblings', navigation.get('name') == 'Move', navigation=navigation)
            for _ in range(2):
                command('ObjectNavigator', 'MoveToNextSibling')
            check('Orca ObjectNavigator locates Minimize', (state().get('navigator') or {}).get('name') == 'Minimize')
            command('ObjectNavigator', 'PerformAction')
            wait(lambda: window(first)['workspace']['name'] == 'special:win-minimized', 'reader minimize action')
            check('Orca PerformAction minimizes captured disposable window', True)
            run(H / '.local/bin/hypr-windowctl', 'restore', address)
        scenario('native controls reader compatibility', controls)

        def taskview():
            run('hyprctl', 'dispatch', f'hl.dsp.focus({{window="address:{address}"}})')
            start = time.monotonic()
            ipc('hoskinson.taskview', 'open')
            wait(lambda: (state().get('focus') or {}).get('identity', '').startswith('taskview-window:'), 'initial Task View reader card')
            for _ in range(len(data('clients')) + 2):
                if (state().get('focus') or {}).get('identity') == 'taskview-window:' + identity:
                    break
                key('Right')
            focus_name('Orca reader QA one')
            heard, texts = speech_since(start, 'Orca reader QA one')
            check('Orca announces Task View selected window', heard, utterances=texts)
            key('Tab')
            wait(lambda: (state().get('focus') or {}).get('identity', '').startswith('taskview-desktop:'), 'reader desktop tab focus')
            command('WhereAmIPresenter', 'WhereAmIBasic')
            check('Orca follows Task View keyboard mode into desktop tab', True, reader_state=state())
            key('Tab')
            focus_name('Orca reader QA one')
            command('ObjectNavigator', 'MoveToFirstChild')
            close = state().get('navigator') or {}
            check('Orca discovers Task View close button from window card', close.get('name') == 'Close Orca reader QA one', navigation=close)
            command('ObjectNavigator', 'MoveToParent')
            command('ObjectNavigator', 'PerformAction')
            wait(lambda: not json.loads(ipc('hoskinson.taskview', 'state'))['opened'], 'reader Task View activation')
            wait(lambda: data('activewindow').get('address') == address, 'Task View reader exact backend focus')
            check('Orca activates exact Task View window through native action', True)
        scenario('Task View reader compatibility', taskview)

        def taskbar():
            task = wait(lambda: next((g for g in json.loads(ipc('hoskinson.windows', 'state'))['taskbarItems'] if address in g['windows']), None), 'QA taskbar group')
            groups = json.loads(ipc('hoskinson.windows', 'state'))['taskbarItems']
            index = next(i for i, g in enumerate(groups) if g['key'] == task['key'])
            start = time.monotonic()
            ipc('hoskinson.windows', 'cycle', str(index + 1))
            wait(lambda: (state().get('focus') or {}).get('name') == 'Window previews' or (state().get('focus') or {}).get('identity', '').startswith('taskbar-window:'), 'reader taskbar preview focus')
            check('taskbar retains selected preview as Orca focus', (state().get('focus') or {}).get('identity', '').startswith('taskbar-window:'), reader_state=state())
            key('Down')
            wait(lambda: (state().get('focus') or {}).get('identity', '').startswith('taskbar-window:'), 'reader next preview after arrow')
            initial_preview = state()['focus']
            heard, texts = speech_since(start, 'Orca reader QA')
            check('Orca announces taskbar preview initial keyboard focus', heard, utterances=texts, focus=initial_preview)
            key('Down')
            next_preview = wait(lambda: state()['focus'] if state()['focus'].get('identity') != initial_preview['identity'] else None, 'reader next preview')
            check('Orca follows taskbar preview arrow navigation', 'Orca reader QA' in next_preview['name'], focus=next_preview)
            command('ObjectNavigator', 'MoveToFirstChild')
            close = state().get('navigator') or {}
            check('Orca finds taskbar preview close action', close.get('name', '').startswith('Close Orca reader QA'), navigation=close)
            command('ObjectNavigator', 'MoveToParent')
            command('ObjectNavigator', 'PerformAction')
            wait(lambda: not json.loads(ipc('hoskinson.windows', 'state'))['popupOpen'], 'reader preview restore')
            wait(lambda: data('activewindow').get('title') == next_preview['name'], 'taskbar reader exact backend focus')
            check('Orca activates taskbar preview through native action', True)
            ipc('hoskinson.windows', 'menu', str(index + 1))
            wait(lambda: (state().get('focus') or {}).get('role') == 'menu item', 'reader taskbar menu focus')
            check('Orca receives taskbar app actions menu focus', True, focus=state()['focus'])
        scenario('taskbar reader compatibility', taskbar)
        check('reader QA preserves existing user native window identities', initial_clients <= {(x['address'], x.get('stableId'), x['pid']) for x in data('clients')})
        check('physical Orca navigation commands are consumed before native arrow handlers', all(c['before'] == c['after'] for c in report['physical_commands'] if c['command'] != 'PerformAction'))
        report['result'] = 'inconclusive' if report.get('input_blocked') else 'pass' if not report['failures'] else 'fail'
    except Exception as error:
        report.update(result='fail', error=repr(error))
    finally:
        for target, config in [('controls', CONTROLS), ('hoskinson.windows', SHELL), ('hoskinson.taskview', SHELL)]:
            try:
                ipc(target, 'hide' if target == 'controls' else 'dismiss' if target == 'hoskinson.windows' else 'close', config=config)
            except Exception:
                pass
        if reader and reader.poll() is None:
            reader.terminate()
            try:
                reader.wait(timeout=5)
            except subprocess.TimeoutExpired:
                reader.kill(); reader.wait()
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill(); p.wait()
        if initial.get('address'):
            run('hyprctl', 'dispatch', f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
        run('hyprctl', 'dispatch', f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        (OUTPUT / 'report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert report['result'] == 'pass'
