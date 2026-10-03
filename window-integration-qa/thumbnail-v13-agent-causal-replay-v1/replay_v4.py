"""Artifact-only causal replay: return boundaries never imply successful effects."""
import hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa')
B=QA/'family-preparation-thumbnail-v13';A=B/'attempt-baseline-1';OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs={}
def read(p):
 p=Path(p);before=p.stat();data=p.read_bytes();after=p.stat()
 assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns)
 inputs[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'mode':stat.S_IMODE(after.st_mode)}
 return data
def load(p):return json.loads(read(p))
manifest=load(B/'frozen-inputs.json');trace=load(A/'actual-preparation-timing.json');report=load(A/'report.json');service=load(A/'service-evidence.json');helpers=load(A/'completed-helpers.json')
assert sha(B/'frozen-inputs.json')=='68a1996ac38b01635b0e91af59cf6c4214f6e4fe165446826f3f076e4b7662bf'
assert trace['traceComplete'] is True and trace['sourceStable'] is True and trace['timingPerturbed'] is True
assert trace['openSpans']==[] and trace['errors']==[] and trace['returnEventProvesSuccess'] is False
for p,w in trace['sources'].items():
 data=read(p);assert inputs[p]['sha256']==w['sha256']==manifest['inputs'][p] and inputs[p]['mode']==w['mode']==manifest['inputModes'][p]
for p in [B/'native_integration.py',B/'helper_observer.py',B/'helper_setup.py',B/'service_observer.py']:
 read(p);assert inputs[str(p)]['sha256']==manifest['inputs'][str(p)] and inputs[str(p)]['mode']==manifest['inputModes'][str(p)]
calls={};returns={};stacks={}
for event in trace['events']:
 n=event['id'];thread=event['thread'];stack=stacks.setdefault(thread,[])
 if event['event']=='call':
  assert n not in calls and event['parent']==(stack[-1] if stack else None)
  assert type(event['codeObjectID']) is int and event['symbol'] in trace['sources'][event['path']]['symbols']
  calls[n]=event;stack.append(n)
 else:
  assert event['event']=='return' and stack.pop()==n and n not in returns
  assert event['durationNs']==event['timeNs']-calls[n]['timeNs']>=0 and event['successClaimed'] is False
  returns[n]=event
assert set(calls)==set(returns) and all(not v for v in stacks.values()) and len(trace['events'])==2160
def descendants(n):
 result=[]
 for m,c in calls.items():
  p=c['parent']
  while p is not None:
   if p==n:result.append(m);break
   p=calls[p]['parent']
 return result
def span(n,origin):
 c=calls[n];return {'id':n,'parent':c['parent'],'thread':c['thread'],'symbol':c['symbol'],'codeObjectID':c['codeObjectID'],'startNs':c['timeNs'],'endNs':returns[n]['timeNs'],'relativeStartMs':(c['timeNs']-origin)/1e6,'durationMs':returns[n]['durationNs']/1e6,'details':c['details'],'returnProvesSuccess':False}
retirements=[load(A/f'service-retirement-{i}.json') for i in (1,2)]
restore=retirements[1]['history'][0];origin=restore['profile']['receivedNs'];deadline=origin+2000000000
assert restore['operation']=='restore' and not restore['validated'] and restore['accepted_operation'] is None
assert restore['sources']==[] and restore['results']==[] and not restore['visual'] and not restore['ready']
assert 'metadataValidatedNs' not in restore['profile'] and restore['profile']['settlementReason']=='controller deadline'
prepare=[n for n,c in calls.items() if c['symbol']=='SceneController.prepare' and c['timeNs']>=origin][0]
tree=descendants(prepare)
planned=[n for n in tree if calls[n]['symbol']=='NativeDesktop.plan_destinations'];individual=[n for n,c in calls.items() if c['symbol']=='NativeDesktop.plan_destination' and calls[planned[0]]['timeNs']<=c['timeNs'] and returns[n]['timeNs']<=returns[planned[0]]['timeNs']]
applied=[n for n in tree if calls[n]['symbol']=='NativeDesktop.apply_destination'];refreshed=[n for n in tree if calls[n]['symbol']=='NativeDesktop.refresh_destination']
assert len(planned)==1 and len(individual)==3 and len({calls[n]['thread'] for n in individual})==3
assert len(applied)==3 and len(refreshed)==2 and not any(calls[n]['symbol']=='NativeDesktop.capture_source' for n in tree)
focus=[n for n in tree if calls[n]['symbol']=='OwnedCommands.run' and calls[n]['details'].get('args',[None,None])[1]=='dispatch']
expected=[]
for member in restore['members']:
 expected.extend([['hyprctl','dispatch','hl.dsp.focus({ monitor = "WAYLAND-1" })'],['hyprctl','dispatch','hl.dsp.focus({ workspace = "1" })']])
