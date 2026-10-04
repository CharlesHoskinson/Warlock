import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
p=REPO/'implementation/elm-geometry-size-policy-v395/candidate/SizeBounds.hpp'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
h=sha(p);out=ROOT/'qa'/('review-'+str(time.time_ns()));out.mkdir();(out/'SizeBounds.hpp').write_bytes(p.read_bytes())
code=r'''#include "SizeBounds.hpp"
int main(){using namespace Elm::SizeBounds; double nan=std::numeric_limits<double>::quiet_NaN(),top=std::numeric_limits<double>::max();
auto good=derive({{128,64},{0,0}},{});if(!good || !good->admits({800,552}))return 1;
auto tiny=derive({{0,0},{1,0}},{std::nullopt,Size{top,top}});if(!tiny || tiny->admits({800,552}))return 2;
if(derive({{0,0},{0,0}},{Size{nan,0},std::nullopt}))return 3;
auto unsafe=intersect(0,0,nan,top);if(!unsafe || !unsafe->admits(800))return 4;
}'''
(out/'audit.cpp').write_text(code)
r={'passed':False,'scope':'Pure policy entry-point review and exposed-helper diagnostic only; no native/model acceptance','input':str(p),'inputSHA256':h,'checks':['same-space minimum-only admits','raw tiny maximum remains restrictive','derive rejects NaN layout minimum','direct intersect diagnostic admits malformed NaN layout minimum']}
try:
 c=subprocess.run(['/usr/bin/c++','-std=c++20','-Wall','-Wextra','-Werror',str(out/'audit.cpp'),'-o',str(out/'audit')],capture_output=True,timeout=30);(out/'compile.stderr').write_bytes(c.stderr);assert c.returncode==0
 c=subprocess.run([str(out/'audit')],capture_output=True,timeout=5);assert c.returncode==0,c.returncode
 assert sha(p)==h and sha(out/'SizeBounds.hpp')==h
 r['passed']=True
except Exception as e:r['error']=repr(e)
(out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(out/'report.json');raise SystemExit(not r['passed'])
