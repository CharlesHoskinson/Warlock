"""Hold exact retained Historical source/model/native evidence and failed attempts."""
import hashlib,json,pathlib,stat,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
provider=REPO/'implementation/warlock-preview-provider-v21';native=REPO/'implementation/warlock-client-provider-native-v14';model=REPO/'implementation/warlock-source-presenter-model-v6'
def sole(root,pattern):
 paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verifyInputs(root,p,r):
 for path,h in r['inputs'].items():assert sha(root/path if not pathlib.Path(path).is_absolute() else path)==h,path
 for rel,h in r.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
build=sole(provider,'qa/build-*/report.json');built=json.loads(build.read_text());assert built['passed'] and len(built['commands'])==50 and all(x['exitCode']==0 for x in built['commands']);verifyInputs(provider,build,built)
assert sha(build.parent/'elm-host')==built['binarySHA256']
for name,count in [('client-observation-tests',153),('typed-source-presenter-replay',46),('client-denial-tests',104),('typed-source-denial-replay',445),('client-resume-tests',69),('client-retained-presentation-tests',32)]:assert json.loads((build.parent/(name+'.stdout')).read_text())['checks']==count
selected=sole(model,'qa/check-*/report.json');checked=json.loads(selected.read_text());assert checked['passed'];verifyInputs(model,selected,checked)
oldModel=json.loads(sole(REPO/'implementation/warlock-source-presenter-model-v5','qa/check-*/report.json').read_text());assert checked['selectedNames'][:39]==oldModel['selectedNames'] and checked['coupledTraces'][:39]==oldModel['coupledTraces']
assert len(checked['selectedNames'])==49 and sum(t['statesCompared'] for t in checked['coupledTraces'])==351 and sum(t['statesCompared'] for t in checked['coupledTraces'] if t['actualCppAndElm'])==318
campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text());assert observed['passed'] and observed['cleanupPassed'] and all(c['passed'] for c in observed['checks']) and all(x['exitCode']==0 for x in observed['ownedExitCodes'])
pre=json.loads((native/'qa/preflight.json').read_text());verifyInputs(native,campaign,dict(inputs=pre['inputs'],artifacts=observed['artifacts']))
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v11','qa/native-*/report.json').read_text());names=[c['name'] for c in prior['checks']];assert len(names)==857 and [c['name'] for c in observed['checks'] if c['name'] in set(names)]==names
failedNative=REPO/'implementation/warlock-client-provider-native-v12';failure=sole(failedNative,'qa/native-*/report.json');failed=json.loads(failure.read_text());assert not failed['passed'] and failed['cleanupPassed'] and failed['error']=="RuntimeError('Original six-second fixture observation deadline')" and all(x['exitCode']==0 for x in failed['ownedExitCodes'])
verifyInputs(failedNative,failure,dict(inputs=json.loads((failedNative/'qa/preflight.json').read_text())['inputs'],artifacts=failed['artifacts']))
failedProvider=REPO/'implementation/warlock-preview-provider-v20';compileFailure=sole(failedProvider,'qa/build-*/report.json');compiled=json.loads(compileFailure.read_text());assert not compiled['passed'] and 'misleading-indentation' in compiled['error'];verifyInputs(failedProvider,compileFailure,compiled)
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);destination.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(failedNative,{'status':'failed-stopped-source-closed-picker-observation-held','nativePassed':False,'cleanupPassed':True,'allOwnedExitsNormal':True,'actualNativeMinimizationAndStoppedScopePassed':True}))
held.append(hold(failedProvider,{'status':'failed-new-test-compile-held','fullGUIBuildPassed':False,'unchangedWerror':True}))
held.append(hold(REPO/'implementation/warlock-client-provider-native-v13',{'status':'untested-intermediate-Historical-reopened-picker-preparation-held','nativePassed':False,'nativeLaunched':False}))
held.append(hold(model,{'status':'forty-nine-selected-source-and-retained-Historical-scenarios-qualified','selectedScenarios':49,'compiledStatesCompared':351,'actualCppAndElmStates':318,'retainedOriginalScenarios':39,'retainedOriginalStates':258}))
held.append(hold(native,{'status':'actual-first-class-minimized-source-and-retained-Historical-GUI-qualified','nativeControls':len(observed['checks']),'retainedOriginalControls':857,'normalOwnedExits':len(observed['ownedExitCodes']),'cleanupPassed':True,'sameOriginalPacketAndExpiry':True,'noCaptureWhileStopped':True,'actualNativeRestore':True,'hardwarePresentationQualified':False,'productionCaptureWired':False,'previewEligible':False}))
held.append(hold(provider,{'status':'current-own-retained-packet-Historical-presentation','fullGUIBuildPassed':True,'actualRetainedPresentationChecks':32,'actualResumeSchedulerBrokerGIOChecks':69,'actualElmDenialChecks':445,'nativeDecoderBrokerGIODenialChecks':104,'actualGIOObservationChecks':153,'qualifiedNative':held[-1],'selectedConformance':held[-2],'productionCaptureWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,campaign,selected,failure,compileFailure]},'boundedNativeStoppedHistoricalQualified':True,'nativeControls':len(observed['checks']),'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Production multi-family and decor/modal/minimized fidelity original preview13, physical async fencing and measured budgets; all remaining coherent GUI release gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':len(observed['checks']),'normalExits':len(observed['ownedExitCodes']),'components':held,'report':str(out)}))
