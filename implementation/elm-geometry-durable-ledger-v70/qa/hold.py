import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];TARGET=ROOT/'component-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not TARGET.exists(),'Never overwrite held component'
up=json.loads((ROOT/'upstream.json').read_text())
for row in up['parents']:assert sha(ROOT.parents[1]/row['path'])==row['sha256']
reports=[]
for prefix,count in [('ledger-',64),('protocols-',60),('journal-',19),('namespace-',42)]:
 p=sorted((ROOT/'qa').glob(prefix+'*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and not r.get('error') and len(r['checks'])==count
 assert all(c['passed'] for c in r['checks'])
 for path,digest in r['inputs'].items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==digest,path
 for path,digest in r.get('artifacts',{}).items():assert sha(p.parent/path)==digest,path
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
p=sorted((ROOT/'qa').glob('mutations-*/report.json'))[-1];m=json.loads(p.read_text());assert m['passed'] and len(m['mutants'])==5 and all(e['caught'] for e in m['mutants'])
for rel,digest in m['inputs'].items():assert sha(ROOT/rel)==digest
for rel,digest in m['artifacts'].items():assert sha(p.parent/rel)==digest
reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'unsafeMutantsCaught':5})
files=[]
for q in sorted(ROOT.rglob('*')):
 if q.is_symlink():files.append({'path':str(q.relative_to(ROOT)),'symlink':os.readlink(q)})
 elif q.is_file():files.append({'path':str(q.relative_to(ROOT)),'sha256':sha(q),'size':q.stat().st_size,'mode':stat.S_IMODE(q.stat().st_mode)})
d={'schema':1,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'frozenNs':time.time_ns(),'scope':'Actual isolated Python durable ledger/filesystem tests plus unchanged inherited storage source tests. No host/broker/Elm/native integration acceptance.','nativeAcceptance':False,'fullRecoveryAcceptance':False,'releaseAccepted':False,'deploymentAccepted':False,'completedRequirementIds':[],'maxUnresolved':64,'maxAllocationScopes':128,'maxLedgerBytes':524288,'reports':reports,'parentInputs':up,'files':files}
with TARGET.open('x') as f:f.write(json.dumps(d,indent=2)+'\n')
TARGET.chmod(0o444);print(json.dumps({'passed':True,'manifest':str(TARGET),'sha256':sha(TARGET),'files':len(files)}))
