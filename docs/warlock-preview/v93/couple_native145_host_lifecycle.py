"""Couple six lifecycle stages to actual original native observations."""
import hashlib,json,pathlib,re,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v132';native=r/'implementation/warlock-client-provider-native-v145'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report=next(native.glob('qa/native-controlled-*/report.json'));n=json.loads(report.read_text());assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==46 and all(x['exitCode']==0 for x in n['ownedExitCodes'])
pre=json.loads((native/'qa/preflight.json').read_text())
for p,h in pre['inputs'].items():assert sha(p)==h,p
for p,h in n['artifacts'].items():assert sha(report.parent/p)==h,p
log=report.parent/'private-evidence/controlled-host.log';text=log.read_text();checks={c['name']:c for c in n['checks']};assert all(c['passed'] for c in checks.values())
first=checks['controlledOriginalNativeTicketsActuallyIssuedAndDelivered']['state'];second=checks['controlledReopenOriginalBindingLaterNativeEpoch']['state'];closed1=checks['controlledFirstRealmStrictlyClosedBeforeFreshRenderer']['state'];closed2=checks['controlledSecondRealmOriginalCustodyDrainedAndStrictlyClosed']['state']
assert first['privatePolicy']['commands']['binding']==second['privatePolicy']['commands']['binding']
assert first['privatePolicy']['realm']['epoch']=='1' and second['privatePolicy']['realm']['epoch']=='2'
for state in [closed1,closed2]:
 assert state['privatePolicy']['realm']['closed'] and not state['privatePolicy']['models'] and not state['retainedInputs'] and not state['postedTickets'] and not state['confirmations'] and not state['returnedEventBatches'] and state['transport']['pending']==0
paints=[json.loads(line.split(': ',1)[1]) for line in text.splitlines() if line.startswith('controlled-native-paint-observation: ')]
assert [(p['nativeEpoch'],p['navigation'],p['lease'],p['opacity']) for p in paints]==[('1','1','1',0),('2','2','2',0)]
assert 'controlled-native-reopened: previousEpoch=1 nativeEpoch=2 samePolicy=1 sameBinding=1 originalNative=1 grantResets=0 rendererPolicies=0' in text
host=gui/'native/controlled-preview-host.h';source=host.read_text();assert 'warlock_policy_driver_policy(controlled_driver,error)!=original_policy' in source
out=pathlib.Path(__file__).with_name('host-lifecycle-coupling-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/host_realm_lifecycle.qnt',out/'inputs/host_realm_lifecycle.qnt')
# Native strict close/independent custody gates are checked above. The abstract
# Drain below projects that proof; a UI close is never used to infer settlement.
open_events=['OpenIntent','DOMReady','Admit','Initialize','Apply'];close_events=['ClosePopup','Drain','Retire'];events=[];runs=[];observations=[]
for name,more,epoch,context,lease,current,retired,origin in [
 ('firstCurrent',open_events,1,1,1,True,False,'controlledOriginalNativeTicketsActuallyIssuedAndDelivered'),
 ('firstStrictClose',close_events,1,1,1,False,True,'controlledFirstRealmStrictlyClosedBeforeFreshRenderer'),
 ('firstFreshContext',['Replace'],1,2,1,False,False,'controlled-renderer-context-replaced: retiredEpoch=1'),
 ('secondCurrent',open_events,2,2,2,True,False,'controlledReopenOriginalBindingLaterNativeEpoch'),
 ('secondStrictClose',close_events,2,2,2,False,True,'controlledSecondRealmOriginalCustodyDrainedAndStrictlyClosed'),
 ('secondFreshContext',['Replace'],2,3,2,False,False,'controlled-renderer-context-replaced: retiredEpoch=2')]:
 events+=more
 if origin.startswith('controlled-renderer-context-replaced:'):assert origin+' ' in text
 condition=f's.epoch=={epoch} and s.context=={context} and s.lease=={lease} and s.current=={str(current).lower()} and s.retired=={str(retired).lower()} and s.policy==1 and not(s.reveal)'
 runs.append(' run '+name+'=init'+''.join('.then(fire('+e+'))' for e in events)+'.then(check('+condition+'))')
 observations.append(dict(name=name,events=list(events),nativeObservation=origin,expected=dict(epoch=epoch,context=context,lease=lease,current=current,retired=retired,policy=1,reveal=False)))
qnt='module concrete_host_lifecycle {\n import host_realm_lifecycle.* from "./host_realm_lifecycle"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n';(out/'inputs/concrete_host_lifecycle.qnt').write_text(qnt)
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
inputs={str(p):sha(p) for p in [report,native/'qa/preflight.json',log,host,gui/'spec/host_realm_lifecycle.qnt',pathlib.Path(__file__)]}
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Six context/realm lifecycle abstraction checkpoints coupled to actual Native145 two-cycle GTK/WebKit original binding/current source image and strict C/Bootstrap closure evidence. Same-policy assertion is backed by held native source pointer comparison. Drain is a projection of separately verified original physical/journal/confirmation strict close; model stages do not establish every implementation transition, pending-intent, async faults, physical reveal/hardware or full release.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_host_lifecycle.qnt']),('selected',[str(tool),'test','concrete_host_lifecycle.qnt','--main=concrete_host_lifecycle','--backend=typescript','--match=^(firstCurrent|firstStrictClose|firstFreshContext|secondCurrent|secondStrictClose|secondFreshContext)$','--seed=1450041','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==6 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,coupledQuintChecks=6,observedLifecycleStages=6,actualNativeReportSHA256=sha(report))
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
