"""Read-only artifact replay; no GUI, queries, source mutation, or performance proof."""
import hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa');OUT=Path(__file__).resolve().parent
A=QA/'family-preparation-thumbnail-v12/attempt-baseline-1';B=A.parent
P=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-restore-planning-v27')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs={}
def read(p):
 p=Path(p);inputs[str(p)]={'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)};return json.loads(p.read_text())
def keep(p):
 p=Path(p);inputs[str(p)]={'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
r=read(A/'report.json');e=read(A/'service-evidence.json');t=read(A/'actual-terminal-binding.json');helpers=read(A/'completed-helpers.json')
a1=read(A/'service-retirement-1.json');a2=read(A/'service-retirement-2.json')
raw_terminal=t
t=e['actualTerminalBinding']
if t.get('usable') is not True or t['errors'] or t['moduleToken']!=raw_terminal['moduleToken'] or t['ledger']!=raw_terminal['ledger']:raise ValueError('canonical post-disk actual terminal authority differs')
root=read(QA/'thumbnail-v12-root-failure-audit-v1.json')
if sha(QA/'thumbnail-v12-root-failure-audit-v1.json')!='f3d2476e1d062bf664659fffb40ec431780e3b89b6e79654fd9623af8ba2601f':raise ValueError('root completed failure audit epoch changed')
manifest=read(B/'frozen-inputs.json');service=read(P/'manifest-restore-planning-v27.json')
if sha(B/'frozen-inputs.json')!=r['sourceManifestSHA256']:raise ValueError('actual collector source differs')
if sha(P/'manifest-restore-planning-v27.json')!='54857ba311e2862e37037195283cf98b6fba8bb286cb33d32e92685671304e40':raise ValueError('actual selected service differs')
module_phases=[]
for name in ('actual-modules-before.json','actual-modules-at-owner-bind.json','actual-modules-after.json','actual-modules-final-confirm.json'):
 m=read(A/name)
 if m.get('rawEvidenceOnly') is not True or m['usable'] is not False or m['moduleToken']!=t['moduleToken'] or m['errors'] or len(m['modules'])!=19 or m['manifestActualSHA256']!=sha(P/'manifest-restore-planning-v27.json'):raise ValueError('actual module authority incomplete')
 for item in m['modules']:
  p=Path(item['actualFile']);w=item['source']
  if p!=P/(item['name']+'.py') or w['sha256']!=sha(p) or service['inputs'][str(p)]!=w['sha256'] or service['inputModes'][str(p)]!=stat.S_IMODE(p.stat().st_mode):raise ValueError('actual source mapping differs')
  keep(p)
 module_phases.append({'phase':m['phase'],'servicePID':m['servicePID'],'serviceStart':m['serviceStart'],'all19ActualPathsAndHashesExact':True})
for name in ('native_integration.py','service_observer.py','module_binding.py','capture_evidence.py','helper_setup.py','helper_observer.py'):keep(B/name)
profile=a2['history'][0]['profile'];received=profile['receivedNs'];deadline=received+2000000000
ledger=t['ledger']['history']
if len(ledger)!=98 or any(x['outcome']!='complete' or not x['closed'] or not x['published'] or x.get('error') or x['evidence'].get('completeServerEOF') is not True for x in ledger):raise ValueError('actual readonly closure incomplete')
rows=[{'index':i,'request':x['request'],'actor':x['actor'],'thread':x['thread'],'startNs':x['registeredNs'],'endNs':x['finishedNs'],'startAfterReceiptMs':(x['registeredNs']-received)/1e6,'endAfterReceiptMs':(x['finishedNs']-received)/1e6} for i,x in enumerate(ledger) if x['actor']==2 and received<=x['registeredNs']<received+3100000000]
plans=[x for x in rows if x['request']=='j/monitors']
if len(plans)!=3 or len({x['thread'] for x in plans})!=3 or max(x['startNs']for x in plans)>=min(x['endNs']for x in plans):raise ValueError('genuine three worker observation overlap absent')
workers=[]
for first in plans:
 chain=[x for x in rows if x['thread']==first['thread']]
 if [x['request']for x in chain]!=['j/monitors','j/workspaces','j/clients']:raise ValueError('original three observations per planner differ')
 workers.append({'thread':first['thread'],'observations':chain})
if len(a1['retainedEpochSources'])!=3 or len(a2['retainedEpochSources'])!=2:raise ValueError('actual returned capture count differs')
for packet in (a1,a2):
 for x in packet['retainedEpochSources']:
  p=Path(x['retainedPath']);keep(p)
  if sha(p)!=x['sha256'] or x['source']['digest']!=x['sha256'] or p.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n' or not x['captureCallbackDelegatedOnce'] or not x['sourceResultUnchanged']:raise ValueError('actual retained capture proof differs')
 for pair in packet['cachePairsAtCapture']:
  for x in pair['files']:
   keep(x['retainedPath'])
   if sha(x['retainedPath'])!=x['sha256']:raise ValueError('actual cache pair changed')
if a2['history'][0]['sources'] or a2['history'][0]['ready'] or 'seedQueuedNs'in profile:raise ValueError('restore seed unexpectedly recorded')
restore_events=a2['rendererEvents'];names=[x.get('event')for x in restore_events]
if any(n in ('seeded','sourceUploaded','uploaded','presented')for n in names):raise ValueError('restore visual authority unexpectedly present')
starts=[x for x in helpers['events']if x['event']=='started'];terms=[x for x in helpers['events']if x['event']=='terminal'];pending={};service_helper_spans=[]
if len(starts)!=30 or len(terms)!=30 or not all(helpers[k]for k in ('allNormal','allExactProcessesGone','allQueriesNormal')):raise ValueError('actual normal helper closure differs')
for x in helpers['events']:
 key=(x['wrapper']['pid'],x['wrapper']['start'])
 if x['event']=='started':
  if key in pending:raise ValueError('helper start reused')
  pending[key]=x
 elif x['event']=='terminal':
  before=pending.pop(key)
  if x['operation']!=before['operation'] or x['exitCode']!=0 or x['delegate']!=before['delegate']:raise ValueError('exact helper terminal differs')
  if x.get('queryRoot')=='service':service_helper_spans.append({'operation':x['operation'],'wrapper':x['wrapper'],'delegate':x['delegate'],'startWallNs':before['timeNs'],'endWallNs':x['timeNs'],'wallDurationMs':(x['timeNs']-before['timeNs'])/1e6,'exitCode':0,'monotonicDurationClaimed':False})
 else:raise ValueError('refused/unknown helper event')
if pending or helpers['harnessQueries']!=1 or helpers['serviceQueries']!=8:raise ValueError('helper exact closure/count changed')
checkrows=[{'name':x['name'],'passed':x['passed']} for x in r['checks']]
if len(checkrows)!=19 or sum(x['passed']for x in checkrows)!=17 or r['result']!='fail':raise ValueError('original preserved failure changed')
if any(x['exitCode']!=0 or not x['gone']for x in r['clientCleanup'].values()):raise ValueError('normal client closure differs')
host=r['hostEvidence']
if host['unexpectedInnerDescendants'] or host['remainingDescendants'] or host['cleanupErrors'] or not host['runtimeGone']:raise ValueError('host disappearance/cleanup differs')
if not all(r['mainPreservation'].values()) or not r['normalNativeUnload'] or not r['allFrozenInputsExact']:raise ValueError('original preserved source/main/unload evidence differs')
for x in e['transports']:
 if x['exitCode']!=0 or not x['closed'] or x['failed'] or x['closeError']:raise ValueError('renderer closure differs')
actors=[]
for packet in (a1,a2):
 h=packet['history'][0];p=h['profile'];begin=p['receivedNs'];actors.append({'actor':packet['retirement']['actor'],'operation':h['operation'],'profile':p,'relativeProfileMs':{k:(v-begin)/1e6 for k,v in p.items()if k.endswith('Ns')and type(v)is int},'actualReturnedCaptures':len(packet['retainedEpochSources']),'capturedStableIds':[x['source']['stableId']for x in packet['retainedEpochSources']],'recordSourceCount':len(h['sources']),'ready':h['ready'],'results':h['results'],'rendererEvents':names if packet is a2 else [x.get('event')for x in packet['rendererEvents']]})
row={'result':'bounded-failure-replay-pass','campaignResult':'fail','nativeAcceptance':False,'inputs':inputs,'modulePhases':module_phases,'actors':actors,'restoreOriginalDeadlineNs':deadline,'restoreWorkerObservations':workers,'restoreReadonlyTimeline':rows,'all98ReadonlyRowsCompleteEOFClosedPublished':True,'serviceHelperSpansWallClockOnly':service_helper_spans,'all30HelpersNormalExactPairedGone':True,'harnessQueries':1,'serviceQueries':8,'checks':checkrows,'normalClientsAndRenderers':True,'original15MainPreservation':r['mainPreservation'],'nativeUnloadNormal':True,'hostUnexpected':host['unexpectedInnerDescendants'],'hostRemaining':host['remainingDescendants'],'runtimeGone':host['runtimeGone'],'normalHostExitCodeProven':False,'timingPerturbedByExistingObserver':e['readonlyEventObserverTimingPerturbation'],'rootWholeSourceAudit':str(QA/'thumbnail-v12-root-failure-audit-v1.json'),'limits':['Three concurrent original planners are established by exact sources and native thread/EOF ledger; per-method start/return spans and exact six focus durations are not retained.','Capture2 returned normally; before third capture the original lease/current check may stop after watchdog settlement, but precise preemption/return boundary is unobserved.','Wall-clock helper stamps cannot be substituted for original receipt monotonic deadline without an actual clock bridge.','B11 metadata1841ms and B12 metadata1092ms are different native attempts, not a controlled performance comparison.','Only2 actors executed, so original default4/helper complete-workload counts remain false; normal closure supplies no feature acceptance.','No CPU fixture timing is substituted for actual native timing; original38/fault34 remain unaccepted.']}
for name,w in inputs.items():
 if sha(name)!=w['sha256'] or stat.S_IMODE(Path(name).stat().st_mode)!=w['mode']:raise ValueError('bounded actual evidence changed during replay')
path=OUT/'report.json'
with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'result':row['result'],'campaignResult':'fail','inputs':len(inputs),'parallelWorkers':3,'restoreMetadataMs':actors[1]['relativeProfileMs']['metadataValidatedNs'],'restoreCaptures':2,'normalReadonly':98,'normalHelpers':30,'normalClients':3,'normalHostExitProven':False}))
