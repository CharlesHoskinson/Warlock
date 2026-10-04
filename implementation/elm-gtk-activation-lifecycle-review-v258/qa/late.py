import importlib.util, json, resource, sys, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
source = r.parent / 'elm-gtk-bootstrap-wire-v252/qa'
sys.path.insert(0, str(source))
spec = importlib.util.spec_from_file_location('review_private_bus', source / 'private_bus.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = r / 'qa' / ('late-' + str(time.time_ns()))
out.mkdir()
manager = m.Activations.__new__(m.Activations)
manager.output = out
state = {'snapshots': 0, 'lateJournal': False, 'busAlive': True}
def snapshots():
    state['snapshots'] += 1
    if state['lateJournal']:
        raise m.Refused('late failed activation would be refused if observed')
    return []
manager.snapshots = snapshots
class Connection:
    def close_sync(self, cancellable):
        # This closes only the observer connection, while private dbus-daemon
        # remains live until inherited host teardown after Activations.close.
        state['lateJournal'] = True
        return True
manager.connection = Connection()
accepted = manager.close(time.monotonic() + 3)
assert accepted == [] and state['snapshots'] == 2 and state['lateJournal'] and state['busAlive']
report = {'passed': True, 'nativeAcceptance': False, 'scope': 'Actual held Activations.close method with mocked discovery/connection close; no daemon or GUI', 'finding': 'No final journal check after observer connection close; bus still permits activation until later inherited teardown', 'acceptedCleanup': accepted, 'state': state, 'limits': 'This is a controlled interleaving witness, not proof a real GTK service hit the race'}
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(out / 'report.json'))
