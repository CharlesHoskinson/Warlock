#!/usr/bin/env python3
"""Invoke actual AT-SPI actions against a disposable native window."""
import json
import subprocess
import time
from pathlib import Path
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi, Gio, GLib

HOME = Path.home()
BIN = HOME / '.local/bin'
CONFIG = HOME / '.local/share/hypr-window-controls'
report = {'checks': [], 'failures': []}
process = None

def ctl(*args):
    return subprocess.check_output(['hyprctl', *args], text=True).strip()

def data(name):
    return json.loads(ctl(name, '-j'))

def run(*args):
    subprocess.run([str(x) for x in args], check=True, stdout=subprocess.DEVNULL)

def wait(fn, label):
    deadline = time.monotonic() + 7
    while time.monotonic() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(.1)
    raise AssertionError('timeout: ' + label)

def check(name, value, **details):
    report['checks'].append(dict(name=name, passed=bool(value), **details))
    if not value:
        report['failures'].append(name)

def nodes():
    desktop = Atspi.get_desktop(0)
    found = []
    def visit(node, depth):
        if depth > 12:
            return
        try:
            node.clear_cache()
            if node.get_name() and node.get_state_set().contains(Atspi.StateType.SHOWING):
                found.append(node)
            for i in range(node.get_child_count()):
                visit(node.get_child_at_index(i), depth + 1)
        except Exception:
            pass
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        if app.get_name() in ('qs', 'quickshell'):
            visit(app, 0)
    return found

def action(name, role=None):
    return wait(lambda: next((n for n in nodes() if n.get_name() == name
                             and (role is None or n.get_role_name() == role)), None), name)

def press(node):
    iface = node.get_action_iface()
    assert iface is not None and iface.get_n_actions(), node.get_name()
    names = [iface.get_action_name(i) for i in range(iface.get_n_actions())]
    assert iface.do_action(0), (node.get_name(), names)
    time.sleep(.5)
    return names

def window():
    return next((w for w in data('clients') if w['pid'] == process.pid), None)

def show(mode='system'):
    run(BIN / 'hypr-window-menu', mode, address)
    def opened():
        result = subprocess.run(['qs', '-p', str(CONFIG), 'ipc', 'call',
                                 'controls', 'state'], capture_output=True, text=True)
        try:
            return json.loads(result.stdout).get('opened')
        except ValueError:
            return False
    return wait(opened, 'menu opened')

initial = data('activewindow')
cursor = data('cursorpos')
motion = HOME / '.config/hypr/reduced-motion'
motion_bytes = motion.read_bytes() if motion.exists() else None
old_reduced = motion_bytes is not None and motion_bytes.strip() == b'1'
bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
def status(method, parameters):
    return bus.call_sync('org.a11y.Bus', '/org/a11y/bus',
        'org.freedesktop.DBus.Properties', method, parameters, None,
        Gio.DBusCallFlags.NONE, 5000, None)
old_a11y = status('GetAll', GLib.Variant('(s)', ('org.a11y.Status',))).unpack()[0]
def set_a11y(name, value):
    status('Set', GLib.Variant('(ssv)', ('org.a11y.Status', name, GLib.Variant('b', value))))
