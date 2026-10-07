"""Freeze actual current failure drain repair and unchanged original regressions."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v139';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
out=pathlib.Path(__file__).with_name('component-report-gui139-current-drain.json');assert not out.exists()
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in range(169,175)];native=[]
for root,count,exits,runner in zip(roots,[22,29,36,35,51,18],[8,13,13,13,17,8],['native168_current_failure_drain_runner.py','native138_controlled_curtain_runner.py','native159_cancelled_reopened_snapshot_runner.py','native155_reopened_snapshot_runner.py','native149_rapid_pending_reader_runner.py','native141_delayed_snapshot_runner.py']):
 p=next(root.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(root/'qa/preflight.json');assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks'])
 assert all(c['exitCode']==(1 if root==roots[0] and c['name']=='controlled-host' else 0) for c in d['ownedExitCodes'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner);native.append((p,d,pre))
cp,current,cpre=native[0];np,n,npre=native[1];op,old,opre=native[2];sp,success,spre=native[3];rp,rapid,rpre=native[4];lp,late,lpre=native[5]
assert all(d['pair']==n['pair'] and pre['controlledHostBuild']==npre['controlledHostBuild'] for _,d,pre in native)
assert current['actualCurrentMatchingErrorNativeQualified'] and current['actualCurrentFailureNativeCustodyDrained'] and current['gracefulCurrentFailureDrainQualified'] and current['expectedFailureExitCode']==1 and not current['normalControlledHostClosureQualified']
checks={c['name']:c for c in current['checks']};state=checks['controlledCurrentFailureNativeCustodyDrainedBeforeFailureExit']['state'];assert state['privatePolicy']['realm']['closed'] and not state['privatePolicy']['models']
text=(cp.parent/'private-evidence/controlled-host.log').read_text();assert 'controlled-native-current-failure-retired: epoch=1 failureRetained=1 originalStrictClose=1' in text and 'shared-host-exit: failure=1 rendered=1' in text and 'Controlled native teardown incomplete:' not in text and 'GLib-GObject-CRITICAL' not in text
assert old['actualCancelledOldResultQualified'] and old['actualReopenedWebKitPixels']['red']==19200 and old['actualReopenedClosedCurtainRegionPixels']['red']==0 and old['actualReopenedNativePaint']['opacity']==0
assert success['actualOldResultAcrossReopenedRealmQualified'] and rapid['actualRapidPointerCloseReopenQualified'] and rapid['actualPendingIntentReopenQualified']
for _,d,_ in native:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
model=next(gui.glob('qa/current-failure-drain-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==8 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
artifacts(model,q);assert sha(q['quint']['path'])==q['quint']['sha256']
coupling=next((r/'docs/warlock-preview/v93').glob('current-failure-drain-coupling-v139-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==5
for n,h in c['inputs'].items():assert sha(n)==h,n
artifacts(coupling,c);assert sha(c['quint']['path'])==c['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v138';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and not held['passed'] and held['actualCurrentFailureDrainCounterexample']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets','spec','qa']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'shared-host.c','controlled-preview-host.h'}:assert sha(gui/base/p.name)==sha(p),p
scope='GUI139 repairs actual held138/Native168 current matching WebKit cancellation exiting before Native drain. Original finish/current scope disposition remains; matching controlled failure retains original error/failure outcome, native opacity0 curtain, original visual invalidation and urgent same-policy quarantine. Original sticky retiring producer/input/step/poll/receipts continue; only original policy/physical/ticket/journal/confirmation strict Native retirement, closed policy and empty custody allow failure exit1. No renderer replacement/reopen/reset/inferred settlement; Native uncertainty retains original refusal path. Exact byte-identical Native168 drain oracle now16922 controls/seven other normal/private cleanup passes: real current G_IO_ERROR_CANCELLED once/no artifact, actual owned->closing->strict closed empty model/input/ticket/confirmation/transport, original failure1 after retirement, no incomplete teardown or GLib/GObject criticals. Failure1 remains negative outcome, not normal-exit success. Unchanged normal17029/13, canceled-old17136/13, successful old17235/13, rapid real-reader17351/17 and closure-delayed17418/8 positive regressions/full119 pass with all normal owned exits/private cleanup. New failure-drain Quint8/200 and5 actual failed/fixed projected stages pass. Native issuer/single Elm reducer/physical product/original retirement gates/deadlines unchanged; only host current-error drain changes. Qualification covers this actual known current-cancellation duty schedule; uncertain/process/reload/Unknown recovery, all async errors, ongoing physical conceal/reveal/hardware, pressure/full workload/RSS, full S09 and release remain open. Installed desktop/drafts/foreign preserved.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('currentFailureDrainNative',cp),('normalNative',np),('cancelledOldResultNative',op),('successfulOldResultNative',sp),('rapidPendingReaderNative',rp),('delayedSnapshotNative',lp),('currentFailureDrainQuint',model),('currentFailureDrainCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualCurrentMatchingErrorNativeQualified':True,'actualCurrentFailureNativeCustodyDrained':True,'gracefulCurrentFailureDrainQualified':True,'currentFailureNativeControls':22,'currentFailureExpectedExitCode':1,'currentFailureOtherNormalOwnedExits':7,'currentFailureGLibCriticalsObserved':False,'normalControlledHostClosureQualified':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'actualCancelledOldResultQualified':True,'cancelledOldResultNativeChecks':36,'cancelledOldResultNormalOwnedExits':13,'successfulOldResultNativeChecks':35,'successfulOldResultNormalOwnedExits':13,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'currentFailureDrainQuintScenarios':8,'currentFailureDrainInvariantSamples':200,'currentFailureDrainCoupledStages':5,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'privateSessionCleanupPassed':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'allCurrentFailuresQualified':False,'uncertainCurrentFailureDrainQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root in [gui,*roots]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files)
 if root in roots:
  idx=roots.index(root);own.update(scope=native[idx][1]['scope'],nativeChecks=[22,29,36,35,51,18][idx],normalOwnedExits=[7,13,13,13,17,8][idx],expectedFailedOwnedExits=1 if idx==0 else 0,normalControlledHostClosureQualified=idx!=0,actualCurrentMatchingErrorNativeQualified=idx==0,actualCurrentFailureNativeCustodyDrained=idx==0,gracefulCurrentFailureDrainQualified=idx==0,actualCancelledOldResultQualified=idx==2)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI139 actual known current snapshot cancellation now retains original failure and continues urgent quarantine/sticky original native drain to strict closed empty policy before failure1 exit. Unchanged168 actual oracle16922/seven other normal/cleanup/no criticals passes, normal17029/13/old-canceled17136/13/old-success17235/13/rapid17351/17/delayed17418/8/full119/Quint8/200/5 actual projected stages. No issuer/reducer/physical/gate/deadline/reset changes. Next PUBLIC102 then uncertain/process/reload recovery, original-clock pressure/expiry and ongoing physical frame/reveal/fullrelease gates; installed drafts foreign preserved.'],'progress',[str((root/'component-manifest.json').relative_to(r)) for root in [gui,*roots]]+[str(out.relative_to(r))]))
