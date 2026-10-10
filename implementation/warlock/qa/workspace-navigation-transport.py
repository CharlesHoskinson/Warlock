"""Protected native QA: lose a real workspace receipt before settlement.

No receipt or desktop fact is synthesized. One owned arm file interrupts the
actual native result; reconnect uses the unchanged durable read-only recovery.
"""
import json, os, pathlib, re, resource, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
import daemon
from endpoint import Refused, start_time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
assert re.search(r'/qa-harness\.slice/qa-harness-[A-Za-z0-9_-]+\.scope', pathlib.Path('/proc/self/cgroup').read_text())
directory = pathlib.Path(sys.argv[1]).resolve().parent
arm = directory / 'workspace-navigation-loss.arm'
marker = directory / 'workspace-navigation-loss.json'
release = directory / 'workspace-navigation-loss.release'


class InterruptedNavigation(daemon.Navigation):
    def settle(self, terminal):
        if arm.exists() and arm.read_text() == 'after-native-before-settlement\n':
            arm.unlink()
            assert terminal['status'] == 'Committed'
            durable = self._load()
            assert durable['status'] == 'Unknown'
            assert all(durable[k] == terminal[k] for k in ['binding', 'intent'])
            proof = {'pid': os.getpid(), 'start': start_time(os.getpid()),
                     'stage': 'after-native-receipt-before-durable-settlement-and-frontend-delivery',
                     'nativeRecord': terminal, 'durableRecord': durable}
            fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'w') as stream:
                json.dump(proof, stream); stream.flush(); os.fsync(stream.fileno())
            # Bound the injected transport hold inside the original six-second
            # observation deadline. The frontend's normal deadline is unchanged.
            deadline = time.monotonic() + 5
            while not release.exists():
                if time.monotonic() >= deadline:
                    raise Refused('QA workspace receipt hold expired')
                time.sleep(.005)
            release.unlink()
            raise Refused('QA workspace receipt lost before settlement')
        return super().settle(terminal)


daemon.Navigation = InterruptedNavigation
original_send = daemon.send


def send(value):
    if value.get('kind') == 'workspace-navigation-outcome' and arm.exists() and arm.read_text() == 'after-settlement-before-frontend\n':
        arm.unlink()
        assert value['status'] == 'Committed'
        config = json.loads(pathlib.Path(sys.argv[1]).read_text())
        journal = pathlib.Path(config['runtime']) / 'elm-window-recovery' / config['instance'] / value['binding']['lifetime'] / 'workspace-navigation-v1.json'
        record = {'schema': 1, **{k: value[k] for k in ['binding', 'intent', 'status', 'reason']}}
        assert json.loads(journal.read_text()) == record
        proof = {'pid': os.getpid(), 'start': start_time(os.getpid()),
                 'stage': 'after-durable-settlement-before-frontend-delivery',
                 'nativeRecord': record, 'durableRecord': record}
        marker = directory / 'workspace-navigation-frontend-loss.json'
        fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            json.dump(proof, stream); stream.flush(); os.fsync(stream.fileno())
        return
    return original_send(value)


daemon.send = send
raise SystemExit(daemon.run())
