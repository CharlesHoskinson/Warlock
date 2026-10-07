"""Project independently checked actual shared-process failure/drain stages."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v143';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text());inputs={};data={}
for v,passed in [(186,False),(187,True)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];n=load(p);pre=load(root/'qa/preflight.json');assert n['passed']==passed and n['cleanupPassed']
 for f,h in pre['inputs'].items():assert sha(f)==h,f
 for f,h in n['artifacts'].items():assert sha(p.parent/f)==h,f
 log=p.parent/'private-evidence/controlled-host.log';inputs.update({str(p):sha(p),str(root/'qa/preflight.json'):sha(root/'qa/preflight.json'),str(log):sha(log)})
 data[v]=(n,{c['name']:c for c in n['checks']},log.read_text())
old,oc,ot=data[186];n,c,t=data[187]
assert not oc['controlledSharedProcessNativeCustodyClosedBeforeGTKRecovery']['passed'] and 'native-recovery-ready:' in ot and 'Controlled native teardown incomplete:' in ot
assert n['actualSharedWebKitProcessTerminationQualified'] and n['actualKnownSharedProcessNativeDrainQualified'] and n['actualGTKRecoveryAfterStrictDrainQualified'] and n['expectedFailureExitCode']==1 and len(n['checks'])==21 and len(n['ownedExitCodes'])==8
assert all(x['passed'] for x in n['checks']) and all(x['exitCode']==(1 if x['name']=='controlled-host' else 0) for x in n['ownedExitCodes'])
closed=c['controlledSharedProcessNativeCustodyClosedBeforeGTKRecovery']['state'];assert closed['privatePolicy']['realm']['closed'] and not closed['privatePolicy']['models'] and not closed['retainedInputs'] and not closed['postedTickets'] and not closed['confirmations'] and not closed['returnedEventBatches'] and closed['transport']['pending']==0
states=[json.loads(line.split(': ',1)[1]) for line in t.splitlines() if line.startswith('controlled-native-private-status: ')]
assert any(s['privatePolicy']['realm']['epoch']=='1' and s['privatePolicy']['models'] and s['privatePolicy']['models'][0]['model']['accepted'] for s in states)
assert any(s['privatePolicy']['realm']['epoch']=='1' and s['privatePolicy']['realm']['closing'] and not s['privatePolicy']['realm']['closed'] for s in states)
assert closed['privatePolicy']['realm']['epoch']=='1' and t.count('controlled-renderer-initialized:')==1
assert t.count('Web process terminated: 2')>=2 and 'controlled-native-qa-process-terminated: epoch=1 currentView=1 reason=2 actualWebKitSignal=1 nativeSettlement=0' in t
markers=['controlled-native-qa-process-stop-requested:','controlled-native-renderer-failure-drain: epoch=1','controlled-native-realm-retired: epoch=1','native-recovery-ready:','shared-host-exit: failure=1 rendered=1'];positions=[t.index(x) for x in markers];assert positions==sorted(positions)
assert 'controlled-native-reopened:' not in t and 'controlled-renderer-context-replaced:' not in t and 'Controlled native teardown incomplete:' not in t and 'GLib-GObject-CRITICAL' not in t
assert n['actualProcessBeforeStopSourcePixels']['red']==19200 and not n['wholeHostRestartQualified'] and not n['durableUnknownRecoveryQualified']
for p in [gui/'native/host.c',gui/'native/shared-host.c',gui/'native/controlled-preview-host.h',gui/'spec/shared_process_drain.qnt',pathlib.Path(__file__)]:inputs[str(p)]=sha(p)
out=pathlib.Path(__file__).with_name('shared-process-drain-coupling-v143-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/shared_process_drain.qnt',out/'inputs/shared_process_drain.qnt')
closed_events=['Signal','NativeSettled','StrictRetire'];recovery=closed_events+['Recovery']
cases=[('actualLegacyPrematureRecovery',['Signal'],'not(safe(earlyRecovery(s)))','Native186 actual original termination/recovery while known models remain/strict teardown refusal'),('actualProcessSignalsPreserveKnownDuties',['Signal','Signal'],'s.failed and s.processFailed and s.closing and s.owned and not(s.recovery)','Native187 actual shared view termination signals/quarantine and original epoch1 closing custody'),('actualOriginalStrictNativeClose',closed_events,'s.failed and s.closed and not(s.owned or s.recovery)','Native187 separately verified original Native policy/physical/journal/confirmation closure and empty custody'),('actualGTKRecoveryOnlyAfterClose',recovery,'s.failed and s.closed and s.recovery and not(s.owned)','Native187 original native-recovery-ready/GTK controls after strict close and original backend normal'),('actualFailureExitAfterRecovery',recovery+['Exit'],'s.failed and s.closed and s.recovery and s.exited','Native187 explicit dismissal retains original failure1, seven other normal exits/private cleanup/no criticals'),('actualNoOriginalIdentityReset',recovery,'s.policy==1 and s.epoch==1 and s.navigation==1 and s.snapshot==1','Native187 original admitted current epoch1/nav1/request1 source, no replacement/reopen/reset; original driver policy preserved and final strict close')]
runs=[];observations=[]
for name,events,condition,origin in cases:
 runs.append(' run '+name+'=init'+''.join('.then(fire('+e+'))' for e in events)+'.then(check('+condition+'))');observations.append(dict(name=name,events=events,condition=condition,nativeObservation=origin))
(out/'inputs/concrete_shared_process_drain.qnt').write_text('module concrete_shared_process_drain {\n import shared_process_drain.* from "./shared_process_drain"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n')
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Six bounded abstract stages projected from independently checked actual Native186 shared-process termination failure and unchanged187 process-stop/drain-before-recovery oracle. Real process reason2/multiple related view signals/current source/quarantine/closing, independently original strict Native closed-empty custody BEFORE original GTK recovery and explicit dismissal/failure1/seven other normal exits/private cleanup. NativeSettled projects original independent physical/journal/confirmation closure, never process disappearance or UI inference. Not a full step refinement or proof of all async delivery-error/termination schedules, uncertain custody, whole-host restart/window commands/durable Unknown, physical/hardware/full S09/release.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 names='|'.join(x[0] for x in cases)
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_shared_process_drain.qnt']),('selected',[str(tool),'test','concrete_shared_process_drain.qnt','--main=concrete_shared_process_drain','--backend=typescript','--match=^('+names+')$','--seed=1430043','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==6 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256'];d.update(passed=True,coupledQuintChecks=6)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
