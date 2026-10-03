#!/usr/bin/env python3
"""Actual taskbar/Task View assistive actions, using only disposable windows/desktops."""
import json
import subprocess
import time
from pathlib import Path
from atspi_qa import Atspi, assistive_session, find, invoke, nodes

H = Path.home()
BIN = H / '.local/bin'
SHELL = '/usr/share/omarchy/shell'
catalog = H / '.config/omarchy/virtual-desktops.json'
report = {'checks': [], 'failures': []}
processes = []
created = []

def run(*args):
    return subprocess.check_output([str(a) for a in args], text=True).strip()
def ctl(*args):
    return run('hyprctl', *args)
def data(name):
    return json.loads(ctl(name, '-j'))
def ipc(target, method):
    return run('qs', '-p', SHELL, 'ipc', 'call', target, method)
def wait(fn, label):
    end = time.monotonic() + 9
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(.12)
    raise AssertionError('timeout: ' + label)
def check(name, condition, **detail):
    report['checks'].append(dict(name=name, passed=bool(condition), **detail))
    if not condition:
        report['failures'].append(name)
def window(process):
    return next((w for w in data('clients') if w['pid'] == process.pid), None)
def node(**kwargs):
    return wait(lambda: find(**kwargs), str(kwargs))
def taskbar():
    return json.loads(ipc('hoskinson.windows', 'state'))
def view():
    return json.loads(ipc('hoskinson.taskview', 'state'))
def desktops():
    return json.loads(run(BIN / 'hypr-desktops', 'list'))['desktops']
def open_view():
    if not view()['opened']:
        invoke(node(name='Task View', role='button'))
    wait(lambda: view()['opened'], 'Task View open')
    time.sleep(.5)