assert [calls[n]['details']['args'] for n in focus]==expected
assert all(returns[a]['timeNs']<=calls[z]['timeNs'] for a,z in zip(focus,focus[1:]))
ledger=service['actualTerminalBinding']['ledger'];assert service['actualTerminalBinding']['usable'] is True
assert ledger['fault'] is False
for row in ledger['history']:
 assert row['closed'] is True and row['published'] is True and row['outcome']=='complete' and row['error'] is None
 assert row['evidence']['completeServerEOF'] is True and row['evidence']['peer']['pid']==ledger['issuer']['compositorPID']
for n in set(tree).union(*(descendants(m) for m in individual)):
 if calls[n]['symbol']=='ReadonlyIPC.query':
  parent=calls[calls[n]['parent']];assert parent['symbol']=='OwnedCommands.run'
  args=parent['details']['args'];request={('clients','-j'):'j/clients',('monitors','-j'):'j/monitors',('workspaces','-j'):'j/workspaces',('repl','print(hl.plugin.hyprbars.window_families())'):'/repl print(hl.plugin.hyprbars.window_families())'}[tuple(args[1:])]
  found=[x for x in ledger['history'] if x['thread']==calls[n]['thread'] and x['request']==request and calls[n]['timeNs']<=x['registeredNs']<=x['finishedNs']<=returns[n]['timeNs']]
  assert len(found)==1 and found[0]['actor']==2
keeper=load(next((A/'host/runtime-archive/hypr-window-motion/qa-family-service').glob('keeper*.json')))
assert keeper['normalStop'] is True and keeper['allGroupsEmpty'] is True
native_jobs=[]
for n in focus:
 launch=[m for m in descendants(n) if calls[m]['symbol']=='OwnedLaunch.__init__'];complete=[m for m in descendants(n) if calls[m]['symbol']=='Keeper.complete']
 assert len(launch)==len(complete)==1 and calls[launch[0]]['details']['actor']==2 and calls[launch[0]]['details']['kind']=='native-effect'
 job=calls[complete[0]]['details']['job'];rows=[x for x in keeper['jobs'] if x['job']==job]
 assert len(rows)==1 and rows[0]['normalCompletion'] is True and rows[0]['groupEmpty'] is True
 native_jobs.append({'span':n,'job':rows[0],'meaning':'exact normal returned owned-job closure; no independent native geometry-effect claim'})
raw=[json.loads(x) for x in read(A/'terminal-helpers/helper-events.jsonl').decode().splitlines()];starts=[x for x in raw if x['event']=='started'];terminal=[x for x in raw if x['event']=='terminal']
assert len(raw)==76 and len(starts)==len(terminal)==38 and not any(x['event']=='refused' for x in raw)
for x in starts:
 z=[v for v in terminal if v['operation']==x['operation']]
 assert len(z)==1 and z[0]['exitCode']==0 and all(z[0].get(k)==x.get(k) for k in ['wrapper','delegate','helper','queryRoot','class','serviceOperation'])
for name in ['taskbar-shell.log','family-service.log']:assert b'Exact private helper refused:' not in read(A/name)
assert helpers['allNormal'] is True and helpers['allQueriesNormal'] is True and helpers['allExactProcessesGone'] is True
refresh_rows=[x for x in starts if x.get('serviceOperation')=='service-motionRefresh']
assert len(refresh_rows)==2
for row,n in zip(refresh_rows,refreshed,strict=True):
 jobs=[calls[m]['details']['job'] for m in descendants(n) if calls[m]['symbol']=='Keeper.complete']
 assert len(jobs)==1 and any(x['job']==jobs[0] and x['pid']==row['wrapper']['pid'] and str(x['start'])==row['wrapper']['start'] for x in keeper['jobs'])
