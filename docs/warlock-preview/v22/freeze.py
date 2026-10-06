"""Freeze qualified shared GUI resumption and exact selected lifecycle refinement."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def sole(root,pattern):
    paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verify(root,p,r):
    for name,h in r['inputs'].items():assert sha(root/name if not pathlib.Path(name).is_absolute() else name)==h,name
    for name,h in r.get('artifacts',{}).items():assert sha(p.parent/name)==h,name
def provider(version):
    root=REPO/f'implementation/warlock-preview-provider-v{version}';p=sole(root,'qa/build-*/report.json');r=json.loads(p.read_text())
    assert r['passed'] and len(r['commands'])==57 and all(x['exitCode']==0 for x in r['commands']);verify(root,p,r)
    assert sha(p.parent/'elm-host')==r['binarySHA256']
    assert json.loads((p.parent/'imported-lifecycle-tests.stdout').read_text())['checks']==67
    return root,p,r
prepared,preparedBuild,preparedBuilt=provider(28)
fresh,build,built=provider(29)
for name,h in preparedBuilt['compiledAssetPackage']['files'].items():assert built['compiledAssetPackage']['files'][name]==h,name
model=REPO/'implementation/warlock-source-presenter-model-v9';replay=sole(model,'qa/check-*/report.json');checked=json.loads(replay.read_text())
assert checked['passed'] and checked['retainedOriginal61'] and len(checked['selectedNames'])==73 and len(checked['coupledTraces'])==73
assert sum(x['statesCompared'] for x in checked['coupledTraces'])==659
verify(model,replay,checked)
priorModel=json.loads(sole(REPO/'implementation/warlock-source-presenter-model-v8','qa/check-*/report.json').read_text())
assert checked['selectedNames'][:61]==priorModel['selectedNames']
assert [(x['trace'],x['statesCompared']) for x in checked['coupledTraces'][:61]]==[(x['trace'],x['statesCompared']) for x in priorModel['coupledTraces']]
untested=REPO/'implementation/warlock-client-provider-native-v22';preparation=sole(untested,'qa/prepare-*/report.json');pre=json.loads(preparation.read_text());assert pre['passed'] and not pre['nativeLaunched'] and not list(untested.glob('qa/native-*'));verify(untested,preparation,pre)
native=REPO/'implementation/warlock-client-provider-native-v23';campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text())
assert observed['passed'] and observed['cleanupPassed'] and len(observed['checks'])==933 and len(observed['ownedExitCodes'])==106
assert all(x['passed'] for x in observed['checks']) and all(x['exitCode']==0 for x in observed['ownedExitCodes'])
verify(native,campaign,dict(inputs=json.loads((native/'qa/preflight.json').read_text())['inputs'],artifacts=observed['artifacts']))
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v21','qa/native-*/report.json').read_text());names=[x['name'] for x in prior['checks']];assert len(names)==918
assert [x['name'] for x in observed['checks'] if x['name'] in set(names)]==names
for name in ['guiResumedExactlyFourDistinctOwnedPackets','guiResumedSameAuthorityAndNewOriginalNativeDeadlines','guiResumedActualElmAcquiresBothNewJobs','guiResumedOwnOriginalACKBeforeNewAcquire','guiResumedBothNewOwnedURIAndDimensions','guiResumedVisibleNewYellowBothSourcesExcludePeer','guiResumedBothExactFinalReleaseACK11And12','guiResumedActualNewPhysicalBeforeFinalACK','guiImportedFullHostNormalExit','allOriginal918OrderedAssertionsRetained']:
    assert next(x for x in observed['checks'] if x['name']==name)['passed'],name
def hold(root,metadata):
    target=root/'component-manifest.json';assert not target.exists();files={}
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if any(x in ['__pycache__','elm-stuff','mutable-elm-home'] for x in rel.parts):continue
        assert not p.is_symlink(),p
        if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
    metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=files)
    target.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)}
held=[hold(prepared,{'status':'compiled-shared-per-entry-lifecycle-before-QA-snapshot-nonreuse-fix','commands':57,'newSharedLifecycleControls':67,'actualNewNativeQualification':False}),hold(untested,{'status':'preflight-only-retained-before-nonvacuous-source-identity-guard','nativeLaunched':False})]
held.append(hold(model,{'status':'selected-shared-two-entry-lifecycle-refinement-qualified','selectedScenarios':73,'comparedStates':659,'retainedOriginalScenarios':61,'retainedOriginalStates':464,'newSharedScenarios':12,'newSharedStates':195,'newTraceScope':'Actual helper/Broker/GIO/ReceiptDelivery with synthetic native scope and heap PNG; existing49 Elm and12 sealedFD traces retained separately'}))
held.append(hold(native,{'status':'actual-shared-two-source-GTK-Elm-second-cycle-qualified','nativeControls':933,'retainedOriginalControls':918,'normalOwnedExits':106,'cleanupPassed':True,'actualTwoSourceGUIResumptionQualified':True,'sameGrantClockAndExactNewIssuedDeadlines':True,'newOwnURIAndVisiblePixelsQualified':True,'physicalRetirementBeforeExactACK11And12':True,'sharedSiblingHeldResumptionNativeQualified':False,'sharedRetainedHistoricalNativeQualified':False,'previewEligible':False}))
held.append(hold(fresh,{'status':'actual-shared-GUI-per-entry-lifecycle-and-two-source-recapture-qualified','commands':57,'newSharedLifecycleControls':67,'qualifiedNative':held[-1],'qualifiedModel':held[-2],'previewEligible':False,'hardwarePresentationQualified':False,'productionFamilyQualified':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists()
out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [preparedBuild,build,replay,preparation,campaign]},'boundedSharedGUIResumptionQualified':True,'nativeControls':933,'normalOwnedExits':106,'selectedScenarios':73,'comparedStates':659,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual native per-entry resumption while sibling held/charged, shared retained Historical new-lease presentation, then original production family/decor/modal preview13, async/hardware/S02/output and all full release gates'},indent=2)+'\n')
print(json.dumps({'passed':True,'nativeControls':933,'normalOwnedExits':106,'selectedScenarios':73,'comparedStates':659,'components':held,'report':str(out)}))
