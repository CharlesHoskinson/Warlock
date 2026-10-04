import hashlib,json,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
kind=sys.argv[1];assert kind in ('receipt','relay');base=ROOT/kind
reports=list((base/'qa').glob(('hold-' if kind=='receipt' else 'test-')+'*/report.json'));assert len(reports)==1
r=json.loads(reports[0].read_text());assert r['passed'] and all(c['passed'] for c in r['checks'])
for name,digest in r['artifacts'].items():assert sha(reports[0].parent/name)==digest
names=['qa/wrapper.py','qa/broker-entrypoint.py'] if kind=='receipt' else ['qa/relay.py'];files={}
for name in names:
 p=base/name;assert p.is_file() and not p.is_symlink();files[name]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
result={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual current278/291 source binding and unchanged CPU receipt/relay controls only; native effects/reconnect separate','files':files,'report':str(reports[0]),'reportSHA256':sha(reports[0])}
p=base/'qa/held-source-manifest.json'
with p.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':True,'kind':kind,'checks':len(r['checks']),'manifestSHA256':sha(p)}))
