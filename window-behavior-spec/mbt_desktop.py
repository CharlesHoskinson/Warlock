#!/usr/bin/env python3
"""Replay Quint ITF traces against actual Snap Group/taskbar pure state functions.

Modules are imported without running CLI entry points. All configuration paths
are redirected to a TemporaryDirectory; clients and subprocess calls are mocked.
The desktop model permits explicit group creation, while the backend creates
maximal disjoint groups automatically. We compare target membership and safety
properties for Snap Groups, and exact app grouping/pin state for the taskbar.
"""
import argparse
from collections import Counter
import importlib.machinery
import importlib.util
import os
import json
from pathlib import Path
import tempfile
import sys
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ZONES = {1: 'left', 2: 'right', 3: 'top_left', 4: 'top_right', 5: 'bottom_left', 6: 'bottom_right',
         8: 'third_left', 9: 'third_center', 10: 'third_right',
         11: 'two_thirds_left', 12: 'two_thirds_right'}


def module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    result = importlib.util.module_from_spec(spec)
    loader.exec_module(result)
    return result


def decode(value):
    if isinstance(value, list):
        return [decode(v) for v in value]
    if not isinstance(value, dict):
        return value
    if '#bigint' in value:
        return int(value['#bigint'])
    if '#set' in value:
        return set(map(decode, value['#set']))
    if '#map' in value:
        return {decode(k): decode(v) for k, v in value['#map']}
    if '#tup' in value:
        return tuple(map(decode, value['#tup']))
    return {k: decode(v) for k, v in value.items()}


def live_windows(model):
    return [dict(address=hex(id), pid=1000 + id, initialClass='app' + str(w['app']),
                 **{'class': 'app' + str(w['app'])}, title='Window ' + str(id), mapped=True,
                 monitor=0, floating=True, pinned=w['pinned'], fullscreen=0, at=[300,300], size=[400,300],
                 workspace={'name': 'special:win-minimized' if w['minimized'] else str(w['workspace'])},
                 focusHistoryID=0 if model['focused'] == id else id)
            for id, w in model['windows'].items()]


