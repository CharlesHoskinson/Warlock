"""Protected read-only adoption audit inventory, no new native claim."""
import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'qa/audit-1791110707171837201/report.json';r=json.loads(p.read_text());assert r['passed'] and len(r['checks'])==16 and all(c['passed'] for c in r['checks']) and r['noCoreMergeNeeded'] and not r['nativeAcceptance']
for path,e in r['pins'].items():
 if path.endswith('/docs/elm-roadmap/delivery/loop-state.json'):continue
 f=Path(path);assert f.stat().st_size==e['size'] and sha(f)==e['sha256'],path
files={str(f.relative_to(ROOT)):{'sha256':sha(f),'size':f.stat().st_size,'mode':stat.S_IMODE(f.stat().st_mode)} for f in ROOT.rglob('*') if f.is_file()}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'menu09CurrentTupleAccepted':False,'releaseAcceptance':False,'scope':'Read-only current tuple ABI/archive lineage and adoption contracts; no build or GUI','noCoreMergeNeeded':True,'auditReport':{'path':str(p.relative_to(ROOT)),'sha256':sha(p)},'files':files}
target=ROOT/'qa/held-source-manifest.json'
with target.open('x') as s:s.write(json.dumps(m,indent=2)+'\n')
target.chmod(0o444);print(json.dumps({'passed':True,'manifest':str(target),'sha256':sha(target),'files':len(files)}))
