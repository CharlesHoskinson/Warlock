"""quint-llm-kit UI-019 usable-area recovery and compiled helper; native/hardware acceptance separate."""
import hashlib,json,pathlib,re,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1]
assert sys.argv[1:] in ([],['--init']);initial=bool(sys.argv[1:])
out=root/'qa/runs'/('reachable-placement-'+str(time.time_ns()));out.mkdir()
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
r=dict(passed=False,scope=__doc__,nativeAcceptance=False,protectedScope=scope,commands=[])
def run(name,args):
 p=subprocess.run(list(map(str,args)),capture_output=True,timeout=180)
 (out/(name+'.stdout')).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
 r['commands'].append(dict(name=name,command=list(map(str,args)),exitCode=p.returncode))
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-2000:]+p.stdout.decode(errors='replace')[-1000:])
 return p.stdout.decode()
try:
 model=root/'qa/reachable-placement.qnt';tests=root/'qa/reachable-placement_test.qnt'
 r['inputs']={str(p.relative_to(root)):sha(p) for p in [model,tests] if p.exists()}
 run('typecheck',['quint','typecheck',model])
 run('init',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1','--max-steps=1','--seed=88000'])
 if not initial:
  run('named',['quint','test',tests,'--backend=typescript','--match=Test$','--max-samples=1','--seed=88001'])
  witnesses=run('witnesses',['quint','run',model,'--backend=typescript','--witnesses','shifted','recovered','roundTrip','unchanged','--max-samples=1000','--max-steps=20','--seed=88002'])
  r['witnessCounts']={n:int(c) for n,c in re.findall(r'(\w+) was witnessed in (\d+) trace',witnesses)}
  assert all(r['witnessCounts'].get(n,0)>0 for n in ('shifted','recovered','roundTrip','unchanged'))
  run('safety',['quint','run',model,'--backend=typescript','--invariants=safety','--max-samples=1000','--max-steps=20','--seed=88003'])
  header=root/'native/core/ReachablePlacement.hpp';r['inputs'][str(header.relative_to(root))]=sha(header)
  test=out/'coordinates.cpp';test.write_text('''#include "ReachablePlacement.hpp"
#include <cassert>
#include <cmath>
#include <limits>
int main(){using WarlockPlacement::reachableCoordinate;
assert(reachableCoordinate(-360,-388,376,108)==-360);
assert(reachableCoordinate(30,-140,128,440)==-44);
assert(reachableCoordinate(230,60,528,440)==230);
assert(reachableCoordinate(-500,-388,376,108)==-388);
assert(reachableCoordinate(0,0,10,440)==0);
assert(reachableCoordinate(5,0,10,2)==5);
assert(reachableCoordinate(30.5,-140.5,128.5,440)==-44);
assert(reachableCoordinate(30,0,0,440)==30);
assert(reachableCoordinate(30,0,-1,440)==30);
assert(std::isnan(reachableCoordinate(std::numeric_limits<double>::quiet_NaN(),0,200,440)));
for(int extent=1;extent<=200;extent++)for(int x=-800;x<=800;x++){
 double c=reachableCoordinate(x,-388,extent,108);assert(c>=-388&&c+std::min({108.,32.,double(extent)})<=-388+extent);
 assert(reachableCoordinate(c,-388,extent,108)==c);
}
}''')
  run('helper-compile',['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-I'+str(header.parent),test,'-o',out/'coordinates'])
  run('helper-tests',[out/'coordinates'])
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=r['passed'],report=str(out/'report.json'),error=r.get('error'))));raise SystemExit(not r['passed'])
