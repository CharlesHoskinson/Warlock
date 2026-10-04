import hashlib,json,resource,stat,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(65536),b''):h.update(b)
 return h.hexdigest()
assert not (ROOT/'component-manifest.json').exists()
w=ROOT/'qa/witness-1791151528129843928/report.json';r=json.loads(w.read_text());assert r['passed'] is True and len(r['checks'])==3
for p,h in r['inputs'].items():assert sha(p)==h
external={};desc=json.loads((ROOT/'inputs/qt-domains-build-report.json').read_text());assert sha(desc['binary'])==desc['binarySHA256'];external[desc['binary']]=desc['binarySHA256'];assert sha(desc['report'])==desc['sha256'];external[desc['report']]=desc['sha256']
build=json.loads(Path(desc['report']).read_text());assert build['passed'] is True and sha(ROOT/'inputs/native/qt-domains.cpp')==build['sourceSHA256']
for group in ['dependencies','libraries','tools']:
 for p,h in build[group].items():assert sha(p)==h,p;external[p]=h
external['/usr/lib/libxkbcommon.so.0']=r['xkbLibrarySHA256'];assert sha('/usr/lib/libxkbcommon.so.0')==r['xkbLibrarySHA256']
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file()}
(ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaign':False,'predecessorDiagnosis':True,'files':files,'externalFiles':external,'witness':str(w),'witnessSHA256':sha(w)},indent=2)+'\n');print(json.dumps({'passed':True,'manifestSHA256':sha(ROOT/'component-manifest.json'),'ownFiles':len(files),'externalFiles':len(external)}))
