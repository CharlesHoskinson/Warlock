import hashlib,json,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(65536),b''):h.update(chunk)
 return h.hexdigest()
assert not (ROOT/'component-manifest.json').exists()
external={};ancestors={}
for name in ['elm-qt6-popup-landmark-fixture-v289','elm-qt6-journal-consumer-v279','elm-keyboardless-toolkit-owning-observer-v223']:
 parent=REPO/'implementation'/name;m=parent/'component-manifest.json';r=json.loads(m.read_text());assert r['sourceHeld'] is True and r['evidenceIntegrityPassed'] is True
 external[str(m)]=sha(m);ancestors[name]=sha(m)
 for relative,row in r['files'].items():
  p=parent/relative;assert sha(p)==row['sha256'],str(p);external[str(p)]=row['sha256']
 for path,row in r['externalFiles'].items():
  expected=row['sha256'] if isinstance(row,dict) else row
  assert sha(path)==expected,path;external[path]=expected
for relative in ['qa/protocol.py','qa/geometry.py','qa/scene.py']:
 p=REPO/'implementation/elm-gtk-native-acquisition-fix-v268'/relative;external[str(p)]=sha(p)
assert (ROOT/'qa/journal.py').read_bytes()==(REPO/'implementation/elm-qt6-journal-consumer-v279/qa/journal.py').read_bytes()
reports=[]
for pattern in ['test-*/report.json','mutations-*/report.json']:
 matches=[]
 for p in (ROOT/'qa').glob(pattern):
  r=json.loads(p.read_text())
  if r.get('passed') is True and all(sha(k)==v for k,v in r['sourceInputs'].items() if Path(k).name not in ('freeze.py',)):matches.append(p)
 assert matches,pattern
 selected=sorted(matches)[-1];reports.append(str(selected))
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file()}
report={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaign':False,'presentationProved':False,'files':files,'externalFiles':external,'ancestors':ancestors,'selectedReports':reports}
(ROOT/'component-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'manifestSHA256':sha(ROOT/'component-manifest.json'),'ownFiles':len(files),'externalFiles':len(external)}))
