import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
p=REPO/'implementation/elm-geometry-coordinate-authority-v406/qa/build-1791125085822287165/inputs/candidate/ProspectiveGeometry.hpp';h=hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();(out/'ProspectiveGeometry.hpp').write_bytes(p.read_bytes())
code=r'''#include "ProspectiveGeometry.hpp"
int main(){using namespace Elm::ProspectiveGeometry;const double top=std::numeric_limits<double>::max();
Input i{Operation::Maximize,{0,0,128,180},{},{},{0,0},1,{{128,0},{0,0}},{{1.,1.},{128.,top}}};
auto p=project(i);if(!p || p->configure.x!=128)return 1;
i.logical={0,0,800,180};if(project(i))return 2;
i.raw={{64,0},{0,0}};i.layout={{1.,1.},{top,top}};if(!project(i))return 3;
}'''
(out/'audit.cpp').write_text(code)
r={'passed':False,'scope':'Actual captured helper diagnostics; fixed-effective-axis admission is a blocker, not production acceptance','input':str(p),'inputSHA256':h,'checks':['effective fixed width accepted counterexample','upper bound still blocks oversize','feasible lower-bound case accepted']}
try:
 c=subprocess.run(['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror',str(out/'audit.cpp'),'-lhyprutils','-o',str(out/'audit')],capture_output=True,timeout=30);(out/'compile.stderr').write_bytes(c.stderr);assert c.returncode==0,c.stderr.decode()
 c=subprocess.run([str(out/'audit')],capture_output=True,timeout=5);assert c.returncode==0,c.returncode
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(out/'report.json');raise SystemExit(not r['passed'])
