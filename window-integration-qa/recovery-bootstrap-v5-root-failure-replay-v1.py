"""Independent read-only classification of the failed original V5 baseline."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

QA = Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope

B = QA / 'family-recovery-bootstrap-v5'
A = B / 'attempt-baseline-1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lifetime(pid):
    try:
        return int(Path(f'/proc/{pid}/stat').read_text().rsplit(')', 1)[1].split()[19])
    except FileNotFoundError:
        return None


def main():
    scope = require_qa_scope()
    report = json.loads((A / 'report.json').read_text())
    helpers = json.loads((A / 'completed-helpers.json').read_text())
    terminal = json.loads((A / 'actual-terminal-binding.json').read_text())
    before = json.loads((A / 'actual-modules-before.json').read_text())
    owner = json.loads((A / 'actual-owner-binding.json').read_text())
    retirement = json.loads((A / 'service-retirement-1.json').read_text())
    checks = []

    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    manifest = json.loads((B / 'frozen-inputs.json').read_text())
    check('Frozen descriptor matches reviewed V5', sha(B / 'frozen-inputs.json') == 'bbd142db7116de7e076df508dcb6d9b57ceda4d6cc5035cec7da6a5867b2e492')
    check('All frozen input hashes and modes remain exact', all(sha(p) == h and stat.S_IMODE(Path(p).stat().st_mode) == manifest['inputModes'][p] for p, h in manifest['inputs'].items()))
    check('All frozen links remain exact', all(Path(p).is_symlink() and os.readlink(p) == target for p, target in manifest['symlinks'].items()))
    check('Original baseline remains rejected after eleven completed gates', report['result'] == 'fail' and len(report['checks']) == 11 and all(c['passed'] for c in report['checks']) and not report['fullContractAccepted'] and not report['fullWindowsParityAccepted'])
    check('Required renderer seed and upload failure retained', 'Actual family renderer seed and uploads required' in report['error'])
    host = report['hostEvidence']
    aq = host['privateAquamarine']
    check('Actual repaired Aquamarine mapped, not merely selected', aq['sha256'] == '4ee1f9958ec83a9d2774f760ba66f90f1d646d1c198dd49d9dfbf1763c2fd296' and host['hyprlandMaps']['files'].get(aq['path']) == aq['sha256'])
    check('One actual startup readiness query', len(host['ipcReadiness']) == 1)
    check('Actual service source and owner tokens retained equal', terminal['moduleToken'] == before['moduleToken'] and terminal['ownerToken'] == owner['ownerToken'])
    sources = retirement['retainedEpochSources']
    check('Three distinct actual captures with unchanged declared bytes', len(sources) == 3 and len({tuple(s['source'][k] for k in ('stableId', 'pid')) for s in sources}) == 3 and all(sha(s['retainedPath']) == s['sha256'] == s['source']['digest'] and Path(s['retainedPath']).stat().st_size == s['bytes'] and s['captureCallbackDelegatedOnce'] and s['sourceResultUnchanged'] for s in sources))
    history = retirement['history']
    record = history[0]
    check('Actual history shows no seeded sources and controller deadline', len(history) == 1 and record['sources'] == [] and record['profile']['settlementReason'] == 'controller deadline' and not any(e.get('event') in ('seeded', 'sourceUploaded', 'presented') for e in retirement['rendererEvents']))
    rows = terminal['ledger']['history']
    refused = [r for r in rows if r['outcome'] == 'refused']
    complete = [r for r in rows if r['outcome'] == 'complete']
    check('Incomplete query archive correctly remains unusable', len(rows) == 41 and len(complete) == 40 and len(refused) == 1 and not terminal['usable'] and any(e['message'] == 'complete closed actual query proof required' for e in terminal['errors']))
    check('Actual refused housekeeping query and absolute deadline retained', refused[0]['actor'] is None and refused[0]['request'] == 'j/clients' and refused[0]['closed'] and refused[0]['published'] and refused[0]['error']['type'] == 'TimeoutError')
    starts = [e for e in helpers['events'] if e['event'] == 'started']
    ends = [e for e in helpers['events'] if e['event'] == 'terminal']
    harness = [e for e in starts if e.get('queryRoot') == 'harness']
    check('Harness-query count failure is zero, not an excess query', len(harness) == 0 and helpers['result'] == 'fail' and helpers['reason'] == 'Exactly one harness query required')
    missing = [e for e in starts if not any(t['operation'] == e['operation'] for t in ends)]
    check('Three missing terminal helper records prevent normal completion claim', len(starts) == 22 and len(ends) == 19 and len(missing) == 3 and all(e['operation'].startswith('forget-closed:') for e in missing))
    identities = [e[k] for e in starts for k in ('wrapper', 'delegate')]
    identities += report['processes']
    check('Every recorded helper and client lifetime actually absent now', all(lifetime(i['pid']) != int(i['start']) for i in identities))
    check('Native unload and private teardown recorded without leftover runtime', report['normalNativeUnload'] and host['runtimeGone'] and not Path(host['runtime']).exists() and host['remainingDescendants'] == [] and host['unexpectedInnerDescendants'] == [] and host['cleanupErrors'] == [])
    check('Observer exit one prevents a normal-service cleanup claim', report['clientCleanup']['family-service']['exitCode'] == 1 and report['clientCleanup']['family-service']['gone'])
    preserved = report['mainPreservation']
    check('No main writes; unclassified layer mismatch remains a failed preservation item', not report['mainGUIWrites'] and not report['mainRestorationWrites'] and preserved['originalLayers'] is False and sum(v is True for v in preserved.values()) == 14)
    durations = [(r['finishedNs'] - r['registeredNs']) / 1e6 for r in complete]
    result = {
        'result': 'pass', 'scope': scope, 'checks': checks,
        'classification': 'Independent failure replay; original native baseline FAIL',
        'originalBaselineAccepted': False, 'fullWindowsParityAccepted': False,
        'allNativeHelpersNormal': False, 'normalServiceClosure': False,
        'mainPreservationAccepted': False, 'mainWrites': False,
        'metadataDurationMs': (record['profile']['metadataValidatedNs'] - record['profile']['metadataStartNs']) / 1e6,
        'completeReadonlyQueryCount': len(complete),
        'completeReadonlyQueryMeanMs': sum(durations) / len(durations),
        'completeReadonlyQueryMaxMs': max(durations),
        'refusedQuery': refused, 'missingHelperTerminals': missing,
        'individualPreparationCause': 'Unclassified; no full phase timing trace exists in this run',
        'inputs': {str(p): sha(p) for p in (B / 'frozen-inputs.json', A / 'report.json', A / 'completed-helpers.json', A / 'actual-terminal-binding.json', A / 'service-retirement-1.json')},
        'replaySourceSHA256': sha(__file__),
    }
    destination = QA / 'recovery-bootstrap-v5-root-failure-replay-v1.json'
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(result, stream, indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    print(json.dumps({'result': result['result'], 'checks': len(checks), 'originalBaselineAccepted': False, 'artifact': str(destination)}))


if __name__ == '__main__':
    main()
