"""Freeze actual imported native ownership, selected conformance and failed attempts."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def sole(root,pattern):
 paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def inputs(root,p,r):
 for path,h in r['inputs'].items():assert sha(root/path if not pathlib.Path(path).is_absolute() else path)==h,path
 for rel,h in r.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
provider=REPO/'implementation/warlock-preview-provider-v23';build=sole(provider,'qa/build-*/report.json');built=json.loads(build.read_text());assert built['passed'] and len(built['commands'])==52 and all(row['exitCode']==0 for row in built['commands']);inputs(provider,build,built)
assert sha(build.parent/'elm-host')==built['binarySHA256']
for name,count in [('client-observation-tests',153),('typed-source-presenter-replay',46),('client-denial-tests',104),('typed-source-denial-replay',445),('client-resume-tests',69),('client-retained-presentation-tests',32),('client-import-tests',100)]:assert json.loads((build.parent/(name+'.stdout')).read_text())['checks']==count
model=REPO/'implementation/warlock-source-presenter-model-v8';selected=sole(model,'qa/check-*/report.json');checked=json.loads(selected.read_text());assert checked['passed'];inputs(model,selected,checked)
oldModel=json.loads(sole(REPO/'implementation/warlock-source-presenter-model-v6','qa/check-*/report.json').read_text());assert checked['selectedNames'][:49]==oldModel['selectedNames'] and checked['coupledTraces'][:49]==oldModel['coupledTraces']
assert len(checked['selectedNames'])==61 and sum(row['statesCompared'] for row in checked['coupledTraces'])==464 and sum(row['statesCompared'] for row in checked['coupledTraces'] if row['actualCppAndElm'])==318 and sum(row['statesCompared'] for row in checked['coupledTraces'] if row.get('actualCppImportedOwnership'))==113
witness=REPO/'implementation/warlock-imported-client-witness-v1';witnessBuild=sole(witness,'qa/build-*/report.json');compiled=json.loads(witnessBuild.read_text());assert compiled['passed'];inputs(witness,witnessBuild,compiled);assert sha(compiled['binary'])==compiled['binarySHA256']
native=REPO/'implementation/warlock-client-provider-native-v17';campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text());assert observed['passed'] and observed['cleanupPassed'] and len(observed['checks'])==904 and len(observed['ownedExitCodes'])==100 and all(row['passed'] for row in observed['checks']) and all(row['exitCode']==0 for row in observed['ownedExitCodes']);inputs(native,campaign,dict(inputs=json.loads((native/'qa/preflight.json').read_text())['inputs'],artifacts=observed['artifacts']))
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v14','qa/native-*/report.json').read_text());names=[row['name'] for row in prior['checks']];assert len(names)==883 and [row['name'] for row in observed['checks'] if row['name'] in set(names)]==names
failureProvider=REPO/'implementation/warlock-preview-provider-v22';failureBuild=sole(failureProvider,'qa/build-*/report.json');failed=json.loads(failureBuild.read_text());assert not failed['passed'] and failed['error']==repr(RuntimeError('Original native-scoped reservation'+chr(10)));inputs(failureProvider,failureBuild,failed)
failureModel=REPO/'implementation/warlock-source-presenter-model-v7';modelFailure=sole(failureModel,'qa/check-*/report.json');failedModel=json.loads(modelFailure.read_text());assert not failedModel['passed'] and 'QNT405' in failedModel['error'];inputs(failureModel,modelFailure,failedModel)
failureNative=REPO/'implementation/warlock-client-provider-native-v16';nativeFailure=sole(failureNative,'qa/native-*/report.json');failedNative=json.loads(nativeFailure.read_text());assert not failedNative['passed'] and failedNative['error']=="KeyError('outcome')" and failedNative['cleanupPassed'];assert [(row['name'],row['exitCode']) for row in failedNative['ownedExitCodes'] if row['exitCode']!=0]==[('imported-native-witness',-15)];inputs(failureNative,nativeFailure,dict(inputs=json.loads((failureNative/'qa/preflight.json').read_text())['inputs'],artifacts=failedNative['artifacts']))
preparation=REPO/'implementation/warlock-client-provider-native-v15';prepared=sole(preparation,'qa/prepare-*/report.json');prep=json.loads(prepared.read_text());assert prep['passed'] and not prep['nativeLaunched'];inputs(preparation,prepared,prep)
def hold(root,metadata):
 destination=root/'component-manifest.json';assert not destination.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);destination.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(destination.relative_to(REPO)),'sha256':sha(destination),'files':len(rows)}
held=[]
held.append(hold(failureProvider,{'status':'failed-synthetic-native-pacing-timestamp-held','fullGUIBuildPassed':False}))
held.append(hold(failureModel,{'status':'failed-Quint-projection-return-type-held','conformancePassed':False}))
held.append(hold(preparation,{'status':'untested-import-native-preparation-held','nativeLaunched':False}))
held.append(hold(failureNative,{'status':'failed-effect-status-field-harness-held','nativePassed':False,'cleanupPassed':True,'forcedWitnessExit':-15,'firstTwoActualImportedSourcesQualifiedBeforeFailure':True}))
held.append(hold(model,{'status':'sixty-one-selected-ownership-and-source-conformance-qualified','selectedScenarios':61,'compiledStatesCompared':464,'actualCppAndElmStates':318,'actualCppImportedOwnershipStates':113,'retainedOriginalScenarios':49,'retainedOriginalStates':351}))
held.append(hold(witness,{'status':'actual-shared-importer-native-witness-compiled','buildPassed':True,'productionGUIWired':False}))
held.append(hold(native,{'status':'two-actual-imported-subjects-one-grant-shared-Broker-native-qualified','nativeControls':904,'retainedOriginalControls':883,'normalOwnedExits':100,'cleanupPassed':True,'earlyNativeRetirementAndIndependentLocalOwnership':True,'sourceStopHistoricalAndLockGuardBeforePolicy':True,'exactOriginalTerminalACKsAfterPhysicalRetire':True,'productionGUIWired':False,'hardwarePresentationQualified':False,'previewEligible':False}))
held.append(hold(provider,{'status':'shared-two-subject-sealed-import-native-ownership','fullGUIBuildPassed':True,'actualImportControls':100,'qualifiedNative':held[-1],'selectedConformance':held[-3],'productionGUIWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,selected,witnessBuild,campaign,failureBuild,modelFailure,nativeFailure,prepared]},'boundedNativeImportedStorageQualified':True,'nativeControls':904,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Wire actual shared importer into full GUI demand/projection/retained receipt routes, original full-family preview13, async/hardware/S02 and remaining coherent GUI gates'},indent=2)+'\n');print(json.dumps({'passed':True,'components':held,'report':str(out),'nativeControls':904,'normalExits':100}))