try:
    # Qt only publishes its accessibility tree when assistive technology is enabled.
    for key in ('IsEnabled', 'ScreenReaderEnabled'):
        set_a11y(key, True)
    process = subprocess.Popen(['foot', '--app-id=window-accessibility-qa',
        '--title=Accessibility action QA', 'sleep', '180'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    w = wait(window, 'disposable foot')
    address = w['address']
    if not w['floating']:
        ctl('dispatch', f'hl.dsp.window.float({{action="set",window="address:{address}"}})')
    ctl('dispatch', f'hl.dsp.window.resize({{x=600,y=350,window="address:{address}"}})')
    ctl('dispatch', f'hl.dsp.window.move({{x=260,y=300,window="address:{address}"}})')
    time.sleep(.5)
    original = window()['at'] + window()['size']
    show()
    minimize = action('Minimize', 'menu item')
    menu_nodes = [n for n in nodes() if n.get_role_name() == 'menu item']
    names = [n.get_name() for n in menu_nodes]
    check('nine named native menu actions exposed', len(menu_nodes) == 9, names=names)
    check('only selected menu action reports focused',
          [n.get_name() for n in menu_nodes if n.get_state_set().contains(Atspi.StateType.FOCUSED)] == ['Restore'])
    press(minimize)
    check('assistive minimize moves own window to dedicated minimized workspace',
          window()['workspace']['name'] == 'special:win-minimized')
    run(BIN / 'hypr-windowctl', 'restore', address)
    time.sleep(.5)
    # An ignored cached Qt interface can reject discovery entirely. Both
    # rejection and an inert exposed callback must leave the native window alone.
    stale_exposed = False
    stale_accepted = False
    try:
        stale_iface = minimize.get_action_iface()
        stale_exposed = bool(stale_iface and stale_iface.get_n_actions())
        if stale_exposed:
            stale_accepted = bool(stale_iface.do_action(0))
    except GLib.Error:
        pass
    time.sleep(.5)
    check('hidden stale assistive action cannot minimize restored window',
          window()['workspace']['name'] != 'special:win-minimized',
          stale_action_exposed=stale_exposed, stale_action_accepted=stale_accepted)
    show()
    pin = action('Pin always on top', 'menu item')
    check('pin begins unchecked', not pin.get_state_set().contains(Atspi.StateType.CHECKED))
    press(pin)
    check('assistive pin changes native pinned state', window()['pinned'])
    show()
    unpin = action('Unpin always on top', 'menu item')
    check('pinned action reports checked', unpin.get_state_set().contains(Atspi.StateType.CHECKED))
    press(unpin)
    check('assistive unpin changes native pinned state', not window()['pinned'])
    show('layouts')
    left = action('Left half', 'button')
    press(left)
    check('assistive Snap layout changes native geometry',
          window()['at'] + window()['size'] != original and any('snap' in t for t in window().get('tags', [])),
          geometry=window()['at'] + window()['size'], tags=window().get('tags'))
    show()
    press(action('Restore', 'menu item'))
    check('assistive Restore returns exact original geometry', window()['at'] + window()['size'] == original,
          actual=window()['at'] + window()['size'], expected=original)
    show()
    press(action('Enable animations' if old_reduced else 'Reduce motion', 'menu item'))
    check('assistive motion toggle changes persisted setting',
          (motion.read_text().strip() == '1') != old_reduced)
    show()
    menu = json.loads(subprocess.check_output(['qs', '-p', str(CONFIG), 'ipc', 'call', 'controls', 'state'], text=True))
    menu['request']['pid'] = -1
    run('qs', '-p', CONFIG, 'ipc', 'call', 'controls', 'open', json.dumps(menu['request']))
    press(action('Minimize', 'menu item'))
    check('stale captured window identity rejects assistive action',
          window()['workspace']['name'] != 'special:win-minimized')
    show()
    press(action('Close   Alt+F4', 'menu item'))
    wait(lambda: window() is None, 'accessible close')
    check('assistive Close closes only its captured window', window() is None)
    report['result'] = 'pass' if not report['failures'] else 'fail'
except Exception as error:
    report.update(result='fail', error=repr(error))
finally:
    run(BIN / 'hypr-window-menu', 'hide')
    if process and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
    run(BIN / 'hypr-reduced-motion', 'on' if old_reduced else 'off')
    if motion_bytes is None:
        motion.unlink(missing_ok=True)
    else:
        motion.write_bytes(motion_bytes)
    if initial.get('address'):
        ctl('dispatch', f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
    ctl('dispatch', f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
    for key in ('IsEnabled', 'ScreenReaderEnabled'):
        set_a11y(key, old_a11y[key])
    (HOME / '.cache/window-accessible-controls-qa.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert report['result'] == 'pass'
