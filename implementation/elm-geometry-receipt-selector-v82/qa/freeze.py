import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];TARGET=ROOT/'qa/held-source-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not TARGET.exists(),'Never overwrite held packet'
parent=json.loads((ROOT/'parent.json').read_text());base=REPO/parent['path'];p=base/'qa/held-source-manifest.json';assert sha(p)==parent['heldManifestSHA256']
for rel,e in json.loads(p.read_text())['files'].items():
 if 'symlink' in e:assert os.readlink(base/rel)==e['symlink']
 else:assert sha(base/rel)==e['sha256']
for rel,digest in parent['files'].items():assert sha(base/rel)==digest
assert sha(ROOT/'qa/test.py')==parent['files']['qa/test.py'] and sha(ROOT/'qa/staged-test.py')==parent['files']['qa/staged-test.py']
reports=[]
for prefix,count in [('staged-',30),('selector-',52)]:
 p=sorted((ROOT/'qa').glob(prefix+'*/report.json'))[-1];r=json.loads(p.read_text());assert r['passed'] and not r.get('error') and len(r['checks'])==count and all(c['passed'] for c in r['checks'])
 for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest,rel
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'checks':count})
p=sorted((ROOT/'qa').glob('hold-*/report.json'))[-1];r=json.loads(p.read_text());assert not r['passed'] and len(r['checks'])==15
assert [c['name'] for c in r['checks'] if not c['passed']]==['Unknown receipt refuses before delivery']
for rel,digest in r['inputs'].items():assert sha(ROOT/rel)==digest
for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest
original={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'passed':False,'checksReached':15,'originalChecksPassedClaimed':False,'reason':'Deliberate uniform Unknown/Refused pass-through policy conflicts with old refusal oracle.'}
files={}
for p in sorted(ROOT.rglob('*')):
 if p.is_symlink():files[str(p.relative_to(ROOT))]={'symlink':os.readlink(p)}
 elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
d={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'frozenNs':time.time_ns(),'nativeAcceptance':False,'geometryMenuNativeAccepted':False,'full09Accepted':False,'releaseAccepted':False,'completedRequirementIds':[],'reports':reports,'originalDiagnostic':original,'parent':parent,'scope':'QA-only distinct bounded receipt selector, actual native09 still required; no ordinal-dependent status policy','files':files}
with TARGET.open('x') as f:f.write(json.dumps(d,indent=2)+'\n')
TARGET.chmod(0o444);print(json.dumps({'passed':True,'manifest':str(TARGET),'sha256':sha(TARGET),'files':len(files)}))
