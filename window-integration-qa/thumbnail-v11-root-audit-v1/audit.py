from pathlib import Path
import hashlib,importlib.util,json,os,stat,datetime
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'family-preparation-thumbnail-v11';A=B/'attempt-baseline-1'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
C=mod('root_b11_closure',B/'collector_v9_closure.py');P=mod('root_b11_helpers',B/'helper_observer.py')
frozen=json.loads((B/'frozen-inputs.json').read_text());C.verify_links(frozen['symlinks'])
for p,h in frozen['inputs'].items():C.retained_file(p,h,frozen['inputModes'][p],frozen['inputs'],frozen['inputModes'],frozen['symlinks'])
C.verify_links(frozen['symlinks'])
r=json.loads((A/'report.json').read_text());s=json.loads((A/'service-evidence.json').read_text());h=json.loads((A/'completed-helpers.json').read_text());config=h['config'];events=h['events']
helpers=P.summarize(events,config['allowed'],require_all=False,expect_harness=True,expected_service=None)
assert helpers is not None and helpers['allNormal'] and helpers['allExactProcessesGone'] and helpers['allQueriesNormal']
assert events==[json.loads(line) for line in (A/'terminal-helpers/helper-events.jsonl').read_text().splitlines() if line]
lifetimes={}
def add(row):
 if isinstance(row,dict) and type(row.get('pid'))is int and row.get('start') is not None:
  lifetimes[(row['pid'],str(row['start']))]=row
for e in events:
 for key in ('wrapper','delegate'):add(e.get(key))
for row in r['processes']:add(row)
for row in r['hostEvidence']['observedDescendantIdentities']:add(row)
for key in ('hyprland','weston','privateBus'):add(r['hostEvidence'][key])
for row in lifetimes.values():
 p=Path('/proc')/str(row['pid'])
 if p.exists():
  t=(p/'stat').read_text();fields=t[t.rfind(')')+2:].split()
  if fields[19]==str(row['start']):raise RuntimeError('Selected exact lifetime still live: '+str(row['pid']))
# This current absence check is additional evidence, not an exit-status substitute.
helperStarts=[e for e in events if e['event']=='started'];helperTerms=[e for e in events if e['event']=='terminal'];assert len(helperStarts)==len(helperTerms)
restore=s['records'][1]['history'][0];minimize=s['records'][0]['history'][0]
restored_sources=[x for x in s['retainedEpochSources'] if x['actor']==2];assert len(restored_sources)==1 and restore['operation']=='restore' and not restore['visual'] and not restore['ready']
checks=r['checks'];assert len(checks)==19 and sum(bool(x['passed']) for x in checks)==17
assert all(r['mainPreservation'].values()) and len(r['mainPreservation'])==15
assert r['allFrozenInputsExact'] and r['normalNativeUnload'] and not r['hostEvidence']['unexpectedInnerDescendants'] and not r['hostEvidence']['remainingDescendants'] and not r['hostEvidence']['cleanupErrors']
assert r['hostEvidence']['runtimeGone'] and not Path(r['hostEvidence']['runtime']).exists()
assert all(x['exitCode']==0 and x['gone'] and not x.get('forcedTermination') and not x.get('forcedKill') for x in r['clientCleanup'].values())
assert s['failure']is None and s['serviceFailure']is None and s['productActorCountAfterStop']==0 and s['productRetiringActorCountAfterStop']==0 and not s['productResourceErrors']
for x in s['retainedEpochSources']:assert sha(x['retainedPath'])==x['sha256'] and Path(x['retainedPath']).stat().st_size==x['bytes']
artifacts={str(p):{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode),'bytes':p.stat().st_size} for p in sorted(A.rglob('*')) if p.is_file() and not p.is_symlink() and p.name!='root-failure-audit-v1.json'}
row={'schema':'root-thumbnail-v11-native-failure-audit-v1','result':'failure-evidence-independently-verified','time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifestSHA256':sha(B/'frozen-inputs.json'),'frozenInputsVerified':len(frozen['inputs']),'frozenLinksVerified':len(frozen['symlinks']),'nativeSession':37821,'nativeExitCode':1,'checksRecorded':19,'checksPassed':17,'fullOriginal38Accepted':False,'firstWorkloadFailure':'restore requires three actual family captures; only owner capture returned','laterFailedPredicates':[x['name']for x in checks if not x['passed']],'restoreMetadataElapsedMs':(restore['profile']['metadataValidatedNs']-restore['profile']['receivedNs'])/1e6,'restoreCapturedSources':len(restored_sources),'restoreReady':restore['ready'],'restoreVisual':restore['visual'],'restoreSettlementReason':restore['profile']['settlementReason'],'helperStarts':len(helperStarts),'helperTerminals':len(helperTerms),'actualAllRegisteredHelpersNormal':True,'actualAllRegisteredHelperIdentitiesGone':True,'harnessQueries':helpers['harnessQueries'],'serviceQueries':helpers['serviceQueries'],'fullWorkloadHelperCountsAccepted':False,'actualClientsNormal0Gone':True,'all15MainPreservation':True,'nativeUnloaded':True,'noUnexpectedOrRemainingDescendants':True,'privateRuntimeGone':True,'hostNormalExitAndNoEscalationProved':False,'hostExitStatusLimit':'Original host stop/close does not record signal/escalation/returncode; empty descendants is not normal-exit proof.','selectedLifetimesCurrentlyGone':len(lifetimes),'artifacts':artifacts,'source':{'path':__file__,'sha256':sha(__file__)},'fault34Authorized':False,'fullParityAccepted':False}
p=A/'root-failure-audit-v1.json';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({k:row[k]for k in ['result','frozenInputsVerified','checksRecorded','checksPassed','helperStarts','helperTerminals','selectedLifetimesCurrentlyGone','restoreMetadataElapsedMs','hostNormalExitAndNoEscalationProved']}));print('root audit SHA',sha(p))
