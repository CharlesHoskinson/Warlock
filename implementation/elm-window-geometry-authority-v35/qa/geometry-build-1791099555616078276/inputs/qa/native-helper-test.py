"""Actual extracted geometry helpers; independent lifecycle/numeric oracles, no GUI."""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/'native/geometry.inc'
OUT=ROOT/'qa'/('native-helper-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=SOURCE.read_text();body=source[:source.index('std::string geometryFacts()')]
fixture=r'''
#include <algorithm>
#include <charconv>
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <limits>
#include <memory>
#include <ranges>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>
struct Object{};
using PHLWORKSPACEREF=std::weak_ptr<Object>;
using PHLMONITORREF=std::weak_ptr<Object>;
struct CBox{double x,y,w,h;};
namespace Fullscreen {enum eFullscreenMode{FSMODE_NONE=0,FSMODE_MAXIMIZED=1,FSMODE_FULLSCREEN=2};}
std::string quote(const std::string&s){return "\""+s+"\"";}
uint64_t outputGeneration=1;
'''
main=r'''
int main(){unsigned checks=0;
 auto verify=[&](bool value,const char*name){++checks;if(!value)std::fprintf(stderr,"FAIL %s\n",name);return value;};
 auto throws=[](auto work){try{work();return false;}catch(const std::runtime_error&){return true;}};
 GeometryOwners<PHLWORKSPACEREF> owners;
 auto a=std::make_shared<Object>();auto first=owners.bind(a);
 if(!verify(first!=0&&owners.bind(a)==first&&owners.live(first),"same owner stable generation"))return 1;
 a.reset();if(!verify(!owners.live(first),"destroyed owner unavailable"))return 1;
 a=std::make_shared<Object>();auto replacement=owners.bind(a);
 if(!verify(replacement>first&&!owners.live(first),"replacement cannot inherit old generation"))return 1;
 if(!verify(throws([&]{owners.bind({});}),"null owner refused"))return 1;
 owners.next=UINT64_MAX;
 if(!verify(owners.bind(a)==replacement,"existing owner still readable at generation bound"))return 1;
 if(!verify(throws([&]{owners.bind(std::make_shared<Object>());}),"owner generation overflow refused"))return 1;
 GeometryOwners<PHLWORKSPACEREF> bounded;std::vector<std::shared_ptr<Object>> held;
 for(unsigned i=0;i<256;++i){held.push_back(std::make_shared<Object>());if(!verify(bounded.bind(held.back())==i+1,"bounded owner allocation"))return 1;}
 if(!verify(throws([&]{bounded.bind(std::make_shared<Object>());}),"257th live owner refused"))return 1;
 auto old=bounded.bind(held.front());held.front().reset();auto fresh=std::make_shared<Object>();auto next=bounded.bind(fresh);
 if(!verify(next==257&&!bounded.live(old)&&bounded.entries.size()==256,"expired slot reclaimed without generation reuse"))return 1;
 auto workspace=std::make_shared<Object>();auto wg=geometryWorkspaces.bind(workspace);
 auto output=std::make_shared<Object>();auto og=geometryOutputs.bind(output);
 auto area=geometryWorkAreaRevision(wg,og,"[0,0,800,600]");
 if(!verify(area!=0&&geometryWorkAreaRevision(wg,og,"[0,0,800,600]")==area,"unchanged workarea revision stable"))return 1;
 auto reserved=geometryWorkAreaRevision(wg,og,"[0,20,800,580]");
 if(!verify(reserved>area,"reserved-area-only change advances revision"))return 1;
 ++outputGeneration;auto config=geometryWorkAreaRevision(wg,og,"[0,20,800,580]");
 if(!verify(config>reserved,"same box output configuration change advances revision"))return 1;
 auto output2=std::make_shared<Object>();auto og2=geometryOutputs.bind(output2);
 auto newOwner=geometryWorkAreaRevision(wg,og2,"[0,20,800,580]");
 if(!verify(newOwner>config,"output replacement advances workarea revision"))return 1;
 workspace.reset();workspace=std::make_shared<Object>();auto wg2=geometryWorkspaces.bind(workspace);
 auto replacementArea=geometryWorkAreaRevision(wg2,og2,"[0,20,800,580]");
 if(!verify(wg2!=wg&&replacementArea>newOwner&&geometryAreas.size()==1,"workspace retirement prunes old area"))return 1;
 geometryAreaRevision=UINT64_MAX;
 if(!verify(geometryWorkAreaRevision(wg2,og2,"[0,20,800,580]")==replacementArea,"unchanged workarea remains readable at overflow"))return 1;
 if(!verify(throws([&]{geometryWorkAreaRevision(wg2,og2,"[1,20,799,580]");}),"workarea revision overflow refused"))return 1;
 for(double value:{0.0,-0.0,0.1,-1.25,1e-200,std::numeric_limits<double>::max()}){
  std::string text=geometryNumber(value);double parsed=0;auto r=std::from_chars(text.data(),text.data()+text.size(),parsed);
  if(!verify(r.ec==std::errc{}&&r.ptr==text.data()+text.size()&&parsed==value,"finite numbers serialize losslessly"))return 1;
 }
 for(double value:{std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()})
  if(!verify(throws([&]{geometryNumber(value);}),"nonfinite number refused"))return 1;
 if(!verify(geometryRect({83,61,320,180})=="[83,61,320,180]","rectangle preserves noncentered origin"))return 1;
 if(!verify(geometryRect({-83,-61,320,180})=="[-83,-61,320,180]","negative origin supported"))return 1;
 for(CBox box:std::vector<CBox>{{0,0,0,1},{0,0,1,0},{0,0,-1,1},{0,0,1,-1},{INFINITY,0,1,1},{0,NAN,1,1},{0,0,NAN,1},{0,0,1,INFINITY},{std::numeric_limits<double>::max(),0,std::numeric_limits<double>::max(),1}})
  if(!verify(throws([&]{geometryRect(box);}),"invalid rectangle refused"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_NONE)=="\"ordinary\"","ordinary enum"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_MAXIMIZED)=="\"maximized\"","maximized enum"))return 1;
 if(!verify(geometryMode(Fullscreen::FSMODE_FULLSCREEN)=="\"fullscreen\"","fullscreen enum"))return 1;
 for(int value:{-1,3,INT32_MAX})if(!verify(throws([&]{geometryMode(static_cast<Fullscreen::eFullscreenMode>(value));}),"unknown mode refused"))return 1;
 std::printf("checks %u\n",checks);return 0;
}
'''
variants=[('actual',body),('unsafe-owner-rebind',body.replace('return entry.generation;','return ++next;')),('unsafe-workarea-omits-rectangle',body.replace('+":"+rectangle','')),('unsafe-workarea-omits-output-generation',body.replace('+":"+std::to_string(outputGeneration)','')),('unsafe-nonfinite-number',body.replace('if(!std::isfinite(value)) throw std::runtime_error("Nonfinite geometry");','')),('unsafe-zero-rectangle',body.replace('box.w<=0 || box.h<=0 || ',''))]
checks=[];inputs={str(p):sha(p) for p in [SOURCE,Path(__file__)]}
for p in [SOURCE,Path(__file__)]:shutil.copy2(p,OUT/p.name)
(OUT/'report.json').write_text(json.dumps({'passed':False,'nativeAcceptance':False,'scope':'Incomplete actual helper CPU attempt; inspect compile/run logs','inputs':inputs},indent=2)+'\n')
for name,piece in variants:
 assert piece!=body or name=='actual',name
 p=OUT/(name+'.cpp');p.write_text(fixture+'\n'+piece+'\n'+main);binary=OUT/name
 result=subprocess.run(['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-Wno-unused-parameter',str(p),'-o',str(binary)],capture_output=True,text=True,timeout=60)
 (OUT/(name+'-compile.log')).write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5)
 (OUT/(name+'-run.log')).write_text(result.stdout+result.stderr)
 checks.append({'name':name,'passed':result.returncode==(0 if name=='actual' else 1),'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
for p in [SOURCE,Path(__file__)]:shutil.copy2(p,OUT/p.name)
assert all(sha(p)==v for p,v in inputs.items()),'Source changed during helper tests'
r={'passed':all(c['passed'] for c in checks),'nativeAcceptance':False,'scope':'Actual extracted owner/workarea/number/rectangle/mode helper behavior; no native geometry eligibility/effect/menu acceptance','inputs':inputs,'checks':checks}
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json')}),flush=True);raise SystemExit(not r['passed'])
