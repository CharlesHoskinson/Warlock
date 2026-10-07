"""Couple real current-error negative control and current positive regressions."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v138';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
inputs={};native={}
for v,passed in [(159,False),(165,True),(166,True),(167,True)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';p=next(root.glob('qa/native-controlled-*/report.json'));n=load(p);pre=load(root/'qa/preflight.json');assert n['passed']==passed and n['cleanupPassed']
 for f,h in pre['inputs'].items():assert sha(f)==h,f
 for f,h in n['artifacts'].items():assert sha(p.parent/f)==h,f
 log=p.parent/'private-evidence/controlled-host.log';inputs.update({str(p):sha(p),str(root/'qa/preflight.json'):sha(root/'qa/preflight.json'),str(log):sha(log)})
 native[v]=(n,{c['name']:c for c in n['checks']},log.read_text())
legacy,lc,lt=native[159];normal,nc,nt=native[165];current,cc,ct=native[166];old,oc,ot=native[167]
assert lc['controlledActualOriginalWebKitCancellationConsumedOnce']['passed'] and not lc['controlledActualStaleSnapshotCompletionRejected']['passed']
assert normal['actualCapturedPixelsQualified'] and len(normal['checks'])==29 and all(c['exitCode']==0 for c in normal['ownedExitCodes'])
assert old['actualCancelledOldResultQualified'] and len(old['checks'])==36 and all(c['exitCode']==0 for c in old['ownedExitCodes'])
assert current['actualCurrentMatchingErrorNativeQualified'] and current['expectedFailureExitCode']==1 and not current['normalControlledHostClosureQualified'] and not current['gracefulCurrentFailureDrainQualified']
assert all(c['passed'] for c in current['checks']) and all(c['exitCode']==(1 if c['name']=='controlled-host' else 0) for c in current['ownedExitCodes'])
state=cc['controlledCurrentFailureRetainsOriginalNativeCustody']['state'];models=state['privatePolicy']['models'];assert not state['privatePolicy']['realm']['closed'] and len(models)==1
model=models[0]['model'];assert model['accepted'] and model['accepted']['owned'] and model['known'] and model['image'].startswith('elm-shell://preview/')
assert ct.count('controlled-native-current-snapshot-error: scopeCurrent=1 actualCancelled=1 originalFinishCalls=1 nativeSettlement=0')==1
assert 'controlled-native-snapshot-refused:' not in ct and ct.count('Native client producer failed: Operation was cancelled')==1 and 'Controlled native teardown incomplete:' in ct
assert ct.count('controlled-native-snapshot-finish-outcome: image=0 cancelled=1 retainedEpoch=1 currentEpoch=1 replacedView=0 originalFinishCalls=1 nativeSettlement=0')==1
assert ot.count('controlled-native-snapshot-finish-outcome: image=0 cancelled=1 retainedEpoch=1 currentEpoch=2 replacedView=1 originalFinishCalls=1 nativeSettlement=0')==1 and oc['controlledActualStaleSnapshotCompletionRejected']['passed'] and 'Native client producer failed:' not in ot
source=gui/'native/shared-host.c';s=source.read_text();a=s.index('static void client_snapshot_complete(GObject *object');b=s.index('static gboolean client_reader_hold(',a);body=s[a:b]
assert body.count('webkit_web_view_get_snapshot_finish(')==1 and body.index('!controlled_snapshot_matches(snapshot,object)')<body.index('if(!image) {')<body.index('client_snapshot_free(snapshot);client_failure(error);return;')
assert 'g_clear_error(&error);client_snapshot_free(snapshot);' in body and 'qa_controlled_current_cancelled_snapshot && qa_controlled_delayed_snapshot' in s
for p in [source,gui/'native/controlled-preview-host.h',gui/'spec/async_error_scope.qnt',pathlib.Path(__file__)]:inputs[str(p)]=sha(p)
out=pathlib.Path(__file__).with_name('current-error-scope-coupling-v138-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/async_error_scope.qnt',out/'inputs/async_error_scope.qnt')
cases=[('actualLegacyOldCancellation','oldScope',False,False,True,False,False,'held Native159 old cancellation incorrectly fails current GUI'),('actualFixedOldCancellation','oldScope',False,True,False,True,False,'current GUI138/Native167 same canceled-old oracle rejects old result and closes normally'),('actualCurrentCancellation','currentScope',False,True,True,False,False,'current GUI138/Native166 real current cancellation reaches original failure1/strict teardown refusal'),('actualCurrentSuccess','currentScope',True,True,False,False,True,'current GUI138/Native165 actual normal source snapshot/pixels/normal closure')]
runs=[];observations=[]
for name,scope,ok,guardFirst,failed,stale,artifact,origin in cases:
 cond=f's.failed=={str(failed).lower()} and s.stale=={str(stale).lower()} and s.artifact=={str(artifact).lower()} and s.finished and s.nativeOwned and s.policy==1'
 runs.append(f' run {name}=init.then(finish({scope},{str(ok).lower()},{str(guardFirst).lower()})).then(check({cond}))');observations.append(dict(name=name,origin=origin,scope=scope,success=ok,guardFirst=guardFirst,expected=dict(failed=failed,stale=stale,artifact=artifact)))
(out/'inputs/concrete_current_error_scope.qnt').write_text('module concrete_current_error_scope {\n import async_error_scope.* from "./async_error_scope"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n')
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Four actual outcomes projected into selected Quint cases: held original old-error defect159; current138 normal165, real matching-current canceled result166 original failure1/strict teardown refusal, and old-canceled167 safe stale rejection/current new pixels/normal closure. NativeOwned projects current pre-exit accepted/known model and strict close refusal; it does NOT prove custody persistence after process exit, graceful failure drain, durable recovery or every native transition. Actual host1 is expected negative evidence, never normal closure. Same single policy/current error/source scope and original six-second observation retained. Full async schedules, physical conceal/reveal/hardware, pressure/recovery/release remain open.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 names='|'.join(x[0] for x in cases)
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_current_error_scope.qnt']),('selected',[str(tool),'test','concrete_current_error_scope.qnt','--main=concrete_current_error_scope','--backend=typescript','--match=^('+names+')$','--seed=1380043','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==4 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256'];d.update(passed=True,coupledQuintChecks=4)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
