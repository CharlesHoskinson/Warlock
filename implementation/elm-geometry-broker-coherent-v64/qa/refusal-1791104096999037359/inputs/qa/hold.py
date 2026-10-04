import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parents=[REPO/'implementation/elm-geometry-broker-fallback-v61',REPO/'implementation/elm-geometry-broker-framing-v62']
for parent in parents:
 manifest=parent/'qa/held-source-manifest.json';m=json.loads(manifest.read_text());assert m['sourceHeld']
 entries=m['files']
 if isinstance(entries,dict):
  for rel,digest in entries.items():assert sha(parent/rel)==digest,rel
 else:
  for row in entries:assert sha(parent/row['path'])==row['sha256'],row['path']
for row in json.loads((ROOT/'parents-inventory.json').read_text()):assert sha(REPO/row['source'])==row['sha256'],row['source']
for p in (ROOT/'adapter').glob('*.py'):assert sha(p)==sha((parents[0] if p.name=='endpoint.py' else parents[1])/'adapter'/p.name),p.name
reports=[]
for pattern,count in [('routing-*',109),('routing-*',115),('strong-*',118),('refusal-*',26),('framing-*',1011)]:
 candidates=[]
 for p in (ROOT/'qa').glob(pattern+'/report.json'):
  r=json.loads(p.read_text())
  if r.get('passed') and not r.get('error') and len(r['checks'])==count:candidates.append(p)
 p=sorted(candidates)[-1];r=json.loads(p.read_text())
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest,rel
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
mutant=sorted((ROOT/'qa').glob('strong-unsafe-*/report.json'))[-1];r=json.loads(mutant.read_text());assert not r['passed'] and 'strong near-bound tail plus read remains per-frame error expectation' in r['error']
assert len(r['checks'])==116 and r['checks'][-1]['passed']==False
rows=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='held-source-manifest.json']
m={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'unsupportedNativeFallbackImplemented':False,'completedRequirementIds':[],'qaScope':scope,'reports':reports,'mutation':{'path':str(mutant.relative_to(ROOT)),'sha256':sha(mutant),'caught':True},'parents':[{'path':str(p.relative_to(REPO)),'heldManifestSHA256':sha(p/'qa/held-source-manifest.json')} for p in parents],'files':rows,'scope':'Exact V62 framing plus V61 typed refusal. Actual handler/strict endpoint CPU only; no geometry menu/native/release acceptance.'}
p=ROOT/'qa/held-source-manifest.json';p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'passed':True,'manifest':str(p),'sha256':sha(p),'files':len(rows)}))
