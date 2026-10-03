#!/usr/bin/env python3
"""Read-only terminal family campaign audit; never contacts a desktop."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import stat
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    path = Path('/proc') / str(row['pid']) / 'stat'
    try:
        raw = path.read_text()
    except FileNotFoundError:
        return True
    return raw[raw.rindex(')') + 2:].split()[19] != str(row['start'])


def main():
    base, attempt = (Path(p).resolve() for p in sys.argv[1:])
    assert base.parent == Path('/home/hoskinson/window-integration-qa')
    assert base.name.startswith(('family-service-taskbar-v','family-continuous-reversal-v','family-continuous-c1-v')) and attempt.parent == base
    report = json.loads((attempt / 'report.json').read_text())
    manifest = json.loads((base / 'frozen-inputs.json').read_text())
    payload = json.loads((base / 'payload-manifest.json').read_text())
    host = report['hostEvidence']
    evidence = json.loads((attempt / 'service-evidence.json').read_text())
    identities = report['processes'] + host['observedDescendantIdentities']
    identities += [host[k] for k in ('privateBus', 'weston', 'hyprland')]
    identities += evidence['transports']
    processes = [{'pid': p['pid'], 'start': p['start'], 'gone': gone(p)} for p in identities]
    sys.path.insert(0, str(base.parent / 'qt-modal-private-v9'))
    spec = importlib.util.spec_from_file_location('_audit_qt', base.parent / 'qt-modal-private-v9/run_native.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    archives = [Path(r['archive']) for r in host['archivedRuntime'] if Path(r['archive']).name == 'hyprland.log']
    assert len(archives) == 1
    logs = [archives[0], attempt / 'host/weston-renderer.log']
    transport = module.transport_log_gate([p.read_text() for p in logs])
    preservation = {
        'allFrozenInputsExact': all(sha(p) == h for p, h in manifest['inputs'].items()),
        'allFrozenLinksExact': all(Path(p).is_symlink() and os.readlink(p) == t for p, t in manifest['symlinks'].items()),
        'allDeclaredFrozenModesExact': all(stat.S_IMODE(Path(p).stat().st_mode) == mode for p, mode in manifest.get('inputModes', {}).items()),
        'allProductionCopiesExact': all(sha(r['source']) == sha(base / 'payload' / r['relative']) == r['sha256'] for r in payload['copies']),
        'all15MainPreservationChecks': len(report['mainPreservation']) == 15 and all(report['mainPreservation'].values()),
        'allRecordedPIDStartIdentitiesGone': all(r['gone'] for r in processes),
        'privateRuntimeGone': host['runtimeGone'] and not Path(host['runtime']).exists(),
        'privateClientsGoneBeforeUnload': report['clientsBeforeUnload'] == [],
        'nativePluginUnloadedNormally': report.get('normalNativeUnload') is True,
        'noRemainingDescendantsOrCleanupErrors': not host['remainingDescendants'] and not host['cleanupErrors'],
        'archivedMandatoryParentTransportHealthy': transport['passed'],
    }
    acceptance = {
        'normalClientLifecycle': all(r.get('exitCode') == 0 and not any(r.get(k) for k in ('error', 'forcedTermination', 'forcedKill', 'evidenceFailure')) for r in report['clientCleanup'].values()),
        'noUnexpectedHelpers': not host['unexpectedInnerDescendants'],
        'allReachedProductChecksPass': all(r['passed'] for r in report['checks']),
        'terminalCampaignPass': report['result'] == 'pass',
    }
    row = {'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'reportSHA256': sha(attempt / 'report.json'), 'manifestSHA256': sha(base / 'frozen-inputs.json'),
           'inputCount': len(manifest['inputs']), 'linkCount': len(manifest['symlinks']),
           'scope': host['qaScope'], 'preservationChecks': preservation,
           'allPreservationChecks': all(preservation.values()), 'acceptanceChecks': acceptance,
           'privateBaselineAccepted': all(preservation.values()) and all(acceptance.values()),
           'processes': processes, 'transport': transport,
           'mainGUIWrites': False, 'mainRestorationWrites': False,
           'fullWindowsParityAccepted': False, 'physicalCadenceAccepted': False, 'rasterAccepted': False}
    target = attempt / 'root-completion.json'
    with target.open('x') as stream:
        json.dump(row, stream, indent=2)
        stream.write('\n')
    target.chmod(0o600)
    print(json.dumps({'artifact': str(target), 'allPreservationChecks': row['allPreservationChecks'],
                      'privateBaselineAccepted': row['privateBaselineAccepted']}))
    return int(not row['allPreservationChecks'])


if __name__ == '__main__':
    raise SystemExit(main())
