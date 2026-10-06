"""Hold shared generated-backdrop source and actual owning native evidence."""
import hashlib,json,pathlib,re,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
    paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verify(path,owner=None):
    value=json.loads(path.read_text())
    for name,digest in value.get('artifacts',{}).items():assert sha(path.parent/name)==digest,(path,name)
    for name,digest in value.get('inputs',{}).items():
        p=pathlib.Path(name);p=p if p.is_absolute() else owner/p
        assert sha(p)==digest,(path,p)
    return value
def held(path):
    value=json.loads(path.read_text())
    if path.parent.name in {'warlock-preview-provider-v35','warlock-preview-provider-v36'}:assert value['passed'] and value['evidence']['typed-backdrop-presenter-replay']['passed']
    else:assert value['sourceHeld'] and value['evidenceIntegrityPassed']
    for name,row in value['files'].items():assert sha(path.parent/name)==row['sha256'],(path,name)
    return value
priorPath=REPO/'docs/warlock-preview/v50/report.json';prior=verify(priorPath);assert prior['passed']
for row in prior['components']:
    p=REPO/row['path'];assert sha(p)==row['sha256'];held(p)
roots=[];evidence=[priorPath]
for version in [88]:
    root=REPO/f'implementation/warlock-client-provider-native-v{version}'
    prep=only(root,'qa/prepare-*/report.json');assert verify(prep)['passed']
    pre=verify(root/'qa/preflight.json');p=only(root,'qa/native-*/report.json');native=verify(p)
    assert pre['pair']==native['pair'] and native['cleanupPassed']
    if version==86:
        assert not native['passed'] and [row['name'] for row in native['checks'] if not row['passed']]==['backdropWebActualSharedURIAndNativeCropDimensions','fullHostCleanupNormalExit']
        image=next(row for row in native['checks'] if row['name']=='backdropWebActualSharedURIAndNativeCropDimensions')['images'][0][0]
        assert [image[key] for key in ['naturalWidth','naturalHeight','width','height']]==[334,254,158,120]
    else:
        assert native['passed'] and len(native['checks'])==2341 and len(native['ownedExitCodes'])==246 and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
        accepted=native;acceptedPre=pre
    roots.append(root);evidence.extend([prep,p])
root=REPO/'implementation/warlock-preview-provider-v36';manifest=held(root/'component-manifest.json')
buildPath=only(root,'qa/build-*/report.json');build=verify(buildPath,root);assert build['passed'] and len(build['commands'])==75
assert sha(buildPath.parent/'elm-host')==build['binarySHA256'] and acceptedPre['fullHostBinary']==str(buildPath.parent/'elm-host')
assert acceptedPre['fullHostAssets']==str(buildPath.parent/'inputs/assets')
modelPath=only(root,'qa/check-*/report.json');model=verify(modelPath,root)
assert model['passed'] and model['compiledChecks']==36 and model['namedScenarios']==10 and len(model['coupledTraces'])==22 and sum(row['statesCompared'] for row in model['coupledTraces'])==564 and model['unsafeMutantsDetected']==3
roots.append(root);evidence.extend([buildPath,modelPath])
originalPath=REPO/'implementation/warlock-client-provider-native-v50/qa/native-1791265841870106110/report.json';original=verify(originalPath)
names=[row['name'] for row in original['checks']];assert len(names)==1783 and [row['name'] for row in accepted['checks'] if row['name'] in set(names)]==names
priorNative=REPO/'implementation/warlock-client-provider-native-v87/qa/native-1791284904509033826/report.json';baseline=verify(priorNative);assert baseline['passed'] and accepted['pair']==baseline['pair']
variable={'styleDimPendingNativeReadonlyScope','styleAgainDimPendingNativeReadonlyScope','styleRestoreIntermediateReadonlyScope','styleCropDimIntermediateReadonlyScope'};assert not variable.intersection(names)
identity=lambda name:re.sub(r'^opacityPrivateForeignWindowMoved-0x[0-9a-f]+$','opacityPrivateForeignWindowMoved-<native-address>',name)
priorRows=[row for row in baseline['checks'] if row['name'] not in variable];cursor=0
for row in accepted['checks']:
    if row['name'] not in variable and cursor<len(priorRows) and identity(row['name'])==identity(priorRows[cursor]['name']):cursor+=1
