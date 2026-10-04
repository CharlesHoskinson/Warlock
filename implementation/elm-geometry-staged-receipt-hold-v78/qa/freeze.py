import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];TARGET=ROOT/'qa/held-source-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not TARGET.exists(),'Never overwrite held packet'
for row in json.loads((ROOT/'upstream.json').read_text()):assert sha(REPO/row['path'])==row['sha256']
parent=REPO/'implementation/elm-geometry-receipt-hold-v63';m=json.loads((parent/'qa/held-source-manifest.json').read_text())
for rel,e in m['files'].items():assert sha(parent/rel)==e['sha256']
reports=[]
for prefix,count in [('hold-',45),('staged-',30)]:
 p=sorted((ROOT/'qa').glob(prefix+'*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and not r.get('error') and len(r['checks'])==count and all(c['passed'] for c in r['checks'])
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest,rel
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
# Preserve the original failed whole-selector fixture capture and report.
failed=[]
for p in sorted((ROOT/'qa').glob('staged-*/report.json')):
 r=json.loads(p.read_text())
 if not r['passed']:
  for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
  failed.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'error':r.get('error')})
assert failed
files={}
for p in sorted(ROOT.rglob('*')):
 if p.is_symlink():files[str(p.relative_to(ROOT))]={'symlink':os.readlink(p)}
 elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
d={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'frozenNs':time.time_ns(),'nativeAcceptance':False,'geometryMenuNativeAccepted':False,'full09Accepted':False,'releaseAccepted':False,'completedRequirementIds':[],'reports':reports,'failedReports':failed,'scope':'QA-only delivery hold fixture CPU; actual native09 remains required; no SIGSTOP or fabricated receipts','files':files}
with TARGET.open('x') as f:f.write(json.dumps(d,indent=2)+'\n')
TARGET.chmod(0o444);print(json.dumps({'passed':True,'manifest':str(TARGET),'sha256':sha(TARGET),'files':len(files)}))
