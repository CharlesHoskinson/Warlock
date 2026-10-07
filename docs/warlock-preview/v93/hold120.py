"""Hold the bounded native driver evidence without claiming GUI activation."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v120';sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
names={'driver':'policy-driver-check-1791374752531149246','refinement':'policy-driver-refinement-1791375056222896012','build':'build-1791374781476163192'}
paths={k:root/'qa'/v/'report.json' for k,v in names.items()};declared=set();verified=set()
def verify(path,current):
 d=json.loads(path.read_text());assert not d['nativeAcceptance'] and not d['fullReleaseAccepted']
 if current:assert d['passed'],path
 for rel,value in d.get('inputs',{}).items():assert sha((root if current else path.parent/'inputs')/rel)==value,(path,rel)
 for rel,value in d.get('artifacts',{}).items():
  p=path.parent/rel;assert sha(p)==value,(path,rel);declared.add(str(p.relative_to(root)))
 for category in ['compilerDependencies','linkedLibraries','tools']:
  for name,row in d.get(category,{}).items():assert sha(name)==row['sha256'],(category,name)
 verified.add(path);return d
reports={k:verify(p,True) for k,p in paths.items()}
e=reports['driver']['evidence'];assert e['checks']==2250 and e['preGrantFaultChecks']==9 and e['nativePolicyInstances']==1 and e['nativeTransportInstances']==1 and e['rendererWindowPolicies']==0 and e['ordinaryInputsRetained']==1065 and e['retainedInputByteLimit']==16*1024*1024 and e['normalOwnedExit'] and e['normalOwnedPeerExit'] and e['nativeGrantResets']==0 and e['actualControlledC'] and e['syntheticNativePeer'] and not e['actualWebKit'] and not e['actualCapturedFD']
r=reports['refinement'];assert r['namedScenarios']==14 and r['invariantSamples']==200 and len(r['concreteTraceWitnesses'])==6 and r['concreteObservedStates']>=20 and len(r['compiledNativeVariants'])==4 and all(x['detected'] and not x['normalCloseClaimed'] for x in r['compiledNativeVariants'])
b=reports['build'];assert len(b['commands'])==116 and all(x['exitCode']==0 for x in b['commands']);assert sha(paths['build'].parent/'elm-host')==b['binarySHA256']
a=json.loads((root/'ANCESTRY.json').read_text());parent=pathlib.Path(a['parent']);manifest=parent/'component-manifest.json';assert sha(manifest)==a['parentManifestSHA256'];prior=json.loads(manifest.read_text());assert prior['sourceHeld'] and prior['passed'] and prior['orderedVisualCustodyCPUQualified'] and prior['fullBuildCommands']==115
for rel,row in prior['files'].items():assert sha(parent/rel)==row['sha256'],rel
for base in ['native','assets','adapter','src','spec']:
 for f in (parent/base).glob('*'):
  if f.is_file():assert sha(root/base/f.name)==sha(f),f
native=pathlib.Path(a['nativeBaselineManifest']);assert sha(native)==a['nativeBaselineManifestSHA256'];baseline=json.loads(native.read_text());assert baseline['sourceHeld'] and baseline['passed'] and baseline['nativeChecks']==2518 and baseline['normalOwnedExits']==278
for rel,row in baseline['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
old=json.loads(pathlib.Path(prior['reports']['build']['path']).read_text());assert [x['name'] for x in b['commands'] if x['name']!='preview-policy-driver.cpp-compile']==[x['name'] for x in old['commands']]
historical=[];failed=[]
for p in sorted((root/'qa').glob('*/report.json')):
 if p not in verified:
  d=verify(p,False);historical.append({'path':str(p),'sha256':sha(p),'passed':d['passed']})
  if not d['passed']:failed.append(str(p))
assert len(failed)==3 and len(historical)==5
result={'schema':1,'owner':a['owner'],'sourceHeld':True,'passed':True,'evidenceIntegrityPassed':True,'reports':{k:{'path':str(p),'sha256':sha(p)} for k,p in paths.items()},'historicalReports':historical,'heldFailedReports':failed,'singlePreviewPolicy':True,'parentElmPolicyUnchanged':True,'parentNativeIssuerAndPhysicalProductUnchanged':True,'parentAssetsAndAdaptersUnchanged':True,'nativeOwnedJavaScriptCore':True,'persistentPolicyContexts':1,'nativePolicyDriverCPUQualified':True,'driverChecks':2250,'preGrantFaultChecks':9,'ordinaryInputCapacity':1065,'ordinaryInputByteLimit':16*1024*1024,'driverScenarios':14,'driverSamples':200,'concreteTraceWitnesses':6,'concreteObservedStates':r['concreteObservedStates'],'compiledNativeVariantsDetected':4,'rendererWindowPolicies':0,'nativeGrantResets':0,'fullBuildCommands':116,'originalBuildCommands':115,'nativeTicketCustodyCPUQualified':True,'independentNativeConfirmationCPUQualified':True,'nativeOutputQueueResourceBoundQualified':False,'realHostPolicyActivated':False,'actualRendererProjectionActivated':False,'actualDOMQualified':False,'actualWebKitContextAuthenticationQualified':False,'physicalConcealmentQualified':False,'ongoingProjectionFreshnessQualified':False,'realHostInputBackpressureQualified':False,'nativeDelayedProposalLivenessQualified':False,'uncertainLiveWorkerRecoveryQualified':False,'processLossInputJournalQualified':False,'fullElmRecoveryQualified':False,'typedHostRoutingActivated':False,'webKitActivated':False,'actualWaylandWindowAcceptance':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'parentManifest':str(manifest),'parentManifestSHA256':sha(manifest),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'scope':(root/'POLICY-DRIVER-HANDOFF.md').read_text()}
files={}
for f in sorted(root.rglob('*')):
 rel=f.relative_to(root);name=str(rel)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts and name not in declared:continue
 assert not f.is_symlink(),f
 if f.is_file():files[name]={'kind':'file','sha256':sha(f),'size':f.stat().st_size,'mode':oct(stat.S_IMODE(f.stat().st_mode))}
result['files']=files;assert not (root/'component-manifest.json').exists();(root/'component-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
out=pathlib.Path(__file__).parent/'component-report120.json';assert not out.exists();out.write_text(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2)+'\n')
task=repo/'openspec/changes/warlock-preview-actor-retirement/tasks.md';text=task.read_text();old='- [ ] Freeze CONTROL-033 native driver atomic input custody';assert text.count(old)==1;task.write_text(text.replace(old,'- [x] Freeze CONTROL-033 native driver atomic input custody'))
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,a['owner'],str(root.relative_to(repo)),['PROGRESS heldGUI120 creator-owned native driver integrates the unchanged original persistent JSC Elm policy and native-issued outbox. Actual C/Native issuer/Broker/receipt/scoped detachment/strict closure with synthetic peer2250, constructor fault checks9, ordinary atomic input1065/16MiB and quarantine through pressure. Exact original ticket retained before separate issued notification/dispatch; callbacks store only; independent native confirmation never settles Unknown physical duties. Quint custody14/200 samples/six concrete ordered witnesses/four compiled guards; full116 retains115. Three failed reports held including fixture transport-size and mutant unused-parameter failures. Parent policy/native issuer/effects/physical/assets/adapters byte-identical. Driver links but actual legacy host does not activate it; Native131 remains actualGUI119 legacy2518/278. Next PUBLIC90 and bounded retained native output/paused producer scheduling before actual controlled host/pure renderer WebKit identity/async frame/physical concealment/URI. Live uncertain/process recovery and delayed never-issued proposal outcomes/full release gates remain open. No installed/foreign changes.'],'progress',[str((root/'component-manifest.json').relative_to(repo)),str(out.relative_to(repo))]))
print(json.dumps({'heldFiles':len(files),'fullBuildCommands':116,'nativeAcceptance':False,'fullReleaseAccepted':False}))
