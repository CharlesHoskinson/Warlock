#!/usr/bin/env python3
"""Replay Quint indicator traces against the installed LauncherEntry receiver."""
import json
from pathlib import Path
from mbt_desktop import decode, module

HERE = Path(__file__).resolve().parent
launcher = module('qa_launcher', Path.home() / '.local/bin/hypr-taskbar-launcher')
PROPERTY = {'Count':'count','CountVisible':'count-visible','Progress':'progress',
            'ProgressVisible':'progress-visible','Urgent':'urgent','Updating':'updating','Quicklist':'quicklist'}
FIELDS = {'count':'count','count-visible':'countVisible','progress':'progress',
          'progress-visible':'progressVisible','urgent':'urgent','updating':'updating','quicklist':'quicklist'}


def main():
    paths = sorted((HERE/'qa-traces').glob('launcher-*.itf.json'))
    assert paths, 'Generate launcher Quint traces first'
    checked = 0
    events = set()
    for path in paths:
        receiver = launcher.Entries()
        for i, expected in enumerate(json.loads(path.read_text())['states']):
            expected = decode(expected)
            tag, payload = expected['lastEvent']['tag'], expected['lastEvent']['value']
            if i:
                events.add(tag)
                if tag == 'Disconnect':
                    receiver.disconnect(':qa.'+str(payload))
                elif tag != 'Connect':
                    sender, app, value = payload
                    if tag == 'Progress':
                        value /= 2
                    elif tag == 'Quicklist':
                        value = '/menu'+str(value) if value else ''
                    receiver.update(':qa.'+str(sender), 'application://app'+str(app)+'.desktop', {PROPERTY[tag]:value})
            actual = receiver.snapshot()
            projected = {}
            for (sender, app), entry in expected['entries'].items():
                if app not in projected or projected[app][1]['serial'] < entry['serial']:
                    projected[app] = (sender, entry)
            assert set(actual) == {'app'+str(app) for app in projected}, (path.name, i, 'app set')
            for app, (sender, entry) in projected.items():
                found = actual['app'+str(app)]
                assert found['sender'] == ':qa.'+str(sender), (path.name, i, 'publisher')
                for prop, field in FIELDS.items():
                    value = found[prop]*2 if prop=='progress' else found[prop]
                    if prop=='quicklist':
                        value = int(value[-1]) if value else 0
                    assert value == entry[field], (path.name, i, prop, value, entry[field])
            checked += 1
    assert events == set(PROPERTY) | {'Disconnect','Connect'}, events
    print(f'Launcher backend replay: {len(paths)} traces, {checked} checked states, all 9 event types')


if __name__ == '__main__':
    main()
