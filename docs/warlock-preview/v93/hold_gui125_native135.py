"""Hold bounded actual controlled admission/drain; retain all failed predecessors."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');gui=repo/'implementation/warlock-preview-provider-v125';native=repo/'implementation/warlock-client-provider-native-v135';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=list(native.glob('qa/native-controlled-*/report.json'));assert len(reports)==1;report=reports[0];d=json.loads(report.read_text())
assert d['passed'] and not d['nativeAcceptance'] and not d['fullReleaseAccepted'] and d['cleanupPassed'] and all(x['exitCode']==0 for x in d['ownedExitCodes'])
checks={x['name']:x for x in d['checks']};assert all(x['passed'] for x in checks.values())
for name in ['controlledFactoryAbsentBeforeActualGTKAdmission','controlledFactoryAfterOriginalGTKAdmission','controlledActualPureWebKitRendererInitializedOnce','controlledActualDOMAndNativeCurrentProjectionReceipt','controlledOriginalNativeTicketsActuallyIssuedAndDelivered','controlledNoLegacyBrowserCommandRoute','controlledOriginalPolicyInputTicketConfirmationCustodyDrained','controlledFullHostNormalExit']:
 assert checks[name]['passed'],name
for key in ['actualControlledFactoryActivated','actualNativePolicyDriverActivated','actualPureWebKitRendererActivated','actualScopedURIRouterRegistered','actualDOMStampReceiptObserved']:assert d[key],key
for key in ['physicalRevealQualified','physicalConcealmentQualified','actualCapturedPixelsQualified','fullWorkloadProgressQualified','reloadRecoveryQualified']:assert not d[key],key
pre=json.loads((native/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in d['artifacts'].items():assert sha(report.parent/rel)==h,rel
build=pathlib.Path(pre['controlledHostBuild']);b=json.loads(build.read_text());assert b['passed'] and len(b['commands'])==119 and all(x['exitCode']==0 for x in b['commands'])
for n,h in b['inputs'].items():assert sha(gui/n)==h,n
for n,h in b['artifacts'].items():assert sha(build.parent/n)==h,n
for category in ['compilerDependencies','linkedLibraries','tools']:
 for p,row in b[category].items():assert sha(p)==row['sha256'],p
assert sha(build.parent/'elm-host')==b['binarySHA256']
parent=repo/'implementation/warlock-preview-provider-v124';prior=json.loads((parent/'component-manifest.json').read_text());assert prior['sourceHeld'] and not prior['passed']
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
scope='QA-only original GTK admission, one persistent native Elm policy, pure WebKit renderer initialized once, current DOM receipt, original native ticket delivery/independent confirmation and strict normal controlled-host drain/teardown qualified on core16/plugin19/AQ155 with the unchanged six-second scenario. Original native readonly actor inventory stops identity-based producer queries after scoped C mapping removal while pending terminal/retirement/detachment delivery continues. All failed GUI122/Native132, GUI123/Native133 and GUI124/Native134 evidence remains immutable. Exact compiled page asset closure/current full119 passed. Native opacity curtain remains closed: this does not qualify physical concealment/reveal, captured pixels, workload/pressure/RSS, reload/uncertain recovery, full S09 preview13 or full release. No installed/draft/foreign changes.'
common={'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':True,'cpuBuildPassed':True,'fullBuildCommands':119,'actualNativeGTKAdmissionObserved':True,'actualPureRendererInitializationObserved':True,'actualPureRendererInitializationQualified':True,'actualCurrentProjectionDOMReceiptObserved':True,'actualControlledAdmissionAndDrainQualified':True,'normalControlledHostClosureQualified':True,'privateSessionCleanupPassed':True,'nativeChecks':len(d['checks']),'normalOwnedExits':len(d['ownedExitCodes']),'nativeGrantResets':0,'singlePreviewPolicy':True,'originalNativePolicyIssuerPhysicalProductUnchanged':True,'compiledPageAssetClosureQualified':True,'physicalConcealmentQualified':False,'physicalRevealQualified':False,'actualCapturedPixelsQualified':False,'fullWorkloadProgressQualified':False,'measuredRSSQualified':False,'reloadRecoveryQualified':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':scope,'reports':{'build':{'path':str(build),'sha256':sha(build)},'controlledNative':{'path':str(report),'sha256':sha(report)}},'heldFailedPredecessors':failed}
for root in [gui,native]:
 files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 out=root/'component-manifest.json';assert not out.exists();out.write_text(json.dumps(dict(common,files=files),indent=2)+'\n');print(root.name,len(files))
out=pathlib.Path(__file__).with_name('component-report125.json');assert not out.exists();out.write_text(json.dumps(common,indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=task.read_text();old='- [ ] Freeze CONTROL-036 exact compiled page script/style/owning allowlist closure';assert s.count(old)==1;s=s.replace(old,old.replace('[ ]','[x]'))
s+='\n- [x] Freeze bounded CONTROL-035 actual original GTK admission, single native policy,\n  one-time pure WebKit renderer/current DOM receipt and strict normal drain/teardown\n  in GUI125/Native135; retain failures. Physical frame/reveal, pressure/performance,\n  reload/uncertain recovery and full controlled-route qualification remain open.\n';task.write_text(s)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,common['owner'],str(gui.relative_to(repo)),['PROGRESS heldGUI125/Native135 bounded actual controlled GTK/native single policy/pure WebKit renderer once/current DOM receipt/original native ticket and independent confirmation/strict normal drain. '+str(common['nativeChecks'])+' checks/'+str(common['normalOwnedExits'])+' normal owned exits/private cleanup, unchanged scenario/deadline6/core16/plugin19/AQ155. Original readonly actor inventory stops identity queries after scoped mapping removal; pending journals continue, absence never settles custody. Full119 and exact page assets pass; all failed122/132,123/133,124/134 held unchanged. Native curtain remains closed; physical frame/reveal/captured pixels/actual pressure/workload/RSS/reload and uncertain recovery/full S09 preview13/full release remain open. Next PUBLIC92, then actual captured-image renderer/WebKit URI/frame/physical qualification. Original legacy Native1312518/278 baseline/installed/drafts/foreign preserved.'],'progress',[str((gui/'component-manifest.json').relative_to(repo)),str((native/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
