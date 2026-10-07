"""Freeze known real renderer reload and separate original regressions/failures."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v141'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
out=pathlib.Path(__file__).with_name('component-report-gui141-known-reload.json');assert not out.exists()
items=[(184,34,12,'native184_renderer_reload_runner.py'),(178,29,13,'native138_controlled_curtain_runner.py'),(179,36,13,'native159_cancelled_reopened_snapshot_runner.py'),(180,22,8,'native168_current_failure_drain_runner.py'),(181,51,17,'native149_rapid_pending_reader_runner.py'),(182,18,8,'native141_delayed_snapshot_runner.py'),(183,35,13,'native155_reopened_snapshot_runner.py'),(177,23,8,'native176_renderer_reload_runner.py')]
native={};reports={};build=None
for v,count,exits,runner in items:
 root=r/f'implementation/warlock-client-provider-native-v{v}';ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];d=load(p);pre=load(root/'qa/preflight.json')
 assert d['passed']==(v!=177) and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits
 assert all(c['passed'] for c in d['checks'])
 assert all(c['exitCode']==(1 if v in {177,180} and c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
 assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 candidate=pathlib.Path(pre['controlledHostBuild']);assert build is None or candidate==build;build=candidate
 native[v]=(root,p,d,pre);reports[f'native{v}']={'path':str(p),'sha256':sha(p),'passed':d['passed'],'checks':count,'ownedExits':exits}
n=native[184][2];p=native[184][1];t=(p.parent/'private-evidence/controlled-host.log').read_text()
assert n['actualControlledRendererReloadQualified'] and n['actualSamePopupLeaseAcrossReloadQualified'] and n['actualSamePolicyRetained'] and n['actualOriginalNativeBindingRetained'] and n['nativeGrantResets']==0
assert n['actualBeforeReloadSourcePixels']['red']==n['actualReopenedWebKitPixels']['red']==19200 and n['actualReopenedClosedCurtainRegionPixels']['red']==0
paint=n['actualReopenedNativePaint'];assert paint['nativeEpoch']=='2' and paint['navigation']=='3' and paint['lease']=='1' and paint['opacity']==0 and not paint['physicalFrameQualified']
markers=['controlled-native-qa-reload-start: epoch=1 navigation=2','controlled-native-reload-quarantine: epoch=1 navigation=2','controlled-native-realm-retired: epoch=1','controlled-renderer-context-replaced: retiredEpoch=1','controlled-native-reopened: previousEpoch=1 nativeEpoch=2','controlled-renderer-initialized: nativeEpoch=2','controlled-native-realm-retired: epoch=2','shared-host-exit: failure=0 rendered=1'];positions=[t.index(x) for x in markers];assert positions==sorted(positions)
assert 'GLib-GObject-CRITICAL' not in t and 'Controlled native teardown incomplete:' not in t and 'Native client producer failed:' not in t
assert native[180][2]['gracefulCurrentFailureDrainQualified'] and native[180][2]['actualCurrentFailureNativeCustodyDrained'] and native[180][2]['expectedFailureExitCode']==1
assert native[179][2]['actualCancelledOldResultQualified'] and native[181][2]['actualRapidPointerCloseReopenQualified'] and native[183][2]['actualOldResultAcrossReopenedRealmQualified']
assert 'image.name.startswith' in native[177][2]['traceback']
b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for n,row in b[category].items():assert sha(n)==row['sha256'],n
reports['build']={'path':str(build),'sha256':sha(build),'passed':True,'commands':119}
model=next(gui.glob('qa/known-renderer-reload-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==9 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
for n,h in q['artifacts'].items():assert sha(model.parent/n)==h,n
assert sha(q['quint']['path'])==q['quint']['sha256'];reports['reloadQuint']={'path':str(model),'sha256':sha(model),'passed':True}
coupling=next((r/'docs/warlock-preview/v93').glob('known-renderer-reload-coupling-v141-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==7
for n,h in c['inputs'].items():assert sha(n)==h,n
for n,h in c['artifacts'].items():assert sha(coupling.parent/n)==h,n
assert sha(c['quint']['path'])==c['quint']['sha256'];reports['reloadCoupling']={'path':str(coupling),'sha256':sha(coupling),'passed':True}
parent=r/'implementation/warlock-preview-provider-v140';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and not held['passed'] and held['actualRendererReloadCounterexample']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets','spec','qa']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name!='controlled-preview-host.h':assert sha(gui/base/p.name)==sha(p),p
scope='GUI141 repairs actual held140/Native176 reload-as-uncertain failure. Known trusted same-URI original initialized view LOAD_STARTED navigation2 invalidates visual authority and urgently quarantines same original realm without claiming native settlement. Original sticky Native input/step/poll/receipts and strict policy/physical/ticket/journal/confirmation close/empty custody precede fresh renderer context replacement inside SAME GTK popup lease1. Fresh DOM/fixed native grant admits later epoch2 on identical original policy/binding, navigation3 and original request2. Actual18434/12 proves real first and current source red19200, current image before-after original grim opacity0 region, final strict closure/all normal owned exits/private cleanup/no criticals. Native177 premature snapshot-wait assertion failure retained; fresh184 waits for request2 while accepting known request1 as pending, keeping original six-second deadline and every actual pixel/output/final strict close oracle. Original normal17829/13, canceled-old17936/13, current-failure18022/host1+seven other normal, rapid18151/17, delayed18218/8 and old-success18335/13 pass separately. Full119, new reload Quint9/200 and7 actual projected stages pass. Historical wrong-build-entry failure and coupling closed-command schema check failure retained. Only host known navigation handling changed; no issuer/Elm reducer/physical product/grant/nav/snapshot/clock/reset/replay changes. Unexpected/uncertain/failing ownership remains failclosed; actual arbitrary/unknown/process/repeated reload schedules, physical reveal/hardware/pressure/full workload/RSS, original full S09 and release remain open. Installed desktop/drafts/foreign preserved.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualKnownRendererReloadQualified':True,'actualSamePopupLeaseAcrossReloadQualified':True,'actualSamePolicyRetained':True,'actualOriginalNativeBindingRetained':True,'reloadNativeChecks':34,'reloadNormalOwnedExits':12,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'cancelledOldResultNativeChecks':36,'cancelledOldResultNormalOwnedExits':13,'currentFailureNativeControls':22,'currentFailureExpectedExitCode':1,'currentFailureOtherNormalOwnedExits':7,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'successfulOldResultNativeChecks':35,'successfulOldResultNormalOwnedExits':13,'reloadQuintScenarios':9,'reloadQuintInvariantSamples':200,'reloadCoupledStages':7,'originalReloadCounterexampleRetained':True,'prematureSnapshotObserverFailureRetained':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'privateSessionCleanupPassed':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'arbitraryNavigationRecoveryQualified':False,'uncertainRecoveryQualified':False,'processRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'reports':reports,'scope':scope,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
roots=[gui,*[native[v][0] for v,_,_,_ in items]]
for root in roots:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root!=gui:
  v=next(v for v,_,_,_ in items if root==native[v][0]);own.update(passed=v!=177,nativeChecks=len(native[v][2]['checks']),ownedExits=len(native[v][2]['ownedExitCodes']),actualKnownRendererReloadQualified=v==184,actualObserverFailureRetained=v==177,normalControlledHostClosureQualified=v not in {177,180},gracefulCurrentFailureDrainQualified=v==180,scope=native[v][2]['scope'])
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS '+scope+' Next PUBLIC103 then real uncertain/process recovery and original-clock pressure/expiry/physical/full-release gates.'],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in roots]+[str(out.relative_to(r))]))
