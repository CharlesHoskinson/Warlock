import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,"/home/hoskinson/window-integration-qa")
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=ROOT/"qa/corrected-1791148562729723625/report.json";r=json.loads(report.read_text());assert r['passed'] is True
for path,digest in r['inputs'].items():assert sha(path)==digest
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
manifest=ROOT/"component-manifest.json";assert not manifest.exists();manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'files':files,'externalFiles':r['inputs'],'report':str(report)},indent=2)+"\n");print(sha(manifest))
