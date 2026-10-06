import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
prior=REPO/'docs/warlock-preview/v27/report.json';previous=json.loads(prior.read_text());assert previous['passed']
for component in previous['components']:
 p=REPO/component['path'];assert sha(p)==component['sha256'];held=json.loads(p.read_text())
 for rel,row in held['files'].items():assert sha(p.parent/rel)==row['sha256'],rel
 for rel,target in held.get('localBuildLinks',{}).items():assert str((p.parent/rel).readlink())==target,rel
campaign=REPO/'implementation/warlock-client-provider-native-v31/qa/native-1791256379960337558/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==1160 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==122 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v30/qa/native-1791256065532190194/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==1079 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
root=campaign.parents[2];pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in native['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
capture=REPO/'implementation/warlock-popup-capture-v1';descriptor=json.loads((capture/'native-build-report.json').read_text());build=pathlib.Path(descriptor['pluginBuildReport']);compiled=json.loads(build.read_text());assert compiled['passed'] and sha(build)==descriptor['pluginBuildReportSHA256'] and not compiled['missingSymbols'] and sha(descriptor['plugin']['path'])==descriptor['plugin']['sha256']
for rel,h in compiled['inputs'].items():assert sha(capture/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in compiled[key].items():assert sha(p)==h,p
for rel,h in compiled['artifacts'].items():assert sha(build.parent/rel)==h,rel
fd=REPO/'implementation/warlock-popup-fd-qualification-v1';pointer=json.loads((fd/'qa/test-report.json').read_text());fdReport=pathlib.Path(pointer['path']);assert sha(fdReport)==pointer['sha256'];proof=json.loads(fdReport.read_text());assert proof['passed'] and all(proof['evidence'][k] for k in ['physicalFDClosed','physicalMappingClosed','chargeReleasedAfterClose'])
for p,h in proof['inputs'].items():assert sha(p)==h,p
for rel,h in proof['artifacts'].items():assert sha(fdReport.parent/rel)==h,rel
samples={row['name']:row for row in native['popupCaptureSamples']};assert len(samples)==5 and all(row['header'][22]==19 and not row['previewEligible'] and not row['hardwarePresentation'] for row in samples.values())
assert samples['popup-bound-cyan']['pixels']['cyan']==64*48 and samples['popup-bound-yellow']['pixels']['yellow']==64*48 and samples['popup-bound-yellow']['pixels']['cyan']==0 and samples['popup-bound-moved']['pixels']['yellow']==64*48 and samples['popup-bound-absent']['pixels']['yellow']==samples['popup-bound-absent']['pixels']['cyan']==0 and samples['popup-bound-replacement']['pixels']['cyan']==64*48 and all(row['pixels']['green']==0 for row in samples.values())
for tag in ['popupCommit','popupPosition','popupDestroy','popupReplacement']:
 assert next(row for row in native['checks'] if row['name']==tag+'OldPopupContextRefused')['passed']
components=[]
for root,status in [(capture,'compiled-native-popup-context-capture-and-new-FD-plane-qualified'),(fd,'actual-sealed-FD-typed-plane-mapping-and-physical-charge-order-qualified'),(campaign.parents[2],'actual-native-popup-capture-1160-controls-122-normal-exits-qualified')]:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():
   assert root==capture and rel==str(build.parent.relative_to(capture))+'/include/hyprland' and p.resolve()==build.parent/'owning-headers',p
   links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'productionFamilyQualified':False,'files':files,'localBuildLinks':links}
 if root==capture or root==campaign.parents[2]:metadata.update(actualNativePopupCaptureQualified=True,nativeControls=1160,retainedOriginalControls=1079,normalOwnedExits=122,cleanupPassed=True)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'priorPacket':{'path':str(prior.relative_to(REPO)),'sha256':sha(prior)},'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,build,fdReport]},'nativeControls':1160,'normalOwnedExits':122,'actualNativePopupCaptureQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete native family/modal/decor membership and crop/full fidelity, then typed full shared GUI adoption and production preview13/hardware/coherent release qualification.'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':1160,'normalOwnedExits':122,'report':str(report)}))
