"""Actual retained Native URI/GIO reader and pending popup lifecycle projection."""
import hashlib,json,pathlib,resource,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v134';native=r/'implementation/warlock-client-provider-native-v151';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
p=next(native.glob('qa/native-controlled-*/report.json'));n=load(p);assert n['passed'] and n['cleanupPassed'] and len(n['checks'])==51 and len(n['ownedExitCodes'])==18 and all(x['exitCode']==0 for x in n['ownedExitCodes'])
pre=load(native/'qa/preflight.json')
for name,h in pre['inputs'].items():assert sha(name)==h,name
for name,h in n['artifacts'].items():assert sha(p.parent/name)==h,name
log=p.parent/'private-evidence/controlled-host.log';text=log.read_text();checks={c['name']:c for c in n['checks']};assert all(c['passed'] for c in checks.values())
held=checks['controlledHeldReaderBlocksEarlyNativeRetirement']['state'];pending=checks['controlledActualLaterGTKPopupKeepsOldReaderDuty']['state'];closed=checks['controlledFirstRealmStrictlyClosedBeforeFreshRenderer']['state'];second=checks['controlledReopenOriginalBindingLaterNativeEpoch']['state']
for state in [held,pending]:
 q=state['privatePolicy'];assert q['realm']['epoch']=='1' and q['realm']['closing'] and not q['realm']['closed'] and len(q['models'])==1 and not q['models'][0]['model']['demand'] and q['models'][0]['model']['accepted'] is None and len(q['models'][0]['model']['retiring'])==1 and q['models'][0]['model']['retiring'][0]['owned']
assert pending['privatePolicy']['visuals']['surface']['lease']=='2' and pending['privatePolicy']['visuals']['surface']['mode']!='closed'
assert closed['privatePolicy']['realm']['closed'] and not closed['privatePolicy']['models'] and not closed['retainedInputs'] and not closed['postedTickets'] and not closed['confirmations'] and closed['transport']['pending']==0
assert second['privatePolicy']['realm']['epoch']=='2' and second['privatePolicy']['commands']['binding']==held['privatePolicy']['commands']['binding']
markers=['controlled-native-reader-held: epoch=1 actualGIO=1 firstByte=137 ','controlled-native-reader-probed: epoch=1 heldRead=-1 heldDenied=1 freshDenied=1 actualGIO=1 physicalSettlement=0','controlled-native-reader-released: epoch=1 originalCloseCalls=1 nativeGrantReset=0','controlled-native-realm-retired: epoch=1 ','controlled-native-replacement-admission: retiredEpoch=1 pendingPopup=1 ','controlled-native-reopened: previousEpoch=1 nativeEpoch=2 samePolicy=1 sameBinding=1 originalNative=1 grantResets=0 rendererPolicies=0']
positions=[text.index(marker) for marker in markers];assert positions==sorted(positions)
host=gui/'native/controlled-preview-host.h';code=host.read_text();assert 'preview_uri_router_open(controlled_router,popup_view,uri,&length,error)' in code and 'g_input_stream_close(controlled_held_reader,NULL,error)' in code and 'warlock_policy_driver_policy(controlled_driver,error)!=original_policy' in code
out=pathlib.Path(__file__).with_name('retained-reader-coupling-v134-'+str(time.time_ns()));out.mkdir();(out/'inputs').mkdir()
for name in ['host_realm_lifecycle.qnt','controlled_reader_lifetime_v4.qnt']:shutil.copy2(gui/'spec'/name,out/'inputs'/name)
ops=['event(OpenIntent)','event(DOMReady)','event(Admit)','event(Initialize)','event(Apply)'];stages=[];runs=[]
for name,more,condition,origin in [
 ('heldOriginal',['hold'],'reader==HeldCurrent and s.epoch==1 and s.context==1 and s.duty and closes==0',markers[0]),
 ('closingReader',['event(ClosePopup)'],'reader==HeldRevoked and s.closing and s.duty and s.native and not(s.current)','controlledHeldReaderBlocksEarlyNativeRetirement'),
 ('revokedReads',['probe'],'reader==HeldRevoked and probed and closes==0 and s.duty',markers[1]),
 ('pendingPopup',['event(OpenIntent)','event(DOMReady)'],'s.popup and s.lease==2 and s.epoch==1 and s.context==1 and s.duty and s.closing','controlledActualLaterGTKPopupKeepsOldReaderDuty'),
 ('oneOriginalClose',['release'],'reader==Released and closes==1 and s.duty and s.native',markers[2]),
 ('independentStrictClose',['event(Drain)','event(Retire)'],'not(s.duty) and not(s.native) and s.retired and s.epoch==1','controlledFirstRealmStrictlyClosedBeforeFreshRenderer'),
 ('samePopupReplacement',['event(Replace)'],'s.popup and s.lease==2 and s.context==2 and not(s.dom) and s.policy==1',markers[4]),
 ('freshLaterEpoch',['event(DOMReady)','event(Admit)','event(Initialize)','event(Apply)'],'s.current and s.epoch==2 and s.context==2 and s.lease==2 and closes==1 and s.policy==1','controlledReopenOriginalBindingLaterNativeEpoch')]:
 ops+=more;runs.append(' run '+name+'=initReader'+''.join('.then('+op+')' for op in ops)+'.then(check('+condition+'))');stages.append(dict(name=name,nativeObservation=origin,expected=condition,operations=list(ops)))
