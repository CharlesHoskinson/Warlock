import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
p=ROOT/'review-1791156335565281820/report.json';r=json.loads(p.read_text());assert r['passed'] and r['authenticated'] is False and r['ownBlockerGrantQualified'] is False
external={}
for x in r['entries']:
 p=Path(x['path']);assert sha(p)==x['sha256'];external[str(p)]=x
for p,w in r['tools'].items():assert sha(p)==w;external[p]={'sha256':w,'size':Path(p).stat().st_size}
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'authenticated':False,'ownBlockerGrantQualified':False,'scope':'Independent corrected diagnostic DTO replay and preserved unsafe ancestor characterization; no live/authenticated grant','files':files,'externalFiles':external,'reviewReport':str(ROOT/'review-1791156335565281820/report.json')}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PASS',len(files),'own',len(external),'external',sha(ROOT/'component-manifest.json'))
