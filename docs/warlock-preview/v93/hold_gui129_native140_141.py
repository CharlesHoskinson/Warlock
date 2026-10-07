"""Hold bounded actual controlled admission/drain; retain all failed predecessors."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v129';native=repo/'implementation/warlock-client-provider-native-v140';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(native.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and d['cleanupPassed'] and all(x['exitCode']==0 for x in d['ownedExitCodes'])
checks={x['name']:x for x in d['checks']};assert all(x['passed'] for x in checks.values())
for name in ['controlledFactoryAbsentBeforeActualGTKAdmission','controlledFactoryAfterOriginalGTKAdmission','controlledActualPureWebKitRendererInitializedOnce','controlledActualDOMAndNativeCurrentProjectionReceipt','controlledOriginalNativeTicketsActuallyIssuedAndDelivered','controlledNoLegacyBrowserCommandRoute','controlledOriginalPolicyInputTicketConfirmationCustodyDrained','controlledFullHostNormalExit']:
 assert checks[name]['passed'],name
for key in ['actualControlledFactoryActivated','actualNativePolicyDriverActivated','actualPureWebKitRendererActivated','actualScopedURIRouterRegistered','actualDOMStampReceiptObserved']:assert d[key],key
for key in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[key],key
assert len(d['checks'])==29 and len(d['ownedExitCodes'])==13 and d['actualCapturedPixelsQualified'] and d['actualScopedURIImageLoadObserved']
pixels=d['actualOffscreenWebKitPixels'];assert pixels['red']==19200 and pixels['green']==0 and pixels['blue']==0
original=json.loads((repo/'implementation/warlock-client-provider-native-v138/qa/native-controlled-1791385665134213100/report.json').read_text());assert {x['name'] for x in original['checks']}<=set(checks) and {x['name'] for x in original['ownedExitCodes']}<={x['name'] for x in d['ownedExitCodes']}
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==119 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
parent=repo/'implementation/warlock-preview-provider-v127';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['sourceHeld'] and prior['passed'] and prior['normalControlledHostClosureQualified']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'controlled-preview-host.h','shared-host.c'}:assert sha(gui/base/p.name)==sha(p),p
failed=[]
for g,n in [(122,132),(123,133),(124,134)]:
 for name in [f'warlock-preview-provider-v{g}',f'warlock-client-provider-native-v{n}']:
  root=repo/'implementation'/name;m=root/'component-manifest.json';held=json.loads(m.read_text());assert held['sourceHeld'] and not held['passed']
  for rel,row in held['files'].items():assert sha(root/rel)==row['sha256'],rel
  failed.append({'path':str(m),'sha256':sha(m)})
scope='SAFE opacity0 GUI129: unchanged original29 actual controlled GTK/native single policy/pure WebKit image/private output/native paint/geometry/region/drain controls pass with13 normal owned exits. Separate Native141 original16 admission/drain controls plus actual delayed-result checks pass18 with8 normal owned exits. One actual original WebKit GAsyncResult/view/completion scope is retained without early finish, then finished once after actual popup closure; stale original projection is rejected, no pixels artifact is written, and original policy/input/ticket/physical/journal/independent-confirmation custody drains to strict normal close. Both private cleanups/current full119/original deadline6/core16/plugin19/AQ155 pass. Original native issuer/Elm policy/physical product unchanged, no grant reset; explicit fault hook is private and disabled normally. Bounded late-after-closure callback qualification does not establish all stale callbacks, renderer reload/process/uncertain recovery, ongoing transition concealment, physical reveal/hardware, pressure/workload/RSS/full preview or release.'
delayed_native=repo/'implementation/warlock-client-provider-native-v141';late_reports=list(delayed_native.glob('qa/native-controlled-*/report.json'));assert len(late_reports)==1;late_report=late_reports[0];late=json.loads(late_report.read_text());assert late['passed'] and late['cleanupPassed'] and len(late['checks'])==18 and len(late['ownedExitCodes'])==8 and all(x['passed'] for x in late['checks']) and all(x['exitCode']==0 for x in late['ownedExitCodes']) and late['pair']==d['pair']
for key in ['actualDelayedWebKitResultRetained','actualStaleSnapshotCallbackQualified','actualStaleSnapshotArtifactRejected','actualRetainedResultConsumedOnce']:assert late[key],key
late_pre=json.loads((delayed_native/'qa/preflight.json').read_text());assert late_pre['passed'] and late_pre['controlledHostBuild']==str(build)
for p,h in late_pre['inputs'].items():assert sha(p)==h,p
for rel,h in late['artifacts'].items():assert sha(late_report.parent/rel)==h,rel
original16=json.loads((repo/'implementation/warlock-client-provider-native-v135/qa/native-controlled-1791383533742031917/report.json').read_text());assert {x['name'] for x in original16['checks']}<={x['name'] for x in late['checks']}
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationObserved':True,'actualPureRendererInitializationQualified':True,'actualCurrentProjectionDOMReceiptObserved':True,'actualControlledAdmissionAndDrainQualified':True,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'nativeGrantResets':0,'singlePreviewPolicy':True,'originalNativePolicyIssuerPhysicalProductUnchanged':True,'compiledPageAssetClosureQualified':True,'actualNativeGTKPaintObservation':d['actualNativeGTKPaintObservation'],'actualClosedCurtainRegionObserved':True,'actualClosedCurtainRegionPixels':d['actualClosedCurtainRegionPixels'],'boundedClosedCurtainRegionQualified':False,'hardwarePresentationQualified':False,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'actualCapturedPixelsQualified':True,'actualScopedURIImageLoadObserved':True,'actualOffscreenWebKitPixels':d['actualOffscreenWebKitPixels'],'actualStaleSnapshotCallbackQualified':True,'actualRetainedResultConsumedOnce':True,'actualStaleSnapshotArtifactRejected':True,'normalRouteNativeChecks':29,'normalRouteNormalOwnedExits':13,'delayedResultNativeChecks':18,'delayedResultNormalOwnedExits':8,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':{'build':{'path':str(build),'sha256':sha(build)},'controlledNative':{'path':str(report),'sha256':sha(report)},'delayedSnapshotNative':{'path':str(late_report),'sha256':sha(late_report)}},'heldFailedPredecessors':failed}
for root in [gui,native,delayed_native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(dict(common,files=files,nativeChecks=18 if root==delayed_native else 29,normalOwnedExits=8 if root==delayed_native else 13,actualCapturedPixelsQualified=root!=delayed_native),indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report129.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
assert d['actualClosedCurtainRegionObserved'] and not d['boundedClosedCurtainRegionQualified'] and d['actualClosedCurtainRegionPixels']['red']==0 and d['actualNativeGTKPaintObservation']['opacity']==0
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Qualify CONTROL-039 actual delayed WebKit result through original popup closure:';assert text.count(old)==1;task.write_text(text.replace(old,old.replace('[ ]','[x]')))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],str(gui.relative_to(repo)),['PROGRESS heldSAFEGUI129 actual original normal Native14029checks13normalexits plus separate real delayed-result Native14118checks8normalexits with original16 admission/drain retained. One actual original WebKit result/view/scope held without finish, actual closure invalidates native projection then same result finished once/rejected/no stale artifact, all original policy/native input/ticket/physical/journal/confirmation duties drain under strict close. Both cleanups/full119/deadline6/core16/plugin19/AQ155 pass; opacity0/single original policy/native issuer/physical product unchanged/no grant reset. CONTROL039 bounded late-after-close qualified, broader stale callbacks/normal realm reopen/reload/process/uncertain recovery/physical frame/reveal/pressure/workload/RSS/full preview/release open. Next PUBLIC95 then safe actual ongoing projection/frame/reveal and original native realm lifecycle/recovery qualification. Legacy and all accepted/failed/unsafe controls preserved; installed/drafts/foreign untouched.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
