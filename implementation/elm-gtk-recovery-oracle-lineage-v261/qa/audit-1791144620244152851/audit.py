"""Recover actual 08/09/10 oracle provenance; no GUI or acceptance transfer."""
import ast
import hashlib
import json
import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    require_qa_scope()
    assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
    out = ROOT / 'qa' / ('audit-' + str(time.time_ns()))
    out.mkdir()
    report = {'passed': False, 'nativeAcceptance': False,
              'currentTupleQualified': False, 'records': [], 'checks': []}

    def check(name, value):
        report['checks'].append({'name': name, 'passed': bool(value)})
        assert value, name

    try:
        for name, run, passed, count in [
            ('elm-geometry-family-menu-receipt-cleanup-native-v100',
             '1791110259133139744', False, 159),
            ('elm-geometry-lifetime-retirement-native-v432',
             '1791129443414985239', True, 161),
        ]:
            base = REPO / 'implementation' / name
            source = base / 'qa/native.py'
            result = base / 'qa' / ('native-' + run) / 'report.json'
            data = json.loads(result.read_text())
            check(name + ':actualReportedSource',
                  data['inputs'][str(source)] == sha(source))
            check(name + ':historicalOutcome', data['passed'] is passed
                  and len(data['checks']) == count
                  and data['cleanupPassed'] is True
                  and data['nativeAcceptance'] is False)
            captured = out / name
            captured.mkdir()
            for path in [source, result]:
                (captured / path.name).write_bytes(path.read_bytes())
            body = source.read_text()
            start = body.index('    # Reconnect occurs after a saved native MAX origin exists.')
            end = body.index("    report['scenarios'].append('GEOMETRY-MENU-10')", start)
            end = body.index('\n', end)
            region = body[start:end]
            (captured / 'geometry08-09-10.txt').write_text(region)
            tree = ast.parse(source.read_text())
            names = [node.args[0].value for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name) and node.func.id == 'check'
                     and node.args and isinstance(node.args[0], ast.Constant)
                     and isinstance(node.args[0].value, str)]
            required = [
                'reconnectQuiescentBeforeEOF', 'reconnectOwnedBrokerNormalEOF',
                'reconnectNoNativeEffectDuringDisconnect',
                'reconnectRenegotiatesPreservingSavedOriginNoReplay',
                'heldReceiptIsActualFullCommittedKey',
                'heldNativeRestoreCommittedBeforeDelivery',
                'heldRealNotificationWhilePending', 'heldNoDuplicateDispatch',
                'heldExactOriginalReceiptReleasedOnce',
                'heldNativePopupRetiredBeforeEffectQueue',
                'retirementNeverTargetsSameTitleReplacement',
            ]
            actual = {r['name']: r['passed'] for r in data['checks']}
            for obligation in required:
                check(name + ':source:' + obligation, obligation in names)
                # Original100 times out during10; its source oracle still remains required.
                if passed or obligation != 'retirementNeverTargetsSameTitleReplacement':
                    check(name + ':executed:' + obligation, actual.get(obligation) is True)
            check(name + ':originalAbsoluteDeadline',
                  'deadline=time.monotonic()+6' in region
                  and "report['scenarios'].append('GEOMETRY-MENU-08')" in region
                  and "report['scenarios'].append('GEOMETRY-MENU-09')" in region)
            report['records'].append({
                'source': str(source), 'sourceSHA256': sha(source),
                'historicalReport': str(result), 'reportSHA256': sha(result),
                'historicalPassed': passed, 'reachedChecks': count,
                'scenarioRegionSHA256': sha(captured / 'geometry08-09-10.txt'),
                'historicalTuple': data.get('pair'),
                'requiredCheckNames': required,
            })
        origin = REPO / 'implementation/elm-geometry-lifetime-retirement-native-v432/origin.json'
        metadata = json.loads(origin.read_text())
        check('432ExplicitOriginal100Lineage',
              metadata['parent'].endswith('/elm-geometry-family-menu-receipt-cleanup-native-v100'))
        (out / 'origin432.json').write_bytes(origin.read_bytes())
        report['originSHA256'] = sha(origin)
        report['passed'] = True
    finally:
        (out / 'audit.py').write_bytes(Path(__file__).read_bytes())
        report['sourceSHA256'] = sha(__file__)
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json')


if __name__ == '__main__':
    main()
