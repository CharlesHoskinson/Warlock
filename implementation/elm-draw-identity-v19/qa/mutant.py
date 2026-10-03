"""Demonstrate identity model rejects omitted authority lifetime comparison."""
import hashlib,json,resource,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('mutant-'+str(time.time_ns()));OUT.mkdir();source=ROOT/'spec/identity.qnt';text=source.read_text()
old='s.heldId==s.current and s.heldAuthority==s.authority';assert old in text
(OUT/'unsafe.qnt').write_text(text.replace(old,'s.heldId==s.current'))
command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint','test','unsafe.qnt','--match=^authorityIdReuseRetiresHeldTest$','--max-samples=1','--seed=190001']
p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/'stdout').write_text(p.stdout);(OUT/'stderr').write_text(p.stderr)
report={'passed':p.returncode!=0 and 'assert' in (p.stdout+p.stderr).lower(),'scope':'Abstract model unsafe variant only; no compiled native mutation equivalence claimed','command':command,'exitCode':p.returncode,'originalSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'unsafeSHA256':hashlib.sha256((OUT/'unsafe.qnt').read_bytes()).hexdigest()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(not report['passed'])
