import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-projection-escape-integrated-v510/qa/slice-manifest.json';assert sha(parent)=='18461a1d0030c34a0aed86650cf26ce65023eb22ef91753189b93716bbb79c4e';held=json.loads(parent.read_text())
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
source=REPO/'implementation/elm-stable-surface-publication-v521';original=REPO/'implementation/elm-projection-native-escape-combined-v507'
for d in ['src','native','adapter','assets']:
 for p in (source/d).glob('*'):
  if not p.is_file():continue
  rel=p.relative_to(source)
  if str(rel)=='src/SurfaceController.elm':
   s=(original/rel).read_text().replace('let stableApplications = case message of', 'let stableSurface = model.publication/=UInt64.zero && not newLease && List.isEmpty effects\n                    && E.encode 0 (Surface.packet model.publication model.lease next)==E.encode 0 (frame current)\n            stableApplications = case message of').replace('in if stableApplications then','in if stableSurface || stableApplications then')
   assert p.read_text()==s
  else:assert sha(p)==sha(original/rel),str(rel)
files=[];links=[];reports=[];native=[]
for n in list(range(516,526))+[527]:
 directory=next((REPO/'implementation').glob('*v'+str(n)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(directory).parts for x in ['inputs','native-evidence']):continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if n==517:assert not j['passed'] and 'parsing failed' in j['error'];continue
  assert j['passed']
  if n==519:assert len(j['namedScenarios'])==8 and j['invariantSamples']==1000 and j['mutantsRejected']==5
  if n==524:assert j['witness']['stateChanged'] and j['witness']['sameSurface'] and j['witness']['publishCount']==1 and j['witness']['before']['publication']=='2'
  if n==522:assert len(j['checks'])==9 and all(e['passed'] for e in j['checks'])
  if n==527:assert len(j['controls'])==4 and all(e['rejected'] for e in j['controls'])
  if n==525:
   assert len(j['checks'])==89 and all(e['passed'] for e in j['checks']) and j['cleanupPassed'] and not j['mainDesktopActions'] and j['pair']==held['nativePair'];native.append(str(p.relative_to(REPO)))
assert len(native)==1
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':str(source.relative_to(REPO)),'parentManifest':str(parent),'parentManifestSHA256':sha(parent),'nativePair':held['nativePair'],'nativeAcceptance':True,'nativeCheckCount':89,'nativeReports':native,'typedCompiledCases':9,'compiledMutantsRejected':4,'quintNamedScenarios':8,'quintSamples':1000,'quintMutantsRejected':5,'files':files,'symlinks':links,'reports':reports,'unresolvedPointerPublicationRace':'implementation/elm-pointer-publication-race-diagnostic-v515/witness.json','pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[]}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
