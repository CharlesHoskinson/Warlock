import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def only(root,pattern):
 matches=list(root.glob(pattern));assert len(matches)==1,(root,pattern,matches);return matches[0]
def artifacts(reportPath):
 report=json.loads(reportPath.read_text())
 for rel,h in report.get('artifacts',{}).items():assert sha(reportPath.parent/rel)==h,rel
 return report
provider=REPO/'implementation/warlock-preview-provider-v34';buildPath=only(provider,'qa/build-*/report.json');build=artifacts(buildPath);assert build['passed'] and len(build['commands'])==65 and all(row['exitCode']==0 for row in build['commands'])
oldPath=REPO/'implementation/warlock-preview-provider-v32/qa/build-1791263435710014061/report.json';old=json.loads(oldPath.read_text());oldNames=[row['name'] for row in old['commands']];assert len(oldNames)==62 and [row['name'] for row in build['commands'] if row['name'] in set(oldNames)]==oldNames
for rel,h in build['inputs'].items():assert sha(provider/rel)==h,rel
for section in ['compilerDependencies','linkedLibraries','tools']:
 for path,row in build[section].items():assert sha(path)==row['sha256'],path
assert sha(buildPath.parent/'elm-host')==build['binarySHA256']
for name,count in [('typed-family-presenter-replay',14),('family-frame-tests',36),('family-fd-physical-tests',295),('family-source-coupled-decoder',107)]:
 proof=json.loads((buildPath.parent/(name+'.stdout')).read_text());assert proof['passed'] and proof['checks']==count,name
modelPath=only(provider,'qa/check-*/report.json');model=artifacts(modelPath);assert model['passed'] and model['compiledChecks']==36 and model['namedScenarios']==10 and model['invariantSamples']==300 and len(model['coupledTraces'])==22 and model['unsafeMutantsDetected']==3
for rel,h in model['inputs'].items():assert sha(provider/rel)==h,rel
failedBuildPath=only(REPO/'implementation/warlock-preview-provider-v33','qa/build-*/report.json');failedBuild=artifacts(failedBuildPath);assert not failedBuild['passed'] and any(row['exitCode']!=0 for row in failedBuild['commands'])
for rel,h in failedBuild['inputs'].items():assert sha(failedBuildPath.parents[2]/rel)==h,rel
failedNativePath=only(REPO/'implementation/warlock-client-provider-native-v44','qa/native-*/report.json');failedNative=artifacts(failedNativePath);assert not failedNative['passed'] and failedNative['cleanupPassed'] and any(row['name']=='familyWebCanonicalFamilyCoverage' and not row['passed'] for row in failedNative['checks']) and any(row['exitCode']!=0 for row in failedNative['ownedExitCodes'])
nativePath=only(REPO/'implementation/warlock-client-provider-native-v45','qa/native-*/report.json');native=artifacts(nativePath);assert native['passed'] and native['cleanupPassed'] and all(row['passed'] for row in native['checks']) and all(row['exitCode']==0 for row in native['ownedExitCodes'])
previousPath=REPO/'implementation/warlock-client-provider-native-v43/qa/native-1791262717179444040/report.json';previous=json.loads(previousPath.read_text());names=[row['name'] for row in previous['checks']];assert len(names)==1739 and [row['name'] for row in native['checks'] if row['name'] in set(names)]==names
required=['familyWebExactReadinessFenceAfterUnsignaledOffer','familyWebCanonicalFamilyCoverage','familyWebActualRootPopupOffscreenModalPixelsAndForeignExclusion','familyWebPhysicalCloseExportReleaseAndProducerRetireBeforeExactACK','familyWebNormalExit','allOriginal1739OrderedAssertionsRetained']
assert all(next(row for row in native['checks'] if row['name']==name)['passed'] for name in required)
family=native['familyWebKitEvidence'];assert not family['previewEligible'] and not family['hardwarePresentation'] and family['frame']['fidelity']=='family' and family['frame']['signaled'] and family['frame']['coverage']==['client','decoration','modal','popup'] and int(family['source']['crop']['pixelX'])<-180
assert family['pixels']['styledRoot']>0 and family['pixels']['styledPopup']>0 and family['pixels']['modalYellow']>0 and family['pixels']['foreignGreen']==0
for report in [failedNativePath,nativePath]:
 pre=json.loads((report.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
 for path,h in pre['inputs'].items():assert sha(path)==h,path
for name in ['demand.hpp','preview_broker.hpp','client_producer.hpp','imported_clients.hpp','imported_lifecycle.hpp','preview_fd.hpp']:
 assert sha(provider/'native'/name)==sha(REPO/'implementation/warlock-preview-provider-v32/native'/name),name
roots=[failedBuildPath.parents[2],provider,failedNativePath.parents[2],nativePath.parents[2]];components=[]
for root in roots:
 target=root/'component-manifest.json';assert not target.exists();files={}
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(part in ['__pycache__','elm-stuff','mutable-elm-home'] for part in rel.parts):continue
  assert not p.is_symlink(),p
  if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 metadata={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'files':files,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'completeFamilyFidelityQualified':False,'actualSharedFamilyWebKitQualified':root in [provider,nativePath.parents[2]],'status':'retained-actual-evidence'}
 if root in [provider,nativePath.parents[2]]:metadata.update(compiledCommands=65,retainedOriginalCommands=62,nativeControls=len(native['checks']),retainedOriginalControls=1739,normalOwnedExits=len(native['ownedExitCodes']),cleanupPassed=True)
 if root==failedBuildPath.parents[2]:metadata.update(buildPassed=False,failure='Actual Elm shadowing of local request/maximum by newly introduced accessors; corrected in fresh34.')
 if root==failedNativePath.parents[2]:metadata.update(nativeCampaignPassed=False,normalExitAcceptance=False,failure='New fixture expected readiness on initial offer instead of separately exact signaled fence; failure cleanup interrupted clients. Fresh45 requires both events without deadline/oracle change.')
 target.write_text(json.dumps(metadata,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [buildPath,oldPath,modelPath,failedBuildPath,previousPath,failedNativePath,nativePath]},'compiledCommands':65,'retainedOriginalCommands':62,'selectedDemandScenarios':10,'coupledTraces':22,'nativeControls':len(native['checks']),'retainedOriginalControls':1739,'normalOwnedExits':len(native['ownedExitCodes']),'actualSharedFamilyWebKitQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Complete actual family source-stop/minimized historical lifetime and style/fidelity, original preview13 and coherent full release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'report':str(report),'nativeControls':len(native['checks']),'normalOwnedExits':len(native['ownedExitCodes'])}))
