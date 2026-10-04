"""Read-only strict relay CPU source/evidence freeze; native lifecycle remains separate."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports=[]
for suffix,count in [('test-1791108738345832488',19),('edges-1791108548316685503',7),('deadline-1791108738113730686',7)]:
 p=ROOT/'qa'/suffix/'report.json';r=json.loads(p.read_text());assert r['passed'] and len(r['checks'])==count and all(c['passed'] for c in r['checks'])
 assert sha(ROOT/'qa/relay.py')==sha(p.parent/'inputs/qa/relay.py')
 for rel,digest in r['artifacts'].items():assert sha(p.parent/rel)==digest,rel
 reports.append({'path':str(p),'sha256':sha(p),'checks':count})
files={};symlinks={}
for p in sorted(ROOT.rglob('*')):
 rel=str(p.relative_to(ROOT))
 if p.is_symlink():symlinks[rel]=str(p.readlink())
 elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
manifest={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'scope':'Strict actual relay pipe/control subprocess CPU qualification, baseline19+transport7+late-publication7; real broker lifecycle and GUI remain unqualified','files':files,'symlinks':symlinks,'reports':reports,'api':{'entrypoint':'qa/relay.py PRIVATE_CONFIG','configFields':['authorityConfig','controlDirectory'],'control':'close_stdin(privateDirectory)','actors':'actor_status(privateDirectory)','completion':'exit_status(privateDirectory)','completionFields':['relay','child','childExit','stdinClosed'],'EOFDeadlineSeconds':3,'queueBytesPerDirection':8192,'broker':'Exact captured V74/V64 adapter; no arbitrary command profile'}}
path=ROOT/'qa/held-source-manifest.json'
with path.open('x') as f:f.write(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'passed':True,'manifest':str(path),'sha256':sha(path),'files':len(files)}))
