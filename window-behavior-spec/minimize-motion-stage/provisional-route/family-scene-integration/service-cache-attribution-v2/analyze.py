"""Read-only attribution of retained family V7; never instantiate native adapter."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from collections import Counter

HERE = Path(__file__).resolve().parent
SERVICE = HERE.parent / 'service-review-v12'
ATTEMPT = Path('/home/hoskinson/window-integration-qa/family-service-taskbar-v7/attempt-1')
sys.dont_write_bytecode = True
sys.path.insert(0, str(SERVICE))
from native_desktop import NativeDesktop


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    evidence = json.loads((ATTEMPT / 'service-evidence.json').read_text())
    history = evidence['records'][0]['history'][0]
    profile = history['profile']
    failure = profile['failure']
    assert 'motionTarget' in failure and 'exit status 125' in failure
    assert history['sources'] == [] and history['visual'] is False
    assert evidence['retainedEpochSources'] == [] and evidence['retainedCache'] == []
    events = Counter(event['event'] for transport in evidence['transports'] for event in transport['events'])
    assert set(events) == {'shaderPrecision', 'backendObserved', 'rasterState', 'gpu', 'outputs'}
    config = json.loads((ATTEMPT / 'terminal-helpers/helper-config.json').read_text())
    assert set(config['queryRoots']) == {'qs', 'harness'}
    service_log = (ATTEMPT / 'family-service.log').read_text()
    assert 'Helper did not originate from exact compositor invocation' in service_log
    results = history['results']
    assert len(results) == 3 and all('motionTarget' in r['reason'] for r in results)

    # Execute the actual frozen capture methods through a rejected target.
    # Bypass __init__ deliberately: no native adapter, process, or GUI is created.
    calls = Counter()
    class Cache:
        def publish(self, *args):
            calls['publish'] += 1
            raise AssertionError('publication reached after rejected target')
    def reject(window):
        calls['target'] += 1
        raise subprocess.CalledProcessError(125, ['omarchy-shell', 'hoskinson.windows', 'motionTarget'])
    with tempfile.TemporaryDirectory(prefix='service-target-refusal-') as temporary:
        adapter = NativeDesktop.__new__(NativeDesktop)
        adapter.root = Path(temporary)
        adapter.capture_lock = threading.RLock()
        adapter.current_capture_epoch = None
        adapter.shared_cache = Cache()
        adapter.capture_serial = 0
        adapter.check_current = lambda window: calls.update(['identity-check'])
        adapter.target = reject
        try:
            adapter.capture_source(history['members'][0], history['token'], 0)
        except subprocess.CalledProcessError as error:
            assert error.returncode == 125
        else:
            raise AssertionError('capture accepted rejected target')
        assert calls == {'identity-check': 1, 'target': 1}
        assert adapter.capture_serial == 0 and adapter.current_capture_epoch is None
        assert list(adapter.root.iterdir()) == []

    manifest = SERVICE / 'manifest-v12.json'
    frozen = json.loads(manifest.read_text())['inputs']
    mismatches = [path for path, expected in frozen.items() if digest(Path(path)) != expected]
    assert not mismatches, mismatches
    inputs = [ATTEMPT / name for name in ('service-evidence.json', 'report.json', 'family-service.log', 'terminal-helpers/helper-config.json', 'terminal-helpers/helper-events.jsonl')]
    inputs += [SERVICE / name for name in ('manifest-v12.json', 'native_desktop.py', 'native_runtime.py', 'snapshot_cache.py')]
    inputs += [ATTEMPT.parent / 'helper_observer.py', Path(__file__)]
    report = {
        'scope': 'retained native failure attribution plus exact frozen capture refusal counterexample; no native launch',
        'conclusion': 'service motionTarget helper ancestry rejection before capture; no demonstrated product publication/pruner defect',
        'productChangeRequiredByThisEvidence': False,
        'failure': failure,
        'serviceLog': service_log.strip(),
        'capturedSources': len(history['sources']),
        'retainedEpochSources': len(evidence['retainedEpochSources']),
        'visual': history['visual'],
        'rendererEvents': dict(events),
        'queryRoots': list(config['queryRoots']),
        'fallbackCommits': len(results),
        'retainedCacheEntries': len(evidence['retainedCache']),
        'captureCounterexample': {'calls': dict(calls), 'captureSerial': adapter.capture_serial, 'publicationCalls': calls['publish'], 'filesCreated': 0},
        'frozenServiceInputsUnchanged': len(frozen),
        'requiredFollowon': ['register exact service query caller and bounded member motionTarget operation in fresh wrapper', 'require three actual captured exact family sources and bound renderer seeds', 'validate three persistent immutable PNG/metadata pairs before actor retirement', 'prove same pairs survive actor disposal and restore consumes exact pairs', 'only then attribute any remaining publication/pruner/lookup failure'],
        'inputs': {str(path): digest(path) for path in inputs},
    }
    destination = HERE / 'report.json'
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'report': str(destination), 'sha256': digest(destination), 'unchangedInputs': len(frozen), 'productChangeRequired': False}))


if __name__ == '__main__':
    main()
