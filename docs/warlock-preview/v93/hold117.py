"""Hold typed visual projection with original policy identity and bounded proofs."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v117';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'nativeElmOutbox':'persistent-policy-visual-native-check-1791367865174261140','visualCodec':'visual-codec-check-1791367865172810846','visualPolicy':'visual-policy-check-1791368330476360072','lifetime':'persistent-policy-lifetime-check-1791368137362036835','backpressure':'persistent-policy-backpressure-check-1791368137361009462','build':'build-1791368137355277472'}
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current=False):
 d=json.loads(path.read_text());assert not d.get('nativeAcceptance',False) and not d.get('fullReleaseAccepted',False)
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():
  p=root/rel
  if current or (p.exists() and sha(p)==value):assert sha(p)==value,(path,rel)
  else:assert sha(path.parent/'inputs'/rel)==value,(path,rel,'held original input')
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 if 'pluginResourceHeaderSHA256' in d:assert sha(root.parent/'warlock-family-style-crop-capture-v19/native/capture-resources.hpp')==d['pluginResourceHeaderSHA256']
 if current:
  for key in ['compilerDependencies','linkedLibraries','tools']:
   for name,row in d.get(key,{}).items():assert sha(name)==row['sha256'],(key,name)
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()};n=reports['nativeElmOutbox']['evidence']
assert n['checks']==207 and n['visualProjectionChecks']==90 and n['singlePreviewPolicy'] and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['syntheticNativeRemainsActive'] and n['nativeOwnedJavaScriptCore'] and n['persistentPolicyContexts']==1 and n['rendererWindowPolicyInstances']==0 and n['pureRendererDecoderInstances']==1 and n['freshJSContexts']==2
c=reports['visualCodec']['evidence'];assert c['checks']==101 and c['windowPolicyInstances']==0 and c['originalPopupCapacity']==2051 and c['originalBarCapacity']==259 and c['losslessUInt64']
v=reports['visualPolicy']['evidence'];assert v['checks']==150 and v['syntheticNativeFacts'] and v['normalOwnedExits']==2 and v['cohorts']==['client','family'] and not v['actualDOM'] and not v['actualCapturedFD']
l=reports['lifetime'];assert l['boundaryChecks']==37 and len(l['constructorFaults'])==13 and l['namedScenarios']==8 and len(l['coupledTraces'])==20 and l['statesCompared']==405 and l['invariantSamples']==200 and l['unsafeCompiledNativeVariantsDetected']==3
p=reports['backpressure'];assert p['checks']==48 and p['explicitWouldBlockControls']==3 and p['normalOwnedExit'] and p['syntheticNativeIssuedFacts']
b=reports['build'];assert len(b['commands'])==112 and all(x['exitCode']==0 for x in b['commands']);assert sha(paths['build'].parent/'elm-host')==b['binarySHA256'];assert 'native-visual-decoder.js' in b['compiledAssetPackage']['files']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);manifest=parent/'component-manifest.json';assert sha(manifest)==a['parentManifestSHA256'];prior=json.loads(manifest.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['fullBuildCommands']==110
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
changed={'src/PreviewLifecycle.elm','src/PreviewPresenter.elm','src/RetainedPreviewPresenter.elm','src/SurfaceRenderer.elm','src/NativePreviewPolicy.elm','native/elm-preview-policy.cpp'}
for base in ['native','assets','adapter','src']:
 for p in (parent/base).glob('*'):
  if p.is_file() and str(p.relative_to(parent)) not in changed:assert sha(root/base/p.name)==sha(p),p
def without_header(text):return '\n'.join(line for line in text.splitlines() if not line.startswith(('module ','import ')))
old=(parent/'src/PreviewLifecycle.elm').read_text();fresh=(root/'src/PreviewLifecycle.elm').read_text();assert without_header(old[:old.index('view :')])==without_header(fresh[:fresh.index('view :')]);assert old[old.index('metadataVisible :'):]==fresh[fresh.index('metadataVisible :'):]
old=(parent/'src/PreviewPresenter.elm').read_text();fresh=(root/'src/PreviewPresenter.elm').read_text();assert without_header(old[:old.index('image :')])==without_header(fresh[:fresh.index('image :')]);assert old[old.index('outcomeName :'):]==fresh[fresh.index('outcomeName :'):]
old=(parent/'src/RetainedPreviewPresenter.elm').read_text();fresh=(root/'src/RetainedPreviewPresenter.elm').read_text();assert without_header(old[:old.index('image :')])==without_header(fresh[:fresh.index('image :')]);assert old[old.index('observe :'):]==fresh[fresh.index('observe :'):]
old=(parent/'native/elm-preview-policy.cpp').read_text();fresh=(root/'native/elm-preview-policy.cpp').read_text();assert fresh.replace('"enrollment", "feedback", "visuals"','"enrollment", "feedback"')==old
for name in ['PreviewVisual.elm','NativePreviewVisual.elm','NativePreviewVisualReplay.elm']:
 body=(root/'src'/name).read_text();assert all(('import '+policy) not in body for policy in ['PreviewLifecycle','PreviewPresenter','RetainedPreviewPresenter'])
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());added={'native-visual-decoder-build','native-visual-decoder-boundaries'};assert [x['name'] for x in b['commands'] if x['name'] not in added]==[x['name'] for x in old['commands']]
history=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p in verified:continue
 d=verify(p);history.append({'path':str(p),'sha256':sha(p),'passed':d['passed'],'qualifiesFinalSource':False})
 if not d['passed']:failed.append(str(p))
assert len(failed)==3
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalPhaseReports':history,'heldFailedReports':failed,'singlePreviewPolicy':True,'originalLifecycleTransitionsUnchanged':True,'sharedVisualDecisionsImplemented':True,'typedVisualProjectionImplemented':True,'pureRendererDecoderWindowPolicies':0,'nativeOwnedJavaScriptCore':True,'persistentPolicyContexts':1,'freshTransportContexts':2,'nativeElmOutboxChecks':207,'additiveVisualProjectionChecks':90,'visualDecoderChecks':101,'visualPolicyChecks':150,'visualPolicyFactsSynthetic':True,'lifetimeBoundaryChecks':37,'constructorFaults':13,'backpressureChecks':48,'lifetimeScenarios':8,'lifetimeTraces':20,'lifetimeStates':405,'lifetimeSamples':200,'lifetimeCompiledNativeVariantsDetected':3,'realmEpochs':2,'nativeGrantResets':0,'fullBuildCommands':112,'originalBuildCommands':110,'parentNativeIssuerAndPhysicalProductUnchanged':True,'parentAssetsAndAdaptersUnchanged':True,'parentManifest':str(manifest),'parentManifestSHA256':sha(manifest),'visualProjectionCPUQualified':True,'hostLibraryLinked':True,'realHostPolicyActivated':False,'actualRendererProjectionActivated':False,'actualDOMQualified':False,'projectionDeliveryOrderingQualified':False,'nativeDelayedProposalLivenessQualified':False,'realHostInputBackpressureQualified':False,'uncertainLiveWorkerRecoveryQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'VISUAL-PROJECTION-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not p.is_symlink(),p
 if p.is_file():files[name]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report117.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Freeze CONTROL-030 shared typed visual projection';assert text.count(old)==1;text=text.replace(old,'- [x] Freeze CONTROL-030 shared typed visual projection');text+='\nGUI117 CPU projection: original C/JSC/native207 plus90 pure visual comparisons,\ncodec101, client/family display150 with explicit synthetic native facts/normal\nexits; current lifetime37/13 faults/backpressure48/Quint8/20 actual C+JSC traces/\n405 states/three guards/full112 retains110. Original lifecycle/native issuance/\nphysical transitions remain unchanged. Three compile failures held. Actual DOM,\ncurrent-projection delivery ordering/custody, controlled host/WebKit/Core/URI\nactivation and all original full release gates remain open.\n';task.write_text(text)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI117 shared typed visual projection from unchanged single window/lifecycle transitions. Same original render/status/auth/concealment decisions feed legacy view and pure DTO decoder. Original C/JSC/native207 plus90 visual comparisons/two epochs/unchanged Native grant/normal exits; codec101; client/family display150 with explicitly synthetic native facts/normal exits; current lifetime37/13 faults/backpressure48/Quint8/20 actual C+JSC traces/405 states/three guards; full112 retains110. Three compile failures held. Native/assets/adapters/issuer/physical product unchanged except private policy output union adding visuals. Actual host/renderer route inactive, no current-projection freshness channel or actual DOM/Core/URI proof. Next PUBLIC86 then native authenticated ordered projection custody and durable input/ticket custody/retry, actual WebKit/Core reload and uncertain worker/revoked proposal outcomes. Native130 legacy2518/278 remains actual baseline; all original full release gates remain open and installed/foreign paths preserved.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':112,'failedAttemptsHeld':len(failed)}))
