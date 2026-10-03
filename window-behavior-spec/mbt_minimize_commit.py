#!/usr/bin/env python3
"""Replay Quint endpoint traces against the installed motion controller.

Only compositor/rendering endpoints are replaced by a deterministic adapter.
The installed request, readiness, cancellation, watchdog, persistence recovery
and identity matching code runs unchanged in temporary directories. This is
controller MBT, not native compositor timing or image correctness evidence.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile

from mbt_desktop import decode, module

HERE = Path(__file__).resolve().parent
SOURCE = Path(os.environ.get('MOTION_MBT_SOURCE', Path.home() / '.local/bin/hypr-window-motion'))
motion = module('installed_motion_mbt', SOURCE)


class Desktop:
    def __init__(self, root):
        self.root = root
        self.is_reduced = False
        self.window = self.make_window(1)
        self.calls = []

    @staticmethod
    def make_window(identity):
        return dict(address='0x10', stableId='stable' + str(identity),
                    pid=100 + identity, mapped=True, pinned=True,
                    at=[79, 88], size=[641, 377] if identity == 1 else [731, 401],
                    workspace={'name': '2'})

    def clients(self):
        return [copy.deepcopy(self.window)] if self.window else []

    def active(self): return '0x10'
    def reduced(self): return self.is_reduced
    def source_screen(self, window, previous=None):
        return dict(name='DP-1', x=0, y=0, width=1920, height=1080, scale=1)
    def select_destination(self, window): return self.source_screen(window)
    def family(self, window, windows, single=False): return [window], window
    def target(self, window):
        return dict(visible=True, screenName='DP-1', monitorX=0, monitorY=0,
                    rect=dict(x=951, y=10, width=19, height=19))
    def capture(self, window, token):
        path = self.root / (token + '.png')
        path.write_bytes(b'deterministic-disposable-image')
        return str(path)
    def ipc(self, method, payload):
        self.calls.append((method, copy.deepcopy(payload)))
        return True
    def commit(self, operation, window, preview_ready=False):
        assert self.window and motion.key(self.window) == motion.key(window)
        self.calls.append(('commit', operation, motion.key(window)))
        self.window['workspace']['name'] = (
            'special:win-minimized' if operation == 'minimize' else '2')


def replay(path):
    states = [decode(s) for s in json.loads(path.read_text())['states']]
    kinds = set()
    with tempfile.TemporaryDirectory(prefix='minimize-commit-mbt-') as directory:
        root = Path(directory)
        desktop = Desktop(root)
        controller = motion.Controller(desktop, root)
        tokens = {}
        geometry = copy.deepcopy((desktop.window['at'], desktop.window['size']))
        for index, snapshot in enumerate(states):
            expected = snapshot['s']
            event = snapshot['lastEvent']
            tag = event['tag']
            label = (path.name, index, event, expected)
            if index:
                kinds.add(tag)
                if tag in ('Minimize', 'Restore', 'Activate'):
                    captured = motion.key(desktop.window)
                    tokens[expected['epoch']] = controller.request(
                        tag.lower(), *map(str, captured))['tokens'][0]
                elif tag in ('Ready', 'Finish'):
                    token = tokens.get(event['value'], 'unknown-stale-token')
                    before = len([c for c in desktop.calls if c[0] == 'commit'])
                    getattr(controller, 'ready' if tag == 'Ready' else 'settle')(token)
                    if expected['stale']:
                        assert before == len([c for c in desktop.calls if c[0] == 'commit']), label
                elif tag == 'Watchdog':
                    for record in controller.pending.values(): record['deadline'] = 0
                    controller.watchdog()
                elif tag == 'Reduce':
                    desktop.is_reduced = True
                    controller.watchdog()
                elif tag == 'EnableMotion':
                    desktop.is_reduced = False
                elif tag == 'Reload':
                    controller = motion.Controller(desktop, root)
                    controller.recover()
                elif tag == 'Close':
                    desktop.window = None
                    controller.watchdog()
                elif tag == 'Reuse':
                    desktop.window = desktop.make_window(expected['identity'])
                    desktop.window['pid'] = expected['pid']
                    geometry = copy.deepcopy((desktop.window['at'], desktop.window['size']))
                elif tag in ('ReuseBeforeReady', 'PIDChangeBeforeReady'):
                    # A replacement appears before the 40ms watchdog runs.
                    # Deliver the old frame readiness directly to the real
                    # identity guard rather than first dropping it ourselves.
                    desktop.window = desktop.make_window(expected['identity'])
                    desktop.window['pid'] = expected['pid']
                    desktop.window['size'] = [731, 401]
                    geometry = copy.deepcopy((desktop.window['at'], desktop.window['size']))
                    before = len([c for c in desktop.calls if c[0] == 'commit'])
                    assert not controller.ready(tokens[expected['epoch']])['ok'], label
                    assert before == len([c for c in desktop.calls if c[0] == 'commit']), label
                else:
                    raise AssertionError(('unhandled model event', label))
            assert bool(desktop.window) == expected['live'], label
            assert bool(controller.pending) == expected['pending'], label
            assert desktop.is_reduced == expected['reduced'], label
            if desktop.window:
                assert desktop.window['stableId'] == 'stable' + str(expected['identity']), label
                assert desktop.window['pid'] == expected['pid'], label
                assert (desktop.window['at'], desktop.window['size']) == geometry, label
                assert desktop.window['pinned'] == expected['pinned'], label
                assert (desktop.window['workspace']['name'] == 'special:win-minimized') == expected['minimized'], label
            if controller.pending:
                record = controller.pending['0x10']
                assert (record['operation'] == 'minimize') == expected['intent'], label
                assert (record['phase'] == 'running') == expected['ready'], label
                assert tuple(record['identity']) == motion.key(desktop.window), label
            else:
                assert not list(root.glob('*.png')), ('orphan snapshot', label)
                if (root / 'pending.json').exists():
                    assert json.loads((root / 'pending.json').read_text()) == [], label
    return len(states), kinds


def main():
    paths = sorted((HERE / 'qa-traces').glob('minimize-commit-*.itf.json'))
    assert paths, 'Generate minimize_commit traces before replay'
    counts = [replay(path) for path in paths]
    kinds = set().union(*(kinds for _, kinds in counts))
    required = {'Minimize', 'Restore', 'Activate', 'Ready', 'Finish',
                'Watchdog', 'Reduce', 'EnableMotion', 'Reload', 'Close', 'Reuse',
                'ReuseBeforeReady', 'PIDChangeBeforeReady'}
    assert required <= kinds, ('missing transition coverage', required - kinds)
    report = dict(source=str(SOURCE), sourceSHA256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  traces=len(paths), states=sum(n for n, _ in counts),
                  eventTypes=sorted(kinds), result='pass',
                  scope='Selected controller source; deterministic compositor/renderer adapter; no native GUI timing')
    destination = Path(os.environ.get('MOTION_MBT_REPORT', HERE / 'minimize-commit-mbt-report.json'))
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(f"Minimize controller ({SOURCE}): {report['traces']} Quint traces / {report['states']} states / {len(kinds)} event types PASS")


if __name__ == '__main__': main()
