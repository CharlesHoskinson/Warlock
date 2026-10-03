#!/usr/bin/env python3
"""Read-only, independent frozen-input/private-cleanup audit after terminal Qt run."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    path = Path('/proc') / str(row['pid']) / 'stat'
    if not path.exists():
        return True
    text = path.read_text()
    return text[text.rindex(')')+2:].split()[19] != str(row['start'])


def main():
    base = Path(sys.argv[1]).resolve()
    attempt = Path(sys.argv[2]).resolve()
    assert base.parent == Path('/home/hoskinson/window-integration-qa')
    assert base.name.startswith(('qt-modal-private-v', 'qt-modal-private-x11-v')) and attempt.parent == base
    report = json.loads((attempt/'report.json').read_text())
    host = report['cleanup']['host']
    toolkit = json.loads((attempt/'qt/report.json').read_text())
    manifest = json.loads((base/'frozen-inputs.json').read_text())
    identities = [host[key] for key in ('privateBus', 'weston', 'hyprland')]
    identities += [toolkit[key] for key in ('fixtureCleanup', 'pointerCleanup')]
    if 'motionCleanup' in toolkit:
        identities.append(toolkit['motionCleanup'])
    if 'x11' in host:
        identities.append(host['x11']['server'])
    identities += host.get('observedDescendantIdentities', [])
    processes = [{'pid': row['pid'], 'start': row['start'], 'gone': gone(row)} for row in identities]
    sys.path.insert(0, str(base))
    spec = importlib.util.spec_from_file_location('audited_qt_runner', base/'run_native.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    archives = [Path(row['archive']) for row in host['archivedRuntime']
                if Path(row['archive']).name == 'hyprland.log']
    assert len(archives) == 1
    logs = [archives[0], attempt/'host/weston-renderer.log']
    transport = module.transport_log_gate([path.read_text() for path in logs])
    checks = {
        'allFrozenFilesExact': all(sha(row['path']) == row['sha256'] for row in manifest['files']),
        'allFrozenLinksExact': all(Path(row['path']).is_symlink() and os.readlink(row['path']) == row['target'] for row in manifest['symlinks']),
        'all18MainPreservationChecks': len(report['mainPreservation']) == 18 and all(report['mainPreservation'].values()),
        'normalOwnedFixtureShutdown': all(toolkit['preservation'].values()),
        'normalOwnedProcessExitCodes': all(toolkit[k].get('exitCode') == 0 and not any(toolkit[k].get(f) for f in ('error', 'forcedTermination', 'forcedKill'))
                                          for k in ('fixtureCleanup', 'pointerCleanup', 'motionCleanup') if k in toolkit),
        'privateClientsGoneBeforeUnload': report['cleanup']['privateClientsBeforeUnload'] == [],
        'bothNativeModulesUnloadedNormally': report['cleanup']['probeUnloadedNormally'] and report['cleanup']['pluginUnloadedNormally'],
        'allRecordedProcessIdentitiesGone': all(row['gone'] for row in processes),
        'privateRuntimeGone': host['runtimeGone'] and not Path(host['runtime']).exists(),
        'noCleanupErrorsOrUnexpectedSurvivors': not any(host[key] for key in ('cleanupErrors', 'unexpectedInnerDescendants', 'remainingDescendants')),
        'archivedParentTransportHealthy': transport['passed'],
    }
    if 'x11' in host:
        x11 = host['x11']
        setups = x11['readOnlySetup']
        checks.update({
            'normalXwaylandDisconnectAndCredentialCleanup': host['x11ServerGoneOnCompositorDisconnect'] and host['x11DisplayArtifactsGone'] and not host['x11CredentialCleanupErrors'],
            'privateDisplayArtifactsActuallyGone': all(not Path(p).exists() for p in ('/tmp/.X' + x11['display'][1:] + '-lock', '/tmp/.X11-unix/X' + x11['display'][1:], '/tmp/.X11-unix/X' + x11['display'][1:] + '_')),
            'actualAuthRefusalAndAcceptance': len(setups) == 2 and setups[0]['kind'] == 'unauthenticated' and setups[0]['status'] == 0 and setups[1]['kind'] == 'authenticated' and setups[1]['status'] == 1 and setups[1]['major'] == 11,
            'actualXcbLoaderAndAllToolkitGates': len(report['x11ProtocolGates']) == 1 and all(r['passed'] for r in report['x11ProtocolGates']) and len(report['toolkitFeatureGates']) == 19 and all(r['passed'] for r in report['toolkitFeatureGates']),
        })
    completion = {
        'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reportSHA256': sha(attempt/'report.json'),
        'frozenFileCount': len(manifest['files']), 'frozenLinkCount': len(manifest['symlinks']),
        'scope': host['qaScope'], 'independentChecks': checks,
        'allIndependentChecks': all(checks.values()), 'processes': processes,
        'archivedTransport': transport, 'logHashes': {str(path): sha(path) for path in logs},
        'toolkitAccepted': report['result'] == 'pass',
        'toolkitFailure': report.get('error'), 'fullWindowsParityAccepted': False,
    }
    path = attempt/'root-completion.json'
    with path.open('x') as output:
        json.dump(completion, output, indent=2); output.write('\n')
    path.chmod(0o600)
    print(json.dumps({'artifact': str(path), 'allIndependentChecks': completion['allIndependentChecks'],
                      'toolkitAccepted': completion['toolkitAccepted']}))
    return int(not completion['allIndependentChecks'])


if __name__ == '__main__':
    raise SystemExit(main())
