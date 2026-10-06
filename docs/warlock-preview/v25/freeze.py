import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
campaign=REPO/'implementation/warlock-client-provider-native-v28/qa/native-1791254165527530711/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==990 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==115 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v27/qa/native-1791253777156909074/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==973 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
root=REPO/'implementation/warlock-client-provider-native-v28';pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for path,h in pre['inputs'].items():assert sha(pathlib.Path(path))==h,path
for rel,h in native['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
fixture=REPO/'implementation/warlock-family-popup-fixture-v1';builds=list(fixture.glob('qa/client-build-*/report.json'));assert len(builds)==1;build=builds[0];built=json.loads(build.read_text());assert built['passed'] and sha(pathlib.Path(built['client']))==built['clientSHA256']
for key in ['inputs','tools','dependencies','linkedLibraries']:
 for path,h in built[key].items():assert sha(pathlib.Path(path))==h,path
for rel,h in built['artifacts'].items():assert sha(build.parent/rel)==h,rel
components=[]
for root,status in [(fixture,'actual-bounded-xdg-popup-fixture-compiled-and-native-lifecycle-qualified'),(root,'actual-xdg-popup-lifecycle-and-client-exclusion-native-qualified')]:
 target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'actualNativePopupLifecycleQualified':True,'productionFamilyQualified':False,'hardwarePresentationQualified':False,'previewEligible':False,'files':files}
 if root.name.endswith('native-v28'):metadata.update(nativeControls=990,retainedOriginalControls=973,normalOwnedExits=115,cleanupPassed=True)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,build]},'nativeControls':990,'normalOwnedExits':115,'actualNativePopupLifecycleQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual owning renderer popup-inclusive pixels and native complete family revision/geometry authority, then all original production preview13 and full GUI release gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':990,'normalOwnedExits':115,'report':str(report)}))
