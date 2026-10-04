"""Exact named model cases plus invariant traces; protected launcher required."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir();shutil.copy2(ROOT/'spec/recovery.qnt',OUT/'recovery.qnt')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(Path(__file__),OUT/'model.py')
report={'passed':False,'scope':'Abstract one-axis integer feasibility and retained scope/input/Unknown gates;100 is an unbounded sentinel for bounded targets. Named cases give semantics; nonnegative mutation invariant is only a trace sanity check. C++ tests cover both axes/nonfinite doubles. No automatic production refinement or native acceptance.','sourceSHA256':sha(ROOT/'spec/recovery.qnt'),'commands':[]}
def run(name,args):
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint',*args]
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'command':command,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr or p.stdout
try:
 run('version',['--version'])
 run('typecheck',['typecheck','recovery.qnt'])
 run('named',['test','recovery.qnt','--backend=typescript','--match=^(minimumOnlyTest|minimumAboveWorkareaTest|finiteMaximumBelowTest|finiteMaximumEqualTest|fixedAxisTest|malformedBoundTest|rawLayoutConflictTest|changedOriginalTest|inputBlockedTest|staleScopeTest|unknownBarrierTest)$','--out-itf=named-{test}-{seq}.itf.json','--seed=170024','--max-samples=1'])
 assert len(list(OUT.glob('named-*.itf.json')))==11
 run('invariants',['run','recovery.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=170025','--out-itf=sample-{seq}.itf.json'])
 mutant=(OUT/'recovery.qnt').read_text().replace('lower<=s.target and ','')
 (OUT/'unsafe.qnt').write_text(mutant)
 command=['/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint','test','unsafe.qnt','--backend=typescript','--match=^minimumAboveWorkareaTest$','--max-samples=1','--seed=170024']
 p=subprocess.run(command,cwd=OUT,capture_output=True,text=True,timeout=180);(OUT/'unsafe.stdout').write_text(p.stdout);(OUT/'unsafe.stderr').write_text(p.stderr)
 report['unsafeLowerBound']={'command':command,'exitCode':p.returncode,'detected':p.returncode!=0}
 assert p.returncode!=0,'Unsafe implicit keyboard-click fallback was not detected'
 report.update(passed=True,namedScenarios=11,invariantSamples=1000,maxSteps=40)
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
