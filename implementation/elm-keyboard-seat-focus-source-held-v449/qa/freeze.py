import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-shared-keyboard-loss-failure-v443/qa/slice-manifest.json';assert sha(parent)=='d0eb12ce88362907866d2373bd12122326539caf2d1fc42cd1c9524b821b3e1e'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];links=[];reports=[]
for name in ['elm-keyboard-focus-resource-observer-v444','elm-shared-menu-focus-diagnostic-v445','elm-keyboard-seat-focus-policy-v446','elm-keyboard-seat-focus-proof-v447','elm-core-seat-focus-compile-v448']:
 source=REPO/'implementation'/name
 for p in sorted(source.rglob('*')):
  if '__pycache__' in p.parts:continue
  if p.is_symlink():links.append({'path':str(p.relative_to(REPO)),'target':str(p.readlink())});continue
  if not p.is_file():continue
  files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or 'inputs' in p.relative_to(source).parts or 'native-evidence' in p.relative_to(source).parts:continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  if name.endswith('445'):
   assert not j['passed'] and j['cleanupPassed'] and len(j['checks'])==24 and j['error']=="RuntimeError('Unchanged observation deadline')"
   diag=[e for e in j['focusDiagnostics'] if e['kind']=='capability'];assert len(diag)==3
   before,clear,after=[e['state'] for e in diag]
   assert before['focus']['surfaceClientPID']==clear['focus']['surfaceClientPID']==j['privateHost']['elm-webview']['pid']
   assert after['focus']['surfaceClientPID']==j['privateHost']['fixture']['pid']!=before['focus']['surfaceClientPID'] and after['seatGrab']
   assert before['focus']['liveKeyboardResources']==after['focus']['liveKeyboardResources']==1 and clear['focus']['liveKeyboardResources']==0
  else:assert j['passed']
proof=next((REPO/'implementation/elm-keyboard-seat-focus-proof-v447/qa').glob('model-*/report.json'));m=json.loads(proof.read_text());assert len(m['namedScenarios'])==7 and m['mutantsRejected']==3 and m['invariantSamples']==1000
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Causal native focus diagnosis and guarded source/full TU compile/Quint proof; no native fix acceptance','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'symlinks':links,'reports':reports,'nativeAcceptance':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'reports':len(reports),'manifestSHA256':sha(output)}))
