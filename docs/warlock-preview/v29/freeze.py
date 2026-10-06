import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
campaign=REPO/'implementation/warlock-client-provider-native-v33/qa/native-1791257049560687982/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==1214 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==125 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v31/qa/native-1791256379960337558/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==1160 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
failed=REPO/'implementation/warlock-client-provider-native-v32/qa/native-1791256828360243563/report.json';failure=json.loads(failed.read_text());assert not failure['passed'] and failure['error']=="AssertionError('familyModalActualParentRelationAndOwnSerial')" and failure['cleanupPassed'] and all(row['exitCode']==0 for row in failure['ownedExitCodes'])
assert (failed.parents[2]/'qa/native.py').read_bytes()==(campaign.parents[2]/'qa/native.py').read_bytes()
for report in [campaign,failed]:
 data=json.loads(report.read_text());pre=json.loads((report.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
 for rel,h in data['artifacts'].items():assert sha(report.parent/rel)==h,rel
builds=[]
for version in [1,2]:
 root=REPO/('implementation/warlock-family-modal-fixture-v'+str(version));reports=list(root.glob('qa/client-build-*/report.json'));assert len(reports)==1;build=reports[0];built=json.loads(build.read_text());assert built['passed'] and sha(built['client'])==built['clientSHA256'];builds.append(build)
 for key in ['inputs','tools','dependencies','linkedLibraries']:
  for p,h in built[key].items():assert sha(p)==h,p
 for rel,h in built['artifacts'].items():assert sha(build.parent/rel)==h,rel
modal=native['modalFixtureQualification'];assert modal['magenta']['magenta']==modal['replacement']['magenta']==96*64 and modal['yellow']['yellow']==96*64 and int(modal['replacementSubject'])>int(modal['firstSubject']) and not modal['productionFamilyCapture']
components=[]
for root,status in [(builds[0].parents[2],'retained-identical-pixel-configure-redraw-fixture'),(builds[1].parents[2],'actual-related-modal-protocol-pixels-and-native-family-effects-qualified'),(failed.parents[2],'retained-no-artificial-parent-commit-failure-normal-teardown'),(campaign.parents[2],'actual-modal-fixture-native1214-125-normal-exits-qualified')]:
 target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'productionFamilyCaptureQualified':False,'files':files}
 if root==campaign.parents[2] or root==builds[1].parents[2]:metadata.update(actualRelatedModalFixtureQualified=True,nativeControls=1214,retainedOriginalControls=1160,normalOwnedExits=125,cleanupPassed=True,rawKeyDeliveryQualified=False,hardwarePresentationQualified=False)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,failed,*builds]},'nativeControls':1214,'normalOwnedExits':125,'actualRelatedModalFixtureQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Implement/qualify complete native root/popup/modal membership and geometry/revision/crop, then family renderer/FD and typed full shared GUI under original production preview13 and coherent release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':1214,'normalOwnedExits':125,'report':str(report)}))
