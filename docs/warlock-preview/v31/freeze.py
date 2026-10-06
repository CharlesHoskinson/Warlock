import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
reports=sorted((REPO/'implementation/warlock-client-provider-native-v37/qa').glob('native-*/report.json'));assert len(reports)==1;campaign=reports[0];native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v34/qa/native-1791257839724867928/report.json';old=json.loads(base.read_text());names=[row['name'] for row in old['checks']];assert len(names)==1351 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
assert len(native['familyCaptureSamples'])==7 and all(row['header'][22]==35 and not row['previewEligible'] for row in native['familyCaptureSamples'])
required=['combinedFamilyRootPopupAndDialogInOneImage','combinedFamilyActualDialogInteriorAndRoot','combinedFamilyUnlinkedDialogExcludedPixels','combinedFamilyReparentedDialogReturnsOwnPixels','combinedFamilyDestroyedDialogAbsentPixels','allOriginal1351OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
failed=REPO/'implementation/warlock-client-provider-native-v35/qa/native-1791258719937490629/report.json';failure=json.loads(failed.read_text());assert not failure['passed'] and failure['cleanupPassed'] and len(failure['ownedExitCodes'])==123 and all(row['exitCode']==0 for row in failure['ownedExitCodes'])
failed36=REPO/'implementation/warlock-client-provider-native-v36/qa/native-1791258972830203329/report.json';f36=json.loads(failed36.read_text());assert not f36['passed'] and f36['cleanupPassed'] and len(f36['ownedExitCodes'])==133 and all(row['exitCode']==0 for row in f36['ownedExitCodes'])
for report in [failed,failed36,campaign]:
 pre=json.loads((report.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
 for rel,h in json.loads(report.read_text())['artifacts'].items():assert sha(report.parent/rel)==h,rel
components=[];evidence=[base,failed,failed36,campaign]
core=REPO/'implementation/warlock-core-family-render-v4';held=core/'component-manifest.json';data=json.loads(held.read_text());assert data['sourceHeld'] and data['evidenceIntegrityPassed']
for rel,row in data['files'].items():assert sha(core/rel)==row['sha256'],rel
components.append({'path':str(held.relative_to(REPO)),'sha256':sha(held),'files':len(data['files'])})
for version in [1,2]:
 source=REPO/('implementation/warlock-family-capture-v'+str(version));descriptor=json.loads((source/'native-build-report.json').read_text());report=pathlib.Path(descriptor['pluginBuildReport']);compiled=json.loads(report.read_text());assert compiled['passed'] and sha(report)==descriptor['pluginBuildReportSHA256'] and not compiled['missingSymbols'] and sha(descriptor['plugin']['path'])==descriptor['plugin']['sha256'];evidence.append(report)
 for rel,h in compiled['inputs'].items():assert sha(source/rel)==h,rel
 for key in ['dependencies','linkedLibraries','tools']:
  for p,h in compiled[key].items():assert sha(p)==h,p
 for rel,h in compiled['artifacts'].items():assert sha(report.parent/rel)==h,rel
fd=REPO/'implementation/warlock-family-fd-qualification-v1';pointer=json.loads((fd/'qa/test-report.json').read_text());report=pathlib.Path(pointer['path']);assert sha(report)==pointer['sha256'];proof=json.loads(report.read_text());assert proof['passed'] and proof['evidence']['checks']==150 and all(proof['evidence'][key] for key in ['physicalFDClosed','physicalMappingClosed','chargeReleasedAfterClose']);evidence.append(report)
for p,h in proof['inputs'].items():assert sha(p)==h,p
for rel,h in proof['artifacts'].items():assert sha(report.parent/rel)==h,rel
roots=[REPO/('implementation/warlock-core-family-render-v'+str(i)) for i in [1,2,3]]+[REPO/('implementation/warlock-family-capture-v'+str(i)) for i in [1,2]]+[fd,failed.parents[2],failed36.parents[2],campaign.parents[2]]
for root in roots:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():
   assert rel.endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p
   links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'files':files,'localBuildLinks':links,'status':'retained-actual-evidence'}
 if root in [REPO/'implementation/warlock-family-capture-v2',campaign.parents[2]]:metadata.update(actualCombinedNativeFamilyFramebufferQualified=True,nativeControls=len(native['checks']),retainedOriginalControls=1351,normalOwnedExits=len(native['ownedExitCodes']),cleanupPassed=True)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in evidence},'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'actualCombinedNativeFamilyFramebufferQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete native source/style/animation/crop/fidelity, typed shared Elm family adoption and original production preview13, coherent release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