def assert_snap(snap, state, clients, expected, label):
    live = {w['address']: w for w in clients}
    occupied = set()
    for group in snap.snapshot(state, clients):
        assert len(group['addresses']) >= 2, label + ': degenerate group'
        slots = set()
        for address in group['addresses']:
            assert address in live and address not in occupied, label + ': stale/duplicate membership'
            occupied.add(address)
            member = state['snapped'][address]
            assert member['identity'] == snap.identity(live[address]), label + ': reused identity'
            assert member['workspace'] == group['workspace'] and member['monitor'] == group['monitor']
            assert not slots.intersection(snap.ZONES[member['zone']]), label + ': overlapping slots'
            slots.update(snap.ZONES[member['zone']])
    for address, member in state['snapped'].items():
        id = int(address, 16)
        assert id in expected['windows'], label + ': closed window retained'
        assert member['zone'] == ZONES[expected['windows'][id]['zone']], label + ': wrong zone target'
        assert member['workspace'] == str(expected['windows'][id]['workspace']), label + ': wrong workspace'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snap', type=Path, default=Path.home() / '.local/bin/hypr-snap-groups')
    parser.add_argument('--taskbar', type=Path, default=Path.home() / '.local/bin/hypr-taskbar')
    parser.add_argument('traces', nargs='*', type=Path)
    args = parser.parse_args()
    paths = args.traces or sorted((HERE / 'qa-traces').glob('desktop-*.itf.json'))
    assert paths, 'Generate Quint traces first'
    snap, taskbar = module('qa_snap', args.snap), module('qa_taskbar', args.taskbar)
    count, events = 0, Counter()
    with tempfile.TemporaryDirectory(prefix='desktop-mbt-') as temporary:
        root = Path(temporary)
        taskbar.HOME = root
        os.environ['XDG_RUNTIME_DIR'] = str(root / 'runtime')
        mocktool = root / '.local/bin/hypr-snap-groups'
        mocktool.parent.mkdir(parents=True)
        mocktool.touch()
        taskbar.CONFIG = root / 'config' 
        taskbar.DATA = root / 'data'
        taskbar.PINS = taskbar.CONFIG / 'taskbar-pins.json'
        if hasattr(taskbar, 'SETTINGS'):
            taskbar.SETTINGS = taskbar.CONFIG / 'taskbar-settings.json'
        if hasattr(taskbar, 'ORDER'):
            taskbar.ORDER = taskbar.CONFIG / 'taskbar-order.json'
        catalog = {f'app{i}': dict(id=f'app{i}', name=f'App {i}', icon='terminal', wmclass=f'app{i}',
                                 mime=[], actions=[], exec='/bin/true', path=f'/tmp/app{i}.desktop', terminal=False)
                   for i in (1, 2, 3)}
        for path in paths:
            state = {'version': 1, 'snapped': {}, 'groups': [], 'next_id': 0}
            for setting in ('PINS', 'ORDER', 'SETTINGS'):
                setting_path = getattr(taskbar, setting, None)
                if setting_path and setting_path.exists():
                    setting_path.unlink()
            trace = [decode(s) for s in json.loads(path.read_text())['states']]
            for index, expected in enumerate(trace):
                clients = live_windows(expected)
                taskbar.clients = lambda: clients
                taskbar.subprocess = SimpleNamespace(check_output=lambda argv, **kw: '[]' if argv[0] == 'hyprctl' else json.dumps(snap.snapshot(state, clients)))
                event = expected['lastEvent']
                tag, value = event['tag'], event['value']
                if index:
                    events[tag] += 1
                    if tag == 'Snap':
                        id, zone = value
                        snap.record(state, clients, hex(id), ZONES.get(zone, 'maximize'))
                    elif tag == 'PinApp':
                        taskbar.set_pin('app' + str(value), value in expected['pinnedApps'], catalog)
                    elif tag == 'Reorder':
                        prior_argv, prior_entries = sys.argv, taskbar.entries
                        taskbar.entries = lambda: catalog
                        try:
                            sys.argv = ['hypr-taskbar', 'reorder', 'app' + str(value[0]), 'app' + str(value[1])]
                            taskbar.main()
                        finally:
                            sys.argv, taskbar.entries = prior_argv, prior_entries
                snap.sync(state, clients)
                label = f'{path.name}:{index}:{tag}'
                assert_snap(snap, state, clients, expected, label)
                output = taskbar.snapshot(catalog)
                actual = {g['key']: g for g in output['groups']}
                if tag == 'Reorder':
                    ordered = [g['key'] for g in output['groups']]
                    assert ordered.index('app' + str(value[0])) < ordered.index('app' + str(value[1])), label + ': reorder ignored'
                expected_apps = expected['pinnedApps'] | {w['app'] for w in expected['windows'].values()}
                assert set(actual) == {'app' + str(i) for i in expected_apps}, label + ': taskbar app set'
                for app in expected_apps:
                    group = actual['app' + str(app)]
                    assert group['pinned'] == (app in expected['pinnedApps']), label + ': app pin'
                    ids = {int(w['address'], 16) for w in group['windows']}
                    assert ids == {id for id, w in expected['windows'].items() if w['app'] == app}, label + ': app windows'
                assert all(not(g.get('windows')) or len({w['address'] for w in g['windows']}) == len(g['windows']) for g in actual.values())
                count += 1
            # Address reuse must never revive a previous Snap Group member.
            if clients:
                victim = clients[0]
                victim['pid'] += 10000
                snap.sync(state, clients)
                assert victim['address'] not in state['snapped'], 'PID reuse retained snap membership'
        # Four quarters, mixed layout, minimize preservation, and idempotent recall recording.
        expected = {'windows': {i: dict(app=1, workspace=1, minimized=False, pinned=False, zone=i + 2) for i in range(1, 5)}, 'focused': 1}
        clients = live_windows(expected)
        state = {'version': 1, 'snapped': {}, 'groups': [], 'next_id': 0}
        for i in range(1, 5):
            snap.record(state, clients, hex(i), ZONES[i + 2])
        assert len(state['groups']) == 1 and len(state['groups'][0]['addresses']) == 4
        groupid = state['groups'][0]['id']
        for client in clients:
            client['workspace']['name'] = 'special:win-minimized'
        snap.sync(state, clients)
        assert state['groups'][0]['id'] == groupid and len(state['groups'][0]['addresses']) == 4
        # Exercise the actual recall CLI with mocked restore/eval transport.
        snap.ROOT = root / 'snap'
        snap.ROOT.mkdir()
        (snap.ROOT / 'state.json').write_text(json.dumps(state))
        calls = []
        snap.clients = lambda: clients
        snap.ctl = lambda *a: calls.append(('eval', a)) or ''
        snap.subprocess = SimpleNamespace(run=lambda a, **kw: calls.append(('restore', a)))
        prior_argv = sys.argv
        try:
            sys.argv = ['hypr-snap-groups', 'recall', groupid]
            snap.main()
        finally:
            sys.argv = prior_argv
        assert [c[1][-1] for c in calls if c[0] == 'restore'] == state['groups'][0]['addresses']
        assert len([c for c in calls if c[0] == 'eval']) == 4
        for kind, args in calls:
            if kind == 'eval':
                assert any('"' + address + '"' in args[-1] for address in state['groups'][0]['addresses'])
        for client in clients:
            client['workspace']['name'] = '1'
            snap.record(state, clients, client['address'], state['snapped'][client['address']]['zone'])
        assert state['groups'][0]['id'] == groupid, 'idempotent recall changed group ID'
        clients[0]['monitor'] = 1
        snap.sync(state, clients)
        assert '0x1' not in state['snapped'], 'monitor move retained old snap membership'
    print(json.dumps({'traces': len(paths), 'states_checked': count, 'events': dict(sorted(events.items())),
                      'result': 'PASS', 'scope': 'actual backend functions, isolated state, mocked compositor'}, indent=2))


if __name__ == '__main__':
    main()
