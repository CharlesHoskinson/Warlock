"""quint-llm-kit UI-019 orphan placement and actual coordinate helper; native/physical acceptance separate."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
assert sys.argv[1:] in ([],['--init']);initial=bool(sys.argv[1:])
out=root/'qa/runs'/('output-placement-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=dict(passed=False,scope=__doc__,nativeAcceptance=False,protectedScope=scope,commands=[])
def run(name,args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=180)
 (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append(dict(name=name,command=list(map(str,args)),exitCode=p.returncode))
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:]+p.stdout.decode(errors='replace')[-1000:])
 return p.stdout.decode()
try:
 model=root/'qa/output-placement.qnt';tests=root/'qa/output-placement_test.qnt'
 r['inputs']={str(p.relative_to(root)):sha(p) for p in (model,tests)}
 run('typecheck',['quint','typecheck',model])
 run('init',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=86000'])
 if not initial:
  run('named',['quint','test',tests,'--backend=typescript','--match=Test$','--max-samples=1','--seed=86001'])
  witnesses=run('witnesses',['quint','run',model,'--backend=typescript','--witnesses','recovered','onFallback','--max-samples=1000','--max-steps=20','--seed=86002'])
  r['witnessCounts']={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',witnesses)}
  assert all(r['witnessCounts'].get(n,0)>0 for n in ('recovered','onFallback'))
  run('safety',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=86003'])
  header=root/'native/core/OrphanedPlacement.hpp';r['inputs'][str(header.relative_to(root))]=sha(header)
  test=out/'coordinates.cpp';test.write_text('''#include "OrphanedPlacement.hpp"
#include <cassert>
#include <limits>
int main(){using WarlockPlacement::orphanedCoordinate;
assert(orphanedCoordinate(40,1920,1920)==1960);
assert(orphanedCoordinate(-40,1920,1920)==3800);
assert(orphanedCoordinate(-40,-800,800)==-40);
assert(orphanedCoordinate(-1600,-800,800)==-800);
assert(orphanedCoordinate(800,0,800)==0);
assert(orphanedCoordinate(40,1920,0)==1920);
assert(orphanedCoordinate(40,1920,-1)==1920);
assert(orphanedCoordinate(40.5,1920,800)==1960.5);
assert(orphanedCoordinate(-0.5,-800,800)==-0.5);
assert(orphanedCoordinate(-1e-20,1920,800)==1920);
assert(orphanedCoordinate(std::numeric_limits<double>::infinity(),1920,800)==1920);
for(int x=-4000;x<=4000;++x){double p=orphanedCoordinate(x,1920,800);assert(p>=1920&&p<2720);}
}''')
  run('helper-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(header.parent),test,'-o',out/'coordinates'])
  run('helper-tests',[out/'coordinates'])
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['passed'],report=str(out/'report.json'),error=r.get('error'))));raise SystemExit(not r['passed'])
