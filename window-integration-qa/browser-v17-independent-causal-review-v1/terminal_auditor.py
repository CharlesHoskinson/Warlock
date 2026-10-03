#!/usr/bin/env python3
"""Read-only terminal Browser/Files evidence audit; never contacts a desktop."""
from pathlib import Path
import base64
import datetime
import hashlib
import importlib.util
import json
import os
import stat
import sys
import xml.etree.ElementTree as ET


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    try:
        raw = Path('/proc', str(row['pid']), 'stat').read_text()
    except FileNotFoundError:
        return True
    return raw[raw.rindex(')') + 2:].split()[19] != str(row['start'])


def main():
    base, attempt = (Path(p).resolve() for p in sys.argv[1:])
    assert base.parent == Path('/home/hoskinson/window-integration-qa')
    assert base.name.startswith('browser-files-flow-v') and attempt.parent == base
    report = json.loads((attempt / 'report.json').read_text())
    flow = json.loads((attempt / 'flow/report.json').read_text())
    manifest = json.loads((base / 'frozen-inputs.json').read_text())
    host = report['cleanup']['host']
    identities = host['observedDescendantIdentities'] + [host[k] for k in ('privateBus', 'weston', 'hyprland')]
    identities += flow['registeredDescendants'] + list(flow['processRoots'].values())
    processes = [{'pid': r['pid'], 'start': r['start'], 'gone': gone(r)} for r in identities]
    sys.path.insert(0, str(base))
    spec = importlib.util.spec_from_file_location('_browser_terminal_audit', base / 'run_native.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    archives = [r for r in host['archivedRuntime'] if Path(r['archive']).name == 'hyprland.log']
    assert len(archives) == 1 and sha(archives[0]['archive']) == archives[0]['sha256']
    logs = [Path(archives[0]['archive']), attempt / 'host/weston-renderer.log']
    transport = module.transport_log_gate([p.read_text() for p in logs])
    policy = host['privateBusActivationPolicy']
    xml = policy['actualConfigXml'].encode()
    root = ET.fromstring(xml)
    forbidden = {'include', 'includedir', 'servicedir', 'standard_session_servicedirs', 'standard_system_servicedirs', 'servicehelper'}
    bus_ok = (hashlib.sha256(xml).hexdigest() == policy['sha256']
              and not any(node.tag in forbidden for node in root.iter())
              and [node.text for node in root.iter('listen')] == ['unix:path=' + host['runtime'] + '/bus']
              and policy['peer']['pid'] == host['privateBus']['pid']
              and policy['peer']['uid'] == os.getuid()
              and policy['activatableNames'] == ['org.freedesktop.DBus']
              and policy['queryExit'] == 0 and not policy['mainBusChanges'])
    environment = json.loads((attempt / 'flow/app-environment-evidence.json').read_text())
    assert environment == flow['actualAppEnvironmentEvidence']
    observations = []
    for name, evidence in environment.items():
        raw = base64.b64decode(evidence['rawInitialRangeBase64'], validate=True)
        assert len(raw) == evidence['rawInitialRangeBytes']
        assert hashlib.sha256(raw).hexdigest() == evidence['rawInitialRangeSHA256']
        values = dict(item.split(b'=', 1) for item in raw.split(b'\0') if b'=' in item)
        selected = {key: values[key.encode()].decode('utf-8', errors='backslashreplace') if key.encode() in values else None for key in evidence['selectedVariables']}
        assert selected == evidence['selectedValues']
        assert (selected == evidence['expectedValues']) == evidence['initialRangeMatches']
        assert evidence['identity'] == flow['processRoots'][name]
        assert evidence['lifetimeBefore'] and evidence['lifetimeAfter'] and not evidence.get('readError')
        observations.append({'name': name, 'identity': evidence['identity'], 'bytes': len(raw),
                             'nonzeroBytes': sum(byte != 0 for byte in raw),
                             'initialRangeMatches': evidence['initialRangeMatches'],
                             'currentLibcSelectorsProved': False})
    checks = {
        'allFrozenBytesModesExact': all(sha(r['path']) == r['sha256'] and stat.S_IMODE(Path(r['path']).stat().st_mode) == r['mode'] for r in manifest['files']),
        'allFrozenLinksExact': all(Path(r['path']).is_symlink() and os.readlink(r['path']) == r['target'] for r in manifest['symlinks']),
        'all18MainPreserved': len(report['mainPreservation']) == 18 and all(report['mainPreservation'].values()),
        'allRecordedPIDStartGone': all(r['gone'] for r in processes),
        'privateRuntimeGone': host['runtimeGone'] and not Path(host['runtime']).exists(),
        'noUnexpectedOrRemainingHelpers': not any(host[k] for k in ('unexpectedInnerDescendants', 'remainingDescendants', 'cleanupErrors')),
        'normalBrowserAndNoForcedCleanup': all(flow['preservation'].values()) and not flow['remainingOwnedDescendants'] and not flow['survivorsBeforeFallback'],
        'nativeProbeAndPluginUnloadedNormally': report['cleanup']['privateClientsBeforeUnload'] == [] and report['cleanup']['probeUnloadedNormally'] and report['cleanup']['pluginUnloadedNormally'],
        'healthyArchivedParentTransport': transport['passed'],
        'actualPrivateBusActivationPolicyVerified': bus_ok,
        'initialRangeDiagnosticIndependentlyReplayed': bool(observations),
    }
    proof_path = attempt / 'flow/actual-browser-bus-authority.json'
    if proof_path.exists():
        proof = json.loads(proof_path.read_text())
        assert proof == flow['actualBrowserBusAuthority']
        launch = json.loads((attempt / 'flow/browser-exec.json').read_text())
        spec = importlib.util.spec_from_file_location('_browser_bus_audit', base / 'bus_authority.py')
        bus_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bus_module)
        assert proof['preExecWitness'] == bus_module.selected_preexec(launch, proof['root'], Path(host['runtime']))
        assert proof['root'] == flow['processRoots']['browser']
        assert proof['bus'] == host['privateBus']
        assert proof['rootLifetimeBefore'] and proof['rootLifetimeAfter']
        names = []
        pids, uids = {}, {}
        for query in proof['queries']:
            method, args = query['method'], query['arguments']
            expected = ['/usr/bin/gdbus', 'call', '--address', 'unix:path=' + host['runtime'] + '/bus',
                        '--dest', 'org.freedesktop.DBus', '--object-path', '/org/freedesktop/DBus',
                        '--method', 'org.freedesktop.DBus.' + method, *args]
            assert query['command'] == expected and query['returncode'] == 0
            assert query['peer']['pid'] == host['privateBus']['pid'] and query['peer']['uid'] == os.getuid()
            value = bus_module.parse_reply(method, query['stdout'])
            assert value == query['parsed']
            if method == 'ListNames':
                assert args == [] and not names
                names = value
            else:
                assert len(args) == 1 and args[0] in names
                (pids if method == 'GetConnectionUnixProcessID' else uids)[args[0]] = value
        connection = proof['connection']
        assert connection['name'] in names
        assert connection['pid'] == pids[connection['name']] == proof['root']['pid']
        assert connection['uid'] == uids[connection['name']] == os.getuid()
        checks['actualBrowserPrivateBusPIDBindingIndependentlyReplayed'] = proof['result'] == 'pass'
    accepted = (all(checks.values()) and report['result'] == 'pass'
                and len(report['toolkitFeatureGates']) == manifest['featureGates']
                and all(r['passed'] for r in report['toolkitFeatureGates'])
                and len(report['hostChecks']) == manifest['hostGates']
                and all(r['passed'] for r in report['hostChecks']))
    result = {'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'reportSHA256': sha(attempt / 'report.json'), 'manifestSHA256': sha(base / 'frozen-inputs.json'),
              'fileCount': len(manifest['files']), 'linkCount': len(manifest['symlinks']),
              'independentChecks': checks, 'allIndependentSafetySourceAndCleanupChecks': all(checks.values()),
              'privateBrowserFilesAccepted': accepted, 'processes': processes, 'transport': transport,
              'environmentObservations': observations, 'failure': flow.get('error'),
              'rawOwnedProcessEvidenceSHA256': sha(attempt / 'flow/owned-process-evidence.json'),
              'mainGUIWrites': False, 'mainRestorationWrites': False, 'fullWindowsParityAccepted': False}
    target = Path('/home/hoskinson/window-integration-qa/browser-v17-independent-causal-review-v1/terminal-audit.json')
    with target.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    target.chmod(0o600)
    print(json.dumps({'artifact': str(target), 'allIndependentChecks': all(checks.values()),
                      'browserFilesAccepted': accepted, 'environmentObservations': observations}))
    return int(not all(checks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