def spawn(title):
    p = subprocess.Popen(['foot', '--app-id=org.omarchy.accessibleshellqa',
        '--title=' + title, 'sleep', '300'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    processes.append(p)
    w = wait(lambda: window(p), title)
    return p, w
def group_for(address):
    return next((g for g in taskbar()['taskbarItems'] if address in g['windows']), None)
def app_node(address):
    group = wait(lambda: group_for(address), 'taskbar group')
    return node(accessible_id='taskbar-app:' + group['key'])

initial = data('activewindow')
cursor = data('cursorpos')
initial_clients = {(w['address'], w.get('stableId'), w['pid']) for w in data('clients')}
catalog_bytes = catalog.read_bytes() if catalog.exists() else None
initial_desktops = [d['id'] for d in desktops()]
initial_workspace = next(m for m in data('monitors') if m['focused'])['activeWorkspace']['name']
with assistive_session():
    try:
        def ready():
            try:
                return isinstance(taskbar().get('popupOpen'), bool) and isinstance(view().get('opened'), bool)
            except ValueError:
                return False
        wait(ready, 'shell plugin reload ready')
        first, w = spawn('Accessible shell window one')
        address, identity = w['address'], w['stableId']
        group = wait(lambda: group_for(address), 'single taskbar app')
        assert group['windows'] == [address], 'QA app must have its own taskbar group'
        check('taskbar exposes Task View and Show desktop controls',
              find(name='Task View', role='button') is not None and find(name='Show desktop', role='button') is not None)
        invoke(app_node(address))
        check('assistive taskbar press minimizes exact active window',
              window(first)['workspace']['name'] == 'special:win-minimized')
        second, other = spawn('Accessible shell window two')
        wait(lambda: len(group_for(address)['windows']) == 2, 'grouped taskbar windows')
        invoke(app_node(address))
        wait(lambda: taskbar()['popupOpen'] and not taskbar()['menuMode'], 'accessible preview popup')
        preview = node(accessible_id='taskbar-window:' + identity)
        check('minimized preview remains exposed without restoring window',
              'Minimized' in preview.get_description() and window(first)['workspace']['name'] == 'special:win-minimized')
        invoke(preview)
        check('assistive preview restores and focuses exact minimized identity',
              window(first)['workspace']['name'] != 'special:win-minimized' and data('activewindow')['address'] == address)
        invoke(app_node(address), 'showMenu')
        wait(lambda: taskbar()['popupOpen'] and taskbar()['menuMode'], 'standard ShowMenu action')
        combine = node(name='Combine: Always', role='menu item')
        check('standard app menu action exposes current checked setting',
              combine.get_state_set().contains(Atspi.StateType.CHECKED))
        settings = H / '.config/omarchy/taskbar-settings.json'
        settings_before = settings.read_bytes() if settings.exists() else None
        run('wtype', '-k', 'Escape')
        wait(lambda: not taskbar()['popupOpen'], 'app menu Escape')
        invoke(combine, allow_defunct=True)
        check('dismissed app menu action cannot change settings',
              (settings.read_bytes() if settings.exists() else None) == settings_before)
        invoke(app_node(address))
        invoke(node(name='Close Accessible shell window two', role='button'))
        wait(lambda: window(second) is None, 'accessible taskbar close')
        check('assistive taskbar Close targets only selected preview', window(first) is not None)
        open_view()
        card = node(accessible_id='taskview-window:' + identity)
        check('Task View exposes named window and captured identity', card.get_name() == 'Accessible shell window one')
        invoke(card)
        wait(lambda: not view()['opened'], 'Task View restore dismissal')
        check('assistive Task View press focuses exact window', data('activewindow')['address'] == address)
        before = window(first)['at'] + window(first)['size']
        invoke(card, allow_defunct=True)
        check('hidden Task View action cannot reopen or change window',
              not view()['opened'] and window(first)['at'] + window(first)['size'] == before)
        for _ in range(2):
            open_view()
            invoke(node(name='New desktop', role='button'))
            current = [d['id'] for d in desktops()]
            new = next(i for i in current if i not in initial_desktops and i not in created)
            created.append(new)
        check('assistive New desktop creates native desktops', len(created) == 2)
        target, peer = created
        run(BIN / 'hypr-desktops', 'switch', initial_workspace)
        open_view()
        invoke(node(accessible_id='taskview-window:' + identity), 'showMenu')
        invoke(node(name='Move window to Desktop ' + target, role='menu item'))
        wait(lambda: window(first)['workspace']['name'] == target, 'assistive desktop move')
        check('assistive window context menu moves captured window', window(first)['workspace']['name'] == target)
        time.sleep(.6)
        invoke(node(accessible_id='taskview-desktop:' + target))
        wait(lambda: not view()['opened'], 'accessible desktop switch')
        check('assistive desktop tab switches native workspace',
              next(m for m in data('monitors') if m['focused'])['activeWorkspace']['name'] == target)
        open_view()
        invoke(node(accessible_id='taskview-desktop:' + target), 'showMenu')
        invoke(node(name='Rename desktop', role='menu item'))
        edit = node(name='Desktop name', role='text')
        assert edit.get_editable_text_iface().set_text_contents('Accessibility QA desktop')
        run('wtype', '-k', 'Return')
        wait(lambda: next(d for d in desktops() if d['id'] == target)['name'] == 'Accessibility QA desktop', 'accessible rename')
        check('assistive rename edits native persisted desktop name', True)
        invoke(node(accessible_id='taskview-desktop:' + target), 'showMenu')
        invoke(node(name='Move desktop right', role='menu item'))
        wait(lambda: [d['id'] for d in desktops()].index(target) > [d['id'] for d in desktops()].index(peer), 'desktop reorder right')
        check('assistive desktop action reorders native catalog', True)
        invoke(node(accessible_id='taskview-desktop:' + target), 'showMenu')
        invoke(node(name='Move desktop left', role='menu item'))
        wait(lambda: [d['id'] for d in desktops()].index(target) < [d['id'] for d in desktops()].index(peer), 'desktop reorder left')
        check('assistive reverse reorder restores desktop order', True)
        invoke(node(name='Close Desktop ' + peer, role='button'))
        wait(lambda: peer not in [d['id'] for d in desktops()], 'accessible desktop close')
        check('assistive close removes only disposable desktop', target in [d['id'] for d in desktops()])
        invoke(node(name='Close Accessible shell window one', role='button'))
        wait(lambda: window(first) is None, 'accessible Task View close')
        check('assistive Task View Close closes only own window', True)
        check('existing user windows retain native identities',
              initial_clients <= {(w['address'], w.get('stableId'), w['pid']) for w in data('clients')})
        report['result'] = 'pass' if not report['failures'] else 'fail'
    except Exception as error:
        report.update(result='fail', error=repr(error))
        report['view_at_failure'] = view()
        report['desktops_at_failure'] = desktops()
        report['accessible_at_failure'] = [dict(name=n.get_name(), role=n.get_role_name(),
            identity=n.get_accessible_id()) for n in nodes() if n.get_accessible_id().startswith('taskview-') or n.get_name() == 'Desktop name']
    finally:
        ipc('hoskinson.windows', 'dismiss')
        ipc('hoskinson.taskview', 'close')
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill(); p.wait()
        for desktop in created:
            if desktop in [d['id'] for d in desktops()]:
                run(BIN / 'hypr-desktops', 'close', desktop)
        run(BIN / 'hypr-desktops', 'switch', initial_workspace)
        if catalog_bytes is not None:
            catalog.write_bytes(catalog_bytes)
        elif catalog.exists():
            catalog.unlink()
        if initial.get('address'):
            ctl('dispatch', f'hl.dsp.focus({{window="address:{initial["address"]}"}})')
        ctl('dispatch', f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})')
        (H / '.cache/window-accessible-shell-qa.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
assert report['result'] == 'pass'
