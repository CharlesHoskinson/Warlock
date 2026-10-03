"""Freeze compiled CPU transaction evidence, never native acceptance."""
import datetime,hashlib,json,resource
from pathlib import Path
ROOT=Path(__file__).resolve().parent
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report_path=sorted((ROOT/'qa').glob('run-*/report.json'))[-1]
report=json.loads(report_path.read_text());assert report['passed']
for relative,digest in report['inputs'].items():assert sha(ROOT/relative)==digest,relative
for relative,digest in report['artifacts'].items():assert sha(report_path.parent/relative)==digest,relative
assert report['compiledUnsafeMutantsDetected']==2
assert report['quintNamedTests']==9 and report['quintInvariantSamples']==1000
assert report['conformance']['passed'] and report['conformance']['traces']==10
manifest={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,
'scope':report['scope'],'report':str(report_path.relative_to(ROOT)),'reportSHA256':sha(report_path),
'elmChecks':report['elmChecks'],'quintNamedTests':9,'quintInvariantSamples':1000,
'conformance':report['conformance'],'compiledUnsafeMutantsDetected':2,
'completedRequirementIds':[],
'files':{str(p.relative_to(ROOT)):sha(p) for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='slice-manifest.json'}}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))
