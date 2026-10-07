"""Couple actual failed/fixed reload observations to bounded Quint stages."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v141'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text());inputs={};data={}
for v,passed in [(176,False),(184,True)]:
 root=r/f'implementation/warlock-client-provider-native-v{v}';ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];n=load(p);pre=load(root/'qa/preflight.json');assert n['passed']==passed and n['cleanupPassed']
 for f,h in pre['inputs'].items():assert sha(f)==h,f
 for f,h in n['artifacts'].items():assert sha(p.parent/f)==h,f
 log=p.parent/'private-evidence/controlled-host.log';inputs.update({str(p):sha(p),str(root/'qa/preflight.json'):sha(root/'qa/preflight.json'),str(log):sha(log)})
 data[v]=(n,{c['name']:c for c in n['checks']},log.read_text())
old,oc,ot=data[176];n,c,t=data[184]
assert not oc['controlledReloadDoesNotFailTheOriginalHost']['passed'] and 'Renderer navigation retains original live policy; reload recovery not qualified' in ot
assert n['actualControlledRendererReloadQualified'] and n['actualSamePolicyRetained'] and n['actualSamePopupLeaseAcrossReloadQualified'] and all(x['passed'] for x in n['checks']) and all(x['exitCode']==0 for x in n['ownedExitCodes'])
closed=c['controlledReloadOriginalRealmStrictlyClosedBeforeReplacement']['state'];assert closed['privatePolicy']['realm']['closed'] and not closed['privatePolicy']['models'] and not closed['retainedInputs'] and not closed['postedTickets'] and not closed['confirmations'] and not closed['returnedEventBatches'] and closed['transport']['pending']==0
reopened=c['controlledReloadOriginalPolicyAndNativeBindingRetained']['state'];assert reopened['privatePolicy']['realm']['epoch']=='2' and reopened['privatePolicy']['commands']['binding']==closed['privatePolicy']['commands']['binding'] and reopened['privatePolicy']['visuals']['surface']['lease']=='1'
states=[json.loads(line.split(': ',1)[1]) for line in t.splitlines() if line.startswith('controlled-native-private-status: ')]
assert any(s['privatePolicy']['realm']['epoch']=='1' and s['privatePolicy']['models'] and s['privatePolicy']['models'][0]['model']['accepted'] for s in states)
assert any(s['privatePolicy']['realm']['epoch']=='1' and s['privatePolicy']['realm']['closing'] and not s['privatePolicy']['realm']['closed'] for s in states)
markers=['controlled-native-qa-reload-start: epoch=1 navigation=2','controlled-native-reload-quarantine: epoch=1 navigation=2','controlled-native-realm-retired: epoch=1','controlled-renderer-context-replaced: retiredEpoch=1','controlled-native-reopened: previousEpoch=1 nativeEpoch=2','controlled-renderer-initialized: nativeEpoch=2','controlled-native-realm-retired: epoch=2','shared-host-exit: failure=0 rendered=1']
positions=[t.index(x) for x in markers];assert positions==sorted(positions)
assert 'Native client producer failed:' not in t and 'Controlled native teardown incomplete:' not in t
assert n['actualReopenedNativePaint']['navigation']=='3' and n['actualReopenedNativePaint']['lease']=='1' and n['actualReopenedNativePaint']['opacity']==0
assert n['actualReopenedWebKitPixels']['red']==19200 and n['actualBeforeReloadSourcePixels']['red']==19200 and n['actualReopenedClosedCurtainRegionPixels']['red']==0
for p in [gui/'native/controlled-preview-host.h',gui/'spec/known_renderer_reload.qnt',pathlib.Path(__file__)]:inputs[str(p)]=sha(p)
out=pathlib.Path(__file__).with_name('known-renderer-reload-coupling-v141-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir();shutil.copy2(gui/'spec/known_renderer_reload.qnt',out/'inputs/known_renderer_reload.qnt')
base=['Reload','NativeSettled','StrictRetire'];fresh=base+['Replace','DOMReady','Admit']
cases=[('actualLegacyUncertainReload',[],'legacyReload(s).failed and legacyReload(s).unknown and legacyReload(s).owned','Native176 actual reload/host1/refused strict teardown'),('actualKnownReloadQuarantine',['Reload'],'s.closing and s.owned and not(s.initialized or s.failed)','Native184 actual navigation2/quarantine and epoch1 closing custody'),('actualOriginalStrictClosedRealm',base,'s.closed and not(s.owned or s.initialized)','Native184 independently verified strict Native close/empty custody'),('actualSamePopupReplacement',base+['Replace'],'s.replaced and s.closed and s.navigation==3 and s.lease==1','Native184 original context replacement inside same current GTK popup lease1'),('actualFreshDOMLaterEpoch',fresh,'s.epoch==2 and s.initialized and s.policy==1 and s.lease==1','Native184 fresh DOM/initializer and original later native epoch2 on identical policy/binding'),('actualMonotonicSnapshot',fresh+['Capture'],'s.snapshot==2 and s.navigation==3 and s.epoch==2','Native184 original first/source PNG and new request2/source red19200/current before-after opacity0 output'),('actualFinalStrictClose',fresh+['Capture','Reload','NativeSettled','StrictRetire'],'s.closed and not(s.owned or s.initialized) and s.epoch==2','Native184 actual pointer closes final popup and independently strict Native retirement/empty custody/normal exits/cleanup; abstract Reload projects visual quarantine only, not that pointer trigger')]
runs=[];observations=[]
for name,events,condition,origin in cases:
 runs.append(' run '+name+'=init'+''.join('.then(fire('+e+'))' for e in events)+'.then(check('+condition+'))');observations.append(dict(name=name,events=events,condition=condition,nativeObservation=origin))
(out/'inputs/concrete_known_reload.qnt').write_text('module concrete_known_reload {\n import known_renderer_reload.* from "./known_renderer_reload"\n action check(ok:bool):bool=all{assert(ok and safety),s\'=s}\n'+'\n'.join(runs)+'\n}\n')
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint')
d={'passed':False,'inputs':inputs,'quint':{'path':str(tool),'sha256':sha(tool)},'observations':observations,'commands':[],'scope':'Seven bounded abstract stages projected from independently checked actual Native176 failure and unchanged Native184 reload oracle. Original-view real navigation2/quarantine/closing, independently original strict close/empty custody before same-popup renderer replacement/navigation3/fresh DOM/later epoch2 on same policy/binding/lease1, actual first/request2 pixels and final strict close/normal exits/private cleanup. NativeSettled projects independent native strict closure, never UI inference. Final abstract Reload projects actual pointer-close visual quarantine, not its trigger. Not full step refinement, arbitrary/process/uncertain reload recovery, hardware/reveal/full workload/full S09/release.','nativeAcceptance':False,'fullReleaseAccepted':False}
try:
 names='|'.join(x[0] for x in cases)
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_known_reload.qnt']),('selected',[str(tool),'test','concrete_known_reload.qnt','--main=concrete_known_reload','--backend=typescript','--match=^('+names+')$','--seed=1410043','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  p=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=p.returncode));print(name,p.returncode,flush=True);assert p.returncode==0,p.stdout+p.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==7 and all(sha(p)==h for p,h in inputs.items()) and sha(tool)==d['quint']['sha256'];d.update(passed=True,coupledQuintChecks=7)
except Exception as error:d['error']=repr(error)
d['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
