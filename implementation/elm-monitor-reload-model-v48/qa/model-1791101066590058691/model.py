import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('model-'+str(time.time_ns()));OUT.mkdir()
shutil.copy2(ROOT/'spec/reload.qnt',OUT/'reload.qnt');shutil.copy2(__file__,OUT/'model.py')
names=['coalescedRequestsTest','noParentFrameNeededTest','renderWinsNoDuplicateTest','reentrantRequestSurvivesTest','renderReentrancySurvivesTest','stoppedTaskCannotApplyTest']
r={'passed':False,'nativeAcceptance':False,'scope':'Bounded serialized reload dispatch abstraction; no actual monitor application proof','commands':[]}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(name,args,expected=0):
 cmd=[shutil.which('quint'),*args];p=subprocess.run(cmd,cwd=OUT,capture_output=True,text=True,timeout=180)
 (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 r['commands'].append({'command':cmd,'exitCode':p.returncode,'expected':expected});print(name,p.returncode,flush=True);assert p.returncode==expected,p.stderr or p.stdout
try:
 run('typecheck',['typecheck','reload.qnt'])
 run('named',['test','reload.qnt','--backend=typescript','--match=^('+'|'.join(names)+')$','--max-samples=1','--seed=48001','--out-itf=named-{test}-{seq}.itf.json'])
 assert len(list(OUT.glob('named-*.itf.json')))==6
 run('invariants',['run','reload.qnt','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=48002'])
 text=(OUT/'reload.qnt').read_text();before='{...s, applied:s.captured, running:false}';assert text.count(before)==1
 (OUT/'clear-late.qnt').write_text(text.replace(before,'{...s, applied:s.captured, running:false, pending:false}'))
 run('mutation-typecheck',['typecheck','clear-late.qnt'])
 run('mutation-rejected',['test','clear-late.qnt','--backend=typescript','--match=^reentrantRequestSurvivesTest$','--max-samples=1','--seed=48003'],expected=1)
 r.update(passed=True,namedScenarios=names,invariantSamples=1000,maxSteps=40,lateClearMutationRejected=True,sourceSHA256=sha(ROOT/'spec/reload.qnt'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
