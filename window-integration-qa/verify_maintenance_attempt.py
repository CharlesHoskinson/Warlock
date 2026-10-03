#!/usr/bin/env python3
"""Independent terminal maintenance source/mode/main/lifetime audit, read only."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    try:
        raw=Path('/proc',str(row['pid']),'stat').read_text()
    except FileNotFoundError:
        return True
    return raw.rsplit(')',1)[1].split()[19]!=str(row['start'])


def main():
    base,attempt=(Path(p).resolve() for p in sys.argv[1:])
    assert base.parent==Path('/home/hoskinson/window-integration-qa/recovery-audit/keyboard-monitor')
    assert base.name.startswith('production-native-proof-v') and attempt.parent==base and attempt.name.startswith('native-maintenance-attempt-')
    manifest=json.loads((base/'proof-frozen-stage-report.json').read_text())
    report=attempt/'native-maintenance-report.json';d=json.loads(report.read_text());h=d['hostEvidence']
    rows=d.get('ownedFixtureProcesses',[])+h.get('observedDescendantIdentities',[])+d.get('unexpectedPrivateClientSurvivors',[])
    rows += [h[k] for k in ('privateBus','weston','hyprland')]
    unique={(r['pid'],str(r['start'])):r for r in rows}
    checks={
        'allOriginalSourceBytesAndModesExact':all(sha(base/k)==v and (base/k).stat().st_mode&0o7777==manifest['dependencyModes'][k] for k,v in manifest['dependencies'].items()),
        'allCopiedSourceBytesAndModesExact':all(sha(attempt/k)==v and (attempt/k).stat().st_mode&0o7777==manifest['dependencyModes'][k] for k,v in manifest['dependencies'].items()),
        'allExternalSourceBytesAndModesExact':all(sha(k)==v and Path(k).stat().st_mode&0o7777==manifest['externalModes'][k] for k,v in manifest['externalDependencies'].items()),
        'allExternalLinksExact':all(Path(k).is_symlink() and os.readlink(k)==v for k,v in manifest['externalSymlinks'].items()),
        'all19MainPreservationChecks':len(d['restoration'])==19 and all(d['restoration'].values()),
        'allRecordedProcessIdentitiesGone':all(gone(r) for r in unique.values()),
        'privateRuntimeGone':h['runtimeGone'] and not Path(h['runtime']).exists(),
        'noUnexpectedOrRemainingDescendants':not any(h[k] for k in ('cleanupErrors','remainingDescendants','unexpectedInnerDescendants')) and not d.get('unexpectedPrivateClientSurvivors'),
        'archivedParentTransportHealthy':any(c['name']=='actual complete campaign archived parent transport stayed healthy' and c['pass_'] for c in d['checks']),
    }
    helper=[c for c in d['checks'] if c['name']=='terminal normal private client cleanup has no unexpected helper processes']
    checks['terminalNoHelperGate']=len(helper)==1 and helper[0]['pass_'] and not helper[0]['unexpected'] and not helper[0]['portalActivations']
    acceptance={
        'terminalCampaignPass':d.get('result')=='pass' and not d.get('failures'),
        'allNativeChecksPass':all(c['pass_'] for c in d['checks']),
        'actualMaintenanceProved':d.get('nativeMaintenanceProved') is True,
        'normalExactRetirementAndUnload':d.get('cleanupNormalUnloadResult')=='ok' and not d.get('cleanupUnloadError') and bool(d.get('cleanupNormalRetirement')),
    }
    disabled=[c for c in d['checks'] if c['name']=='actual disabled bootstrap refuses before Orca imports']
    row={'updatedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reportSHA256':sha(report),
         'manifestSHA256':sha(base/'proof-frozen-stage-report.json'),'sourceCounts':{'local':len(manifest['dependencies']),'external':len(manifest['externalDependencies']),'links':len(manifest['externalSymlinks'])},
         'independentChecks':checks,'allIndependentSafetySourceAndCleanupChecks':all(checks.values()),'acceptanceChecks':acceptance,
         'privateMaintenanceAccepted':all(checks.values()) and all(acceptance.values()),
         'disabledReaderImportRefusalAccepted':len(disabled)==1 and disabled[0]['pass_'],
         'checksReached':len(d['checks']),'checksPassed':sum(c['pass_'] for c in d['checks']),
         'processes':[{'pid':r['pid'],'start':r['start'],'gone':gone(r)} for r in unique.values()],
         'failures':d.get('failures',[]),'fullWindowsParityAccepted':False,'productionAccepted':False,
         'mainGUIWrites':False,'physicalHardwareAccepted':False}
    target=attempt/'root-completion.json'
    with target.open('x') as stream:json.dump(row,stream,indent=2);stream.write('\n')
    target.chmod(0o600)
    print(json.dumps({'artifact':str(target),'allIndependentChecks':all(checks.values()),'privateMaintenanceAccepted':row['privateMaintenanceAccepted'],'checksReached':row['checksReached'],'disabledReaderRefusalAccepted':row['disabledReaderImportRefusalAccepted']}))
    return int(not all(checks.values()))


if __name__=='__main__':raise SystemExit(main())
