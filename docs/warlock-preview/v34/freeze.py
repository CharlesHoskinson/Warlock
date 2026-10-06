import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
modelPointer=REPO/'implementation/warlock-family-style-revisions-v2/qa/model-report.json';pointer=json.loads(modelPointer.read_text());modelPath=pathlib.Path(pointer['path']);assert sha(modelPath)==pointer['sha256'];model=json.loads(modelPath.read_text());assert model['passed'] and len(model['selectedNames'])==9 and model['states']==29 and len(model['implementationReplay'])==9
for path,h in model['inputs'].items():assert sha(path)==h,path
fdPointer=REPO/'implementation/warlock-family-style-crop-fd-qualification-v1/qa/test-report.json';fp=json.loads(fdPointer.read_text());fdPath=pathlib.Path(fp['path']);assert sha(fdPath)==fp['sha256'];fd=json.loads(fdPath.read_text());assert fd['passed'] and fd['evidence']['legacy']['checks']==150 and fd['evidence']['qualify']['checks']==295 and fd['evidence']['qualify']['physicalFDClosed'] and fd['evidence']['qualify']['physicalMappingClosed']
for path,h in fd['inputs'].items():assert sha(path)==h,path
source=REPO/'implementation/warlock-family-style-crop-capture-v1';assert sha(source/'native/style_revision.hpp')==sha(REPO/'implementation/warlock-family-style-revisions-v2/native/style_revision.hpp')
pair=json.loads((source/'native-build-report.json').read_text());assert pair['result']=='pass' and sha(pair['plugin']['path'])==pair['plugin']['sha256'] and sha(pair['binary'])==pair['sha256'];buildPath=pathlib.Path(pair['pluginBuildReport']);assert sha(buildPath)==pair['pluginBuildReportSHA256'];build=json.loads(buildPath.read_text());assert build['passed'] and not build['missingSymbols']
for rel,h in build['inputs'].items():assert sha(source/rel)==h,rel
for section in ['dependencies','linkedLibraries','tools']:
 for path,h in build[section].items():assert sha(path)==h,path
oldPath=REPO/'implementation/warlock-client-provider-native-v41/qa/native-1791261901860161292/report.json';old=json.loads(oldPath.read_text());names=[row['name'] for row in old['checks']];assert old['passed'] and len(names)==1636
nativePath=REPO/'implementation/warlock-client-provider-native-v43/qa/native-1791262717179444040/report.json';native=json.loads(nativePath.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==1739 and len(native['ownedExitCodes'])==159 and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
assert [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['styleCropOnlyNativeStyleChanged','styleCropOldStyleScopeRejectedBeforeAllocation','styleCropStaleScopeAllocatesNoProducer','styleCropChangedStyleChangesActualPixels','styleCropWholeOffscreenModalAndPopupRetained','allOriginal1636OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
samples=native['styleCropCaptureSamples'];assert len(samples)==3 and [row['pixels']['rootRGBA'][0] for row in samples]==[178,102,128] and all(row['header'][1]==3 and row['header'][22]==131 and not row['previewEligible'] and not row['hardwarePresentation'] for row in samples)
assert samples[2]['pixels']['yellow']==96*64 and samples[2]['pixels']['styledCyan']==64*48
failedPath=REPO/'implementation/warlock-client-provider-native-v42/qa/native-1791262614875927452/report.json';failure=json.loads(failedPath.read_text());assert not failure['passed'] and any(row['name']=='stoppedNewLeaseRetainsOriginalNativeJob' and not row['passed'] for row in failure['checks']) and failure['cleanupPassed'] and any(row['exitCode']!=0 for row in failure['ownedExitCodes'])
for report in [nativePath,failedPath]:
 pre=json.loads((report.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
 for p,h in pre['inputs'].items():assert sha(p)==h,p
for report in [modelPath,fdPath,buildPath,nativePath,failedPath]:
 for rel,h in json.loads(report.read_text()).get('artifacts',{}).items():assert sha(report.parent/rel)==h,rel
roots=[source,fdPath.parents[2],failedPath.parents[2],nativePath.parents[2]];components=[]
for root in roots:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in p.relative_to(root).parts):continue
  if p.is_symlink():assert rel.endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p;links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'files':files,'localBuildLinks':links,'status':'retained-actual-evidence'}
 if root in [source,nativePath.parents[2]]:metadata.update(actualNativeStyleCropQualified=True,nativeControls=len(native['checks']),retainedOriginalControls=1636,normalOwnedExits=len(native['ownedExitCodes']),cleanupPassed=True)
 if root==failedPath.parents[2]:metadata.update(nativeCampaignPassed=False,normalExitAcceptance=False,failure='Fixture selected original stopped lease before later reopened lease; failed cleanup interrupted clients; original assertions/deadlines retained in43.')
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [modelPath,fdPath,buildPath,oldPath,failedPath,nativePath]},'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes']),'actualNativeStyleCropQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Integrate actual style-cropped family metadata/FD3 into typed shared Elm provider; retain full style/renderer source, original production preview13 and coherent release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
