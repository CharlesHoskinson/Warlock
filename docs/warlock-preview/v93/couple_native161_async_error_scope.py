"""Project actual failed/fixed callback observations into selected Quint cases."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v137';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
inputs={};native={}
for v,passed in [(159,False),(160,True),(161,True),(162,True)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';p=next(root.glob('qa/native-controlled-*/report.json'));n=load(p);pre=load(root/'qa/preflight.json');assert n['passed']==passed and n['cleanupPassed']
 for f,h in pre['inputs'].items():assert sha(f)==h,f
 for f,h in n['artifacts'].items():assert sha(p.parent/f)==h,f
 log=p.parent/'private-evidence/controlled-host.log';inputs.update({str(p):sha(p),str(root/'qa/preflight.json'):sha(root/'qa/preflight.json'),str(log):sha(log)})
 native[v]=(n,{c['name']:c for c in n['checks']},log.read_text())
legacy,lc,lt=native[159];fixed,fc,ft=native[161];normal,nc,nt=native[160];success,sc,st=native[162]
cancel='controlled-native-snapshot-finish-outcome: image=0 cancelled=1 retainedEpoch=1 currentEpoch=2 replacedView=1 originalFinishCalls=1 nativeSettlement=0'
assert lt.count(cancel)==1 and ft.count(cancel)==1
assert lc['controlledActualOriginalWebKitCancellationConsumedOnce']['passed'] and not lc['controlledActualStaleSnapshotCompletionRejected']['passed'] and 'Native client producer failed: Operation was cancelled' in lt
assert fc['controlledActualOriginalWebKitCancellationConsumedOnce']['passed'] and fc['controlledActualStaleSnapshotCompletionRejected']['passed'] and 'Native client producer failed:' not in ft
assert len(fixed['checks'])==36 and all(c['passed'] for c in fixed['checks']) and len(fixed['ownedExitCodes'])==13 and all(c['exitCode']==0 for c in fixed['ownedExitCodes'])
assert len(normal['checks'])==29 and normal['actualCapturedPixelsQualified'] and all(c['exitCode']==0 for c in normal['ownedExitCodes'])
assert len(success['checks'])==35 and success['actualOldResultAcrossReopenedRealmQualified'] and sc['controlledActualStaleSnapshotCompletionRejected']['passed']
assert fixed['actualReopenedWebKitPixels']['red']==19200 and fixed['actualReopenedClosedCurtainRegionPixels']['red']==0 and fixed['actualReopenedNativePaint']['opacity']==0
for state in [fc['controlledRealOldResultSurvivesStrictRealmCloseAndViewReplacement']['state'],fc['controlledReopenedOriginalNativeCustodyDrainedAndStrictlyClosed']['state']]:
 assert state['privatePolicy']['realm']['closed'] and not state['privatePolicy']['models'] and not state['retainedInputs'] and not state['postedTickets'] and not state['confirmations'] and not state['returnedEventBatches'] and state['transport']['pending']==0
old=r/'implementation/warlock-preview-provider-v136/native/shared-host.c';new=gui/'native/shared-host.c';oldtext=old.read_text();newtext=new.read_text()
def body(s):return s[s.index('static void client_snapshot_complete(GObject *object'):s.index('static gboolean client_reader_hold(',s.index('static void client_snapshot_complete(GObject *object'))]
oldbody,newbody=body(oldtext),body(newtext)
failure='if(!image) {client_snapshot_free(snapshot);client_failure(error);return;}'
guard='if(snapshot->controlled_visual && !controlled_snapshot_matches(snapshot,object))'
assert oldbody.index(failure)<oldbody.index(guard) and newbody.index(guard)<newbody.index(failure)
assert newbody.count('webkit_web_view_get_snapshot_finish(')==1 and 'if(image)cairo_surface_destroy(image);' in newbody and 'g_clear_error(&error);client_snapshot_free(snapshot);' in newbody
assert oldbody.count(failure)==1 and newbody.count(failure)==1
for p in [old,new,gui/'native/controlled-preview-host.h',gui/'spec/async_error_scope.qnt',pathlib.Path(__file__)]:inputs[str(p)]=sha(p)
out=pathlib.Path(__file__).with_name('async-error-scope-coupling-v137-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/async_error_scope.qnt',out/'inputs/async_error_scope.qnt')
cases=[('actualLegacyOldCancellation',False,False,True,False,False,'Native159 actual canceled old result and host1'),('actualFixedOldCancellation',False,True,False,True,False,'Native161 same real canceled result/original oracle passes, current new request2 pixels/native closure'),('actualFixedOldSuccess',True,True,False,True,False,'Native162 original successful held result remains refused'),('actualCurrentSuccess',True,True,False,False,True,'Native160 original current snapshot and actual source pixels')]
runs=[];observations=[]
for name,ok,guardFirst,failed,stale,artifact,origin in cases:
 scope='currentScope' if name=='actualCurrentSuccess' else 'oldScope';cond=f's.failed=={str(failed).lower()} and s.stale=={str(stale).lower()} and s.artifact=={str(artifact).lower()} and s.finished and s.nativeOwned and s.policy==1'
 runs.append(f' run {name}=init.then(finish({scope},{str(ok).lower()},{str(guardFirst).lower()})).then(check({cond}))')
 observations.append(dict(name=name,origin=origin,success=ok,scope=scope,guardFirst=guardFirst,expected=dict(failed=failed,stale=stale,artifact=artifact,finished=True,nativeOwned=True,policy=1)))
qnt='module concrete_async_error_scope {\n import async_error_scope.* from "./async_error_scope"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n';(out/'inputs/concrete_async_error_scope.qnt').write_text(qnt)
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Four bounded actual callback outcomes projected into explicitly selected Quint cases: held Native159 old cancellation shutdown, same exact Native161 cancellation oracle after source guard ordering fix, Native162 old success rejection, Native160 normal current success. Source order/original finish once/current error branch and actual strict native closure verified separately. The model nativeOwned flag projects unchanged authority, not every native resource transition. Current matching failure is only a model and unchanged source-branch witness here; no actual matching-current cancellation qualification follows. Does not prove all asynchronous schedules, process/reload/Unknown recovery, physical reveal/hardware or full release.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 names='|'.join(x[0] for x in cases)
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_async_error_scope.qnt']),('selected',[str(tool),'test','concrete_async_error_scope.qnt','--main=concrete_async_error_scope','--backend=typescript','--match=^('+names+')$','--seed=1370043','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==4 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,coupledQuintChecks=4,actualNative159ReportSHA256=sha(next((r/'implementation/warlock-client-provider-native-v159').glob('qa/native-controlled-*/report.json'))),actualNative161ReportSHA256=sha(next((r/'implementation/warlock-client-provider-native-v161').glob('qa/native-controlled-*/report.json'))))
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
