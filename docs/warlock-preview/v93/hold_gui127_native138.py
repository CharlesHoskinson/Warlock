"""Hold bounded actual controlled admission/drain; retain all failed predecessors."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v127';native=repo/'implementation/warlock-client-provider-native-v138';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(native.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and d['cleanupPassed'] and all(x['exitCode']==0 for x in d['ownedExitCodes'])
checks={x['name']:x for x in d['checks']};assert all(x['passed'] for x in checks.values())
for name in ['controlledFactoryAbsentBeforeActualGTKAdmission','controlledFactoryAfterOriginalGTKAdmission','controlledActualPureWebKitRendererInitializedOnce','controlledActualDOMAndNativeCurrentProjectionReceipt','controlledOriginalNativeTicketsActuallyIssuedAndDelivered','controlledNoLegacyBrowserCommandRoute','controlledOriginalPolicyInputTicketConfirmationCustodyDrained','controlledFullHostNormalExit']:
 assert checks[name]['passed'],name
for key in ['actualControlledFactoryActivated','actualNativePolicyDriverActivated','actualPureWebKitRendererActivated','actualScopedURIRouterRegistered','actualDOMStampReceiptObserved']:assert d[key],key
for key in ['physicalRevealQualified','physicalConcealmentQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[key],key
assert len(d['checks'])==29 and len(d['ownedExitCodes'])==13 and d['actualCapturedPixelsQualified'] and d['actualScopedURIImageLoadObserved']
pixels=d['actualOffscreenWebKitPixels'];assert pixels['red']==19200 and pixels['green']==0 and pixels['blue']==0
original=json.loads((repo/'implementation/warlock-client-provider-native-v137/qa/native-controlled-1791384978375197831/report.json').read_text());assert {x['name'] for x in original['checks']}<=set(checks) and {x['name'] for x in original['ownedExitCodes']}<={x['name'] for x in d['ownedExitCodes']}
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==119 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
parent=repo/'implementation/warlock-preview-provider-v126';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['sourceHeld'] and prior['passed'] and prior['normalControlledHostClosureQualified']
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','src','adapter','assets']:
 for p in (parent/base).glob('*'):
  if p.is_file() and p.name!='controlled-preview-host.h':assert sha(gui/base/p.name)==sha(p),p
failed=[]
for g,n in [(122,132),(123,133),(124,134)]:
 for name in [f'warlock-preview-provider-v{g}',f'warlock-client-provider-native-v{n}']:
  root=repo/'implementation'/name;m=root/'component-manifest.json';held=json.loads(m.read_text());assert held['sourceHeld'] and not held['passed']
  for rel,row in held['files'].items():assert sha(root/rel)==row['sha256'],rel
  failed.append({'path':str(m),'sha256':sha(m)})
scope='QA-only actual original native popup/view/projection scoped GTK after-paint and GDK geometry observer, with strong single pending callback ownership and cancellation. Original grim private output independently decodes248976 opaque samples in live native popup region[58,96,684,364], with zero red/green/blue while original pure WebKit reference contains19200 red pixels and the original native image/context stays current before/after capture. All original26 controls retained;29 checks/13 normal owned exits/private cleanup/original deadline6/core16/plugin19/AQ155/full119. This is a positive bounded region observation; an actual unsafe-curtain control is still required before qualification. GTK paint phase is not compositor/hardware proof, and ongoing transition concealment/physical reveal/recovery remain open. Original Elm policy/Native issuer/physical/journal/independent confirmation/strict close unchanged; full release unqualified.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationObserved':True,'actualPureRendererInitializationQualified':True,'actualCurrentProjectionDOMReceiptObserved':True,'actualControlledAdmissionAndDrainQualified':True,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'nativeGrantResets':0,'singlePreviewPolicy':True,'originalNativePolicyIssuerPhysicalProductUnchanged':True,'compiledPageAssetClosureQualified':True,'actualNativeGTKPaintObservation':d['actualNativeGTKPaintObservation'],'actualClosedCurtainRegionObserved':True,'actualClosedCurtainRegionPixels':d['actualClosedCurtainRegionPixels'],'boundedClosedCurtainRegionQualified':False,'hardwarePresentationQualified':False,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'actualCapturedPixelsQualified':True,'actualScopedURIImageLoadObserved':True,'actualOffscreenWebKitPixels':d['actualOffscreenWebKitPixels'],'actualStaleSnapshotCallbackQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':{'build':{'path':str(build),'sha256':sha(build)},'controlledNative':{'path':str(report),'sha256':sha(report)}},'heldFailedPredecessors':failed}
for root in [gui,native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(dict(common,files=files),indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report127.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
assert d['actualClosedCurtainRegionObserved'] and not d['boundedClosedCurtainRegionQualified'] and d['actualClosedCurtainRegionPixels']['red']==0 and d['actualNativeGTKPaintObservation']['opacity']==0
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],str(gui.relative_to(repo)),['PROGRESS heldGUI127/Native138 positive original native popup/view/current-projection GTK paint and GDK geometry observation: actual x50/y48/700x420, opacity0/GTKframe6; independent native output region[58,96,684,364]248976opaque samples zero preview/foreign colors while original WebKit image19200red/native image remains current. Original26 controls retained;29checks13normalexits/privatecleanup/deadline6/core16/plugin19/AQ155/full119. Strong one pending callback with cancellation implemented. Bounded closed-curtain region remains unqualified pending actual unsafe-curtain negative control; GTK after-paint is not physical compositor/hardware proof, ongoing transition concealment/reveal/recovery/full release open. Next fresh GUI128/Native139 actual QA-only unsafe opacity1 variant under unchanged Native138 oracle, retain original failure and resource custody; qualify only detector evidence. Policy/native issuer/physical/journal/confirmation/strict close unchanged. Legacy, all failures,125/135,126/136,137 preserved; installed/drafts/foreign untouched.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
