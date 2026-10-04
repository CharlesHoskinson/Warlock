"""Read-only closure of the actual V229 native run; no new GUI acceptance."""
import hashlib, importlib.util, json, os, time
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
RUNNER = REPO / 'implementation/elm-xdg-pointer-current-tuple-v229'
RUN = RUNNER / 'qa/native-1791136614787320167'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    out = HERE / 'qa' / ('verify-' + str(time.time_ns()))
    out.mkdir(parents=True)
    closure = {}
    def verify(path, expected):
        path = Path(path)
        assert digest(path) == expected, str(path)
        closure[str(path)] = expected
    report = {'passed': False, 'fullRoadmapAccepted': False,
              'physicalHardwareAccepted': False, 'current470BoundedAccepted': False}
    try:
        manifest = RUNNER / 'component-manifest.json'
        verify(manifest, '897905772959d60c8778ccf342760cb8834f94ef046992ffb15b4bb8d6f2519d')
        frozen = json.loads(manifest.read_text())
        for name, row in frozen['files'].items():
            verify(RUNNER / name, row['sha256'])
        for name, row in frozen['externalFiles'].items():
            verify(name, row['sha256'])
        review = REPO / 'implementation/elm-xdg-pointer-current-tuple-review-v230/component-manifest.json'
        verify(review, 'ed125d2f63141e4101d5c8fe93273f80e90668372ccdb3fff132d79c56611bfe')
        for name, row in json.loads(review.read_text())['files'].items():
            verify(review.parent / name, row['sha256'])
        native = json.loads((RUN / 'report.json').read_text())
        closure[str(RUN / 'report.json')] = digest(RUN / 'report.json')
        for path, expected in native['inputs'].items():
            verify(path, expected)
        for path, expected in native['artifacts'].items():
            verify(RUN / path, expected)
        assert native['passed'] is True and native['cleanupPassed'] is True
        assert len(native['checks']) == 285 and all(r['passed'] is True for r in native['checks'])
        assert not native['profileCleanupErrors'] and not native['finalCleanupErrors']
        assert native['cleanup']['qaScope']['coreLimit'] == 1
        assert native['cleanup']['mainDisplayUsed'] is False
        stages = native['pointerStages']
        assert [s['profile'] for s in stages] == ['zero-scale1'] * 3 + ['origin-scale1'] + ['zero-scale2'] * 3 + ['origin-scale2']
        pointer = load('pointer', RUNNER / 'qa/pointer.py')
        observer = load('observer', RUNNER / 'qa/parent_observation.py')
        receipts = observations = gestures = 0
        revisions = []
        for stage in stages:
            assert len(stage['gestures']) == 5
            for gesture in stage['gestures']:
                gestures += 1
                proofs = []
                for key in ('motionAdmission', 'pairAdmission'):
                    record = gesture[key]
                    assert record['registered'] is True and record['exitCode'] == 0
                    assert record['probeAccepted'] is True and not record.get('error')
                    # Bind copied native evidence, rather than trusting report receipts.
                    relative = Path(record['stdout']).relative_to(Path(record['stdout']).parents[2])
                    raw = RUN / 'native-evidence' / relative
                    assert raw.stat().st_size == record['stdoutBytes']
                    assert digest(raw) == record['stdoutPrefixSHA256'] and record['stdoutTruncated'] is False
                    decoded = pointer.receipts(raw.read_bytes(), record['commands'])
                    assert decoded == record['receipts']
                    receipts += 1
                    peer = record['peer']
                    assert peer['pid'] == record['peerAfter']['pid']
                    assert peer['identity'] == record['peerAfter']['identity']
                    for row in decoded[1:]:
                        if row['scope'] != 'parent-surface-observation':
                            continue
                        value = row['observation']
                        target = value['target']
                        proof = observer.proof(value, sequence=row['sequence'],
                            parent_pid=peer['pid'], parent_start=peer['process']['start'], uid=os.getuid(),
                            controller_pid=record['process']['pid'], controller_start=record['actualStart'],
                            target_pid=native['cleanup']['compositorPID'], target_start=native['cleanup']['compositorStart'], global_point=gesture['globalPoint'])
                        assert target == {'pid': value['pointer']['focusedPid'], 'started': value['pointer']['focusedStarted']}
                        proofs.append(proof)
                        revisions.append(proof['revision'])
                        observations += 1
                assert len(proofs) == 3
                assert all(proofs[0][k] == proofs[1][k] == proofs[2][k]
                           for k in ('viewId', 'surfaceId', 'output', 'corners', 'destination'))
        assert receipts == 80 and observations == 120 and gestures == 40
        assert revisions == sorted(set(revisions))
        assert len(native['pixelCaptures']) == 16 and all(c['passed'] is True for c in native['pixelCaptures'])
        report.update(passed=True, nativeChecks=285, stages=8, gestures=gestures,
                      helperReceipts=receipts, parentObservations=observations, pixelCaptures=16, current470BoundedAccepted=True, nonzeroCapabilityAccepted=False,
                      scope='Exact core470/plugin471/AQ155 + parent225, zero ordinary/MAX/restore and nonzero ordinary only, buffer scales1/2, monitor scale1; synthetic native seat input only',
                      files=closure)
    except Exception as error:
        report.update(error=repr(error), files=closure)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': str(out / 'report.json'), 'files': len(closure)}))
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
