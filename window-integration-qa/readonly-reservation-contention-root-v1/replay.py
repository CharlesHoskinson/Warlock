"""Actual frozen read-only IPC under a contended reservation lock; no GUI."""
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
from test_readonly_ipc import ReadonlyKernelTests


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    scope = require_qa_scope()
    paths = [Path(__file__), SERVICE/'readonly_ipc.py', SERVICE/'native_runtime.py',
             SERVICE/'service_runtime.py', SERVICE/'test_readonly_ipc.py']
    before = {str(p): {'sha256': digest(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
    manifest = SERVICE/'manifest-family-preparation-v24.json'
    frozen = json.loads(manifest.read_text())
    assert digest(manifest) == 'b017d8d2a126f76c637429fffc2d77d510161fb89d3f3826795abb47d30b9f2c'
    for p in paths[1:]:
        assert digest(p) == frozen['inputs'][str(p)]
        assert before[str(p)]['mode'] == frozen['inputModes'][str(p)]
    case = ReadonlyKernelTests()
    case.setUp()
    thread = None
    queries = []
    observations = {}
    result = {'result': 'fail', 'nativeLaunch': False, 'mainChanged': False}
    try:
        def data_query(connection, data):
            queries.append(data.decode('ascii'))
            connection.sendall(b'[]')
        case.handler = data_query
        initial_version_connections = len(case.control.children)
        def worker():
            observations['startedNs'] = time.monotonic_ns()
            try:
                observations['value'] = case.query(timeout=.6)
            except BaseException as error:
                observations['error'] = {'type': type(error).__name__, 'message': str(error)}
            finally:
                observations['finishedNs'] = time.monotonic_ns()
        # This is the genuine fixture reservation RLock used by the frozen
        # register -> publish -> JournalStore path. Authority, time and IPC are
        # unmodified. Hold it past the existing .6-second housekeeping budget.
        with case.lock:
            thread = threading.Thread(target=worker, name='root-readonly-query')
            thread.start()
            observation_limit = time.monotonic()+2
            while len(case.control.children) <= initial_version_connections:
                if time.monotonic() >= observation_limit:
                    raise AssertionError('actual NativeSession version connection not observed')
                time.sleep(.002)
            observations['authorityVersionConnectionObservedNs'] = time.monotonic_ns()
            release_after = observations['startedNs']+750_000_000
            while time.monotonic_ns() < release_after:
                time.sleep(.002)
            observations['lockReleaseNs'] = time.monotonic_ns()
        thread.join(timeout=3)
        assert not thread.is_alive()
        assert observations.get('error') == {'type': 'TimeoutError', 'message': 'read-only complete reply absolute deadline'}
        assert 'value' not in observations and queries == []
        history = case.reader.snapshot()['history']
        assert len(history) == 1
        refused = history[0]
        assert refused['closed'] is True and refused['published'] is True
        assert refused['outcome'] == 'refused' and refused['evidence']['peer'] is None
        assert refused['evidence']['replyBytes'] == 0
        assert refused['evidence']['completeServerEOF'] is False
        assert case.store.read()['readonlyOwnership'] == case.reader.snapshot()
        # The same fixed request and budget work with a free reservation lock;
        # preserve the original refusal in the durable history.
        assert case.query(timeout=.6) == b'[]'
        final = case.reader.snapshot()
        assert queries == ['j/clients'] and len(final['history']) == 2
        assert final['history'][0] == refused
        assert final['history'][1]['outcome'] == 'complete'
        assert final['history'][1]['evidence']['completeServerEOF'] is True
        assert case.store.read()['readonlyOwnership'] == final
        case.reader.assert_closed()
        result.update(result='pass', scope=scope,
                      experiment='genuine frozen Unix peer/NativeSession/RuntimeLease/JournalStore, real reservation-lock contention',
                      queryBudgetSeconds=.6, observations=observations,
                      refusedRow=refused, subsequentUncontendedRow=final['history'][1],
                      actualDataRequests=queries,
                      registrationToRefusalMs=(refused['finishedNs']-refused['registeredNs'])/1e6,
                      sourceUnchanged=True,
                      limits=['A reachable pre-connect timeout path; native row33 manager-lock holder and timing are unproved.',
                              'No product changes, deadline reset, skipped ledger proof or native feature acceptance.',
                              'CPU peer is a fixture; no Hyprland or Quickshell launched.'])
    finally:
        if thread is not None:
            thread.join(timeout=3)
        case.tearDown()
        after = {str(p): {'sha256': digest(p), 'mode': stat.S_IMODE(p.stat().st_mode)} for p in paths}
        assert before == after
        result['inputs'] = before
        result['selectedManifest'] = str(manifest)
        result['selectedManifestSHA256'] = digest(manifest)
        destination = OUT/'report.json'
        fd = os.open(destination, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
    print(json.dumps({'result': result['result'], 'report': str(OUT/'report.json'),
                      'nativeLaunch': False, 'mainChanged': False}))
    return int(result['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
