import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-stable-publication-integrated-v531/qa/slice-manifest.json';assert sha(parent)=='0f49d27e22ac4aaa816bd2a7d2a00c401eb75583d3c3bccec75c2095d11dace9'
files=[];links=[];reports=[]
for number in [535,536,537,538,539]:
 directory=next((REPO/'implementation').glob('*v'+str(number)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name=='report.json':
   j=json.loads(p.read_text());assert j['passed']==(number!=536);assert j['nativeAcceptance']==False;reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
   for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
   if number in [535,537]:assert len(j['namedScenarios'])==9 and j['invariantSamples']==1000 and j['mutantsRejected']==6
   if number==537:assert j['fuzzInitialState']=='released live gesture with available proof'
   if number==538:assert len(j['checks'])==2 and all(c['passed'] for c in j['checks']);assert sha(Path(j['capturedLog']))==j['capturedLogSHA256']
   if number==539:assert len(j['checks'])==2 and all(c['passed'] for c in j['checks'])
assert len(reports)==5
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md',REPO/'implementation/elm-publication-input-counterfactual-v540/HANDOFF.md',REPO/'implementation/elm-publication-input-counterfactual-v540/qa/freeze.py',REPO/'implementation/elm-publication-input-counterfactual-v540/qa/slice-manifest.json']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
result={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'source':'implementation/elm-stable-surface-publication-v521','parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'nativeAcceptance':False,'scope':'Live-gesture abstract Quint and actual compiled Elm/C counterfactual with captured frames and synthetic engine/input proof; no new native acceptance','pointerRaceCausallyResolved':False,'fullReleaseAccepted':False,'completedRequirementIds':[],'files':files,'symlinks':links,'reports':reports}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
