"""Actual query EOF then controller receipt-lock contention; private CPU only."""
from pathlib import Path
from copy import deepcopy
import hashlib
import json
import os
import stat
import sys
import threading
import time

QA = Path('/home/hoskinson/window-integration-qa')
SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-preview-lock-admission-v25')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope
sys.path.insert(0, str(SERVICE))
from native_runtime import NativeFactory
from owned_commands import OwnedCommands
from snapshot_cache import SnapshotCache
from test_readonly_ipc import ReadonlyKernelTests
from test_scene_controller import SceneTests


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class NoHelper:
    def register(self, *args, **kwargs):
        raise AssertionError('read-only housekeeping must not launch a helper')


def main():
    scope = require_qa_scope()
    manifest = SERVICE / 'manifest-preview-admission-v25.json'
    assert sha(manifest) == 'f0b6916151c587501ae73a8fcfacdcc5156c661289592358d13bce66e23ef6e2'
    frozen = json.loads(manifest.read_text())
    names = ('native_runtime.py', 'owned_commands.py', 'snapshot_cache.py',
             'readonly_ipc.py', 'scene_controller.py', 'scene_manager.py',
             'test_readonly_ipc.py', 'test_scene_controller.py')
    paths = [Path(__file__), manifest] + [SERVICE / name for name in names]
    stamps = {str(p): {'sha256': sha(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
    for path in paths[2:]:
        assert stamps[str(path)]['sha256'] == frozen['inputs'][str(path)]
        assert stamps[str(path)]['mode'] == frozen['inputModes'][str(path)]
    ipc, scene = ReadonlyKernelTests(), SceneTests()
    ipc.setUp()
    scene.setUp()
    query_thread = commit_thread = None
    release_reply = threading.Event()
    data_seen = threading.Event()
    observations = {}
    requests = []
    result = {'result': 'fail', 'GUI': False, 'mainChanged': False}
    try:
        scene.c.lock = ipc.lock
        record = scene.seed()
        factory = NativeFactory.__new__(NativeFactory)
        factory.guard, factory.readonly = ipc.guard, ipc.reader
        factory.journal_lock = ipc.lock
        factory.keeper = NoHelper()
        factory.housekeeping_commands = OwnedCommands(factory.keeper, ipc.env, readonly=ipc.reader)
        factory.shared_cache = SnapshotCache(ipc.root / 'actual-empty-cache',
            lambda *_: (_ for _ in ()).throw(AssertionError('empty cache has no snapshot')),
            session=ipc.session)

        def ordinary_reply(connection, data):
            requests.append(data.decode('ascii'))
            connection.sendall(b'[]')

        expected = ['j/clients', '/repl print(hl.plugin.hyprbars.window_families())', 'j/clients']
        ipc.handler = ordinary_reply
        factory.housekeep()
        assert requests == expected
        requests.clear()
        scene.d.commit_block = threading.Event()
        scene.d.started.clear()

        def gated_reply(connection, data):
            requests.append(data.decode('ascii'))
            observations['dataRequestReceivedNs'] = time.monotonic_ns()
            data_seen.set()
            assert release_reply.wait(2), 'CPU peer reply permit missing'
            connection.sendall(b'[]')
            observations['replySentNs'] = time.monotonic_ns()
            # CpuServer closes this genuine Unix connection on normal return.

        ipc.handler = gated_reply

        def housekeeping():
            observations['housekeepingStartedNs'] = time.monotonic_ns()
            try:
                factory.housekeep()
                observations['housekeepingReturned'] = True
            except BaseException as error:
                observations['housekeepingError'] = {'type': type(error).__name__, 'message': str(error)}
            finally:
                observations['housekeepingFinishedNs'] = time.monotonic_ns()

        def commit():
            observations['commitStartedNs'] = time.monotonic_ns()
            try:
                observations['commitResult'] = scene.event(record, 'ready')
            except BaseException as error:
                observations['commitError'] = {'type': type(error).__name__, 'message': str(error)}
            finally:
                observations['commitFinishedNs'] = time.monotonic_ns()

        query_thread = threading.Thread(target=housekeeping, name='actual-housekeeping-query')
        query_thread.start()
        assert data_seen.wait(2)
        # Registration and the actual query send have completed before commit.
        commit_thread = threading.Thread(target=commit, name='actual-controller-ready')
        commit_thread.start()
        assert scene.d.started.wait(2)
        assert not ipc.lock.acquire(blocking=False)
        observations['replyPermittedNs'] = time.monotonic_ns()
        release_reply.set()
        release_at = observations['replyPermittedNs'] + 750_000_000
        while time.monotonic_ns() < release_at:
            time.sleep(.002)
        observations['commitReleasedNs'] = time.monotonic_ns()
        scene.d.commit_block.set()
        query_thread.join(3)
        commit_thread.join(3)
        assert not query_thread.is_alive() and not commit_thread.is_alive()
        assert observations.get('commitResult') is True and 'commitError' not in observations
        assert len(scene.d.commits) == len(record.results) == 3
        assert observations.get('housekeepingError') == {
            'type': 'TimeoutError', 'message': 'read-only complete reply absolute deadline'}
        assert 'housekeepingReturned' not in observations and requests == ['j/clients']
        history = ipc.reader.snapshot()['history']
        assert len(history) == 4
        refused = deepcopy(history[-1])
        assert refused['outcome'] == 'refused' and refused['closed'] and refused['published']
        assert refused['evidence']['peer']['pid'] == os.getpid()
        assert refused['evidence']['peer']['uid'] == os.getuid()
        assert refused['evidence']['completeServerEOF'] and refused['evidence']['replyBytes'] == 2
        assert refused['evidence']['replySHA256'] == hashlib.sha256(b'[]').hexdigest()
        assert observations['replySentNs'] - observations['housekeepingStartedNs'] < 600_000_000
        assert ipc.store.read()['readonlyOwnership'] == ipc.reader.snapshot()
        requests.clear()
        ipc.handler = ordinary_reply
        factory.housekeep()
        final = ipc.reader.snapshot()
        assert len(final['history']) == 7 and final['history'][3] == refused
        assert requests == expected and all(r['outcome'] == 'complete' for r in final['history'][4:])
        assert ipc.store.read()['readonlyOwnership'] == final
        ipc.reader.assert_closed()
        result.update(result='pass', scope=scope, observations=observations,
            refusedRow=refused, sceneCommitResults=record.results,
            subsequentActualDataRequests=requests, originalHousekeepingQueryBudgetSeconds=.6,
            limits=['Real frozen controller/housekeeping/read-only code and genuine Unix peer/EOF/durable journal.',
                    'CPU peer reply permit and CPU native-effect commit barrier are explicit scheduling fixtures.',
                    'Actual complete reply precedes original deadline; native-effect lock blocks terminal confirmation.',
                    'Reachable post-EOF contention path, not attribution of the historical live query lock holder.',
                    'No native GUI, source mutation, hidden refusal, or relaxed query deadline.'])
    finally:
        release_reply.set()
        if scene.d.commit_block:
            scene.d.commit_block.set()
        for thread in (query_thread, commit_thread):
            if thread is not None:
                thread.join(3)
                assert not thread.is_alive()
        scene.tearDown()
        ipc.tearDown()
        assert stamps == {str(p): {'sha256': sha(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
        result['sourceUnchanged'] = True
        result['inputs'] = stamps
        with os.fdopen(os.open(OUT / 'report.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), 'w') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    print(json.dumps({'result': result['result'], 'report': str(OUT / 'report.json')}))
    return int(result['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
