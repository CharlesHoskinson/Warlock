"""Quint kit modal focus-only admission; actual graph/native delivery separate."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
model=root/'qa/modal-activation.qnt'
out=root/'qa/runs'/('modal-activation-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
witnesses=['modalFocused','nestedFocused','ambiguousRefused','ownerAfterRetirement']
report={'passed':False,'scope':'Ordinary MAX blocked-parent focus-only admission with abstract constraint cases; no native graph, timing, grabs/layers/lock, pixels, transforms, ABI, presentation or AT acceptance.','nativeAcceptance':False,'protectedScope':scope,'inputs':{p.name:sha(p) for p in [model,model.with_name('modal-activation_test.qnt')]},'commands':[]}
try:
 for name,args in [
  ('typecheck',['typecheck']),
  ('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79501']),
  ('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=10000','--max-steps=80','--seed=79502']),
  ('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79503'])]:
  command=['quint',args[0],str(model.with_name('modal-activation_test.qnt') if name=='named' else model),*args[1:]]
  p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'name':name,'command':command,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(modalFocused|nestedFocused|ambiguousRefused|ownerAfterRetirement) was witnessed in (\d+) trace',p.stdout)}
   assert len(counts)==len(witnesses) and all(counts.values()),p.stdout
   report['witnessCounts']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':(report.get('error') or '')[:400]}))
raise SystemExit(not report['passed'])
