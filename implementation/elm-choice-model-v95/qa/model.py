"""Exact named model cases plus invariant traces; protected launcher required."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir();shutil.copy2(ROOT/'spec/surfaces.qnt',OUT/'surfaces.qnt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(Path(__file__),OUT/'model.py')
report={'passed':False,'scope':'Deferred first choice after close: matching fresh projection, binding/output/root/application checks, cancellation and at-most-once dispatch. Abstract model; compiled Elm and native regression provide separate evidence.','sourceSHA256':sha(ROOT/'spec/surfaces.qnt'),'commands':[]}
def run(name,args):
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint',*args]
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
try:
 run('version',['--version'])
 run('typecheck',['typecheck','surfaces.qnt'])
 run('named',['test','surfaces.qnt','--backend=typescript','--match=^(closeBeforeDispatchTest|freshRevisionTest|duplicateTest|staleTest|retiredRootTest|changedApplicationTest|changedOutputTest|blockedTest|disconnectedTest|reboundTest)$','--out-itf=named-{test}-{seq}.itf.json','--seed=170016','--max-samples=1'])
 assert len(list(OUT.glob('named-*.itf.json')))==10
 run('invariants',['run','surfaces.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=170017','--out-itf=sample-{seq}.itf.json'])
 report.update(passed=True,namedScenarios=10,invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
