import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];report=s/'qa/test-1791131816698238978/report.json';d=json.loads(report.read_text());assert d['passed'] and len(d['checks'])==24 and not d['nativeAcceptance']
files={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
manifest={'sourceHeld':True,'cpuCandidateChecks':24,'sourceReviewPending':True,'nativeAcceptance':False,'releaseAcceptance':False,'files':files};(s/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifest':str(s/'component-manifest.json'),'sha256':hashlib.sha256((s/'component-manifest.json').read_bytes()).hexdigest()}))
