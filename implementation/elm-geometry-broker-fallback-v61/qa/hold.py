import hashlib,json,resource,time
from pathlib import Path
import sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports=[]
for prefix,count in [('routing-',109),('refusal-',26)]:
 p=sorted((ROOT/'qa').glob(prefix+'*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and not r.get('error') and len(r['checks'])==count
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest,rel
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
for row in json.loads((ROOT/'parent-inputs.json').read_text()):assert sha(ROOT.parents[1]/row['source'])==row['sha256']
rows=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='held-source-manifest.json']
m={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'unsupportedNativeFallbackImplemented':False,'completedRequirementIds':[],'qaScope':scope,'reports':reports,'files':rows,'scope':'Bounded typed refusal validation and strict observe-only compatibility. Actual V8 ambiguous request-schema remains fatal; native fallback and full geometry compatibility stay open.'}
p=ROOT/'qa/held-source-manifest.json';p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(rows)}))
