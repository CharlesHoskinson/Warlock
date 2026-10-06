import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
modelPointer=REPO/'implementation/warlock-family-style-revisions-v2/qa/model-report.json';pointer=json.loads(modelPointer.read_text());modelPath=pathlib.Path(pointer['path']);assert sha(modelPath)==pointer['sha256'];model=json.loads(modelPath.read_text());assert model['passed'] and len(model['selectedNames'])==9 and model['states']==29 and len(model['implementationReplay'])==9
for path,h in model['inputs'].items():assert sha(path)==h,path
controlPointer=REPO/'implementation/warlock-family-style-controls-v1/qa/test-report.json';cp=json.loads(controlPointer.read_text());controlsPath=pathlib.Path(cp['path']);assert sha(controlsPath)==cp['sha256'];controls=json.loads(controlsPath.read_text());assert controls['passed'] and controls['evidence']['checks']==140
for path,h in controls['inputs'].items():assert sha(path)==h,path
source=REPO/'implementation/warlock-family-style-source-v3';assert sha(source/'native/style_revision.hpp')==sha(REPO/'implementation/warlock-family-style-revisions-v2/native/style_revision.hpp')
pair=json.loads((source/'native-build-report.json').read_text());assert pair['result']=='pass' and sha(pair['plugin']['path'])==pair['plugin']['sha256'];buildPath=pathlib.Path(pair['pluginBuildReport']);assert sha(buildPath)==pair['pluginBuildReportSHA256'];build=json.loads(buildPath.read_text());assert build['passed'] and not build['missingSymbols']
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for section in ['dependencies','linkedLibraries','tools']:
 for path,h in build[section].items():assert sha(path)==h,path
oldPath=REPO/'implementation/warlock-client-provider-native-v38/qa/native-1791260728575460795/report.json';old=json.loads(oldPath.read_text());names=[row['name'] for row in old['checks']];assert old['passed'] and len(names)==1612
reports=list((REPO/'implementation/warlock-client-provider-native-v41/qa').glob('native-*/report.json'));assert len(reports)==1;nativePath=reports[0];native=json.loads(nativePath.read_text());assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
assert [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['styleUnchangedObservationRetainsEpoch','styleFocusNoRootClientCommit','styleExactNativeDimmingChannel','styleConfigureNoRootClientCommit','styleConfigurationAdvancesNativeEpoch','styleOnlyChangeNoFamilyClientRevision','styleOnlyChangeAdvancesDistinctStyleRevision','styleRestorePrivateNativeConfiguration','allOriginal1612OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
failedPath=REPO/'implementation/warlock-client-provider-native-v39/qa/native-1791261513235004983/report.json';failure=json.loads(failedPath.read_text());assert not failure['passed'] and failure['error']=="AssertionError('combined-family-rootExactNativePopupStylingAndBounds')" and failure['cleanupPassed'] and len(failure['ownedExitCodes'])==124 and all(row['exitCode']==0 for row in failure['ownedExitCodes'])
failed40Path=REPO/'implementation/warlock-client-provider-native-v40/qa/native-1791261710782416002/report.json';failure40=json.loads(failed40Path.read_text());assert not failure40['passed'] and failure40['error']=="AssertionError('styleConfigurationRestoreLaterEpoch')" and failure40['cleanupPassed'] and len(failure40['ownedExitCodes'])==146 and all(row['exitCode']==0 for row in failure40['ownedExitCodes'])
for report in [nativePath,failedPath,failed40Path]:
 pre=json.loads((report.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
for report in [modelPath,controlsPath,buildPath,nativePath,failedPath,failed40Path]:
 for rel,h in json.loads(report.read_text()).get('artifacts',{}).items():assert sha(report.parent/rel)==h,rel
roots=[REPO/f'implementation/warlock-family-style-revisions-v{i}' for i in [1,2]]+[REPO/f'implementation/warlock-family-style-source-v{i}' for i in [1,2,3]]+[REPO/'implementation/warlock-family-style-controls-v1',failedPath.parents[2],failed40Path.parents[2],nativePath.parents[2]]
components=[]
for root in roots:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():assert rel.endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'files':files,'localBuildLinks':links,'status':'retained-actual-evidence'}
 if root in [source,nativePath.parents[2]]:metadata.update(actualNativeStyleChannelsQualified=True,nativeControls=len(native['checks']),retainedOriginalControls=1612,normalOwnedExits=len(native['ownedExitCodes']),cleanupPassed=True)
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [modelPath,controlsPath,buildPath,oldPath,failedPath,failed40Path,nativePath]},'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeStyleChannelsQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Qualify complete native style/render source inputs; integrate distinct style-aware crop capture and shared typed Elm. Original production preview13 and whole coherent release gates remain open.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