settle=[n for n,c in calls.items() if c['symbol']=='SceneController.settle' and origin<=c['timeNs']<origin+3000000000]
assert len(settle)==1 and calls[refreshed[1]]['timeNs']<deadline<calls[settle[0]]['timeNs']<returns[refreshed[1]]['timeNs']
assert restore['profile']['cleanupAckNs']<returns[refreshed[1]]['timeNs'] and restore['profile']['cleanupAckNs']>=deadline
assert not any(calls[n]['symbol']=='SceneController.commit_members' for n in descendants(settle[0]))
failed=[x['name'] for x in report['checks'] if not x['passed']];assert len(report['checks'])==19 and len(failed)==2
assert 'Actual complete native family restore' in report['error'] and report['result']=='fail'
assert all(x['exitCode']==0 and x['gone'] for x in report['clientCleanup'].values()) and report['normalNativeUnload'] is True
host=load(A/'host/host-evidence.json');read(A/'after-main/preservation.json')
persist=[m for n in focus for m in descendants(n) if calls[m]['symbol']=='RuntimeService.persist']
min_origin=retirements[0]['history'][0]['profile']['receivedNs']
captures=[span(n,min_origin) for n,c in calls.items() if c['symbol']=='NativeDesktop.capture_source']
assert len(captures)==3 and len(retirements[0]['retainedEpochSources'])==3 and retirements[1]['retainedEpochSources']==[]
for p in (A/'service-epochs').glob('*.png'):read(p)
for p in (A/'service-cache-pairs').glob('*'):read(p)
read(__file__)
result={'result':'causal-replay-pass','campaignResult':'fail','earliestFeatureFailure':'Actual complete native family restore timeout before restore captures','checksRecorded':19,'checksPassed':17,'observedRestore':{'actor':2,'receipt':2,'receivedNs':origin,'originalDeadlineNs':deadline,'metadataValidated':False,'captures':0,'seeded':False,'results':[],'prepare':span(prepare,origin),'parallelPlanning':span(planned[0],origin),'individualPlans':[span(n,origin) for n in individual],'apply':[span(n,origin) for n in applied],'focusCommands':[span(n,origin) for n in focus],'normalOwnedFocusJobClosures':native_jobs,'focusEnvelopeMs':sum(returns[n]['durationNs'] for n in focus)/1e6,'focusPersistenceCalls':len(persist),'focusPersistenceEnvelopeMs':sum(returns[n]['durationNs'] for n in persist)/1e6,'refresh':[span(n,origin) for n in refreshed],'normalRefreshHelpers':refresh_rows,'watchdogSettlement':span(settle[0],origin),'cleanupAckNs':restore['profile']['cleanupAckNs'],'sourceConclusion':'deadline watchdog clears an unvalidated first restore scene; accepted_operation is None, so settle performs no native restore member commits; the second normal refresh drains afterward and prepare sees lost ownership'},'minimizeCaptureSpans':captures,'rawHelpers':{'starts':38,'normalTerminals':38,'refusals':0,'harnessQueries':1,'serviceQueries':5,'allRecordedExactProcessesGone':True,'fullExpectedWorkloadComplete':False},'readonlyQueries':{'count':len(ledger['history']),'allClosedPublishedFullEOF':True,'refused':0},'secondaryFailedChecks':failed,'partialWorkloadFallout':['default pipeline requires four actors; only two exist','original full service helper budgets unmet after early restore timeout'],'trace':{'events':2160,'spans':len(calls),'open':0,'errors':[],'sourceStable':True,'timingPerturbed':True,'returnsNeverProveSuccessfulEffects':True},'normalNativeUnload':True,'normalClientExits':True,'hostNormalExitProven':False,'hostEvidence':host,'originalBaseline38Accepted':False,'originalFault34Accepted':False,'historicalB12CallDurationsInferred':False,'nativeLaunch':False,'mainChanges':False,'inputs':inputs}
path=OUT/'report.json'
with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps({'result':result['result'],'campaign':'fail','report':str(path),'sha256':sha(path),'inputs':len(inputs),'focusEnvelopeMs':result['observedRestore']['focusEnvelopeMs']}))
