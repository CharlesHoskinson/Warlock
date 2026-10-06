import hashlib,json,pathlib,resource,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
REPO=pathlib.Path('/home/hoskinson/omarchy-windows-parity');OUT=pathlib.Path(__file__).parent
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
campaign=REPO/'implementation/warlock-client-provider-native-v34/qa/native-1791257839724867928/report.json';native=json.loads(campaign.read_text());assert native['passed'] and native['cleanupPassed'] and len(native['checks'])==1351 and all(r['passed'] for r in native['checks']) and len(native['ownedExitCodes'])==125 and all(r['exitCode']==0 for r in native['ownedExitCodes'])
base=REPO/'implementation/warlock-client-provider-native-v33/qa/native-1791257049560687982/report.json';old=json.loads(base.read_text());names=[r['name'] for r in old['checks']];assert len(names)==1214 and [r['name'] for r in native['checks'] if r['name'] in set(names)]==names
assert len(native['familyRevisionReplay'])==6 and sum(r['statesCompared'] for r in native['familyRevisionReplay'])==34
pre=json.loads((campaign.parents[2]/'qa/preflight.json').read_text());assert pre['passed']
for p,h in pre['inputs'].items():assert sha(p)==h,p
for rel,h in native['artifacts'].items():assert sha(campaign.parent/rel)==h,rel
failed=REPO/'implementation/warlock-family-source-revisions-v1/qa/build-1791257315293739522/report.json';failure=json.loads(failed.read_text());assert not failure['passed'] and 'misleading-indentation' in failure['error']
source=REPO/'implementation/warlock-family-source-revisions-v2';descriptor=json.loads((source/'native-build-report.json').read_text());build=pathlib.Path(descriptor['pluginBuildReport']);compiled=json.loads(build.read_text());assert compiled['passed'] and not compiled['missingSymbols'] and sha(build)==descriptor['pluginBuildReportSHA256'] and sha(descriptor['plugin']['path'])==descriptor['plugin']['sha256']
assert native['pair']['plugin']==descriptor['plugin'] and native['pair']['core']['sha256']==descriptor['sha256']
for rel,h in compiled['inputs'].items():assert sha(source/rel)==h,rel
for key in ['dependencies','linkedLibraries','tools']:
 for p,h in compiled[key].items():assert sha(p)==h,p
for report in [failed,build]:
 for rel,h in json.loads(report.read_text())['artifacts'].items():assert sha(report.parent/rel)==h,rel
model=REPO/'implementation/warlock-family-revision-model-v1';pointer=json.loads((model/'qa/model-report.json').read_text());modelReport=pathlib.Path(pointer['path']);assert sha(modelReport)==pointer['sha256'];proof=json.loads(modelReport.read_text());assert proof['passed'] and len(proof['selectedNames'])==8 and proof['states']==48 and len(proof['implementationReplay'])==8
for p,h in proof['inputs'].items():assert sha(p)==h,p
for rel,h in proof['artifacts'].items():assert sha(modelReport.parent/rel)==h,rel
components=[]
for root,status in [(failed.parents[2],'retained-Werror-family-observer-compilation-failure'),(source,'compiled-native-read-only-family-revision-observer-qualified'),(model,'eight-selected-CPU-family-revision-projections-qualified'),(campaign.parents[2],'actual-native-family-projections-1351-controls-125-normal-exits-qualified')]:
 target=root/'component-manifest.json';assert not target.exists();files={};links={}
 for p in sorted(root.rglob('*')):
  rel=str(p.relative_to(root))
  if any(x in ['__pycache__','elm-stuff','mutable-elm-home'] for x in p.relative_to(root).parts):continue
  if p.is_symlink():
   assert rel.endswith('/include/hyprland') and p.resolve()==p.parent.parent/'owning-headers',p
   links[rel]=str(p.readlink());continue
  if p.is_file():files[rel]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
 held={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'status':status,'nativeAcceptance':False,'fullReleaseAccepted':False,'previewEligible':False,'productionFamilyCaptureQualified':False,'files':files,'localBuildLinks':links}
 if root in [source,campaign.parents[2]]:held.update(actualNativeFamilyObservationQualified=True,nativeControls=1351,retainedOriginalControls=1214,normalOwnedExits=125,cleanupPassed=True,nativeFamilyTraces=6,nativeFamilyStates=34)
 if root==model:held.update(selectedCPUTraces=8,CPUStates=48,syntheticGraphRefusalNativeQualified=False)
 target.write_text(json.dumps(held,indent=2)+'\n');components.append({'path':str(target.relative_to(REPO)),'sha256':sha(target),'files':len(files)})
report=OUT/'report.json';assert not report.exists();report.write_text(json.dumps({'schema':1,'passed':True,'components':components,'evidence':{str(p.relative_to(REPO)):sha(p) for p in [campaign,base,failed,build,modelReport]},'nativeControls':1351,'normalOwnedExits':125,'actualNativeFamilyObservationQualified':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'next':'Implement and qualify combined family renderer/crop/FD and complete source inputs, typed shared GUI adoption, original preview13 and coherent GUI release gates.'},indent=2)+'\n');print(json.dumps({'passed':True,'nativeControls':1351,'normalOwnedExits':125,'report':str(report)}))
