#!/usr/bin/env python3
"""Read-only independent source/private-lifetime audit of a terminal pointer run."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    path = Path('/proc') / str(row['pid']) / 'stat'
    return not path.exists() or path.read_text().rsplit(')', 1)[1].split()[19] != str(row['start'])


def main():
    base = Path(sys.argv[1]).resolve(); attempt = Path(sys.argv[2]).resolve()
    expected = Path('/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor')
    assert base.parent == expected and base.name.startswith('pointer-private-host-v')
    assert attempt.parent == base and attempt.name.startswith('native-pointer-attempt-')
    report = attempt / 'native-pointer-report.json'
    d = json.loads(report.read_text()); m = json.loads((base / 'pointer-frozen-stage-report.json').read_text())
    h = d['hostEvidence']
    rows = d['ownedFixtureProcesses'] + d.get('unexpectedPrivateClientSurvivors', [])
    rows += [h[k] for k in ('privateBus', 'weston', 'hyprland')]
    rows += h.get('observedDescendantIdentities', [])
    rows = list({(r['pid'], str(r['start'])): r for r in rows}.values())
    checks = {
        'originalFrozenSourcesExact': all(sha(base / k) == v for k, v in m['dependencies'].items()),
        'copiedFrozenSourcesExact': all(sha(attempt / k) == v for k, v in m['dependencies'].items()),
        'externalFrozenSourcesExact': all(sha(k) == v for k, v in m['externalDependencies'].items()),
        'externalFrozenLinksExact': all(Path(k).is_symlink() and os.readlink(k) == v for k, v in m['externalSymlinks'].items()),
        'all19MainPreservationChecks': len(d['restoration']) == 19 and all(d['restoration'].values()),
        'normalQuiescentNativeUnload': d.get('cleanupUnloadQuiescent') is True and d.get('cleanupNormalUnloadResult') == 'ok' and not d.get('cleanupUnloadError'),
        'exactAllRecordedIdentitiesGone': all(gone(r) for r in rows),
        'ownedRuntimeGone': h['runtimeGone'] and not Path(h['runtime']).exists(),
        'normalHostCleanup': not any(h[k] for k in ('cleanupErrors', 'remainingDescendants', 'unexpectedInnerDescendants')),
        'archivedParentTransportHealthy': any(c['name'] == 'actual complete campaign archived parent transport stayed healthy' and c['pass_'] for c in d['checks']),
    }
    helper_gates = [c for c in d['checks'] if 'normal client shutdown has no activated or leaked private helpers' in c['name'] or c['name'] == 'terminal normal private client cleanup has no unexpected helper processes']
    full = d.get('result') == 'pass' and all(checks.values()) and not d.get('failures')
    full = full and len(helper_gates) == 4 and all(c['pass_'] and not c['unexpected'] and not c['portalActivations'] for c in helper_gates)
    full = full and len(d['phases']) == 3 and all(p['pass_'] and p['checks'] > 0 for p in d['phases'])
    full = full and all(c['pass_'] for c in d['checks']) and d['nativePointerProved'] and d['nativeInputProved']
    row = {'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'reportSHA256': sha(report), 'scope': h['qaScope'],
           'allIndependentSafetySourceAndCleanupChecks': all(checks.values()), 'independentChecks': checks,
           'sourceCounts': {'local': len(m['dependencies']), 'external': len(m['externalDependencies']), 'links': len(m['externalSymlinks'])},
           'normalFixtureLifecycleAccepted': bool(full), 'fullPrivateCampaignAccepted': bool(full),
           'nativePointerAccepted': bool(full and d['nativePointerProved']),
           'nativeKeyboardAccepted': bool(full and d['nativeInputProved']),
           'checksReached': len(d['checks']), 'checksPassed': sum(c['pass_'] for c in d['checks']),
           'phases': d['phases'], 'helperGates': helper_gates,
           'processes': [{'pid': r['pid'], 'start': r['start'], 'gone': gone(r)} for r in rows],
           'fullWindowsParityAccepted': False, 'physicalHardwareAccepted': False,
           'productionDeployment': False, 'failures': d.get('failures', [])}
    path = attempt / 'root-completion.json'
    with path.open('x') as output:
        json.dump(row, output, indent=2); output.write('\n')
    path.chmod(0o600)
    print(json.dumps({'artifact': str(path), 'allIndependentChecks': all(checks.values()),
                      'fullPrivateCampaignAccepted': bool(full), 'sourceCounts': row['sourceCounts']}))
    return int(not all(checks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
