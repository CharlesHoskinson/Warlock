"""Hold reviewed original geometry campaign source before native execution."""
import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'qa/preflight-1791111336419919994/report.json'
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
result={'passed':False,'nativeAcceptance':False}
try:
    proof=json.loads(REPORT.read_text());assert proof['passed'] and len(proof['checks'])==18
    assert all(row['passed'] for row in proof['checks'])
    for relative,expected in proof['candidateSources'].items():assert sha(ROOT/relative)==expected,relative
    for relative,expected in proof['artifacts'].items():assert sha(REPORT.parent/relative)==expected,relative
    for absolute,expected in proof['inputs'].items():assert sha(Path(absolute))==expected,absolute
    files=[p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and not p.is_relative_to(OUT)]
    inventory={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in files}
    packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRoadmapAccepted':False,
            'scope':'Exact original96 geometry assertions and7pixel stages plus2 cleanup checks, current owning tuple; actual native execution pending',
            'preflightReport':str(REPORT),'preflightReportSHA256':sha(REPORT),'files':inventory}
    (ROOT/'qa/held-source-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
    result.update(passed=True,files=len(files))
except Exception as error:result['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'report':str(OUT/'report.json'),**result}));raise SystemExit(not result['passed'])
