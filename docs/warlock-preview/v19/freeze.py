"""Hold qualified actual C import bridge source and native route evidence."""
import pathlib,json,hashlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def sole(root,pattern):
 paths=list(root.glob(pattern));assert len(paths)==1,(root,pattern);return paths[0]
def verify(root,p,r):
 for path,h in r['inputs'].items():assert sha(root/path if not pathlib.Path(path).is_absolute() else path)==h,path
 for rel,h in r.get('artifacts',{}).items():assert sha(p.parent/rel)==h,rel
provider=REPO/'implementation/warlock-preview-provider-v24';build=sole(provider,'qa/build-*/report.json');built=json.loads(build.read_text());assert built['passed'] and len(built['commands'])==55 and all(row['exitCode']==0 for row in built['commands']);verify(provider,build,built);assert sha(build.parent/'elm-host')==built['binarySHA256'];assert json.loads((build.parent/'imported-c-boundary-tests.stdout').read_text())['checks']==6;assert json.loads((build.parent/'client-import-tests.stdout').read_text())['checks']==100
witness=REPO/'implementation/warlock-imported-client-witness-v2';witnessBuild=sole(witness,'qa/build-*/report.json');compiled=json.loads(witnessBuild.read_text());assert compiled['passed'];verify(witness,witnessBuild,compiled);assert sha(compiled['binary'])==compiled['binarySHA256']
native=REPO/'implementation/warlock-client-provider-native-v18';campaign=sole(native,'qa/native-*/report.json');observed=json.loads(campaign.read_text());assert observed['passed'] and observed['cleanupPassed'] and len(observed['checks'])==905 and len(observed['ownedExitCodes'])==100 and all(row['passed'] for row in observed['checks']) and all(row['exitCode']==0 for row in observed['ownedExitCodes']);verify(native,campaign,dict(inputs=json.loads((native/'qa/preflight.json').read_text())['inputs'],artifacts=observed['artifacts']))
prior=json.loads(sole(REPO/'implementation/warlock-client-provider-native-v17','qa/native-*/report.json').read_text());names=[row['name'] for row in prior['checks']];assert len(names)==904 and [row['name'] for row in observed['checks'] if row['name'] in set(names)]==names
assert compiled['inputs'][str(provider/'native/imported-clients.cpp')]==built['inputs']['native/imported-clients.cpp']
def hold(root,metadata):
 target=root/'component-manifest.json';assert not target.exists();rows={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():rows[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata.update(schema=1,sourceHeld=True,evidenceIntegrityPassed=True,nativeAcceptance=False,fullReleaseAccepted=False,files=rows);target.write_text(json.dumps(metadata,indent=2)+'\n');return {'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(rows)}
held=[]
held.append(hold(witness,{'status':'actual-shared-C-bridge-native-witness-compiled','buildPassed':True,'actualGTKWidgetQualified':False}))
held.append(hold(native,{'status':'actual-C-bridge-shared-import-native-qualified','nativeControls':905,'retainedOriginalControls':904,'normalOwnedExits':100,'cleanupPassed':True,'refusedClosePreservesOwnerAndReceiver':True,'exactEmptyCloseBeforeNativeBootstrapFree':True,'actualGTKWidgetQualified':False,'productionGUIWired':False,'hardwarePresentationQualified':False,'previewEligible':False}))
held.append(hold(provider,{'status':'trusted-shared-import-GTK-C-ABI-compiled-native-qualified','fullGUIBuildPassed':True,'commands':55,'strictCBoundaryControls':6,'actualImportControls':100,'qualifiedNative':held[-1],'actualGTKWidgetQualified':False,'productionGUIWired':False,'previewEligible':False}))
out=pathlib.Path(__file__).parent/'report.json';assert not out.exists();out.write_text(json.dumps({'schema':1,'passed':True,'components':held,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [build,witnessBuild,campaign]},'boundedNativeCBridgeQualified':True,'nativeControls':905,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual full GUI two-entry picker admission, same compiled Elm demand/Release/ACK and retained source lifecycle; then all original release/family/hardware gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':905,'normalExits':100,'components':held,'report':str(out)}))
