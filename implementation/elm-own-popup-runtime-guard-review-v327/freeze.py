import hashlib,json,os,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
p=ROOT/'review-1791157942036863437/report.json';r=json.loads(p.read_text());assert r['passed'] and r['authenticatedHost'] is False and r['nativeAcceptance'] is False
external={}
for x in r['entries']:
 p=Path(x['path'])
 if 'symlink' in x:assert p.is_symlink() and os.readlink(p)==x['symlink']
 else:assert sha(p)==x['sha256']
 external[str(p)]=x
for p,w in r['tools'].items():assert sha(p)==w;external[p]={'sha256':w,'size':Path(p).stat().st_size}
files={}
for p in sorted(ROOT.rglob('*')):
 if p.name=='component-manifest.json' or '__pycache__' in p.parts:continue
 if p.is_symlink():files[str(p.relative_to(ROOT))]={'symlink':os.readlink(p)}
 elif p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size}
m={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'authenticatedHost':False,'scope':'Independent final330 source/runtime guard CPU qualification; rejected326/329 and all unsafe witnesses preserved; no host/menu authorization or native acceptance','files':files,'externalFiles':external,'reviewReport':str(ROOT/'review-1791157942036863437/report.json'),'sourceManifestSHA256':'66527cb94aa2fc22e7b2bfc29af1e868a90a42668a2008af33adcc204583960f'}
(ROOT/'component-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print('PASS',len(files),'own',len(external),'external',sha(ROOT/'component-manifest.json'))
