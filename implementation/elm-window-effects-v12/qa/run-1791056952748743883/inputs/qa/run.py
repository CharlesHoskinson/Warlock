"""Protected append-only compiled Elm transaction and Quint qualification."""
import datetime,hashlib,json,os,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1),'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('run-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
files=[ROOT/'elm.json',*sorted((ROOT/'src').glob('*.elm')),*sorted((ROOT/'qa').glob('*.py')),*sorted((ROOT/'qa').glob('*.cjs')),*sorted((ROOT/'spec').glob('*.qnt'))]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
report={'passed':False,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputs':inputs,'scope':'Compiled pure Elm first-class minimize/restore intent/receipt prototype; no native effects, first-class native minimized state, complete policy or product acceptance','commands':[]}
def run(name,command,env=None,cwd=INPUT):
 proc=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(proc.stdout);(OUT/(name+'.stderr')).write_text(proc.stderr)
 report['commands'].append({'name':name,'command':command,'exitCode':proc.returncode});print(name,proc.returncode,flush=True)
 assert proc.returncode==0,proc.stderr or proc.stdout
try:
 run('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(OUT/'replay.js')])
 run('elm-effects',['node','qa/check.cjs'],dict(os.environ,ELM_REPLAY=str(OUT/'replay.js'),ELM_REPORT=str(OUT/'elm-report.json')))
 quint='/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
 run('quint-version',[quint,'--version']);run('quint-typecheck',[quint,'typecheck','spec/effects.qnt'])
 traces=OUT/'traces';traces.mkdir()
 run('quint-tests',[quint,'test','spec/effects.qnt','--match','Test$','--seed','121201','--max-samples','1','--out-itf',str(traces/'named-{test}-{seq}.itf.json')])
 run('quint-invariants',[quint,'run','spec/effects.qnt','--invariants','safety','--seed','121202','--max-samples','1000','--max-steps','40','--out-itf',str(traces/'sample-{seq}.itf.json')])
 run('quint-elm-conformance',['node','qa/conformance.cjs'],dict(os.environ,ELM_REPLAY=str(OUT/'replay.js'),QUINT_TRACES=str(traces),CONFORMANCE_REPORT=str(OUT/'conformance-report.json')))
 report['elmChecks']=json.loads((OUT/'elm-report.json').read_text())['checks'];report['quintNamedTests']=9;report['quintInvariantSamples']=1000;report['quintMaxSteps']=40;report['conformance']={k:v for k,v in json.loads((OUT/'conformance-report.json').read_text()).items() if k!='receipts'};report['passed']=True
except Exception as error:report['error']=str(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
