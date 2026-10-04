"""Record type-only validation; approval is required before model logic."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('sketch-'+str(time.time_ns()));OUT.mkdir()
s=ROOT/'spec/geometry-sketch.qnt';q=shutil.which('quint');assert q
shutil.copy2(s,OUT/'geometry-sketch.qnt')
p=subprocess.run([q,'typecheck',str(s)],capture_output=True,text=True,timeout=60)
(OUT/'stdout.log').write_text(p.stdout);(OUT/'stderr.log').write_text(p.stderr)
r={'passed':p.returncode==0,'scope':'Types/declarations only; no executed transitions or safety proof','modelLogicApproved':False,'command':[q,'typecheck',str(s)],'exitCode':p.returncode,'source':str(s),'sourceSHA256':hashlib.sha256(s.read_bytes()).hexdigest()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json')}));raise SystemExit(p.returncode)
