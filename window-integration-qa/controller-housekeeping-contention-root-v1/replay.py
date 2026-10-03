"""Frozen controller commit versus actual housekeeping IPC; private CPU only."""
from pathlib import Path
import hashlib
import json
import os
import stat
import sys
import threading
import time

QA = Path('/home/hoskinson/window-integration-qa')
SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v24')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope
sys.path.insert(0, str(SERVICE))
from native_runtime import NativeFactory
from owned_commands import OwnedCommands
from snapshot_cache import SnapshotCache
from test_readonly_ipc import ReadonlyKernelTests
from test_scene_controller import SceneTests


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class NoHelper:
    def register(self, *args, **kwargs):
        raise AssertionError('readonly housekeeping must not launch a helper')


def main():
    scope = require_qa_scope()
    names = ('native_runtime.py', 'owned_commands.py', 'snapshot_cache.py',
             'readonly_ipc.py', 'scene_controller.py', 'test_readonly_ipc.py',
             'test_scene_controller.py')
    paths = [Path(__file__)] + [SERVICE/name for name in names]
    stamps = {str(p): {'sha256': digest(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
    manifest = SERVICE/'manifest-family-preparation-v24.json'
    assert digest(manifest) == 'b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'
    frozen = json.loads(manifest.read_text())
    for p in paths[1:]:
        assert stamps[str(p)]['sha256'] == frozen['inputs'][str(p)]
        assert stamps[str(p)]['mode'] == frozen['inputModes'][str(p)]
    ipc = ReadonlyKernelTests()
    scene = SceneTests()
    ipc.setUp()
    scene.setUp()
    query_thread = commit_thread = None
    result = {'result': 'fail', 'GUI': False, 'mainChanged': False}
    observations = {}
    data_requests = []
    try:
        scene.c.lock = ipc.lock
        record = scene.seed()
        factory = NativeFactory.__new__(NativeFactory)
        factory.guard = ipc.guard
        factory.readonly = ipc.reader
        factory.keeper = NoHelper()
        factory.housekeeping_commands = OwnedCommands(factory.keeper, ipc.env, readonly=ipc.reader)
        factory.shared_cache = SnapshotCache(ipc.root/'actual-empty-cache',
            lambda *_: (_ for _ in ()).throw(AssertionError('empty cache has no snapshot')),
            session=ipc.session)

        def reply(connection, data):
            data_requests.append(data.decode('ascii'))
            connection.sendall(b'[]')
        ipc.handler = reply
        # The whole frozen factory path, including three original .6s queries,
        # real native-identity coverage and empty-cache flock/prune succeeds.
        factory.housekeep()
        expected = ['j/clients', '/repl print(hl.plugin.hyprbars.window_families())', 'j/clients']
        assert data_requests == expected
        assert len(ipc.reader.snapshot()['history']) == 3
        data_requests.clear()

        scene.d.commit_block = threading.Event()
        scene.d.started.clear()

        def commit():
            observations['commitStartedNs'] = time.monotonic_ns()
            try:
                observations['commitResult'] = scene.event(record, 'ready')
            except BaseException as error:
                observations['commitError'] = str(error)
            finally:
                observations['commitFinishedNs'] = time.monotonic_ns()

        commit_thread = threading.Thread(target=commit, name='frozen-controller-ready')
        commit_thread.start()
        assert scene.d.started.wait(2)
        # The actual controller ready -> commit_members -> Desktop.commit
        # now holds its shared receipt lock. Only Desktop's native effect is
        # an explicit controllable CPU fixture, not a real GUI command.
        assert not ipc.lock.acquire(blocking=False)
        initial_version_connections = len(ipc.control.children)

        def housekeeping():
            observations['housekeepingStartedNs'] = time.monotonic_ns()
            try:
                factory.housekeep()
                observations['housekeepingReturned'] = True
            except BaseException as error:
                observations['housekeepingError'] = {'type': type(error).__name__, 'message': str(error)}
            finally:
                observations['housekeepingFinishedNs'] = time.monotonic_ns()

        query_thread = threading.Thread(target=housekeeping, name='frozen-native-housekeep')
        query_thread.start()
        limit = time.monotonic()+2
        while len(ipc.control.children) < initial_version_connections+2:
            if time.monotonic() >= limit:
                raise AssertionError('factory and ReadonlyIPC authority peers not observed')
            time.sleep(.002)
        observations['queryAuthorityObservedNs'] = time.monotonic_ns()
        release_at = observations['housekeepingStartedNs']+750_000_000
        while time.monotonic_ns() < release_at:
            time.sleep(.002)
        observations['commitReleaseNs'] = time.monotonic_ns()
        scene.d.commit_block.set()
        query_thread.join(3)
        commit_thread.join(3)
        assert not query_thread.is_alive() and not commit_thread.is_alive()
        assert observations.get('commitResult') is True and 'commitError' not in observations
        assert len(scene.d.commits) == len(record.results) == 3
        assert observations.get('housekeepingError') == {'type': 'TimeoutError',
            'message': 'read-only complete reply absolute deadline'}
        assert 'housekeepingReturned' not in observations and data_requests == []
        history = ipc.reader.snapshot()['history']
        assert len(history) == 4
        refused = history[-1]
        assert refused['closed'] and refused['published'] and refused['outcome'] == 'refused'
        assert refused['evidence']['peer'] is None and refused['evidence']['replyBytes'] == 0
        assert not refused['evidence']['completeServerEOF']
        assert ipc.store.read()['readonlyOwnership'] == ipc.reader.snapshot()
        factory.housekeep()
        final = ipc.reader.snapshot()
        assert len(final['history']) == 7 and final['history'][3] == refused
        assert data_requests == expected
        assert all(r['outcome'] == 'complete' for r in final['history'][4:])
        assert ipc.store.read()['readonlyOwnership'] == final
        ipc.reader.assert_closed()
        result.update(result='pass', scope=scope, observations=observations,
            sceneCommitResults=record.results, refusedRow=refused,
            subsequentActualDataRequests=data_requests,
            originalHousekeepingQueryBudgetSeconds=.6,
            sourceUnchanged=True,
            limits=['Actual frozen controller callback and NativeFactory.housekeep share the real receipt lock; native effect is controlled CPU fixture.',
                    'Actual Unix peers, original query guards, durable JournalStore and SnapshotCache prune run without deadline changes.',
                    'Reachable native-commit contention path, not retrospective attribution of native baseline query33.',
                    'No GUI, production mutation, hidden refusal, or accepted feature baseline.'])
    finally:
        if scene.d.commit_block:
            scene.d.commit_block.set()
        for thread in (query_thread, commit_thread):
            if thread is not None:
                thread.join(3)
        scene.tearDown()
        ipc.tearDown()
        assert stamps == {str(p): {'sha256': digest(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
        result['inputs'] = stamps
        destination = OUT/'report.json'
        with os.fdopen(os.open(destination, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600), 'w') as f:
            json.dump(result, f, indent=2)
            f.write('\n')
            f.flush()
            os.fsync(f.fileno())
    print(json.dumps({'result': result['result'], 'report': str(destination)}))
    return int(result['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
