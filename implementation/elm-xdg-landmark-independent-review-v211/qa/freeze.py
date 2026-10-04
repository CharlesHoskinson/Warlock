import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OLD=REPO/'implementation/elm-xdg-presented-landmark-oracle-v208';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=OLD/'component-manifest.json';assert sha(manifest)=='48fcb8bd0017ebf6924fcb1a484585bfbe3eb8f9d09b6196367ad6c7cedf7bb8'
m=json.loads(manifest.read_text());external={}
for rel,row in m['files'].items():
 p=OLD/rel;assert sha(p)==row['sha256'];external[str(p)]={'sha256':sha(p),'size':p.stat().st_size}
external[str(manifest)]={'sha256':sha(manifest),'size':manifest.stat().st_size}
witness=ROOT/'witness.json';w=json.loads(witness.read_text());assert w['passed'] and w['sourceSHA256']==sha(OLD/'oracle.py') and len(w['rows'])==3 and all(x['accepted'] for x in w['rows'])
assert w['rows'][1]['historyTypes']==['float'] and w['rows'][2]['historyTypes']==['bool']
target=ROOT/'component-manifest.json';assert not target.exists();files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in ROOT.rglob('*') if p.is_file() and p!=target}
target.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'scope':'Independent read-only boundary finding with synthetic actual208 acceptance witness, not native qualification','nativeAcceptance':False,'files':files,'externalClosure':external,'findingReproduced':True},indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(target),'manifestSHA256':sha(target)}))
