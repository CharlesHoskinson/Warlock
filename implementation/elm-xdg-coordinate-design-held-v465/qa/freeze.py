import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-nonzero-origin-presentation-failure-v462/qa/slice-manifest.json';assert sha(parent)=='ea3657b7a15b5f7083a9cc0e4f67a989e404193a8f23f1112c251dc4f14f9290'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];reports=[];links=[]
for name in ['elm-xdg-origin-render-diagnosis-v463','elm-xdg-coordinate-contract-v464']:
 source=REPO/'implementation'/name
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json':continue
  j=json.loads(p.read_text());assert j['passed'];reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel))==digest
  if name.endswith('463'):assert len(j['checks'])==9 and all(e['passed'] for e in j['checks']) and j['redExtent']==[15,23,22,30]
  else:assert len(j['namedScenarios'])==8 and j['invariantSamples']==1000 and j['maxSteps']==40 and j['mutantsRejected']==4
assert len(reports)==2
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Frozen image/owning-source diagnosis plus typed executable coordinate architecture; no native correction acceptance','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'diagnosticChecks':9,'quintNamedScenarios':8,'quintSamples':1000,'quintMaxSteps':40,'quintMutantsRejected':4,'nativeAcceptance':False,'nativeCoordinateCorrectionAccepted':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(output)}))
