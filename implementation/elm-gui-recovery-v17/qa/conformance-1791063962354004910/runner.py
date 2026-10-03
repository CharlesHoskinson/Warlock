"""Replay preserved actual Quint journals against compiled pure Shell update."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('conformance-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model_path=sorted((ROOT/'qa').glob('model-*/report.json'))[-1];model=json.loads(model_path.read_text());assert model['passed'] and model['sourceSHA256']==sha(ROOT/'spec/recovery.qnt')
build_path=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];build=json.loads(build_path.read_text());assert build['passed']
for rel,digest in build['inputs'].items():assert sha(ROOT/rel)==digest,rel
shutil.copy2(__file__,OUT/'runner.py');shutil.copy2(ROOT/'qa/conformance.cjs',OUT/'conformance.cjs')
command=['node',str(OUT/'conformance.cjs'),str(build_path.parent/'shell.js'),str(model_path.parent),str(OUT/'replay-report.json')]
p=subprocess.run(command,capture_output=True,text=True,timeout=20);(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
report={'passed':False,'command':command,'exitCode':p.returncode,'modelReportSHA256':sha(model_path),'buildReportSHA256':sha(build_path),'compiledShellSHA256':sha(build_path.parent/'shell.js')}
if p.returncode==0 and (OUT/'replay-report.json').exists():
 replay=json.loads((OUT/'replay-report.json').read_text());report.update(passed=replay['passed'],traces=replay['traces'],transitions=replay['transitions'])
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(not report['passed'])
