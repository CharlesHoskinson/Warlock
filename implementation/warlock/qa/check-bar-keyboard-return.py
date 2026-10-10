"""Sampled exact GTK replay return; real GTK key delivery is verified separately."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
model=root/'qa/bar-keyboard-return.qnt'
out=root/'qa/runs'/('bar-keyboard-return-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
report={'passed':False,'scope':'Exact original GTK replay signature/receiver abstraction; native GTK/WebKit timing, physical input, clock wrap and ABI excluded','nativeAcceptance':False,'protectedScope':scope,'inputs':{p.name:sha(p) for p in [model,model.with_name('bar-keyboard-return_test.qnt')]},'commands':[]}
try:
 for name,args in [
  ('typecheck',['typecheck']),
  ('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79211']),
  ('witnesses',['run','--backend=typescript','--witnesses','repeatedReturn','originalReplayCompleted','foreignReplayRefused','--max-samples=1000','--max-steps=30','--seed=79212']),
  ('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79213'])]:
  command=['quint',args[0],str(model.with_name('bar-keyboard-return_test.qnt') if name=='named' else model),*args[1:]]
  p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'name':name,'command':command,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(repeatedReturn|originalReplayCompleted|foreignReplayRefused) was witnessed in (\d+) trace',p.stdout)}
   assert len(counts)==3 and all(counts.values()),p.stdout
   report['witnessCounts']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
