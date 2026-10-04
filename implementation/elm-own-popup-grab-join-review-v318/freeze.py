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
p=ROOT/'review-1791155139030949935/report.json';d=json.loads(p.read_text());assert d['passed'] and not d['nativeAcceptance'];assert d['sourceManifestSHA256']=='e89897fcd85478caa182957abf09a8be1f2cd9d661a985111c54aa5c6565c705'
external={}
for row in d['entries']:
 p=Path(row['path']);assert sha(p)==row['sha256'];external[str(p)]=row
own={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json' and '__pycache__' not in p.parts}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Diagnostic source/closure review only; original unchecked owner finding preserved; no callback/native/authenticated-host admission proof','files':own,'externalFiles':external,'reviewReport':str(ROOT/'review-1791155139030949935/report.json'),'sourceManifestSHA256':d['sourceManifestSHA256'],'coreManifestSHA256':d['coreManifestSHA256']}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PASS',len(own),'own',len(external),'external',sha(ROOT/'component-manifest.json'))
