"""Protected, append-only CPU qualification of the actual compiled Elm observer."""
import datetime,hashlib,json,os,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('run-'+str(time.time_ns()));OUT.mkdir()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
records=[]
inputs={}
for p in [ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),*sorted((ROOT/'qa').glob('*.py')),*sorted((ROOT/'qa').glob('*.cjs')),*sorted((ROOT/'spec').rglob('*.qnt'))]:
 if not p.is_file():continue
 relative=p.relative_to(ROOT);dest=OUT/'inputs'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 inputs[str(relative)]=hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,command,env=None):
 p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 records.append({'name':name,'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
report={'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'CPU-only typed observer; no native authentication, coherent snapshot or GPU claim','passed':False,'inputs':inputs}
try:
 run('syntax',['node','--check','qa/check.cjs'])
 run('elm-version',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','--version'])
 run('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(OUT/'replay.js')])
 env=dict(os.environ,ELM_REPLAY=str(OUT/'replay.js'),ELM_REPORT=str(OUT/'elm-report.json'),ELM_TRANSCRIPTS=str(OUT/'transcripts.json'))
 run('replay',['node','qa/check.cjs'],env)

 quint='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
 trace=OUT/'traces';trace.mkdir()
 run('quint-version',[quint,'--version'])
 run('quint-typecheck',[quint,'typecheck','spec/observer.qnt'])
 run('quint-tests',[quint,'test','spec/observer.qnt','--match','Test$','--seed','610304','--max-samples','1','--out-itf',str(trace/'named-{test}-{seq}.itf.json')])
 run('quint-invariants',[quint,'run','spec/observer.qnt','--invariants','safety','--seed','610305','--max-samples','1000','--max-steps','40','--out-itf',str(trace/'sample-{seq}.itf.json')])
 env.update(QUINT_TRACES=str(trace),CONFORMANCE_REPORT=str(OUT/'conformance-report.json'))
 run('quint-elm-conformance',['node','qa/conformance.cjs'],env)
 report['passed']=json.loads((OUT/'elm-report.json').read_text())['passed'] and json.loads((OUT/'conformance-report.json').read_text())['passed']
except Exception as error:report['error']=str(error)
report['commands']=records
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'),flush=True)
raise SystemExit(not report['passed'])
