"""quint-llm-kit sampled popup/output retirement, fresh view identity and keyboard destination; internal FALLBACK suspension with atomic topology abstraction; native gates separate."""
import hashlib,json,pathlib,re,subprocess,sys,time
assert not sys.argv[1:] or sys.argv[1:]==['--init']
initial=bool(sys.argv[1:])
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1];model=root/'qa/output-retirement.qnt'
out=root/'qa/runs'/('output-retirement-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();witnesses=['keyboardRight','retiredPopup','replacementIsolated','allGone']
r={'passed':False,'scope':__doc__,'nativeAcceptance':False,'protectedScope':scope,'inputs':{str(p.relative_to(root)):sha(p) for p in [p for p in [model,model.with_name('output-retirement_test.qnt'),root/'native/authority.cpp',root/'native/shared-host.c',root/'src/OutputController.elm',root/'src/Shortcuts.elm',root/'src/Desktop.elm'] if p.exists()]},'commands':[]}
try:
 checks=[('typecheck',['typecheck']),('named',['test','--backend=typescript','--match=Test$','--max-samples=1','--seed=84001']),('witnesses',['run','--backend=typescript','--witnesses',*witnesses,'--max-samples=1000','--max-steps=30','--seed=84002']),('safety',['run','--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=30','--seed=84003'])]
 if initial:checks=[('typecheck',['typecheck']),('initial',['run','--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=84000'])]
 for name,args in checks:
  cmd=['quint',args[0],str(model.with_name('output-retirement_test.qnt') if name=='named' else model),*args[1:]];p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode})
  if p.returncode:raise RuntimeError(p.stderr or p.stdout)
  if name=='witnesses':
   counts={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',p.stdout)};assert all(counts.get(n,0)>0 for n in witnesses),p.stdout;r['witnessCounts']=counts
 r['passed']=True
except Exception as error:r['error']=repr(error)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'error':(r.get('error') or '')[:400]}));raise SystemExit(not r['passed'])
