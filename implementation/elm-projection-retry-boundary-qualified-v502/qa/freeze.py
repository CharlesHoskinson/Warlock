import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-projection-terminal-qualified-v493/qa/slice-manifest.json';assert sha(parent)=='211838ad44f800a9efbd3a6c052a5e10015ea501f589f4276fed6098cf603e1f'
held=json.loads(parent.read_text())
for e in held['files']:assert sha(REPO/e['path'])==e['sha256']
source=REPO/'implementation/elm-projection-retry-exhaustion-v498';previous=REPO/'implementation/elm-projection-correlated-terminal-v490'
for d in ['src','native','assets','adapter']:
 for p in (source/d).rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(source);original=previous/rel
  if str(rel)=='src/Shell.elm':
   assert p.read_text()==original.read_text().replace('phase = Exhausted, expected = Nothing, notice = "Restart the shell to continue."','phase = Exhausted, expected = Nothing, projectionRetryQueued=False, notice = "Restart the shell to continue."')
  else:assert sha(p)==sha(original),str(rel)
files=[];links=[];reports=[]
for n in range(494,502):
 directory=next((REPO/'implementation').glob('*v'+str(n)))
 for p in sorted(directory.rglob('*')):
  if '__pycache__' in p.parts or 'elm-stuff' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or any(x in p.relative_to(directory).parts for x in ['inputs','native-evidence']):continue
  j=json.loads(p.read_text());assert j['passed'];reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':True})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  if n==496:assert j['defectReproduced'] and len(j['checks'])==10
  if n==498 and p.parent.name.startswith('model-'):assert len(j['namedScenarios'])==9 and j['invariantSamples']==1000 and j['mutantsRejected']==6
  if n==499:assert len(j['checks'])==14 and all(c['passed'] for c in j['checks'])
  if n==500:assert len(j['checks'])==89 and all(c['passed'] for c in j['checks']) and j['cleanupPassed'] and j['pair']==held['nativePair'] and not j['mainDesktopActions']
for p in [Path(__file__).resolve(),ROOT/'HANDOFF.md']:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
assert len(reports)==5
m={'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'parentManifest':str(parent.relative_to(REPO)),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'source':str(source.relative_to(REPO)),'nativePair':held['nativePair'],'nativeAcceptance':True,'nativeCheckCount':89,'typedCompiledCases':14,'quintNamedScenarios':9,'quintSamples':1000,'quintMutantsRejected':6,'uiUxReview':'implementation/elm-uiux-resumption-review-v501/REVIEW.md','fullReleaseAccepted':False,'completedRequirementIds':[]}
p=ROOT/'qa/slice-manifest.json';assert not p.exists();p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(p)}))
