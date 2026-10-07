"""Freeze actual rapid pending-intent repair and separate original regressions."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=r/'implementation/warlock-preview-provider-v134';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(pathlib.Path(p).read_text())
def artifacts(p,d):
 for n,h in d['artifacts'].items():assert sha(p.parent/n)==h,n
roots=[r/f'implementation/warlock-client-provider-native-v{v}' for v in [150,151,152,153]];native=[]
for root,count,exits,runner in zip(roots,[29,51,51,18],[13,18,17,8],['native138_controlled_curtain_runner.py','native148_pending_reader_runner.py','native149_rapid_pending_reader_runner.py','native141_delayed_snapshot_runner.py']):
 rows=list(root.glob('qa/native-controlled-*/report.json'));assert len(rows)==1;p=rows[0];d=load(p);pre=load(root/'qa/preflight.json');assert d['passed'] and d['cleanupPassed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and len(d['checks'])==count and len(d['ownedExitCodes'])==exits and all(c['passed'] for c in d['checks']) and all(c['exitCode']==0 for c in d['ownedExitCodes'])
 for n,h in pre['inputs'].items():assert sha(n)==h,n
 artifacts(p,d);assert sha(root/'qa/native-controlled-host.py')==sha(r/'docs/warlock-preview/v93'/runner)
 native.append((p,d,pre))
np,n,npre=native[0];sp,slow,spre=native[1];rp,rapid,rpre=native[2];lp,late,lpre=native[3]
assert all(d['pair']==n['pair'] and pre['controlledHostBuild']==npre['controlledHostBuild'] for _,d,pre in native)
original=[c['name'] for c in n['checks']]
for d in [slow,rapid]:
 assert [c['name'] for c in d['checks'] if c['name'] in original]==original
 for k in ['actualGUIRealmReopenQualified','actualPendingIntentReopenQualified','actualOriginalReaderHeldAcrossNewPopup','actualOriginalHeldAndFreshReadsRevoked','actualPendingPopupLeaseRetained','actualSamePolicyRetained','actualOriginalNativeBindingRetained','actualFreshRendererPerEpoch','actualNavigationAndSnapshotChronologyRetained']:assert d[k],k
 assert d['actualOriginalReaderCloseCalls']==1 and d['actualNormalGUIReopenCycles']==2 and d['actualOffscreenWebKitPixels']['red']==19200 and d['actualReopenedWebKitPixels']['red']==19200 and d['actualReopenedClosedCurtainRegionPixels']['red']==0 and d['actualReopenedNativePaint']['opacity']==0
assert rapid['actualRapidPointerCloseReopenQualified']
for k in ['actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert late[k],k
for _,d,_ in native:
 for k in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[k],k
build=pathlib.Path(npre['controlledHostBuild']);b=load(build);assert b['passed'] and len(b['commands'])==119 and all(c['exitCode']==0 for c in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
artifacts(build,b)
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
model=next(gui.glob('qa/controlled-reader-lifetime-model-v4-*/report.json'));q=load(model);assert q['passed'] and q['namedScenarios']==6 and q['invariantSamples']==200
closing=next(gui.glob('qa/closing-observation-model-v3-*/report.json'));c=load(closing);assert c['passed'] and c['namedScenarios']==8 and c['invariantSamples']==200
for p,d in [(model,q),(closing,c)]:
 for name,h in d['inputs'].items():assert sha(gui/name)==h,name
 artifacts(p,d);assert sha(d['quint']['path'])==d['quint']['sha256']
reader_coupling=next((r/'docs/warlock-preview/v93').glob('retained-reader-coupling-v134-*/report.json'));rc=load(reader_coupling);assert rc['passed'] and rc['coupledQuintChecks']==8 and rc['actualNativeReportSHA256']==sha(sp)
closing_coupling=next((r/'docs/warlock-preview/v93').glob('closing-observation-coupling-*/report.json'));cc=load(closing_coupling);assert cc['passed'] and cc['coupledQuintChecks']==4 and cc['actualFailureAndFixQualified']
for p,d in [(reader_coupling,rc),(closing_coupling,cc)]:
 for name,h in d['inputs'].items():assert sha(name)==h,name
 artifacts(p,d);assert sha(d['quint']['path'])==d['quint']['sha256']
parent=r/'implementation/warlock-preview-provider-v133';pm=parent/'component-manifest.json';held=load(pm);assert held['sourceHeld'] and not held['passed'] and held['rapidOriginalDeadlineFailed']
for name,row in held['files'].items():assert sha(parent/name)==row['sha256'],name
foundation=r/'implementation/warlock-preview-provider-v132';fm=foundation/'component-manifest.json';fd=load(fm);assert fd['sourceHeld'] and fd['passed'] and fd['actualGUIRealmReopenQualified']
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name!='controlled-preview-host.h':assert sha(gui/base/p.name)==sha(p),p
scope='GUI134 fixes the actual Native149 rapid pending-intent deadlock with two sticky old-realm producer guards only: poll original closing scope with no current presentation stamps and continue original detachment observations even when a later popup is ready. Native issuer/single persistent Elm policy/physical/journal/independent confirmation/router/readers/deadlines unchanged. Disabled-by-default QA-only original URI/GIO reader from held133 keeps a real owned Retiring job alive across old popup closure/later actual GTK configuration; old held/fresh reads revoke, one original reader close precedes independent strict Native close, then the retired renderer is replaced inside the same later GTK popup lease/grab and fresh DOM admission creates later same-binding epoch/pure fixed-grant renderer. Original failed rapid14933/12 normal others/host1/clean private teardown and original6s counterexample remain held. Same byte-identical rapid oracle on current Native152 passes51/17 normal exits/private cleanup, two current source URI/red19200 images, monotonic epoch/navigation/lease/request1->2, current opacity0 closed-curtain output and both strict closes. Slower Native15151/18, unchanged Native15029/13 normal and delayed Native15318/8 real-result regressions/cleanups pass separately. Current full119, reader Quint6named200samples/8 coupled stages and closing producer Quint8named200samples/4 cases coupled to actual failed/passed Native traces/source gates pass. Pending-intent/rapid coverage is these actual fixture schedules, not all timings. Broader old-context async/process/reload/Unknown, ongoing conceal/reveal/hardware, pressure/workload/RSS, original full S09/release remain open; no installed desktop/draft changes or grant reset.'
reports={name:{'path':str(p),'sha256':sha(p)} for name,p in [('build',build),('normalNative',np),('pendingReaderNative',sp),('rapidPendingReaderNative',rp),('delayedSnapshotNative',lp),('readerQuint',model),('closingProducerQuint',closing),('readerCoupling',reader_coupling),('closingProducerCoupling',closing_coupling)]}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualGUIRealmReopenQualified':True,'actualPendingIntentReopenQualified':True,'actualRapidPointerCloseReopenQualified':True,'stickyClosingRealmProducerQualified':True,'nativeRealmRebindingActivated':True,'actualNormalGUIReopenCycles':2,'singlePreviewPolicy':True,'nativeGrantResets':0,'navigationResets':0,'snapshotOrdinalResets':0,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'pendingReaderNativeChecks':51,'pendingReaderNormalOwnedExits':18,'rapidPendingReaderNativeChecks':51,'rapidPendingReaderNormalOwnedExits':17,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'readerQuintScenarios':6,'readerInvariantSamples':200,'readerCoupledStages':8,'closingProducerQuintScenarios':8,'closingProducerInvariantSamples':200,'closingProducerCoupledChecks':4,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'hardwarePresentationQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'directPermanentRetirementQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':reports,'heldFailedParentManifest':{'path':str(pm),'sha256':sha(pm)},'heldAcceptedFoundationManifest':{'path':str(fm),'sha256':sha(fm)}}
for root,count,exits in [(gui,51,17),*zip(roots,[29,51,51,18],[13,18,17,8])]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 m=root/'component-manifest.json';assert not m.exists();own=dict(common,files=files,nativeChecks=count,normalOwnedExits=exits)
 if root in roots:
  idx=roots.index(root);own.update(scope=native[idx][1]['scope'],actualGUIRealmReopenQualified=idx in [1,2],actualPendingIntentReopenQualified=idx in [1,2],actualRapidPointerCloseReopenQualified=idx==2,actualNormalGUIReopenCycles=2 if idx in [1,2] else 0,actualStaleSnapshotCallbackQualified=idx==3,actualRetainedResultConsumedOnce=idx==3,actualStaleSnapshotArtifactRejected=idx==3,actualCapturedPixelsQualified=idx!=3)
 m.write_text(json.dumps(own,indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report134.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,common['owner'],str(gui.relative_to(r)),['PROGRESS heldGUI134 fixes actual rapid Native149 original6s closing-subject deadlock by sticky old-realm producer poll/detachment scope across later popup. Original Native/Elm policy/physical/journal/confirmation/readers/deadlines unchanged; no resets. Current same rapid byte-identical oracle Native15251/17 normal, slower15151/18, unchanged15029/13 normal and delayed15318/8 cleanups/full119 pass. Real original GIO reader/owned Retiring job spans later GTK popup, held/fresh reads denied, one original close then independent strict close, same later popup lease/grab/new fixed renderer and actual source URI/red19200 both epochs/closed output. Reader Quint6/200/8coupled and closingQuint8/200/4failure-fix coupled; failed133/149 and model syntax failures held. Next PUBLIC98 then old-context delayed async results across later epoch and ongoing native physical frame/reveal/pressure/recovery. Original full release gates/installed/drafts/foreign preserved.'],'progress',[str((gui/'component-manifest.json').relative_to(r)),*[str((root/'component-manifest.json').relative_to(r)) for root in roots],str(out.relative_to(r))]))
