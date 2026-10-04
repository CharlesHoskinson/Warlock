import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OLD=REPO/'implementation/elm-xdg-pointer-journal-oracle-v213';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=OLD/'component-manifest.json';assert sha(manifest)=='af45469f364e5b63cb49732775caa81240a2f587c016b1f1269254b4d1f9df77'
m=json.loads(manifest.read_text());external={}
for rel,row in m['files'].items():
 p=OLD/rel;assert sha(p)==row['sha256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
for p in m['reports']:
 report=Path(p);j=json.loads(report.read_text());assert j['passed']
 for path,d in j.get('inputs',{}).items():
  q=Path(path);assert sha(q)==d;external[path]={'sha256':d,'size':q.stat().st_size}
external[str(manifest)]={'sha256':sha(manifest),'size':manifest.stat().st_size}
assert sha(OLD/'oracle.py')=='45a97d355179b186bb40d74890e813231f3917b43bacdc9e547f10076728ad21'
target=ROOT/'component-manifest.json';assert not target.exists();files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p!=target}
target.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Independent selected-pointer-record source review; no native injection/hardware qualification','reviewStatus':'scoped clear','nativeAcceptance':False,'files':files,'externalClosure':external},indent=2)+'\n')
print(json.dumps({'passed':True,'verifiedEntries':len(external),'manifest':str(target),'manifestSHA256':sha(target)}))
