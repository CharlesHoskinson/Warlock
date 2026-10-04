import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
reports=[s/'qa/test-1791132610286534238/report.json',s/'qa/callback-1791132610712052929/report.json']
for p in reports:
 d=json.loads(p.read_text());assert d['passed'] and not d['nativeAcceptance']
 for name,digest in d['inputs'].items():assert sha(name)==digest,name
 if 'artifacts' in d:
  for name,digest in d['artifacts'].items():assert sha(p.parent/name)==digest,name
files={str(p.relative_to(s)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(s/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'sourceReviewPending':True,'nativeAcceptance':False,'releaseAccepted':False,'reports':[str(p) for p in reports],'files':files},indent=2)+'\n');print(json.dumps({'manifest':str(s/'component-manifest.json'),'sha256':sha(s/'component-manifest.json')}))