source='module concrete_retained_reader {\n import host_realm_lifecycle.* from "./host_realm_lifecycle"\n import controlled_reader_lifetime_v4.* from "./controlled_reader_lifetime_v4"\n action check(ok:bool):bool=all{assert(ok and readerSafety),s\'=s,reader\'=reader,probed\'=probed,closes\'=closes}\n'+'\n'.join(runs)+'\n}\n';(out/'inputs/concrete_retained_reader.qnt').write_text(source)
tool=pathlib.Path('/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint');inputs={str(x):sha(x) for x in [p,native/'qa/preflight.json',log,host,gui/'spec/host_realm_lifecycle.qnt',gui/'spec/controlled_reader_lifetime_v4.qnt',pathlib.Path(__file__)]}
d=dict(passed=False,inputs=inputs,quint=dict(path=str(tool),sha256=sha(tool)),commands=[],observations=stages,scope='Eight retained-reader/pending-popup lifecycle abstraction stages coupled to actual Native151 real original URI/GIO read, revoked held/fresh reads, original owned Retiring job, current later GTK popup, one actual reader close, original independent strict Native close, same policy/binding and current second image/output. Reader close is not Native settlement; model Drain projects separately verified original C/physical/journal/confirmation closure. No complete transition refinement, rapid scheduling variant, physical reveal/hardware, recovery or full release claim.',nativeAcceptance=False,fullReleaseAccepted=False)
try:
 for name,args in [('typecheck',[str(tool),'typecheck','concrete_retained_reader.qnt']),('selected',[str(tool),'test','concrete_retained_reader.qnt','--main=concrete_retained_reader','--backend=typescript','--match=^('+'|'.join(x['name'] for x in stages)+')$','--seed=1480042','--max-samples=1','--out-itf='+str(out/'coupled-{test}-{seq}.itf.json')])]:
  q=subprocess.run(args,cwd=out/'inputs',capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(q.stdout);(out/(name+'.stderr')).write_text(q.stderr);d['commands'].append(dict(name=name,argv=args,exitCode=q.returncode));print(name,q.returncode,flush=True);assert q.returncode==0,q.stdout+q.stderr
 assert len(list(out.glob('coupled-*.itf.json')))==8 and all(sha(name)==h for name,h in inputs.items()) and sha(tool)==d['quint']['sha256']
 d.update(passed=True,coupledQuintChecks=8,observedLifecycleStages=8,actualNativeReportSHA256=sha(p))
except Exception as error:d['error']=repr(error)
d['artifacts']={str(x.relative_to(out)):sha(x) for x in out.rglob('*') if x.is_file()};(out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'passed':d['passed'],'report':str(out/'report.json'),'error':d.get('error','')}),flush=True);raise SystemExit(not d['passed'])
