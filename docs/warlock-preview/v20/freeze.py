"""Freeze actual two-source GTK/Elm ownership and retain the clipping failure."""
import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def sole(root,pattern):
    paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verify(root,p,r):
    for name,h in r['inputs'].items():
        assert sha(root/name if not pathlib.Path(name).is_absolute() else name)==h,name
    for name,h in r.get('artifacts',{}).items():assert sha(p.parent/name)==h,name
def provider(version):
    root=REPO/f'implementation/warlock-preview-provider-v{version}'
    p=sole(root,'qa/build-*/report.json');r=json.loads(p.read_text())
    assert r['passed'] and len(r['commands'])==55 and all(x['exitCode']==0 for x in r['commands'])
    verify(root,p,r);assert sha(p.parent/'elm-host')==r['binarySHA256']
    return root,p,r
old,oldBuild,oldBuilt=provider(25)
fresh,build,built=provider(26)
for name,h in oldBuilt['compiledAssetPackage']['files'].items():
    if name!='shell.css':assert built['compiledAssetPackage']['files'][name]==h,name
failed=REPO/'implementation/warlock-client-provider-native-v19'
failure=sole(failed,'qa/native-*/report.json');bad=json.loads(failure.read_text())
assert not bad['passed'] and bad['cleanupPassed']
clipping=next(x for x in bad['checks'] if x['name']=='guiImportedVisibleBothSourcePixelsExcludePeer')
assert not clipping['passed'] and clipping['pixels']['red']==33312 and clipping['pixels']['blue']==768 and clipping['pixels']['green']==0
verify(failed,failure,dict(inputs=json.loads((failed/'qa/preflight.json').read_text())['inputs'],artifacts=bad['artifacts']))
native=REPO/'implementation/warlock-client-provider-native-v20'
campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text())
assert observed['passed'] and observed['cleanupPassed'] and all(x['passed'] for x in observed['checks'])
assert all(x['exitCode']==0 for x in observed['ownedExitCodes'])
verify(native,campaign,dict(inputs=json.loads((native/'qa/preflight.json').read_text())['inputs'],artifacts=observed['artifacts']))
assert sha(native/'qa/native.py')==sha(failed/'qa/native.py')
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v18','qa/native-*/report.json').read_text())
names=[x['name'] for x in prior['checks']];assert len(names)==905
assert [x['name'] for x in observed['checks'] if x['name'] in set(names)]==names
pixels=next(x for x in observed['checks'] if x['name']=='guiImportedVisibleBothSourcePixelsExcludePeer')['pixels']
assert pixels['width']==700 and pixels['height']==420 and pixels['blue']==32*24 and pixels['red']>=2*160*120-32*24 and pixels['green']==0
for name in ['guiImportedTwoNativeSeedAndPacketOwners','guiImportedActualElmAcquireBothExactJobs','guiImportedOneBindingNativeClockOriginalDeadlines','guiImportedTwoActualLoadedOwnedURIs','guiImportedBothExactElmReleaseAndFinalACK','guiImportedActualPhysicalBeforeTerminalACK','guiImportedFullHostNormalExit','allOriginal905OrderedAssertionsRetained']:
    assert next(x for x in observed['checks'] if x['name']==name)['passed'],name
def hold(root,metadata):
    target=root/'component-manifest.json';assert not target.exists();files={}
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root)
        if any(x in ['__pycache__','elm-stuff','mutable-elm-home'] for x in rel.parts):continue
        assert not p.is_symlink(),p
        if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
    metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=files)
    target.write_text(json.dumps(metadata,indent=2)+'\n')
    return {'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)}
held=[hold(failed,{'status':'failed-visible-two-image-clipping-and-incomplete-early-host-teardown','nativeControlsReached':len(bad['checks']),'cleanupPassed':True}),hold(old,{'status':'actual-shared-two-source-GUI-compiled-native-clipping-failed','commands':55,'actualGTKWidgetQualified':False})]
held.append(hold(native,{'status':'actual-two-source-GTK-Elm-pixel-and-physical-retirement-qualified','nativeControls':len(observed['checks']),'retainedOriginalControls':905,'normalOwnedExits':len(observed['ownedExitCodes']),'cleanupPassed':True,'actualGTKWidgetQualified':True,'hardwarePresentationQualified':False,'previewEligible':False}))
held.append(hold(fresh,{'status':'actual-two-source-GTK-Elm-admission-render-release-ACK-qualified','commands':55,'actualGTKWidgetQualified':True,'qualifiedNative':held[-1],'hardwarePresentationQualified':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists()
out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [oldBuild,build,failure,campaign]},'boundedNativeGUIQualified':True,'nativeControls':len(observed['checks']),'normalOwnedExits':len(observed['ownedExitCodes']),'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Shared retained new-lease re-presentation, per-entry resumption and Unknown settlement; production family/decor/modal preview13, async hardware/S02/output and all original full release gates remain open'},indent=2)+'\n')
print(json.dumps({'passed':True,'nativeControls':len(observed['checks']),'normalOwnedExits':len(observed['ownedExitCodes']),'components':held,'report':str(out)}))
