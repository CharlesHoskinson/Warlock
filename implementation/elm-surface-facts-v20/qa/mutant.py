"""Check capture/history oracle rejects reconstructing retained facts at query."""
import hashlib,json,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mutant-'+str(time.time_ns()));OUT.mkdir()
source=ROOT/'spec/facts.qnt';text=source.read_text()
old="action query=s'=s";assert text.count(old)==1
(OUT/'unsafe.qnt').write_text(text.replace(old,"action query=s'={...s,stored:s.live}"))
command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint','test','unsafe.qnt','--match=^resizePreservesHeldTest$','--max-samples=1','--seed=200001']
p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180)
(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
report={'passed':p.returncode!=0 and 'assert' in (p.stdout+p.stderr).lower(),'scope':'Abstract retained geometry query mutation only; no native mutation equivalence claimed','command':command,'exitCode':p.returncode,'originalSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'unsafeSHA256':hashlib.sha256((OUT/'unsafe.qnt').read_bytes()).hexdigest()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(not report['passed'])
