"""Protected incremental Quint LLM Kit registration model checks, no GUI claim."""
import hashlib,json,pathlib,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
model=root/'qa/shortcut-registration.qnt'
out=root/'qa/runs'/('shortcut-registration-'+str(time.time_ns()));out.mkdir(parents=True)
report={'passed':False,'scope':'Sampled singleton native owner/configuration model; filesystem, physical input, AT and ABI excluded','nativeAcceptance':False,'protectedScope':scope,'modelSHA256':hashlib.sha256(model.read_bytes()).hexdigest(),'commands':[]}
try:
 for name,args in [
  ('typecheck',['typecheck']),
  ('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79191']),
  ('witnesses',['run','--backend=typescript','--witnesses','defaultReady','keptAfterReload','alternateAfterReload','unknownAfterReload','--max-samples=1000','--max-steps=30','--seed=79192']),
  ('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79193'])]:
  command=['quint',args[0],str(model.with_name('shortcut-registration_test.qnt') if name=='named' else model),*args[1:]]
  p=subprocess.run(command,capture_output=True,text=True,timeout=180)
  (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
  report['commands'].append({'name':name,'command':command,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   import re
   counts={n:int(count) for n,count in re.findall(r'(defaultReady|keptAfterReload|alternateAfterReload|unknownAfterReload) was witnessed in (\d+) trace',p.stdout)}
   assert len(counts)==4 and all(counts.values()),p.stdout
   report['witnessCounts']=counts
 report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
