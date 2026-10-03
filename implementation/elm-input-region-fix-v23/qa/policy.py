"""Replay the unchanged scene policy abstraction; native geometry is separate."""
import hashlib,json,re,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1), 'Use protected qa_run.py'
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parent.parent/'docs/elm-roadmap/prototypes/quint'
OUT=ROOT/'qa'/('policy-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for name in ('scene_model.qnt','scene_tests.qnt'):
 shutil.copy2(SOURCE/name,OUT/name)
names=re.findall(r'run (\w+) =',(OUT/'scene_tests.qnt').read_text())
report={'passed':False,'scope':'Unchanged abstract scene eligibility policy only; not input-coordinate refinement or exhaustive verification',
        'inputs':{n:sha(OUT/n) for n in ('scene_model.qnt','scene_tests.qnt')},'selectedNames':names,'commands':[]}
def run(name,args):
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint',*args]
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True)
 assert p.returncode==0,p.stderr or p.stdout
try:
 run('typecheck',['typecheck','scene_tests.qnt'])
 run('named',['test','scene_tests.qnt','--main=scene_tests','--match=^('+'|'.join(names)+')$','--backend=typescript','--seed=610103','--max-samples=1','--out-itf=named-{test}-{seq}.itf.json'])
 assert len(list(OUT.glob('named-*.itf.json')))==len(names)
 run('invariants',['run','scene_model.qnt','--main=scene','--invariants','noExcludedPaint','noExcludedInput','focusSafe','proxyInert','leaseValid','proxyValid','--seed=610104','--max-samples=1000','--max-steps=40','--backend=typescript'])
 report.update(passed=True,namedScenarios=len(names),invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json',flush=True)
raise SystemExit(not report['passed'])
