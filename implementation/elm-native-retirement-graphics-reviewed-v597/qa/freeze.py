import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parent=REPO/'implementation/elm-registration-query-qualified-v587/qa/slice-manifest.json';assert sha(parent)=='2e77e814c7e9a908aa852046785e61e94d723904bb455b61f692d6d919110fb6'
files=[];links=[];components=[];native=[]
for number in [588,589,590,591,592,594,595,596]:
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 manifest=directory/'component-manifest.json'
 if manifest.exists():
  j=json.loads(manifest.read_text());assert j['sourceHeld'];rows=j['files']
  rows=list(rows.items()) if isinstance(rows,dict) else [(r['path'],r) for r in rows]
  for rel,row in rows:
   wanted=row['sha256'] if isinstance(row,dict) else row;assert sha(directory/rel)==wanted,(number,rel)
   if isinstance(row,dict):assert (directory/rel).stat().st_size==row['size']
  components.append({'path':str(manifest.relative_to(REPO)),'sha256':sha(manifest)})
  if number==588:assert j['quintNamedScenarios']==22 and j['quintInvariantSamples']==1000 and j['quintMutationControls']==10 and j['compiledChecks']==2069 and j['typedCompiledMutationControls']==11
  if number==592:assert j['checks']==35 and j['optimizedAssetsMatch'] and j['productionChanges']==['src/Surface.elm','assets/elm.js']
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if number in [591,596] and p.name=='report.json' and p.parent.name.startswith('native-'):
   j=json.loads(p.read_text());expected={591:14,596:42}[number];assert j['passed'] and len(j['checks'])==expected and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions']
   for rel,digest in j['artifacts'].items():assert sha(p.parent/rel)==digest,(number,rel)
   native.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'checks':expected,'cleanupPassed':True,'pair':j['pair']})
   if number==591:assert j['browserWebGPU']['status']=='unavailable' and not j['browserWebGPU']['hardwareQualified'] and not j['performanceAcceptance']
assert len(native)==2 and len(components)==4
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
r={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-native-grant-retirement-authority-v594','guiCandidate':'implementation/elm-recovery-context-feedback-v592','nativeGrantRetirementAccepted':True,'nativeGrantRetirementChecks':42,'graphicsComponentNativeChecks':14,'currentGraphicsComponentAccepted':True,'browserWebGPUStatus':'unavailable','browserWebGPUHardwareAccepted':False,'performanceAccepted':False,'quintNamedScenarios':22,'quintSamples':1000,'quintMutantsRejected':10,'compiledGrantChecks':2069,'compiledGrantMutantsRejected':11,'recoveryPresentationCompiledChecks':35,'recoveryPresentationNativeAccepted':False,'durableReconciliationImplemented':False,'fullReleaseAccepted':False,'nativeAcceptance':False,'completedRequirementIds':[],'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'adoptedComponents':components,'nativeCampaigns':native,'files':files,'symlinks':links}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(p)}))
