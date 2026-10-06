import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=REPO/'docs/warlock-preview/v23/report.json';old=json.loads(prior.read_text());assert old['passed']
for component in old['components']:
 p=REPO/component['path'];assert sha(p)==component['sha256'];held=json.loads(p.read_text())
 for rel,row in held['files'].items():
  q=p.parent/rel;assert q.is_file() and not q.is_symlink() and sha(q)==row['sha256'] and q.stat().st_size==row['size']
provider=REPO/'implementation/warlock-preview-provider-v30';builds=list(provider.glob('qa/build-*/report.json'));assert len(builds)==1;build=builds[0];built=json.loads(build.read_text());assert built['passed'] and len(built['commands'])==57 and all(row['exitCode']==0 for row in built['commands'])
for rel,h in built['inputs'].items():assert sha(provider/rel)==h
campaign=REPO/'implementation/warlock-client-provider-native-v27/qa/native-1791253777156909074/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==973 and all(row['passed'] for row in native['checks']) and len(native['ownedExitCodes'])==114 and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v24/qa/native-1791253306487720300/report.json';original=json.loads(base.read_text());names=[row['name'] for row in original['checks']];assert len(names)==951 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['sharedHistoricalNewLeaseOwnNativeScope','sharedHistoricalActualElmLabelAndNewLease','sharedHistoricalVisibleOriginalPixelsExcludePeer','sharedHistoricalNoRecaptureRenewalOrPrematureRelease','sharedHistoricalExactOriginalOpaqueURIsAndSizes','sharedHistoricalRetainsOriginalPhysicalSharedMappings','sharedHistoricalOriginalPacketExpiryPreserved','sharedHistoricalExactElmReleaseFinalACK5And6','sharedHistoricalPhysicalDrainBeforeFinalACK','sharedHistoricalFullHostNormalExit','allOriginal951OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
for version in [25,26,27]:
 root=REPO/('implementation/warlock-client-provider-native-v'+str(version));pre=json.loads((root/'qa/preflight.json').read_text());assert pre['passed']
 for path,h in pre['inputs'].items():assert sha(pathlib.Path(path))==h,path
 reports=list(root.glob('qa/native-*/report.json'));assert len(reports)==1;observed=json.loads(reports[0].read_text());assert observed['passed']==(version==27)
 for rel,h in observed['artifacts'].items():assert sha(reports[0].parent/rel)==h,rel
components=[]
for name,status in [('warlock-client-provider-native-v25','retained-pre-pointer-scope-assumption-failure'),('warlock-client-provider-native-v26','retained-duplicated-original-check-name-inventory-failure'),('warlock-client-provider-native-v27','actual-shared-Historical-GTK-Elm-new-lease-qualified'),('warlock-preview-provider-v30','compiled-retained-presentation-QA-specimen-and-Historical-GUI-qualified')]:
 root=REPO/'implementation'/name;target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(p.relative_to(root))]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'files':files}
 if name.endswith('native-v27'):metadata.update(nativeControls=973,retainedOriginalControls=951,normalOwnedExits=114,cleanupPassed=True,actualSharedHistoricalNewLeaseGUIQualified=True,physicalRetirementBeforeExactACK5And6=True,previewEligible=False,hardwarePresentationQualified=False,productionFamilyQualified=False)
 if name.endswith('provider-v30'):metadata.update(commands=57,qaArtifactOrdinalOnly=True,originalLifecycleUnchanged=True,actualSharedHistoricalNewLeaseGUIQualified=True,previewEligible=False,hardwarePresentationQualified=False,productionFamilyQualified=False)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'priorPacket':{'path':str(prior.relative_to(REPO)),'sha256':sha(prior)},'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,build]},'nativeControls':973,'normalOwnedExits':114,'sharedHistoricalNewLeaseGUIQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Original production family/decor/modal/popup preview13; hardware/async/fences/S02/output and all coherent GUI release gates'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':973,'normalOwnedExits':114,'report':str(report)}))
