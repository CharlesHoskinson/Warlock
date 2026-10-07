"""Freeze bounded actual canceled old-result fix and unchanged regressions."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v137';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [160,161,162,163,164]];native=[]
for root,count,exits,runner in zip(roots,[29,36,35,18,51],[13,13,13,8,17],['native138_controlled_curtain_runner.py','native159_cancelled_reopened_snapshot_runner.py','native155_reopened_snapshot_runner.py','native141_delayed_snapshot_runner.py','native149_rapid_pending_reader_runner.py']):
 p=next(root.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(root/'qa/preflight.json');assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner);native.append((p,d,pre))
np,n,npre=native[0];xp,cancel,xpre=native[1];sp,success,spre=native[2];lp,late,lpre=native[3];rp,rapid,rpre=native[4]
assert all(d['pair']==n['pair'] and pre['controlledHostBuild']==npre['controlledHostBuild'] for _,d,pre in native)
for k in ['actualCancelledOldResultQualified','actualOldResultAcrossReopenedRealmQualified','actualGUIRealmReopenQualified','actualSamePolicyRetained','actualOriginalNativeBindingRetained','actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert cancel[k],k
assert cancel['actualReopenedWebKitPixels']['red']==19200 and cancel['actualReopenedClosedCurtainRegionPixels']['red']==0 and cancel['actualReopenedNativePaint']['opacity']==0 and not cancel['actualCapturedPixelsQualified']
assert success['actualOldResultAcrossReopenedRealmQualified'] and rapid['actualRapidPointerCloseReopenQualified'] and rapid['actualPendingIntentReopenQualified']
for _,d,_ in native:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
model=next(gui.glob('qa/async-error-scope-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==10 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
artifacts(model,q);assert sha(q['quint']['path'])==q['quint']['sha256']
coupling=next((r/'docs/warlock-preview/v93').glob('async-error-scope-coupling-v137-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==4 and c['actualNative161ReportSHA256']==sha(xp)
for n,h in c['inputs'].items():assert sha(n)==h,n
artifacts(coupling,c);assert sha(c['quint']['path'])==c['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v136';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and not held['passed'] and held['actualCancelledOldResultCounterexample']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets','spec','qa']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name!='shared-host.c':assert sha(gui/base/p.name)==sha(p),p
scope='GUI137 repairs held GUI136/Native159 actual old cancellation shutting down reopened GUI. Original WebKit finish consumes the real result once, then existing view/epoch/navigation/projection/current-channel guard rejects stale results before current error handling. NULL-image-safe disposal clears only old image/error, without current policy/job/grant/physical settlement. Matching-current error branch remains byte-identical; actual matching-current cancellation remains a separate open native gate. Same byte-identical Native159 cancellation oracle now Native16136/13 passes: actual original G_IO_ERROR_CANCELLED/image0 after old strict close/replaced view/new epoch2, one finish, no old artifact/current failure; current request2 actual source red19200/current original image before-after opacity0 output and both strict closes/same policy/binding/no resets. Unchanged normal16029/13, successful old result16235/13, delayed16318/8, rapid real reader16451/17 all pass with normal owned exits/private cleanup. Full119, error-scope Quint10/200 and4 actual failure/fix/success projected cases pass. No native issuer/single Elm policy/physical product/sticky producer/deadline changes. Qualification covers these actual old-cancellation/success schedules, not all async scopes, current failure, process/reload/Unknown recovery, physical conceal/reveal/hardware, pressure/workload/RSS, full S09 or release. Installed/drafts/foreign untouched.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',np),('cancelledReopenedSnapshotNative',xp),('successfulReopenedSnapshotNative',sp),('delayedSnapshotNative',lp),('rapidPendingReaderNative',rp),('asyncErrorScopeQuint',model),('asyncErrorScopeCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualCancelledOldResultQualified':True,'actualOldResultAcrossReopenedRealmQualified':True,'actualOldSnapshotPixelsAccepted':False,'actualNewRealmCapturedPixelsQualified':True,'actualGUIRealmReopenQualified':True,'actualPendingIntentReopenQualified':True,'actualRapidPointerCloseReopenQualified':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'cancelledReopenedSnapshotNativeChecks':36,'cancelledReopenedSnapshotNormalOwnedExits':13,'successfulReopenedSnapshotNativeChecks':35,'successfulReopenedSnapshotNormalOwnedExits':13,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'asyncErrorScopeQuintScenarios':10,'asyncErrorScopeInvariantSamples':200,'asyncErrorScopeCoupledCases':4,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'currentMatchingErrorNativeQualified':False,'allCancelledOrFailedOldResultsQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root,count,exits in [(gui,36,13),*zip(roots,[29,36,35,18,51],[13,13,13,8,17])]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files,nativeChecks=count,normalOwnedExits=exits)
 if root in roots:
  idx=roots.index(root);own.update(scope=native[idx][1]['scope'],actualCancelledOldResultQualified=idx==1,actualOldResultAcrossReopenedRealmQualified=idx in [1,2],actualNewRealmCapturedPixelsQualified=idx in [1,2],actualGUIRealmReopenQualified=idx in [1,2,4],actualPendingIntentReopenQualified=idx==4,actualRapidPointerCloseReopenQualified=idx==4,actualStaleSnapshotCallbackQualified=idx in [1,2,3],actualRetainedResultConsumedOnce=idx in [1,2,3],actualStaleSnapshotArtifactRejected=idx in [1,2,3])
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report137.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI137 actual canceled old WebKit result loses current failure authority after existing scope guard ordering fix. Original Native159 failure held; exact same oracle Native16136/13 passes plus normal16029/13/success16235/13/delayed16318/8/rapid16451/17/full119/Quint10/200/4 actual-projected cases. Matching current error source unchanged, actual current cancellation remains separate gate. Next PUBLIC100 then real current matching error/projection/navigation/async/process recovery and physical frame/reveal/pressure gates. Full release open/installed drafts foreign preserved.'],'progress',[str((gui/'component-manifest.json').relative_to(r)),*[str((root/'component-manifest.json').relative_to(r)) for root in roots],str(out.relative_to(r))]))
