"""Exact selected native-minimize policy model checks; not native equivalence."""
import datetime,hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Protected launcher required'
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir();shutil.copy2(ROOT/'spec/lifecycle.qnt',OUT/'lifecycle.qnt');shutil.copy2(__file__,OUT/'model.py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
quint='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
report={'passed':False,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Abstract family birth/retirement/ambiguous restore native-minimize policy only; no native/model refinement, pixels, AT, timing or whole product acceptance','inputs':{'spec/lifecycle.qnt':sha(ROOT/'spec/lifecycle.qnt'),'qa/lifecycle_model.py':sha(__file__)},'commands':[]}
try:
 for name,args in [('version',['--version']),('typecheck',['typecheck','lifecycle.qnt']),('tests',['test','lifecycle.qnt','--match','Test$','--seed','131301','--max-samples','1','--out-itf',str(OUT/'named-{test}-{seq}.itf.json')]),('invariants',['run','lifecycle.qnt','--invariants','safety','--seed','131302','--max-samples','1000','--max-steps','40','--out-itf',str(OUT/'sample-{seq}.itf.json')])]:
  p=subprocess.run([quint,*args],cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'command':[quint,*args],'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
 assert len(list(OUT.glob('named-*.itf.json')))==13
 report.update(passed=True,namedScenarios=13,invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=str(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
