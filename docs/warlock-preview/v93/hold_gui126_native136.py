"""Hold bounded actual controlled admission/drain; retain all failed predecessors."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v126';native=repo/'implementation/warlock-client-provider-native-v136';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(native.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and d['cleanupPassed'] and all(x['exitCode']==0 for x in d['ownedExitCodes'])
checks={x['name']:x for x in d['checks']};assert all(x['passed'] for x in checks.values())
for name in ['controlledFactoryAbsentBeforeActualGTKAdmission','controlledFactoryAfterOriginalGTKAdmission','controlledActualPureWebKitRendererInitializedOnce','controlledActualDOMAndNativeCurrentProjectionReceipt','controlledOriginalNativeTicketsActuallyIssuedAndDelivered','controlledNoLegacyBrowserCommandRoute','controlledOriginalPolicyInputTicketConfirmationCustodyDrained','controlledFullHostNormalExit']:
 assert checks[name]['passed'],name
for key in ['actualControlledFactoryActivated','actualNativePolicyDriverActivated','actualPureWebKitRendererActivated','actualScopedURIRouterRegistered','actualDOMStampReceiptObserved']:assert d[key],key
for key in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[key],key
assert len(d['checks'])==21 and len(d['ownedExitCodes'])==10 and d['actualCapturedPixelsQualified'] and d['actualScopedURIImageLoadObserved']
pixels=d['actualOffscreenWebKitPixels'];assert pixels['red']==19200 and pixels['green']==0 and pixels['blue']==0
original=json.loads((repo/'implementation/warlock-client-provider-native-v135/qa/native-controlled-1791383533742031917/report.json').read_text());assert {x['name'] for x in original['checks']}<=set(checks) and {x['name'] for x in original['ownedExitCodes']}<={x['name'] for x in d['ownedExitCodes']}
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==119 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
parent=repo/'implementation/warlock-preview-provider-v125';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['sourceHeld'] and prior['passed'] and prior['normalControlledHostClosureQualified']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name not in {'controlled-preview-host.h','shared-host.c','controlled-popup-adapter.js'}:assert sha(gui/base/p.name)==sha(p),p
failed=[]
for g,n in [(122,132),(123,133),(124,134)]:
 for name in [f'warlock-preview-provider-v{g}',f'warlock-client-provider-native-v{n}']:
  root=repo/'implementation'/name;m=root/'component-manifest.json';held=json.loads(m.read_text());assert held['sourceHeld'] and not held['passed']
  for rel,row in held['files'].items():assert sha(root/rel)==row['sha256'],rel
  failed.append({'path':str(m),'sha256':sha(m)})
scope='Actual QA-only pure WebKit renderer loads the original scoped native URI and displays an original 320x240 real Core client capture at160x120. Original independent pixel oracle finds19200 red/zero green/zero blue pixels while an unrelated green peer is mapped. All original16 admission/drain checks retained;21 checks/10 owned normal exits/private cleanup on unchanged core16/plugin19/AQ155 and original six-second scenario. Snapshot admission and completion check original current native projection/view/epoch/navigation; actual stale-callback fault qualification remains open. One persistent original native Elm policy, original physical/journal/confirmation and strict close unchanged. Full119 and current synthetic adapter generation/mount controls pass. Physical curtain remains closed: offscreen pixels do not qualify Wayland physical frame/concealment/reveal, workload/pressure/RSS, reload/uncertain recovery, full S09 preview13 or full release.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationObserved':True,'actualPureRendererInitializationQualified':True,'actualCurrentProjectionDOMReceiptObserved':True,'actualControlledAdmissionAndDrainQualified':True,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'nativeGrantResets':0,'singlePreviewPolicy':True,'originalNativePolicyIssuerPhysicalProductUnchanged':True,'compiledPageAssetClosureQualified':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'actualCapturedPixelsQualified':True,'actualScopedURIImageLoadObserved':True,'actualOffscreenWebKitPixels':d['actualOffscreenWebKitPixels'],'actualStaleSnapshotCallbackQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':{'build':{'path':str(build),'sha256':sha(build)},'controlledNative':{'path':str(report),'sha256':sha(report)}},'heldFailedPredecessors':failed}
for root in [gui,native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(dict(common,files=files),indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report126.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();s+='\n- [x] Freeze bounded CONTROL-037 actual pure-renderer original URI/image load and\n  independent offscreen source pixels in GUI126/Native136 with all original16\n  admission/drain checks retained; actual stale callback, physical frame/reveal,\n  resource/performance and recovery/full release gates remain open.\n';task.write_text(s)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],str(gui.relative_to(repo)),['PROGRESS heldGUI126/Native136 actual pure WebKit renderer/scoped native URI loads actual320x240 Core client image at160x120, independent original oracle19200red/zero green and blue with mapped unrelated green peer. Original16 admission/drain checks retained;21checks10normalownedexits/privatecleanup/originaldeadline6/core16/plugin19/AQ155. Snapshot request and callback native-current projection/view/epoch/navigation guards implemented, actual stale-callback fault qualification remains open. Full119 and current synthetic adapter controls pass; original native policy/issuer/physical/journal/confirmation/strict close unchanged. Physical curtain remains closed; frame/concealment/reveal/workload/RSS/pressure/reload/uncertain recovery/full S09 preview13/full release open. Next PUBLIC93 then actual frame/physical concealment and stale async snapshot qualification. Legacy Native1312518/278, failed122/132,123/133,124/134 and accepted125/135 preserved; installed/drafts/foreign untouched.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
