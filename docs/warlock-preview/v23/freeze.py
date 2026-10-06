import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=REPO/'docs/warlock-preview/v22/report.json';old=json.loads(prior.read_text());assert old['passed']
for component in old['components']:
 p=REPO/component['path'];assert sha(p)==component['sha256'];held=json.loads(p.read_text())
 for rel,row in held['files'].items():
  q=p.parent/rel;assert q.is_file() and not q.is_symlink() and sha(q)==row['sha256'] and q.stat().st_size==row['size']
campaign=REPO/'implementation/warlock-client-provider-native-v24/qa/native-1791253306487720300/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==951 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==110 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v23/qa/native-1791252749472257123/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==933 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
preflight=REPO/'implementation/warlock-client-provider-native-v24/qa/preflight.json';pre=json.loads(preflight.read_text());assert pre['passed']
for path,h in pre['inputs'].items():assert sha(pathlib.Path(path))==h,path
for rel,h in native['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
components=[]
for name,status in [('warlock-imported-client-witness-v3','retained-actual-Werror-failure-before-native-issuance-field-correction'),('warlock-imported-client-witness-v4','actual-shared-C-bridge-asymmetric-witness-compiled-and-native-qualified'),('warlock-client-provider-native-v24','actual-native-per-entry-resumption-with-sibling-held-qualified')]:
 root=REPO/'implementation'/name;target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'files':files}
 if name.endswith('native-v24'):metadata.update(nativeControls=951,retainedOriginalControls=933,normalOwnedExits=110,cleanupPassed=True,actualNativeSiblingHeldResumptionQualified=True,actualNewGTKGateQualification=False,sharedHistoricalNewLeaseGUIQualified=False,previewEligible=False)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'priorPacket':{'path':str(prior.relative_to(REPO)),'sha256':sha(prior)},'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,preflight]},'nativeControls':951,'normalOwnedExits':110,'nativeSiblingHeldResumptionQualified':True,'actualNewGTKGateQualification':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Actual shared retained Historical new-lease GUI; production family preview13 and all original coherent GUI release gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':951,'normalOwnedExits':110,'report':str(report)}))
