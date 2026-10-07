"""Hold ordered visual custody with actual bounded proofs and original identity."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v119';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'channel':'visual-channel-check-1791371205851102125','refinement':'visual-channel-refinement-1791371509385015823','boundaries':'visual-channel-boundaries-1791371697960291443','nativeElmOutbox':'readonly-visual-native-check-1791371575025222675'}
builds=list((root/'qa').glob('build-*/report.json'));assert len(builds)==1;names['build']=builds[0].parent.name
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current):
 d=json.loads(path.read_text());assert not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():
  if current:assert sha(root/rel)==value,(path,rel)
  else:assert sha(path.parent/'inputs'/rel)==value,(path,rel)
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 for category in ['compilerDependencies','linkedLibraries','tools']:
  for name,row in d.get(category,{}).items():assert sha(name)==row['sha256'],(category,name)
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()}
c=reports['channel']['evidence'];assert c['checks']==67 and c['persistentNativePolicies']==1 and c['pureRendererInstances']==2 and c['rendererWindowPolicies']==0 and c['normalOwnedExit'] and c['syntheticTrustedGrantAndClose'] and c['syntheticMaximumSequence'] and not c['actualWebKitContext'] and not c['actualDOM']
r=reports['refinement'];assert r['namedScenarios']==14 and r['invariantSamples']==200 and len(r['coupledTraces'])==26 and r['observableStatesCompared']==451 and r['compiledNativeVariantsDetected']==4 and len(r['counterBoundaries'])==2 and all(x['normalOwnedExit'] for x in r['counterBoundaries'])
n=reports['nativeElmOutbox']['evidence'];assert n['checks']==207 and n['visualProjectionChecks']==90 and n['readonlyProjectionChecks']==74 and n['singlePreviewPolicy'] and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['persistentPolicyContexts']==1 and n['rendererWindowPolicyInstances']==0
d=reports['boundaries'];assert d['checks']==33 and d['normalOwnedExit'] and d['syntheticNativeGrantAndClose']
b=reports['build'];assert len(b['commands'])==115 and all(x['exitCode']==0 for x in b['commands']);assert sha(paths['build'].parent/'elm-host')==b['binarySHA256'];assert {'native-visual-receiver.js','native-visual-renderer.js'}<=set(b['compiledAssetPackage']['files'])
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);manifest=parent/'component-manifest.json';assert sha(manifest)==a['parentManifestSHA256'];prior=json.loads(manifest.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['readonlyVisualCPUQualified'] and prior['fullBuildCommands']==112
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','assets','adapter','src']:
 for f in (parent/base).glob('*'):
  if f.is_file():assert sha(root/base/f.name)==sha(f),f
added={'native-visual-receiver-build','native-visual-renderer-build','preview-visual-channel.cpp-compile'};old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());assert [x['name'] for x in b['commands'] if x['name'] not in added]==[x['name'] for x in old['commands']]
for name in ['NativePreviewReceiver.elm','NativePreviewRenderer.elm','NativePreviewReceiverReplay.elm']:
 text=(root/'src'/name).read_text();assert all(('import '+policy) not in text for policy in ['PreviewLifecycle','PreviewPresenter','RetainedPreviewPresenter'])
failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p not in verified:
  d=verify(p,False);assert not d['passed'];failed.append(str(p))
assert len(failed)==1
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'heldFailedReports':failed,'singlePreviewPolicy':True,'parentElmPolicyUnchanged':True,'parentNativeIssuerAndPhysicalProductUnchanged':True,'parentAssetsAndAdaptersUnchanged':True,'nativeOwnedJavaScriptCore':True,'persistentPolicyContexts':1,'nativeElmOutboxChecks':207,'additiveVisualProjectionChecks':90,'readonlyProjectionChecks':74,'visualChannelChecks':67,'visualChannelBoundaryChecks':33,'pureRendererInstances':2,'rendererWindowPolicies':0,'visualChannelScenarios':14,'visualChannelTraces':26,'visualChannelObservableStates':451,'visualChannelSamples':200,'visualChannelCompiledNativeVariantsDetected':4,'compiledSeededCounterBoundaries':2,'nativeContextOwnershipCPUQualified':True,'orderedVisualCustodyCPUQualified':True,'nativeControlOrdinalsUnchanged':True,'fullBuildCommands':115,'originalBuildCommands':112,'realmEpochs':2,'nativeGrantResets':0,'realHostPolicyActivated':False,'actualRendererProjectionActivated':False,'actualDOMQualified':False,'actualWebKitContextAuthenticationQualified':False,'physicalConcealmentQualified':False,'ongoingProjectionFreshnessQualified':False,'realHostInputBackpressureQualified':False,'nativeDelayedProposalLivenessQualified':False,'uncertainLiveWorkerRecoveryQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'parentManifest':str(manifest),'parentManifestSHA256':sha(manifest),'scope':(root/'VISUAL-CHANNEL-HANDOFF.md').read_text()}
files={}
for f in sorted(root.rglob('*')):
 rel=f.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not f.is_symlink(),f
 if f.is_file():files[name]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report119.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Freeze CONTROL-032 native context/lease/visual-sequence custody';assert text.count(old)==1;task.write_text(text.replace(old,'- [x] Freeze CONTROL-032 native context/lease/visual-sequence custody'))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI119 native creator/context-owned ordered visual custody and pure Elm receiver. Parent policy/issuer/effects/physical/assets/adapters unchanged; native leases/separate visual sequence never consume control ordinals; strong context ref until detach; exact pending retries and latest committed-cache/domain comparison; pure renderer ignores stale lease/domain/sequence, duplicates only acceptance receipt, malformed/conflicting current visuals conceal and latch. Channel actual C/JSC/Elm67/boundaries33; Quint14/26 actual C+JSC observable traces/451 states/200 samples/four compiled guards/two seeded UInt64 exhaustion boundaries; original native207+90+74/two epochs/unchanged grant/normal; full115 retains112. One compile failure held. No actual WebKit callback authentication/DOM/frame/physical concealment/ongoing freshness: host must physically conceal before transitions and bind actual callback context/lease/async frame/URI barriers. Next PUBLIC88 then Native131 current legacy source coherence and actual controlled host input/ticket custody/retry + renderer/native WebKit barriers. Uncertain live worker/revoked delayed proposals/full release remain open, Native130 remains actual bounded legacy2518/278; installed/foreign paths preserved.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':115}))
