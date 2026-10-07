"""Hold persistent native-owned Elm lifetime evidence without host activation."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v116';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'nativeElmOutbox':'persistent-policy-native-check-v3-1791365589086439980','lifetime':'persistent-policy-lifetime-check-1791366150195930012','backpressure':'persistent-policy-backpressure-check-1791366361682821759','build':'build-1791366361680010300'}
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
assert n['checks']==207 and n['singlePreviewPolicy'] and n['normalOwnedExit'] and n['realmEpochs']==2 and n['nativeGrantResets']==0 and n['syntheticNativeRemainsActive'] and n['nativeOwnedJavaScriptCore'] and n['persistentPolicyContexts']==1 and n['rendererElmInstances']==0 and n['freshJSContexts']==2
l=reports['lifetime'];assert l['boundaryChecks']==37 and l['originalInvalidInputs']==12 and len(l['constructorFaults'])==13 and all(x['beforeNativeGrant'] and x['normalOwnedExit'] for x in l['constructorFaults']);assert l['namedScenarios']==8 and len(l['coupledTraces'])==20 and l['statesCompared']==405 and l['invariantSamples']==200 and l['unsafeCompiledNativeVariantsDetected']==3 and all(x['normalOwnedExit'] for x in l['coupledTraces'])
p=reports['backpressure'];assert p['checks']==48 and p['explicitWouldBlockControls']==3 and p['normalOwnedExit'] and p['singlePreviewPolicy'] and p['syntheticNativeIssuedFacts']
b=reports['build'];assert len(b['commands'])==110 and all(x['exitCode']==0 for x in b['commands']);assert sha(paths['build'].parent/'elm-host')==b['binarySHA256'];assert 'native-preview-policy.js' in b['compiledAssetPackage']['files']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);manifest=parent/'component-manifest.json';assert sha(manifest)==a['parentManifestSHA256'];prior=json.loads(manifest.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['fullBuildCommands']==108
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','assets','adapter','src']:
 for p in (parent/base).glob('*'):
  if p.is_file():assert sha(root/base/p.name)==sha(p),p
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());added={'native-owned-policy-build','elm-preview-policy.cpp-compile'};assert [x['name'] for x in b['commands'] if x['name'] not in added]==[x['name'] for x in old['commands']]
assert sha(root/'qa/build.py')==sha(parent/'qa/build.py')
history=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p in verified:continue
 d=verify(p);history.append({'path':str(p),'sha256':sha(p),'passed':d['passed'],'qualifiesFinalSource':False})
 if not d['passed']:failed.append(str(p))
assert len(failed)==5
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalPhaseReports':history,'heldFailedReports':failed,'singlePreviewPolicy':True,'originalWindowPolicyUnchanged':True,'nativeOwnedJavaScriptCore':True,'persistentPolicyContexts':1,'rendererElmInstancesInCoupling':0,'freshTransportContexts':2,'nativeElmOutboxChecks':207,'lifetimeBoundaryChecks':37,'constructorFaults':13,'backpressureChecks':48,'explicitWouldBlockControls':3,'lifetimeScenarios':8,'lifetimeTraces':20,'lifetimeStates':405,'lifetimeSamples':200,'lifetimeCompiledNativeVariantsDetected':3,'realmEpochs':2,'nativeGrantResets':0,'fullBuildCommands':110,'originalBuildCommands':108,'parentNativeProductUnchanged':True,'parentAssetsAndAdaptersUnchanged':True,'parentManifest':str(manifest),'parentManifestSHA256':sha(manifest),'persistentPolicyCPUQualified':True,'hostLibraryLinked':True,'realHostPolicyActivated':False,'rendererProjectionImplemented':False,'nativeDelayedProposalLivenessQualified':False,'realHostInputBackpressureQualified':False,'uncertainLiveWorkerRecoveryQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':(root/'PERSISTENT-POLICY-HANDOFF.md').read_text()}
files={}
for p in sorted(root.rglob('*')):
 rel=p.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not p.is_symlink(),p
 if p.is_file():files[name]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report116.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Freeze CONTROL-029 persistent native-owned JavaScriptCore Elm policy';assert text.count(old)==1;text=text.replace(old,'- [x] Freeze CONTROL-029 persistent native-owned JavaScriptCore Elm policy');text+='\nGUI116 current CPU qualification: native-owned JSC/original C coupling207/two\nepochs/unchanged Native grant/two fresh transport contexts/one policy/normal exits;\nlifetime37/13 pre-grant faults; explicit WOULD_BLOCK48 controls; Quint8/20 actual\nC+JSC traces/405 states/200 samples/three compiled guard variants; full110 retains\noriginal108. Five failed attempts held. Actual host library links but does not\ncreate a worker or switch Popup routes. Renderer projection without another\npolicy, durable host input/ticket custody, WebKit/Core activation, uncertain live\nworker/process recovery and all original release gates remain open.\n';task.write_text(text)
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI116 native-owned persistent JavaScriptCore optimized Elm worker, unchanged original single window policy. Actual C/Native synthetic peer coupling207/two epochs/unchanged Native grant/two fresh transport contexts/one policy/normal exits; lifetime37/13 pre-grant faults; explicit WOULD_BLOCK48; Quint8/20 actual C+JSC traces/405 states/200 samples/three compiled guards; full110 retains108. Five failed attempts and exact original snapshots remain. Actual host links library but worker/Popup route inactive. Next PUBLIC85 then typed stateless renderer projection, durable host input custody/backpressure and native sender channel/ticket custody/retry before real WebKit/Core activation. Live uncertain worker/process recovery and delayed expiry/revocation liveness remain separate. Native130 legacy2518/278/core16/plugin19/AQ155 remains actual baseline; all original full release gates open, no installed changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':110,'failedAttemptsHeld':len(failed)}))
