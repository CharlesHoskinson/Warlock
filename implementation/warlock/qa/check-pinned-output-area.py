"""quint-llm-kit UI-019 pinned usable-area recovery; sampled/named results are separate from native acceptance."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
assert sys.argv[1:] in ([],['--init']);initial=bool(sys.argv[1:])
out=root/'qa/runs'/('pinned-output-area-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=dict(passed=False,scope=__doc__,nativeAcceptance=False,protectedScope=scope,commands=[])
def run(name,args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=180)
 (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append(dict(name=name,command=list(map(str,args)),exitCode=p.returncode))
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:]+p.stdout.decode(errors='replace')[-1000:])
 return p.stdout.decode()
try:
 model=root/'qa/pinned-output-area.qnt';tests=root/'qa/pinned-output-area_test.qnt'
 r['inputs']={str(p.relative_to(root)):sha(p) for p in [model,tests,root/'qa/reachable-placement.qnt'] if p.exists()}
 run('typecheck',['quint','typecheck',model])
 run('init',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=89000'])
 if not initial:
  run('named',['quint','test',tests,'--backend=typescript','--match=Test$','--max-samples=1','--seed=89001'])
  witnesses=run('witnesses',['quint','run',model,'--backend=typescript','--witnesses','shifted','recovered','restored','unchanged','--max-samples=1000','--max-steps=20','--seed=89002'])
  r['witnessCounts']={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',witnesses)}
  assert all(r['witnessCounts'].get(n,0)>0 for n in ('shifted','recovered','restored','unchanged'))
  run('safety',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=89003'])
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['passed'],report=str(out/'report.json'),error=r.get('error'))));raise SystemExit(not r['passed'])
