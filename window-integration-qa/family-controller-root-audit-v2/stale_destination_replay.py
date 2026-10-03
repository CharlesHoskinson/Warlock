"""Controlled replay of the exact copied candidate's native effect boundary."""
import json
from pathlib import Path
import threading
import time

from scene_controller import SceneController, ids
from test_scene_controller import Desktop, Transport


def wait(predicate):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.002)
    raise AssertionError("expected controlled boundary not reached")


def main():
    desktop, transport = Desktop(), Transport()
    controller = SceneController(desktop, transport)
    window = desktop.windows[0]
    def request(operation):
        return controller.request(operation, window['address'], window['stableId'], window['pid'], context=1)
    first = request('minimize')
    wait(lambda: any(m['command'] == 'validate' and m['token'] == first['token'] for m in transport.sent))
    initial = controller.current
    controller.event({'event': 'ready', 'token': initial.token, 'identities': ids(initial.members),
                      'servicePromoted': True, 'sourceDigests': [{k: s[k] for k in ('stableId', 'pid', 'digest')} for s in initial.sources]})
    old_lookup_started, release_old_lookup = threading.Event(), threading.Event()
    actual_fresh = controller.fresh
    def controlled_fresh(record):
        result = actual_fresh(record)
        if record.operation == 'restore':
            old_lookup_started.set()
            if not release_old_lookup.wait(3):
                raise AssertionError('root did not release old lookup')
        return result
    controller.fresh = controlled_fresh
    try:
        obsolete = request('restore')
        assert old_lookup_started.wait(1)
        latest = request('minimize')
        wait(lambda: controller.current and controller.current.token == latest['token'] and controller.current.validated)
        assert not desktop.destinations
        release_old_lookup.set()
        controller.workers.shutdown(wait=True, cancel_futures=False)
        assert not desktop.destinations, 'obsolete worker changed destination'
        report = {'kind': 'actual copied scene_controller.py stale restore native destination effect',
                  'obsoleteToken': obsolete['token'], 'latestToken': latest['token'],
                  'currentToken': controller.current.token, 'currentOperation': controller.current.operation,
                  'obsoleteValidationEmitted': any(m['command'] == 'validate' and m['token'] == obsolete['token'] for m in transport.sent),
                  'actualDestinationCallsAfterLatestAccepted': desktop.destinations,
                  'counterexampleReproduced': False,
                  'repairVerified': controller.current.token == latest['token'] and not desktop.destinations,
                  'nativeGUIUsed': False, 'scope': 'controlled desktop adapter; exact copied coordinator function executes'}
        Path('repair-replay.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
    finally:
        release_old_lookup.set()
        controller.workers.shutdown(wait=True, cancel_futures=True)


if __name__ == '__main__':
    main()
