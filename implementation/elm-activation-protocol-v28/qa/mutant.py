"""Show model detects declaring activation committed despite wrong seat focus."""
import hashlib,json,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mutant-'+str(time.time_ns()));OUT.mkdir();source=ROOT/'spec/activation.qnt'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=source.read_text();needle='status:"Unknown",before:s.mutations';assert s.count(needle)==1
(OUT/'unsafe.qnt').write_text(s.replace(needle,'status:"Committed",before:s.mutations'))
command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint','test','unsafe.qnt','--match=^unknownSeatPostconditionTest$','--max-samples=1','--seed=280001']
p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180)
(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
report={'passed':p.returncode!=0 and 'assert' in (p.stdout+p.stderr).lower(),'scope':'Abstract wrong-seat receipt mutant only; no compiled native mutation equivalence claimed','command':command,'exitCode':p.returncode,'originalSHA256':sha(source),'unsafeSHA256':sha(OUT/'unsafe.qnt')}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(not report['passed'])
