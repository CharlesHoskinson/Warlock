"""quint-llm-kit UI-019 delayed shortcut generation: sampled model, not native acceptance."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
model=root/'qa/shortcut-generation.qnt';initial=sys.argv[1:]==['--init']
assert initial or not sys.argv[1:]
out=root/'qa/runs'/('shortcut-generation-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
witnesses=['captured','nativeRetired','hostReplaced','reconciled','staleConsumed','freshOpened']
r={'passed':False,'nativeAcceptance':False,'scope':__doc__,'protectedScope':scope,'commands':[],
 'inputs':{str(p.relative_to(root)):sha(p) for p in [model,model.with_name('shortcut-generation_test.qnt')] if p.exists()}}
try:
 checks=[('typecheck',['typecheck']),('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=87001']),('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=1000','--max-steps=20','--seed=87002']),('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=87003'])]
 if initial:checks=[('typecheck',['typecheck']),('initial',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=87000'])]
 for name,args in checks:
  cmd=['quint',args[0],str(model.with_name('shortcut-generation_test.qnt') if name=='named' else model),*args[1:]]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  for stream in ['stdout','stderr']:(out/(name+'.'+stream)).write_text(getattr(p,stream))
  r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',p.stdout)}
   assert all(counts.get(n,0)>0 for n in witnesses),p.stdout;r['witnessCounts']=counts
 r['passed']=True
except Exception as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':(r.get('error') or '')[:400]}));raise SystemExit(not r['passed'])
