"""Couple actual failed/fixed current-failure drain stages to bounded Quint."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v139';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
inputs={};native={}
for v,passed in [(168,False),(169,True)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';p=next(root.glob('qa/native-controlled-*/report.json'));n=load(p);pre=load(root/'qa/preflight.json');assert n['passed']==passed and n['cleanupPassed']
 for f,h in pre['inputs'].items():assert sha(f)==h,f
 for f,h in n['artifacts'].items():assert sha(p.parent/f)==h,f
 log=p.parent/'private-evidence/controlled-host.log';inputs.update({str(p):sha(p),str(root/'qa/preflight.json'):sha(root/'qa/preflight.json'),str(log):sha(log)})
 native[v]=(n,{c['name']:c for c in n['checks']},log.read_text())
legacy,lc,lt=native[168];fixed,fc,ft=native[169]
assert not lc['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']['passed'] and fc['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']['passed']
assert fixed['gracefulCurrentFailureDrainQualified'] and fixed['expectedFailureExitCode']==1 and len(fixed['checks'])==22 and all(c['passed'] for c in fixed['checks'])
assert all(c['exitCode']==(1 if c['name']=='controlled-host' else 0) for c in fixed['ownedExitCodes'])
closed=fc['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']['state'];assert closed['privatePolicy']['realm']['closed'] and not closed['privatePolicy']['models'] and not closed['retainedInputs'] and not closed['postedTickets'] and not closed['confirmations'] and not closed['returnedEventBatches'] and closed['transport']['pending']==0
states=[json.loads(line.split(': ',1)[1]) for line in ft.splitlines() if line.startswith('controlled-native-private-status: ')]
owned=next(s for s in states if s['privatePolicy']['models'] and s['privatePolicy']['models'][0]['model']['accepted']);closing=next(s for s in states if s['privatePolicy']['realm']['closing'] and not s['privatePolicy']['realm']['closed'])
assert owned['privatePolicy']['realm']['epoch']==closing['privatePolicy']['realm']['epoch']==closed['privatePolicy']['realm']['epoch']=='1'
assert any(m['model']['known'] or m['model']['retiring'] for m in closing['privatePolicy']['models'])
assert 'controlled-native-current-failure-drain: epoch=1 quarantine=1 originalNative=1 failureRetained=1 inferredSettlement=0' in ft and 'controlled-native-current-failure-retired: epoch=1 failureRetained=1 originalStrictClose=1' in ft
assert ft.index('controlled-native-current-failure-drain:')<ft.index('controlled-native-realm-retired:')<ft.index('shared-host-exit: failure=1 rendered=1')
assert 'Controlled native teardown incomplete:' not in ft and 'GLib-GObject-CRITICAL' not in ft and 'controlled-native-reopened:' not in ft
header=gui/'native/controlled-preview-host.h';source=header.read_text();a=source.index('static void controlled_snapshot_failure(');b=source.index('static gboolean controlled_wire_room',a);failure=source[a:b]
assert 'failed=TRUE;controlled_failure_draining=TRUE;controlled_retiring=TRUE;' in failure and 'warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&native_error)' in failure and 'gtk_main_quit' not in failure
assert source.index('if(!warlock_policy_driver_retire(controlled_driver,error))return FALSE;')<source.index('if(controlled_failure_draining) {')
for p in [header,gui/'native/shared-host.c',gui/'spec/current_failure_drain.qnt',pathlib.Path(__file__)]:inputs[str(p)]=sha(p)
out=pathlib.Path(__file__).with_name('current-failure-drain-coupling-v139-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/current_failure_drain.qnt',out/'inputs/current_failure_drain.qnt')
cases=[('actualOriginalEarlyExitViolatesCustody',['Fault'],'not(safe(earlyExit(s)))','Native168 failed strict-drain oracle/known duties at exit'),('actualCurrentFailureQuarantinesOwnedScope',['Fault'],'s.failed and s.closing and s.owned and not(s.exited)','Native169 actual current cancellation/quarantine/known or retiring duties'),('actualLaterNativeRetirementSettlesCustody',['Fault','NativeSettled'],'s.failed and not(s.owned) and not(s.closed or s.exited)','Native169 separately verified original strict Native/physical/journal/confirmation close projects independent settlement'),('actualOriginalStrictClose',['Fault','NativeSettled','StrictRetire'],'s.failed and s.closed and not(s.owned or s.exited)','Native169 original native retire/closed policy report/empty custody'),('actualFailureExitAfterStrictClose',['Fault','NativeSettled','StrictRetire','Exit'],'s.failed and s.closed and s.exited and not(s.owned)','Native169 original failure1 after strict closed state/seven other normal exits/private cleanup')]
runs=[];observations=[]
for name,events,condition,origin in cases:
 runs.append(' run '+name+'=init'+''.join('.then(fire('+e+'))' for e in events)+'.then(check('+condition+'))');observations.append(dict(name=name,events=events,nativeObservation=origin,condition=condition))
(out/'inputs/concrete_current_failure_drain.qnt').write_text('module concrete_current_failure_drain {\n import current_failure_drain.* from "./current_failure_drain"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n')
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Five bounded abstract stages coupled to actual same immutable Native168 failed and Native169 fixed current WebKit cancellation/drain oracle. Actual current owning/closing/strict closed policy states, original real finish/error/failure1 chronology, original strict Native closure and private cleanup are separately checked. NativeSettled projects that independently verified strict physical/journal/confirmation gate; this is not a complete step refinement or proof of all native transitions/schedules, uncertain/process/reload recovery, future async classes, physical reveal/hardware/workload or release. Failure1 remains failure, never normal exit. No source/ABI/deadline/issuer/single policy/grant resets.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 names='|'.join(x[0] for x in cases)
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_current_failure_drain.qnt']),('selected',[str(tool),'test','concrete_current_failure_drain.qnt','--main=concrete_current_failure_drain','--backend=typescript','--match=^('+names+')$','--seed=1390043','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==5 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256'];d.update(passed=True,coupledQuintChecks=5)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
