import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
campaign=REPO/'implementation/warlock-client-provider-native-v30/qa/native-1791256065532190194/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==1079 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==117 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v29/qa/native-1791255181974132197/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==1011 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
root=campaign.parents[2];pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in native['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
observer=REPO/'implementation/warlock-popup-source-revisions-v1';descriptor=json.loads((observer/'native-build-report.json').read_text());build=pathlib.Path(descriptor['pluginBuildReport']);compiled=json.loads(build.read_text());assert compiled['passed'] and sha(build)==descriptor['pluginBuildReportSHA256'] and not compiled['missingSymbols'] and sha(descriptor['plugin']['path'])==descriptor['plugin']['sha256']
for rel,h in compiled['inputs'].items():assert sha(observer/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in compiled[key].items():assert sha(p)==h,p
for rel,h in compiled['artifacts'].items():assert sha(build.parent/rel)==h,rel
model=REPO/'implementation/warlock-popup-revision-model-v2';pointer=json.loads((model/'qa/model-report.json').read_text());modelReport=pathlib.Path(pointer['path']);assert sha(modelReport)==pointer['sha256'];proof=json.loads(modelReport.read_text());assert proof['passed'] and len(proof['traces'])==5 and proof['states']==28 and len(proof['implementationReplay'])==5
assert len(native['popupRevisionReplay'])==4 and sum(x['statesCompared'] for x in native['popupRevisionReplay'])==21
failed=REPO/'implementation/warlock-popup-revision-model-v1/qa/model-1791255954017387348/report.json';failure=json.loads(failed.read_text());assert not failure['passed'] and 'Built-in name' in failure['error']
for report in [modelReport,failed]:
 data=json.loads(report.read_text())
 for p,h in data['inputs'].items():assert sha(p)==h,p
 for rel,h in data['artifacts'].items():assert sha(report.parent/rel)==h,rel
assert native['popupSnapshotPixels']['cyanScope']['context']==native['popupSnapshotPixels']['yellowScope']['context']
components=[]
for root,status in [(observer,'compiled-and-native-popup-observer-qualified'),(failed.parents[2],'retained-reserved-Quint-name-failure'),(model,'five-selected-projections-compiled-TreeRevision-replayed'),(campaign.parents[2],'four-selected-native-popup-traces-and-1011-original-controls-qualified')]:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():
   assert root==observer and rel==str(build.parent.relative_to(observer))+'/include/hyprland' and p.resolve()==build.parent/'owning-headers',p
   links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'productionFamilyQualified':False,'captureBindingQualified':False,'files':files,'localBuildLinks':links}
 if root==observer or root==campaign.parents[2]:metadata.update(actualNativePopupObserverQualified=True,nativeControls=1079,retainedOriginalControls=1011,normalOwnedExits=117,cleanupPassed=True)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,build,modelReport,failed]},'nativeControls':1079,'normalOwnedExits':117,'actualNativePopupObserverQualified':True,'modelScenarios':5,'modelStates':28,'nativeProjectionTraces':4,'nativeProjectionStates':21,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Bind distinct native popup context at actual capture start/end with a distinct typed FD plane, then full family/modal/decor and original production preview13/coherent GUI release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':1079,'normalOwnedExits':117,'report':str(report)}))
