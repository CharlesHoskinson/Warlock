import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OLD=REPO/'implementation/elm-xdg-presented-landmark-oracle-v210';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=OLD/'component-manifest.json';assert sha(manifest)=='cab09061c578e6b4015abfd495f6bfb022f578c1d0b920ccc059557c6e1e96b9'
m=json.loads(manifest.read_text());external={}
for rel,row in m['files'].items():
 p=OLD/rel;assert sha(p)==row['sha256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
assert sha(OLD/'oracle.py')=='a209e966d2601548ca4bdac49f3e1dc4791f8b1bcfde3949d265f66bfefbd7ec'
for rel,count in [('qa/test-1791132578072609671/report.json',24),('qa/test-1791132578058133747/report.json',64)]:
 j=json.loads((OLD/rel).read_text());assert j['passed'] and len(j['checks'])==count
j=json.loads((OLD/'qa/mutations-1791132524188492751/report.json').read_text());assert j['passed'] and len(j['controls'])==4 and all(c['rejected'] for c in j['controls']) and j['sourceSHA256']==sha(OLD/'oracle.py')
external[str(manifest)]={'sha256':sha(manifest),'size':manifest.stat().st_size}
target=ROOT/'component-manifest.json';assert not target.exists();files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p!=target}
target.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Read-only canonical metadata/source review; no native capture qualification','reviewStatus':'scoped clear','nativeAcceptance':False,'files':files,'externalClosure':external},indent=2)+'\n')
print(json.dumps({'passed':True,'verifiedEntries':len(external),'manifest':str(target),'manifestSHA256':sha(target)}))
