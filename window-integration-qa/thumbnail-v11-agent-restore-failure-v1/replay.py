from pathlib import Path
from collections import Counter
import hashlib,json,os,stat
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'family-preparation-thumbnail-v11';A=B/'attempt-baseline-1';D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((A/'report.json').read_text());e=json.loads((A/'service-evidence.json').read_text());p1=json.loads((A/'service-retirement-1.json').read_text());p2=json.loads((A/'service-retirement-2.json').read_text());helpers=json.loads((A/'completed-helpers.json').read_text());ledger=e['actualTerminalBinding']['ledger'];body=e['actualTerminalBinding']['journal'];keeper=json.loads(next(A.rglob('keeper-*.json')).read_text())
inputs={};modes={}
for p in A.rglob('*'):
 if p.is_file():inputs[str(p)]=sha(p);modes[str(p)]=stat.S_IMODE(p.stat().st_mode)
manifest=json.loads((B/'frozen-inputs.json').read_text());assert sha(B/'frozen-inputs.json')=='53f6ddde08633dc3bfab3cbadfde2997695bf189b095382e2805cd1e8441a3c9'
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-housekeeping-admission-v26')
for p in [B/'native_integration.py',B/'capture_evidence.py',B/'service_observer.py',B/'helper_setup.py',B/'helper_observer.py',B/'module_binding.py',SERVICE/'scene_controller.py',SERVICE/'native_desktop.py',SERVICE/'production_motion_6d9.py',SERVICE/'batch_preview.py']:
 assert sha(p)==manifest['inputs'][str(p)]and stat.S_IMODE(p.stat().st_mode)==manifest['inputModes'][str(p)];inputs[str(p)]=sha(p);modes[str(p)]=stat.S_IMODE(p.stat().st_mode)
def actor(packet):
 h=packet['history'][0];profile=h['profile'];received=profile['receivedNs']
 return dict(actor=packet['retirement']['actor'],operation=h['operation'],receivedNs=received,profileOffsetsMs={k:(v-received)/1e6 for k,v in profile.items()if k.endswith('Ns')and type(v)is int},captured=len(packet['retainedEpochSources']),cachePairs=len(packet['cachePairsAtCapture']),recordSources=len(h['sources']),validated=h['validated'],visual=h['visual'],running=h['running'],ready=h['ready'],recordFailure=profile.get('failure'),settlementReason=profile.get('settlementReason'),rendererEvents=dict(Counter(x['event']for x in packet['rendererEvents'])),nativeCommandSubmissions=h['results'],retirement=packet['retirement'])
first,second=actor(p1),actor(p2);assert first['captured']==3 and first['recordSources']==3 and first['rendererEvents']['seeded']==1;assert second['captured']==1 and second['recordSources']==0 and not second['visual']and second['settlementReason']=='controller deadline';assert not second['rendererEvents'].get('seeded',0)
for packet in [p1,p2]:
 for row in packet['retainedEpochSources']:assert row['captureCallbackDelegatedOnce']is True and row['sourceResultUnchanged']is True and sha(row['retainedPath'])==row['sha256']==row['source']['digest']
 for pair in packet['cachePairsAtCapture']:
  for f in pair['files']:assert sha(f['retainedPath'])==f['sha256']
minimizedPairs={f['source']:f['sha256']for pair in p1['cachePairsAtCapture']for f in pair['files']}
restorePair={f['source']:f['sha256']for pair in p2['cachePairsAtCapture']for f in pair['files']};assert restorePair.items()<=minimizedPairs.items()
assert all(row['outcome']=='complete'and row['closed']is True and row['published']is True and row['error']is None and row['evidence']['completeServerEOF']is True for row in ledger['history'])
starts=[x for x in helpers['events']if x['event']=='started'];terms=[x for x in helpers['events']if x['event']=='terminal'];assert len(starts)==len(terms)
for start in starts:
 matches=[x for x in terms if x['operation']==start['operation']];assert len(matches)==1 and matches[0]['exitCode']==0
 for k in ['wrapper','delegate','class','queryRoot','helper','serviceOperation']:assert matches[0].get(k)==start.get(k)
service=Counter(x['serviceOperation']for x in starts if x.get('queryRoot')=='service')
assert helpers['allNormal']is True and helpers['allExactProcessesGone']is True and helpers['allQueriesNormal']is True and helpers['harnessQueries']==1
checks=r['checks'];assert sum(x['passed']for x in checks)==17 and len(checks)==19
main=r['mainPreservation'];assert len(main)==15 and all(main.values());host=r['hostEvidence']
row=dict(result='failure-replay-complete',campaignAccepted=False,requiredBaselineGates=38,recordedChecks=19,passingRecordedChecks=17,unrecordedChecks=19,primaryFailure=dict(type='ValueError',message='Three actual family captures required before cache acceptance',source='native_integration.py:687 -> capture_evidence.py:25',capturedRestore=1,requiredRestore=3,originalGatePreserved=True),actors=[first,second],actualReadonly=dict(rows=len(ledger['history']),outcomes=dict(Counter(x['outcome']for x in ledger['history'])),allClosedPublishedFullEOF=True,refusalRows=[]),actualHelpers=dict(starts=len(starts),terminals=len(terms),allNormal=True,allExactProcessesGone=True,allQueriesNormal=True,harnessQueries=1,serviceQueries=helpers['serviceQueries'],serviceOperationCounts=dict(service),remainingFullExpectedCountsPreserved=True),partialWorkloadFallout=[x['name']for x in checks if not x['passed']],cachePairs=dict(minimize=3,restoreReturned=1,allSixMinimizedFilesRetainedExact=True,returnedRestoreOwnerPairExactOriginal=True,threeRestoreCacheOrSeedAcceptance=False),serviceClosed=e['serviceClosed'],serviceFailure=e['serviceFailure'],productResourceErrors=e['productResourceErrors'],keeperNormalStop=keeper['normalStop'],keeperAllGroupsEmpty=keeper['allGroupsEmpty'],mainGates=main,normalNativeUnload=r['normalNativeUnload'],host=dict(unexpected=host['unexpectedInnerDescendants'],remaining=host['remainingDescendants'],cleanupErrors=host['cleanupErrors'],runtimeGone=host['runtimeGone'],normalExitStatusRecorded=False,normalHostExitAccepted=False),limits=['Profile spans include ordinary QA observer timing perturbation; per-effect start/finish callsite timing is not retained.','Source proves three individual destination plans, six guarded monitor/workspace focus submissions and three refresh helpers before metadataValidated; no historical attribution to one specific slow call.','Repeated minimize ready/watchdog command submissions are not proof of duplicate native state mutation.','Correct original deadline fallback and normal closure do not satisfy capture3/seed/restore/full38 feature acceptance.'],inputs=inputs,inputModes=modes)
fd=os.open(D/'report.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:row[k]for k in ['result','recordedChecks','passingRecordedChecks','primaryFailure','actualReadonly','actualHelpers','normalNativeUnload','host']}))
