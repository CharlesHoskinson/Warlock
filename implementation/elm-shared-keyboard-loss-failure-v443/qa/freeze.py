import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parent=REPO/'implementation/elm-shared-keyboard-integrated-v439/qa/slice-manifest.json';assert sha(parent)=='111b2e70f9dc1d77f67b36f826785d59977e1439c7ab3aa111f5239598e5820c'
for e in json.loads(parent.read_text())['files']:assert sha(REPO/e['path'])==e['sha256']
files=[];reports=[]
for name in ['elm-shared-keyboard-loss-runtime-v440','elm-shared-menu-held-key-loss-v441','elm-shared-menu-held-key-recovery-v442']:
 source=REPO/'implementation'/name
 for p in sorted(source.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  assert not p.is_symlink();files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
  if p.name!='report.json' or 'inputs' in p.relative_to(source).parts or 'native-evidence' in p.relative_to(source).parts:continue
  j=json.loads(p.read_text());reports.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'passed':j['passed']})
  for rel,digest in j.get('artifacts',{}).items():assert sha(p.parent/rel)==digest
  for rel,digest in j.get('inputs',{}).items():assert sha(Path(rel) if Path(rel).is_absolute() else source/rel)==digest
  assert not j['passed'] and j['cleanupPassed']
  assert len(j['checks'])==(14 if name.endswith('441') else 24)
  assert j['error']==("ValueError('Expected one bounded parent-input command')" if name.endswith('441') else "RuntimeError('Unchanged observation deadline')")
  assert all(c['passed'] for c in j['checks'])
assert len(reports)==2
for p in [ROOT/'HANDOFF.md',Path(__file__).resolve()]:files.append({'path':str(p.relative_to(REPO)),'sha256':sha(p),'size':p.stat().st_size})
output=ROOT/'qa/slice-manifest.json';assert not output.exists();output.write_text(json.dumps({'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Frozen shared open-menu keyboard restoration failure; source439 remains candidate, no new native acceptance','parentManifest':str(parent),'parentManifestSHA256':sha(parent),'files':files,'reports':reports,'nativeAcceptance':False,'fullReleaseAccepted':False,'completedRequirementIds':[]},indent=2)+'\n');print(json.dumps({'passed':True,'files':len(files),'manifestSHA256':sha(output)}))
