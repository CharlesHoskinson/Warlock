import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=ROOT/'qa/orphan-1791146165317384287';report=json.loads((out/'report.json').read_text())
assert report['passed'] and report['nativeAcceptance'] is False and len(report['cases'])==8
assert sha(out/'activation-supervisor.py')==report['sourceSHA256']
assert (out/'test.py').read_bytes()==(ROOT/'qa/test.py').read_bytes()
for case in report['cases']:
 assert case['passed'] and case['runtimeGone'] and not case['cleanupSignals'] and not case['liveOrphans']
 assert case['normalCompletionMarkers']==case['recordedOrphans']==8
 assert len(case['terminal']['allWaitStatuses'])==9
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Eight actual live-orphan fork trees on captured268 supervisor only; not exhaustive scheduling proof','files':files,'report':str(out/'report.json')},indent=2)+'\n')
print(json.dumps({'passed':True,'manifestSHA256':sha(manifest)}))
