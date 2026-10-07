"""Freeze actual shared-process known native drain and separate regressions."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v143';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
out=pathlib.Path(__file__).with_name('component-report-gui143-shared-process-drain.json');assert not out.exists()
items=[(187,21,8,'native186_process_stop_drain_runner.py'),(188,29,13,'native138_controlled_curtain_runner.py'),(189,34,12,'native184_renderer_reload_runner.py'),(190,22,8,'native168_current_failure_drain_runner.py'),(191,36,13,'native159_cancelled_reopened_snapshot_runner.py'),(192,51,17,'native149_rapid_pending_reader_runner.py'),(193,18,8,'native141_delayed_snapshot_runner.py'),(194,35,13,'native155_reopened_snapshot_runner.py')]
native={};reports={};build=None
for v,count,exits,runner in items:
 root=r/f'implementation/warlock-client-provider-native-v{v}';ps=list(root.glob('qa/native-controlled-*/report.json'));assert len(ps)==1;p=ps[0];d=load(p);pre=load(root/'qa/preflight.json')
 assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks'])
 assert all(c['exitCode']==(1 if v in {187,190} and c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
 assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
 candidate=pathlib.Path(pre['controlledHostBuild']);assert build is None or candidate==build;build=candidate
 native[v]=(root,p,d,pre);reports[f'native{v}']={'path':str(p),'sha256':sha(p),'checks':count,'ownedExits':exits,'passed':True}
n=native[187][2];p=native[187][1];t=(p.parent/'private-evidence/controlled-host.log').read_text()
assert n['actualSharedWebKitProcessTerminationQualified'] and n['actualKnownSharedProcessNativeDrainQualified'] and n['actualGTKRecoveryAfterStrictDrainQualified'] and n['expectedFailureExitCode']==1 and not n['normalControlledHostClosureQualified'] and not n['wholeHostRestartQualified'] and not n['durableUnknownRecoveryQualified']
assert n['actualProcessBeforeStopSourcePixels']['red']==19200
markers=['controlled-native-qa-process-stop-requested:','controlled-native-renderer-failure-drain: epoch=1','controlled-native-realm-retired: epoch=1','native-recovery-ready:','shared-host-exit: failure=1 rendered=1'];positions=[t.index(x) for x in markers];assert positions==sorted(positions)
assert t.count('Web process terminated: 2')>=2 and 'currentView=1 reason=2 actualWebKitSignal=1 nativeSettlement=0' in t
assert 'controlled-native-reopened:' not in t and 'controlled-renderer-context-replaced:' not in t and 'GLib-GObject-CRITICAL' not in t and 'Controlled native teardown incomplete:' not in t
assert native[189][2]['actualControlledRendererReloadQualified'] and native[189][2]['actualSamePolicyRetained'] and native[189][2]['actualReopenedNativePaint']['opacity']==0 and native[189][2]['actualReopenedNativePaint']['navigation']=='3' and native[189][2]['actualReopenedNativePaint']['lease']=='1'
assert native[190][2]['gracefulCurrentFailureDrainQualified'] and native[190][2]['actualCurrentFailureNativeCustodyDrained'] and native[191][2]['actualCancelledOldResultQualified'] and native[192][2]['actualRapidPointerCloseReopenQualified'] and native[194][2]['actualOldResultAcrossReopenedRealmQualified']
b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for n,row in b[category].items():assert sha(n)==row['sha256'],n
reports['build']={'path':str(build),'sha256':sha(build),'passed':True,'commands':119}
model=next(gui.glob('qa/shared-process-drain-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==9 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
for n,h in q['artifacts'].items():assert sha(model.parent/n)==h,n
assert sha(q['quint']['path'])==q['quint']['sha256'];reports['processDrainQuint']={'path':str(model),'sha256':sha(model),'passed':True}
coupling=next((r/'docs/warlock-preview/v93').glob('shared-process-drain-coupling-v143-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==6
for n,h in c['inputs'].items():assert sha(n)==h,n
for n,h in c['artifacts'].items():assert sha(coupling.parent/n)==h,n
assert sha(c['quint']['path'])==c['quint']['sha256'];reports['processDrainCoupling']={'path':str(coupling),'sha256':sha(coupling),'passed':True}
parent=r/'implementation/warlock-preview-provider-v142';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and not held['passed'] and held['actualSharedRendererProcessCounterexample']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets','spec','qa']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'host.c','shared-host.c','controlled-preview-host.h'}:assert sha(gui/base/p.name)==sha(p),p
scope='GUI143 repairs actual held142/Native186 shared related WebKit process death presenting GTK recovery with original known native duties retained. Owning shared termination wrapper retains actual reason/failure and urgent original same-policy quarantine; original native input/step/poll/receipts continue until original strict policy/physical/ticket/journal/confirmation close and empty custody. Multiple actual related-view signals never cancel drain. Optional original evaluation finish/error hook retains its original failure but defers early GTK exit in this controlled known realm; standalone/noncontrolled default remains original. Only strict retired custody permits original GTK recovery controls; unretired/uncertain custody explicitly refuses them. Native187 unchanged186 oracle passes21 controls: actual API termination/reason2/shared signals/original first source red19200, known owning/closing/strict closed before GTK recovery/backend normal, explicit recovery dismissal keeps failure1/seven other normal exits/private cleanup/no criticals or incomplete teardown. No new renderer/realm/reset/replay/inferred settlement. Normal18829/13, known-reload18934/12, current-failure19022/host1+seven other normal, old-canceled19136/13, rapid19251/17, delayed19318/8 and old-success19435/13 pass separately with original source/pixel/output/strict close controls. Full119/new process-drain Quint9/200/6 actual projected stages pass. This qualifies known preview-duty drain before GTK recovery for this actual shared process stop; all evaluation-error/termination schedules, whole-host restart/window-command journal/durable Unknown/actual native uncertainty, physical/hardware/pressure/full workload/RSS, original full S09/release remain open. Original policy/issuer/physical product/grants/epochs/nav/snapshot/clocks/deadlines unchanged; installed desktop/drafts/foreign preserved.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualKnownSharedProcessNativeDrainQualified':True,'actualGTKRecoveryAfterStrictDrainQualified':True,'processFailureNativeControls':21,'processFailureExpectedHostExitCode':1,'processFailureOtherNormalOwnedExits':7,'processFailureGLibCriticalsObserved':False,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'reloadNativeChecks':34,'reloadNormalOwnedExits':12,'currentFailureNativeControls':22,'currentFailureExpectedExitCode':1,'currentFailureOtherNormalOwnedExits':7,'cancelledOldResultNativeChecks':36,'cancelledOldResultNormalOwnedExits':13,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'successfulOldResultNativeChecks':35,'successfulOldResultNormalOwnedExits':13,'processDrainQuintScenarios':9,'processDrainQuintInvariantSamples':200,'processDrainCoupledStages':6,'originalProcessCounterexampleRetained':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'privateSessionCleanupPassed':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'wholeHostRestartQualified':False,'durableUnknownRecoveryQualified':False,'uncertainProcessDrainQualified':False,'allProcessFailureSchedulesQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
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
  v=next(v for v,_,_,_ in items if root==native[v][0]);own.update(nativeChecks=len(native[v][2]['checks']),ownedExits=len(native[v][2]['ownedExitCodes']),actualKnownSharedProcessNativeDrainQualified=v==187,actualGTKRecoveryAfterStrictDrainQualified=v==187,normalControlledHostClosureQualified=v not in {187,190},gracefulCurrentFailureDrainQualified=v==190,scope=native[v][2]['scope'])
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS '+scope+' Next PUBLIC104 then original native uncertainty, durable Unknown/window-command/whole-host restart, original-clock pressure/expiry/physical/full-release gates.'],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in roots]+[str(out.relative_to(r))]))
