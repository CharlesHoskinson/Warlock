"""Exact named model cases plus invariant traces; protected launcher required."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir();shutil.copy2(ROOT/'spec/view.qnt',OUT/'view.qnt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(Path(__file__),OUT/'model.py')
report={'passed':False,'scope':'Abstract launcher view/focus retirement; Browser DOM scheduling, AT/IME and native refinement separate','sourceSHA256':sha(ROOT/'spec/view.qnt'),'commands':[]}
def run(name,args):
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint',*args]
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
try:
 run('version',['--version'])
 run('typecheck',['typecheck','view.qnt'])
 run('named',['test','view.qnt','--backend=typescript','--match=^(openingTest|firstEntryTest|closeTest|staleCloseTest|staleRefreshTest|closedReplyTest|receiptTest|pendingRefreshTest)$','--out-itf=named-{test}-{seq}.itf.json','--seed=170016','--max-samples=1'])
 assert len(list(OUT.glob('named-*.itf.json')))==8
 run('invariants',['run','view.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=170017','--out-itf=sample-{seq}.itf.json'])
 report.update(passed=True,namedScenarios=8,invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
