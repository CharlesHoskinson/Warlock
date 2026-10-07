"""Freeze bounded original result across actual retired/reopened native realms."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v135';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [154,155,156,157]];native=[]
for root,count,exits,runner in zip(roots,[29,35,18,51],[13,13,8,17],['native138_controlled_curtain_runner.py','native155_reopened_snapshot_runner.py','native141_delayed_snapshot_runner.py','native149_rapid_pending_reader_runner.py']):
 p=next(root.glob('qa/native-controlled-*/report.json'));d=load(p);pre=load(root/'qa/preflight.json');assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner);native.append((p,d,pre))
np,n,npre=native[0];xp,cross,xpre=native[1];lp,late,lpre=native[2];rp,rapid,rpre=native[3]
assert all(d['pair']==n['pair'] and pre['controlledHostBuild']==npre['controlledHostBuild'] for _,d,pre in native)
for k in ['actualOldResultAcrossReopenedRealmQualified','actualGUIRealmReopenQualified','actualSamePolicyRetained','actualOriginalNativeBindingRetained','actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert cross[k],k
assert cross['actualReopenedWebKitPixels']['red']==19200 and cross['actualReopenedClosedCurtainRegionPixels']['red']==0 and cross['actualReopenedNativePaint']['opacity']==0 and not cross['actualCapturedPixelsQualified']
for k in ['actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert late[k],k
assert rapid['actualRapidPointerCloseReopenQualified'] and rapid['actualPendingIntentReopenQualified']
for _,d,_ in native:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
model=next(gui.glob('qa/host-realm-lifecycle-model-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==9 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(gui/n)==h,n
artifacts(model,q);assert sha(q['quint']['path'])==q['quint']['sha256']
coupling=next((r/'docs/warlock-preview/v93').glob('host-lifecycle-coupling-v135-*/report.json'));c=load(coupling);assert c['passed'] and c['coupledQuintChecks']==7 and c['actualNativeReportSHA256']==sha(xp)
for n,h in c['inputs'].items():assert sha(n)==h,n
artifacts(coupling,c);assert sha(c['quint']['path'])==c['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v134';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and held['passed'] and held['actualRapidPointerCloseReopenQualified']
for n,row in held['files'].items():assert sha(parent/n)==row['sha256'],n
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'shared-host.c','controlled-preview-host.h'}:assert sha(gui/base/p.name)==sha(p),p
scope='GUI135 adds disabled-by-default QA retention of one real original WebKit result/strong old view across strict old C/Bootstrap close, renderer replacement and later same-policy/native epoch. It calls original finish once only after current new-view native projection acknowledgement; unchanged original view/epoch/navigation/projection guard rejects old request1 pixels/artifact. Actual Native15535 checks/13 normal exits/private cleanup prove epoch/navigation1->2/old view replaced, old result consumed once with zero old artifact, then new current source URI/red19200 request2 pixels, current image before/after actual opacity0 output region, both original strict native closes/same policy/binding/no reset. Original snapshot pixels remain rejected; new realm captured pixels qualify separately. Unchanged Native15429/13 normal, Native15618/8 closure-delayed result and Native15751/17 rapid real-reader regressions pass separately. Current full119, lifecycle Quint9named200samples and7 stages coupled to actual observations pass. Native issuer/single Elm policy/physical product/readers/original completion guard/sticky producer/deadlines unchanged. This actual retained-success-result schedule does not qualify canceled/failed result, all async timing/process/reload/Unknown recovery, ongoing conceal/reveal/hardware, pressure/workload/RSS, full S09 or release. Installed/drafts/foreign untouched.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',np),('reopenedSnapshotNative',xp),('delayedSnapshotNative',lp),('rapidPendingReaderNative',rp),('hostLifecycleQuint',model),('hostLifecycleCoupling',coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualOldResultAcrossReopenedRealmQualified':True,'actualOldSnapshotPixelsAccepted':False,'actualNewRealmCapturedPixelsQualified':True,'actualGUIRealmReopenQualified':True,'actualPendingIntentReopenQualified':True,'actualRapidPointerCloseReopenQualified':True,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'reopenedSnapshotNativeChecks':35,'reopenedSnapshotNormalOwnedExits':13,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'hostLifecycleQuintScenarios':9,'hostLifecycleInvariantSamples':200,'hostLifecycleCoupledStages':7,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'canceledOrFailedOldResultQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldParentManifest':{'path':str(pm),'sha256':sha(pm)}}
for root,count,exits in [(gui,35,13),*zip(roots,[29,35,18,51],[13,13,8,17])]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files,nativeChecks=count,normalOwnedExits=exits)
 if root in roots:
  idx=roots.index(root);own.update(scope=native[idx][1]['scope'],actualOldResultAcrossReopenedRealmQualified=idx==1,actualNewRealmCapturedPixelsQualified=idx==1,actualGUIRealmReopenQualified=idx in [1,3],actualPendingIntentReopenQualified=idx==3,actualRapidPointerCloseReopenQualified=idx==3,actualStaleSnapshotCallbackQualified=idx in [1,2],actualRetainedResultConsumedOnce=idx in [1,2],actualStaleSnapshotArtifactRejected=idx in [1,2])
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report135.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI135 actual old real WebKit result/strong view across strict old C close, renderer replacement, later same-policy native epoch/current projection; original finish once unchanged view epoch navigation projection rejects request1 artifact, new current original source red19200 request2/current closed-curtain output and strict close. Native15535/13 normal/cleanup, unchanged normal15429/13/delayed15618/8/rapid15751/17/full119 pass; Quint9/200/7 actual-coupled stages. Native policy issuer physical product original guard sticky producer deadlines unchanged/no resets. Next PUBLIC99 then real canceled/failed old async result guard and physical frame/reveal/pressure/recovery. All original full release gates/installed/drafts/foreign remain.'],'progress',[str((gui/'component-manifest.json').relative_to(r)),*[str((root/'component-manifest.json').relative_to(r)) for root in roots],str(out.relative_to(r))]))
