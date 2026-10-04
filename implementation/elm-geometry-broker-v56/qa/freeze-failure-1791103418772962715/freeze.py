"""Append-only held broker source/evidence manifest; protected CPU only."""
import hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
PASS=ROOT/'qa/routing-1791103266064226897/report.json';FAIL=ROOT/'qa/routing-1791103252549791516/report.json'
TARGET=ROOT/'qa/held-source-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
assert not TARGET.exists(),'Never overwrite held source evidence'
passed=json.loads(PASS.read_text());assert passed['passed'] is True and passed['nativeAcceptance'] is False and len(passed['checks'])==109 and all(x['passed'] is True for x in passed['checks'])
for rel,wanted in passed['inputs'].items():assert sha(ROOT/rel)==sha(PASS.parent/'inputs'/rel)==wanted,rel
failed=json.loads(FAIL.read_text());assert failed['passed'] is False and failed['nativeAcceptance'] is False
for path,report in [(PASS,passed),(FAIL,failed)]:
 for rel,wanted in report['artifacts'].items():assert sha(path.parent/rel)==wanted,(path,rel)
 for rel,wanted in report['inputs'].items():assert sha(path.parent/'inputs'/rel)==wanted,(path,rel)
lineage=json.loads((ROOT/'source-lineage.json').read_text())
for entry in lineage:assert sha(REPO/entry['source'])==sha(ROOT/entry['target'])==entry['sha256'],entry
files={}
for p in sorted(ROOT.rglob('*')):
 if p==TARGET:continue
 assert not p.is_symlink(),'Held broker source must not contain symlinks: '+str(p)
 if p.is_file():files[str(p.relative_to(ROOT))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'nativeAcceptance':False,'scope':'Actual imported broker routing/framing with real copied validators and synthetic native transport; no socket/process authentication or native/Elm end-to-end acceptance','routingReport':str(PASS.relative_to(ROOT)),'routingReportSHA256':sha(PASS),'routingChecks':109,'retainedFailureReport':str(FAIL.relative_to(ROOT)),'retainedFailureReportSHA256':sha(FAIL),'coalescedLargeFramesQualified':False,'unsupportedGeometryFallbackQualified':False,'files':files}
with TARGET.open('x') as f:f.write(json.dumps(packet,indent=2)+'\n')
TARGET.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(TARGET),'manifestSHA256':sha(TARGET),'files':len(files),'routingReportSHA256':sha(PASS),'sourceHashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'adapter').glob('*.py'))}}),flush=True)
