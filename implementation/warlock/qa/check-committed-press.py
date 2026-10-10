"""Quint kit scoped press admission; native delivery is a separate oracle."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
model=root/'qa/committed-press.qnt'
out=root/'qa/runs'/('committed-press-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
witnesses=['lowerReceived','noHitSuppressed','releaseAfterShape','suppressedRelease']
report={'passed':False,'scope':'Ordinary MAX button admission and release lifecycle, two abstract roots/one button. Admitted eligible refocus assumed; no native timing, grabs/layers/lock/constraints, pixels, transforms, ABI or presentation acceptance.','nativeAcceptance':False,'protectedScope':scope,'inputs':{p.name:sha(p) for p in [model,model.with_name('committed-press_test.qnt')]},'commands':[]}
try:
 for name,args in [
  ('typecheck',['typecheck']),
  ('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79401']),
  ('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=1000','--max-steps=30','--seed=79402']),
  ('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79403'])]:
  command=['quint',args[0],str(model.with_name('committed-press_test.qnt') if name=='named' else model),*args[1:]]
  p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'name':name,'command':command,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(lowerReceived|noHitSuppressed|releaseAfterShape|suppressedRelease) was witnessed in (\d+) trace',p.stdout)}
   assert len(counts)==len(witnesses) and all(counts.values()),p.stdout
   report['witnessCounts']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