assert cursor==len(priorRows),cursor
assert accepted['blurBodyEvidence']['pixels']==baseline['blurBodyEvidence']['pixels'] and accepted['blurBodyExactPixels']==baseline['blurBodyExactPixels']
gui=accepted['backdropWebKitEvidence'];first=gui['initialSource'];changed=gui['changedLiveSource'];frame=gui['originalFrame']
assert first['source']['generatedBackdrop']['colorARGB']=='4294967295' and changed['source']['generatedBackdrop']['colorARGB']=='4278190080'
assert frame['job']['binding']==first['source']['binding']==changed['source']['binding'] and int(frame['job']['deadline'])==int(first['source']['scope']['now'])+2000000000
assert int(changed['source']['scope']['context']['content'])>int(first['source']['scope']['context']['content']) and int(changed['lease'])>int(first['lease'])
assert gui['pixels']['passed'] and gui['pixels']['matchingNativeColorPixels']==12516 and gui['pixels']['foreignGreenPixels']==0 and gui['pixels']['expectedNativeRGBA']==[204,127,127,255]
assert gui['acks']==[{'kind':'acknowledge','job':frame['job'],'sequence':'3'}]
assert any(row['job']==frame['job'] and row['charge']=='0' and all(row[key] for key in ['mappedFDClosed','exportReleased','producerRetired']) and not row['retirementPending'] for row in gui['ownership'])
assert not gui['allBodyPixelEqualityClaimed']
loss=accepted['backdropSourceLossEvidence'];assert accepted['nativeSharedGeneratedBackdropSourceLossQualified'] and loss['rootCommitsUnchanged'] and not loss['frontendStallQualified']
assert loss['denial']=={'protocolVersion':3,'kind':'refused','reason':'preview-family-backdrop-source-unavailable'}
assert loss['events']==[{'kind':'source-denied','job':loss['frame']['job'],'reason':'source-unavailable'}]
assert loss['acks']==[{'kind':'acknowledge','job':loss['frame']['job'],'sequence':'3'}]
assert any(row['job']==loss['frame']['job'] and row['charge']=='0' and all(row[key] for key in ['mappedFDClosed','exportReleased','producerRetired']) for row in loss['ownership'])
assert manifest['evidence']['backdrop-denial-tests']['checks']==109 and manifest['evidence']['typed-backdrop-denial-replay']['checks']==445
evidence.extend([originalPath,priorNative])
root=REPO/'openspec/changes/warlock-preview-shared-backdrop-source-loss';p=only(root,'qa/validate-*/report.json');assert verify(p)['passed'];roots.append(root);evidence.append(p)
components=[]
for root in roots:
    path=root/'component-manifest.json'
    if not path.exists():
        files={}
        for p in sorted(root.rglob('*')):
            rel=p.relative_to(root)
            if any(part in {'__pycache__','elm-stuff','mutable-elm-home'} for part in rel.parts):continue
            assert not p.is_symlink(),p
            if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
        path.write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeSharedGeneratedBackdropGUIQualified':root.name=='warlock-client-provider-native-v88','nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False},indent=2)+'\n')
    value=held(path);components.append({'path':str(path.relative_to(REPO)),'sha256':sha(path),'files':len(value['files'])})
report={'schema':1,'passed':True,'qaScope':scope,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':2341,'retainedOriginalControls':1783,'retainedPriorNativeControls':len(priorRows),'normalOwnedExits':246,'nativeSharedGeneratedBackdropGUIQualified':True,'sharedGUIBuild':str(buildPath),'backdropWebKitEvidence':gui,'nativeSharedGeneratedBackdropSourceLossQualified':True,'backdropSourceLossEvidence':accepted['backdropSourceLossEvidence'],'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'next':'Reconcile original S09 nine requirements/thirteen scenario identities on coherent GUI36/native88/owning tuple; implement next unmet original gate and remaining restore/recovery/drag/input/AT/IME/hardware/resources/release obligations.'}
assert not (OUT/'report.json').exists();(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'report':str(OUT/'report.json'),'components':len(components),'nativeControls':2341,'normalOwnedExits':246}))
