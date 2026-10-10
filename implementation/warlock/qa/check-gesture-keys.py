"""quint-llm-kit sampled captured gesture key/cancel/release contract; native keys/identity/AT separate."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1];model=root/'qa/gesture-keys.qnt'
out=root/'qa/runs'/('gesture-keys-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();witnesses=['began','ordinaryRetains','releaseKeyRetains','chordRetains','cancelled','released']
r={'passed':False,'scope':__doc__,'nativeAcceptance':False,'protectedScope':scope,'inputs':{str(p.relative_to(root)):sha(p) for p in [model,model.with_name('gesture-keys_test.qnt'),root/'native/core/GestureKeyPolicy.hpp',root/'native/core/KeybindManager.cpp']},'commands':[]}
try:
 for name,args in [('typecheck',['typecheck']),('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=79921']),('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=1000','--max-steps=30','--seed=79922']),('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=79923'])]:
  cmd=['quint',args[0],str(model.with_name('gesture-keys_test.qnt') if name=='named' else model),*args[1:]];p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',p.stdout)};assert all(counts.get(n,0)>0 for n in witnesses),p.stdout;r['witnessCounts']=counts
 r['passed']=True
except Exception as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':(r.get('error') or '')[:400]}));raise SystemExit(not r['passed'])
