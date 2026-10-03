"""Exact named model cases plus invariant traces; protected launcher required."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir();shutil.copy2(ROOT/'spec/taskbar.qnt',OUT/'taskbar.qnt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Abstract taskbar decisions and displayed-scope guards; native refinement and full UX remain separate','sourceSHA256':sha(ROOT/'spec/taskbar.qnt'),'commands':[]}
def run(name,args):
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint',*args]
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
try:
 run('version',['--version'])
 run('typecheck',['typecheck','taskbar.qnt'])
 run('named',['test','taskbar.qnt','--backend=typescript','--match=^(zeroPinnedTest|zeroUnpinnedTest|inactiveTest|activeTest|minimizedTest|unavailableTest|multipleTest|pickerActiveTest|pickerMinimizedTest|staleRevisionTest|staleSessionTest|pendingTest)$','--out-itf=named-{test}-{seq}.itf.json','--seed=170016','--max-samples=1'])
 assert len(list(OUT.glob('named-*.itf.json')))==12
 run('invariants',['run','taskbar.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=170017','--out-itf=sample-{seq}.itf.json'])
 report.update(passed=True,namedScenarios=12,invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
