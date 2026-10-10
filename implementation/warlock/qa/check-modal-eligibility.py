"""quint-llm-kit sampled modal topology/eligibility/draft model; no native acceptance."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1];model=root/'qa/modal-eligibility.qnt'
out=root/'qa/runs'/('modal-eligibility-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
witnesses=['eligibleModalReached','nestedModalReached','blockedModalRefused','noFocusModalRefused','unrelatedDraftPreserved']
r={'passed':False,'scope':__doc__,'protectedScope':scope,'nativeAcceptance':False,'inputs':{str(p.relative_to(root)):sha(p) for p in [model,model.with_name('modal-eligibility_test.qnt'),root/'native/core/ModalRecipient.hpp']},'commands':[]}
try:
 for name,args in [('typecheck',['typecheck']),('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79801']),('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=1000','--max-steps=40','--seed=79802']),('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=40','--seed=79803'])]:
  cmd=['quint',args[0],str(model.with_name('modal-eligibility_test.qnt') if name=='named' else model),*args[1:]];p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',p.stdout)};assert all(counts.get(n,0)>0 for n in witnesses),p.stdout;r['witnessCounts']=counts
 r['passed']=True
except Exception as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':(r.get('error') or '')[:400]}));raise SystemExit(not r['passed'])
