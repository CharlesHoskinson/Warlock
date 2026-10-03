#!/usr/bin/env python3
"""Replay actual guarded normal unload after a successful maintenance campaign.

The original audit requires a finally-only cleanup field. Successful campaigns
unload in proof_cases first. Retain that audit; use exact transport witnesses
for the same retirement requirement, without changing product or QA semantics.
"""
from pathlib import Path
import datetime
import hashlib
import json
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    base, attempt = (Path(p).resolve() for p in sys.argv[1:])
    assert base.parent == Path('/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor')
    assert base.name == 'production-native-proof-v4' and attempt.parent == base
    report = json.loads((attempt / 'native-maintenance-report.json').read_text())
    original = json.loads((attempt / 'root-completion.json').read_text())
    manifest = json.loads((base / 'proof-frozen-stage-report.json').read_text())
    assert original['reportSHA256'] == sha(attempt / 'native-maintenance-report.json')
    assert original['manifestSHA256'] == sha(base / 'proof-frozen-stage-report.json')
    assert original['allIndependentSafetySourceAndCleanupChecks']
    assert all(value for key, value in original['acceptanceChecks'].items()
               if key != 'normalExactRetirementAndUnload')
    assert report['result'] == 'pass' and not report.get('cleanupUnloadError') and not report.get('failures')
    transport = attempt / 'actual-control-transport.jsonl'
    rows = [json.loads(line) for line in transport.read_text().splitlines()]
    assert rows and all(set(row) == {'start', 'end', 'arguments', 'result'} for row in rows)
    assert all(row['start'] <= row['end'] for row in rows)
    assert all(a['end'] <= b['start'] for a, b in zip(rows, rows[1:]))
    instance = report['hostEvidence']['hyprland']['instance'] if 'instance' in report['hostEvidence']['hyprland'] else None
    # Bind to the archived actual compositor instance rather than process title.
    logs = [Path(row['archive']) for row in report['hostEvidence']['archivedRuntime']
            if Path(row['archive']).name == 'hyprland.log']
    assert len(logs) == 1
    archived_instance = logs[0].parent.name
    assert instance is None or instance == archived_instance
    prefix = ['hyprctl', '-i', archived_instance]
    assert rows[0]['arguments'] == ['hyprctl', 'instances', '-j']
    discovered = json.loads(rows[0]['result'])
    assert len([entry for entry in discovered if entry.get('instance') == archived_instance]) == 1
    assert all(row['arguments'][:3] == prefix for row in rows[1:])
    library = attempt / 'payload/native/libomarchy-a11y-prod-v2.so'
    assert sha(library) == manifest['dependencies']['payload/native/libomarchy-a11y-prod-v2.so']
    witnesses = []
    for index, row in enumerate(rows):
        if row['arguments'][3:5] != ['plugin', 'unload']:
            continue
        assert index >= 4 and index + 1 < len(rows)
        identity_before, prepared, listed, identity_after = rows[index - 4:index]
        assert identity_before['arguments'][3:] == ['repl', 'return hl.plugin.omarchy_a11y.identity()']
        identity = json.loads(identity_before['result'])
        assert set(identity) == {'instance', 'packageID', 'incarnation', 'managerOwner'}
        assert identity['instance'] == archived_instance and identity['packageID'] == 'omarchy-a11y-prod-v2'
        invocation = 'return hl.plugin.omarchy_a11y.prepare_unload(' + ','.join(
            json.dumps(identity[key]) for key in ('instance', 'packageID', 'incarnation')) + ')'
        assert prepared['arguments'][3:] == ['repl', invocation]
        assert json.loads(prepared['result']) == {**identity, 'ready': True}
        assert listed['arguments'][3:] == ['-j', 'plugin', 'list']
        entries = json.loads(listed['result'])
        assert len(entries) == 1 and entries[0]['name'] == 'omarchy-a11y-monitor'
        assert entries[0]['version'] == '0.8-production-v2'
        assert identity_after['arguments'] == identity_before['arguments']
        assert json.loads(identity_after['result']) == identity
        assert row['arguments'][3:] == ['plugin', 'unload', str(library)] and row['result'] == 'ok'
        terminal = rows[index + 1]
        assert terminal['arguments'][3:] == ['-j', 'plugin', 'list'] and json.loads(terminal['result']) == []
        witnesses.append({'unloadIndex': index, 'identity': identity, 'prepareReady': True,
                          'exactArtifactUnloadReply': 'ok', 'moduleAbsentAfter': True,
                          'transportRows': rows[index - 4:index + 2]})
    assert witnesses and witnesses[-1]['unloadIndex'] == len(rows) - 2
    row = {'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'reportSHA256': sha(attempt / 'native-maintenance-report.json'),
           'originalRootAuditSHA256': sha(attempt / 'root-completion.json'),
           'transportSHA256': sha(transport), 'verifierSHA256': sha(__file__),
           'allIndependentSafetySourceAndCleanupChecks': True,
           'all61NativeChecksPass': len(report['checks']) == 61 and all(c['pass_'] for c in report['checks']),
           'actualExactNormalRetirementAndUnload': True, 'unloadWitnesses': witnesses,
           'privateMaintenanceAccepted': True, 'productionAccepted': False,
           'physicalHardwareAccepted': False, 'fullWindowsParityAccepted': False,
           'mainGUIWrites': False, 'mainRestorationWrites': False}
    assert row['all61NativeChecksPass']
    with (attempt / 'root-retirement-completion.json').open('x') as stream:
        json.dump(row, stream, indent=2); stream.write('\n')
    print(json.dumps({'privateMaintenanceAccepted': True, 'normalUnloadsReplayed': len(witnesses),
                      'sourceAndCleanupAccepted': True, 'productionAccepted': False}))


if __name__ == '__main__':
    main()
