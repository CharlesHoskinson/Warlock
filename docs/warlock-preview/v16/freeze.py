"""Hold fresh native-demand resumption, exact retained oracles and failed attempt."""
import hashlib,json,pathlib,stat,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v19';native=REPO/'implementation/warlock-client-provider-native-v11';model=REPO/'implementation/warlock-source-presenter-model-v5'
def sole(root,pattern):
 paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verifyBuild(root):
 p=sole(root,'qa/build-*/report.json');r=json.loads(p.read_text());assert r['passed'] and len(r['commands'])==48 and all(c['exitCode']==0 for c in r['commands'])
 for rel,h in r['inputs'].items():assert sha(root/rel)==h,rel
 for rel,h in r['artifacts'].items():assert sha(p.parent/rel)==h,rel
 assert sha(p.parent/'elm-host')==r['binarySHA256']
 for name,count in [('client-observation-tests',153),('typed-source-presenter-replay',46),('client-denial-tests',104),('typed-source-denial-replay',445),('client-resume-tests',69)]:assert json.loads((p.parent/(name+'.stdout')).read_text())['checks']==count
 return p,r
oldBuild,oldBuilt=verifyBuild(REPO/'implementation/warlock-preview-provider-v18');build,built=verifyBuild(provider)
# The corrected host C reporting does not change any selected Elm/C++ model input.
for rel,h in oldBuilt['inputs'].items():
 if rel.startswith(('src/','native/')) and rel!='native/shared-host.c':assert built['inputs'][rel]==h,rel
assert built['compiledAssetPackage']['files']==oldBuilt['compiledAssetPackage']['files']
selected=sole(model,'qa/check-*/report.json');checked=json.loads(selected.read_text());assert checked['passed']
for p,h in checked['inputs'].items():assert sha(p)==h,p
for rel,h in checked['artifacts'].items():assert sha(selected.parent/rel)==h,rel
oldModel=json.loads(sole(REPO/'implementation/warlock-source-presenter-model-v4','qa/check-*/report.json').read_text());assert checked['selectedNames'][:30]==oldModel['selectedNames'] and checked['coupledTraces'][:30]==oldModel['coupledTraces']
assert len(checked['selectedNames'])==39 and len(checked['coupledTraces'])==39 and sum(t['statesCompared'] for t in checked['coupledTraces'])==258
campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text());assert observed['passed'] and observed['cleanupPassed'] and all(c['passed'] for c in observed['checks']) and all(x['exitCode']==0 for x in observed['ownedExitCodes'])
pre=json.loads((native/'qa/preflight.json').read_text())
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in observed['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v9','qa/native-*/report.json').read_text());names=[c['name'] for c in prior['checks']];assert len(names)==828 and [c['name'] for c in observed['checks'] if c['name'] in set(names)]==names
failedRoot=REPO/'implementation/warlock-client-provider-native-v10';failure=sole(failedRoot,'qa/native-*/report.json');failed=json.loads(failure.read_text());assert not failed['passed'] and failed['cleanupPassed'] and failed['error']=="AssertionError('resumedNewPhysicalRetirementBeforeACK6')" and all(x['exitCode']==0 for x in failed['ownedExitCodes'])
for p,h in json.loads((failedRoot/'qa/preflight.json').read_text())['inputs'].items():assert sha(p)==h,p
for rel,h in failed['artifacts'].items():assert sha(failure.parent/rel)==h,rel
originalPixels=observed['resumedPixels']['original'];newPixels=observed['resumedPixels']['new'];assert originalPixels['yellow']==768 and originalPixels['blue']==0 and newPixels['blue']==768 and newPixels['yellow']==0 and newPixels['green']==0 and originalPixels['green']==0 and not observed['resumedPixels']['hardwarePresentation']
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);destination.write_text(json.dumps(metadata,indent=2)+'\n')
 return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(REPO/'implementation/warlock-preview-provider-v18',{'status':'full-compiled-native-fresh-demand-resumption','fullGUIBuildPassed':True,'actualResumeSchedulerBrokerGIOChecks':69,'nativeAttempt':str(failure.relative_to(REPO)),'nativeAttemptPassed':False,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(failedRoot,{'status':'failed-final-physical-observation-gate-held','nativePassed':False,'cleanupPassed':True,'error':failed['error'],'allOwnedExitsNormal':True}))
held.append(hold(model,{'status':'thirty-nine-selected-source-observation-denial-resumption-scenarios-qualified','selectedScenarios':39,'compiledStatesCompared':258,'actualCppAndElmStates':sum(t['statesCompared'] for t in checked['coupledTraces'] if t['actualCppAndElm']),'retainedOriginalScenarios':30,'retainedOriginalStates':172,'sameModelCodeAndElmInCorrectedProviderVerified':True}))
held.append(hold(native,{'status':'actual-full-GUI-new-lease-fresh-capture-after-lock-retirement-and-ACK-qualified','nativeControls':len(observed['checks']),'retainedOriginalControls':828,'normalOwnedExits':len(observed['ownedExitCodes']),'cleanupPassed':True,'samePhysicalBrokerAndReceiptSequence':True,'currentChangedWebKitPixels':True,'originalDeadlinesPreserved':True,'hardwarePresentationQualified':False,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(provider,{'status':'fresh-native-demand-and-command-time-physical-ownership','fullGUIBuildPassed':True,'actualResumeSchedulerBrokerGIOChecks':69,'actualElmDenialChecks':445,'nativeDecoderBrokerGIODenialChecks':104,'actualGIOObservationChecks':153,'qualifiedNativeResumption':held[-1],'selectedConformance':held[-2],'productionCaptureWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [oldBuild,build,campaign,selected,failure]},'boundedNativeFreshDemandQualified':True,'nativeControls':len(observed['checks']),'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual native stopped/minimized source and Historical retention; then production multi-family/fidelity original preview13 and all remaining coherent GUI release gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':len(observed['checks']),'normalExits':len(observed['ownedExitCodes']),'components':held,'report':str(out)}))
