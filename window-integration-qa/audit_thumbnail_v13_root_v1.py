"""Review the completed causal native failure without launching or retrying it."""
import hashlib
import json
import os
from pathlib import Path
import stat
from collections import Counter

QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v13'
A=B/'attempt-baseline-1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    r=json.loads((A/'report.json').read_text())
    s=json.loads((A/'service-evidence.json').read_text())
    t=json.loads((A/'actual-preparation-timing.json').read_text())
    m=json.loads((B/'frozen-inputs.json').read_text())
    assert sha(B/'frozen-inputs.json')==r['sourceManifestSHA256']=='68a1996ac38b01635b0e91af59cf6c4214f6e4fe165446826f3f076e4b7662bf'
    for n,d in m['inputs'].items(): assert sha(n)==d and stat.S_IMODE(Path(n).stat().st_mode)==m['inputModes'][n]
    for n,target in m['symlinks'].items(): assert Path(n).is_symlink() and os.readlink(n)==target
    assert r['result']=='fail' and len(r['checks'])==19 and sum(c['passed'] for c in r['checks'])==17
    assert 'Actual complete native family restore' in r['error']
    assert len(r['mainPreservation'])==15 and all(r['mainPreservation'].values())
    assert r['normalNativeUnload'] and r['allFrozenInputsExact'] and not r['mainGUIWrites'] and not r['mainRestorationWrites']
    host=r['hostEvidence']
    assert host['runtimeGone'] and not host['remainingDescendants'] and not host['unexpectedInnerDescendants'] and not host['cleanupErrors']
    clients=r['clientCleanup']
    assert len(clients)==3 and all(v['exitCode']==0 and v['gone'] for v in clients.values())
    events=r['helperArchive']['events']
    started=[e for e in events if e['event']=='started']; terminal=[e for e in events if e['event']=='terminal']
    def key(e):return tuple(e['wrapper'][k] for k in ('pid','start','pgid','parent'))
    assert len(started)==len(terminal)==38
    assert Counter(map(key,started))==Counter(map(key,terminal)) and all(v==1 for v in Counter(map(key,started)).values())
    assert all(e['exitCode']==0 for e in terminal)
    for e in started:
        assert not Path('/proc',str(e['wrapper']['pid'])).exists()
    gate=next(c['evidence'] for c in r['checks'] if 'Every exact' in c['name'])
    assert gate['allNormal'] and gate['allExactProcessesGone'] and gate['allQueriesNormal']
    assert not s['failure'] and not s['serviceFailure'] and not s['causalSpanFailure'] and s['causalSpanTraceComplete']
    assert s['serviceClosed'] and s['readonlyEventObserverStopped'] and not s['readonlyEventObserverFailures']
    assert s['productActorCountAfterStop']==s['productRetiringActorCountAfterStop']==0 and not s['productResourceErrors']
    assert t['sourceStable'] and t['traceComplete'] and not t['errors'] and not t['openSpans'] and t['timingPerturbed']
    assert len(t['events'])==2160 and not t['returnEventProvesSuccess'] and not t['nativeAuthority']
    calls={e['id']:e for e in t['events'] if e['event']=='call'}
    returns={e['id']:e for e in t['events'] if e['event']=='return'}
    assert len(calls)==len(returns)==1080 and calls.keys()==returns.keys()
    for n,c in calls.items(): assert returns[n]['durationNs']==returns[n]['timeNs']-c['timeNs']
    observed=[]
    for n,c in calls.items():
        if c['symbol'] in ('SceneController.prepare','NativeDesktop.plan_destinations','NativeDesktop.apply_destination','NativeDesktop.refresh_destination'):
            observed.append({'id':n,'thread':c['thread'],'parent':c['parent'],'symbol':c['symbol'],
                             'offsetMs':(c['timeNs']-t['startedNs'])/1e6,'durationMs':returns[n]['durationNs']/1e6})
    artifacts={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in A.rglob('*') if p.is_file() and not p.is_symlink()}
    row={'result':'failure-preserved-and-reviewed','nativeResult':'fail','nativeTerminalExitCode':1,
         'reportSHA256':sha(A/'report.json'),'manifestSHA256':sha(B/'frozen-inputs.json'),
         'checksPassed':17,'checksRecorded':19,'originalBaseline38Accepted':False,'fault34Run':False,
         'primaryFailure':'Actual complete native family restore timeout before metadata validation',
         'originalDeadlineUnchanged':True,'timingPerturbed':True,'timingComplete':True,'timingEvents':2160,
         'startedTerminalHelperPairs':38,'all38HelpersNormalZeroAndGone':True,'helperRefusalObserved':False,
         'failedHelperGateDoesNotProveAbnormalExit':True,'serviceQueries':gate['serviceQueries'],
         'harnessQueries':gate['harnessQueries'],'clientsNormalZeroAndGone':3,'normalNativeUnload':True,
         'mainPreservationPassed':15,'runtimeGone':True,'unknownDescendants':0,'cleanupErrors':0,
         'completeFrozenInputsVerified':len(m['inputs']),'linksVerified':len(m['symlinks']),
         'selectedTimingSpans':observed,'artifacts':artifacts,'mainChanged':False,
         'rootDiagnosticCorrections':['one SyntaxError and one absent optional-field KeyError in read-only projections did not edit evidence',
                                      'preliminary helper-refusal inference corrected; raw38terminal exits all0'],
         'hostNormalExitCodesProven':False,'fullWindowsParityAccepted':False}
    dest=QA/'thumbnail-v13-root-failure-audit-v1.json'
    with os.fdopen(os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:
        json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'result':row['result'],'helpersNormal':38,'clientsNormal':3,'mainGates':15,'timingComplete':True,'auditSHA256':sha(dest)}))

if __name__=='__main__':main()
