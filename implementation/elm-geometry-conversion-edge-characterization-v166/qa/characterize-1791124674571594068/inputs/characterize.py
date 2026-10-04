"""Actual owning method slices and real paired Hyprutils; no policy/model/GUI."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('characterize-'+str(time.time_ns()));(OUT/'inputs').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review=REPO/'implementation/elm-geometry-constraint-coordinate-review-v155/reviewed-inputs.json'
pair=REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json'
provenance=json.loads(review.read_text());pairdata=json.loads(pair.read_text())
for name,row in provenance['files'].items():assert sha(Path(name))==row['sha256'],name
def source(suffix):
 p=next(Path(name) for name in provenance['files'] if name.endswith(suffix))
 shutil.copy2(p,OUT/'inputs'/p.name);return p.read_text(),p
window,windowpath=source('/desktop/view/Window.cpp')
xdg,xdgpath=source('/protocols/XDGShell.cpp')
target,targetpath=source('/layout/target/WindowTarget.cpp')
def braces(text,anchor):
 start=text.index(anchor);opening=text.index('{',start);level=1;i=opening+1
 while level:
  if text[i]=='{':level+=1
  elif text[i]=='}':level-=1
  i+=1
 return text[opening+1:i-1]
minmethod='Vector2D CXDGToplevelResource::layoutMinSize() {'+braces(xdg,'Vector2D CXDGToplevelResource::layoutMinSize()')+'}\n'
maxmethod='Vector2D CXDGToplevelResource::layoutMaxSize() {'+braces(xdg,'Vector2D CXDGToplevelResource::layoutMaxSize()')+'}\n'
maxbody=braces(target,'} else if (FSMODES.internal == Fullscreen::FSMODE_MAXIMIZED)')
finalstart=target.index('        m_window->updateWindowDecos();',target.index('} else if (FSMODES.internal == Fullscreen::FSMODE_MAXIMIZED)'))
finalend=target.index('        return;',finalstart)+len('        return;')
finalization=target[finalstart:finalend]
reportbody=braces(window,'Vector2D CWindow::realToReportSize()')
wayland=reportbody[:reportbody.index('    static auto PXWLFORCESCALEZERO')]
mathpath=REPO/'implementation/maximized-stack-v1/native-core-v2/src/helpers/math/Math.hpp'
constant=next(line for line in mathpath.read_text().splitlines() if 'constexpr const Vector2D VECTOR2D_MAX' in line)
shutil.copy2(mathpath,OUT/'inputs/Math.hpp')
slices={'MAX-body':maxbody,'MAX-finalization':finalization,'layoutMinSize':minmethod,'layoutMaxSize':maxmethod,'realToReportSize-Wayland':wayland,'VECTOR2D_MAX':constant}
for name,text in slices.items():(OUT/'inputs'/(name+'.txt')).write_text(text)
for path,w in pairdata['dependencies'].items():
 if '/hyprutils/' in path:assert sha(Path(path))==w,path
library=Path('/usr/lib/libhyprutils.so.0.14.2');assert sha(library)==pairdata['linkedLibraries'][str(library)]
prelude=r'''
#include <hyprutils/math/Box.hpp>
#include <cmath>
#include <limits>
#include <iostream>
#include <memory>
#include <stdexcept>
using Hyprutils::Math::Vector2D;
using Hyprutils::Math::CBox;
using Hyprutils::Math::SBoxExtents;
namespace Math { CONSTANT }
struct GeometryOwner { struct {CBox geometry;} m_current; };
struct CXDGToplevelResource {
 struct {Vector2D minSize,maxSize;} m_current;
 GeometryOwner* m_owner=nullptr;
 Vector2D layoutMinSize();Vector2D layoutMaxSize();
};
struct Goal {Vector2D value;Vector2D goal(){return value;}};
struct CWindow {
 bool m_isX11=false;double monitorScale=1;
 Goal goal;Goal* m_realSize=&goal;CBox realBox;SBoxExtents reserved;
 Vector2D configured;int sends=0,decos=0;
 SBoxExtents getFullWindowReservedArea(){return reserved;}
 void setBox(CBox box){realBox=box;goal.value=box.size();}
 void updateWindowDecos(){decos++;}
 void sendWindowSize(){configured=realToReportSize();sends++;}
 Vector2D realToReportSize();
};
struct CWindowTarget {
 struct {CBox logicalBox,visualBox;} m_box;
 CWindow* m_window;
 void characterizeMax(bool CONFIGURECLIENT);
};
'''.replace('CONSTANT',constant)
tail=r'''
int total=0,failed=0;
void check(const char* name,bool value){total++;std::cout<<(value?"PASS ":"FAIL ")<<name<<"\n";if(!value)failed++;}
bool vectorEq(Vector2D a,Vector2D b){return a==b;}
bool boxEq(CBox a,CBox b){return vectorEq(a.pos(),b.pos())&&vectorEq(a.size(),b.size());}
int main(){
 CWindow w;CWindowTarget t;t.m_window=&w;
 t.m_box={CBox{0,0,800,600},CBox{}};t.characterizeMax(true);
 check("no-reserve empty visual uses logical box",boxEq(w.realBox,{0,0,800,600}));
 check("actual configure and decoration calls occur once",w.sends==1&&w.decos==1&&vectorEq(w.configured,{800,600}));
 t.m_box={CBox{0,0,800,600},CBox{20,30,700,500}};t.characterizeMax(true);
 check("distinct visual box governs prospective client box",boxEq(w.realBox,{20,30,700,500}));
 check("bare logical workarea control differs",!boxEq(w.realBox,t.m_box.logicalBox));
 w.reserved={{3,7},{5,11}};t.characterizeMax(true);
 check("asymmetric decoration extents applied exactly once",boxEq(w.realBox,{23,37,692,482}));
 check("asymmetric configure uses real client size",vectorEq(w.configured,{692,482}));
 t.m_box={CBox{-200,-100,900,700},CBox{-10.25,20.25,100.25,80.25}};
 w.reserved={{1,2},{3,4}};t.characterizeMax(true);
 std::cout<<"OBSERVED real-box "<<w.realBox.x<<" "<<w.realBox.y<<" "<<w.realBox.w<<" "<<w.realBox.h<<"\n";
 check("fractional negative origin real CBox rounding then reservation",boxEq(w.realBox,{-9,22,96,75}));
 int sends=w.sends;t.characterizeMax(false);
 check("no-client-configure path still updates prospective box",w.sends==sends&&boxEq(w.realBox,{-9,22,96,75}));
 GeometryOwner owner;owner.m_current.geometry={9,13,200,100};CXDGToplevelResource x;x.m_owner=&owner;
 x.m_current.minSize={108,42};x.m_current.maxSize={0,0};
 check("GTK108x42 raw minimum converts with nonzero geometry origin",vectorEq(x.layoutMinSize(),{117,55}));
 check("zero maximum remains zero despite geometry origin",vectorEq(x.layoutMaxSize(),{0,0}));
 x.m_owner=nullptr;check("ownerless GTK minimum stays raw108x42",vectorEq(x.layoutMinSize(),{108,42}));
 x.m_owner=&owner;x.m_current.maxSize={1,1};check("raw positive maximum1 is suppressed by actual layout threshold",vectorEq(x.layoutMaxSize(),{0,0}));
 for(int n=2;n<=4;n++){
  x.m_current.maxSize={n,n};check(("tiny raw maximum "+std::to_string(n)+" adds geometry offset").c_str(),vectorEq(x.layoutMaxSize(),Vector2D{n+9,n+13}));
 }
 owner.m_current.geometry={-8,-3,200,100};x.m_current.maxSize={4,2};
 check("negative geometry origin can produce negative layout maximum",vectorEq(x.layoutMaxSize(),{-4,-1}));
 x.m_current.minSize={0,1};check("zero and1 minimum axes suppressed before geometry offset",vectorEq(x.layoutMinSize(),{0,0}));
 owner.m_current.geometry={0,0,200,100};x.m_current.maxSize={120,80};
 check("zero geometry origin preserves finite maximum",vectorEq(x.layoutMaxSize(),{120,80}));
 w.goal.value={108,42};w.monitorScale=1;check("Waylandscale1 configure size remains logical108x42",vectorEq(w.realToReportSize(),{108,42}));
 w.monitorScale=2;check("Waylandscale2 configure size does not multiply",vectorEq(w.realToReportSize(),{108,42}));
 check("client-times-scale unsafe control differs at scale2",!vectorEq(w.realToReportSize(),w.goal.value*w.monitorScale));
 w.goal.value={-4,42};check("actual Wayland report clamps negative axis to zero",vectorEq(w.realToReportSize(),{0,42}));
 w.goal.value={108.25,42.75};check("Wayland report preserves fractional logical goal",vectorEq(w.realToReportSize(),{108.25,42.75}));
 std::cout<<"TOTAL "<<total<<" FAILED "<<failed<<"\n";return failed?1:0;
}
'''
def program(body,reportbranch):
 return prelude+minmethod+maxmethod+'Vector2D CWindow::realToReportSize(){'+reportbranch+'throw std::runtime_error("X11 excluded");}\n'+'void CWindowTarget::characterizeMax(bool CONFIGURECLIENT){'+body+finalization+'}\n'+tail
report={'passed':False,'scope':'Extracted actual MAX body/XDG layout min-max/Wayland report branch with stub dependencies and real paired Hyprutils; no policy, native, X11 or presentation acceptance',
 'reviewedInputs':str(review),'reviewedInputsSHA256':sha(review),'pairReport':str(pair),'pairReportSHA256':sha(pair),'slices':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in slices.items()},'runs':{}}
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils'],text=True))
 variants=[('actual',program(maxbody,wayland),0),('unsafe-bare-workarea',program('m_window->setBox(m_box.logicalBox);',wayland),1),
 ('unsafe-client-times-scale',program(maxbody,wayland.replace('m_realSize->goal().clamp(Vector2D{0, 0}, Math::VECTOR2D_MAX)','(m_realSize->goal()*monitorScale).clamp(Vector2D{0, 0}, Math::VECTOR2D_MAX)')),1)]
 for name,code,expected in variants:
  c=OUT/(name+'.cpp');c.write_text(code);binary=OUT/name
  command=['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/(name+'.d')),str(c),'-o',str(binary),*flags]
  result=subprocess.run(command,capture_output=True,text=True,timeout=60);(OUT/(name+'.compile.stderr')).write_text(result.stderr)
  assert result.returncode==0,result.stderr
  result=subprocess.run([str(binary)],capture_output=True,text=True,timeout=2)
  (OUT/(name+'.stdout')).write_text(result.stdout);(OUT/(name+'.stderr')).write_text(result.stderr)
  report['runs'][name]={'command':command,'exitCode':result.returncode,'binarySHA256':sha(binary),'checks':sum(line.startswith(('PASS ','FAIL ')) for line in result.stdout.splitlines()),'failedNames':[line[5:] for line in result.stdout.splitlines() if line.startswith('FAIL ')]}
  assert result.returncode==expected,name+': '+result.stdout
 deps=shlex.split((OUT/'actual.d').read_text().replace('\\\n',' ').split(':',1)[1])
 report['dependencies']={p:sha(Path(p)) for p in deps}
 libraries=subprocess.check_output(['ldd',str(OUT/'actual')],text=True);(OUT/'ldd.stdout').write_text(libraries)
 report['linkedLibraries']={p:sha(Path(p)) for line in libraries.splitlines() for p in line.split() if p.startswith('/')}
 for p,w in report['dependencies'].items():
  if '/hyprutils/' in p:assert pairdata['dependencies'][p]==w,p
 assert sha(library)==pairdata['linkedLibraries'][str(library)]
 report['pairedHyprutils']={'library':str(library),'sha256':sha(library),'headerCount':sum('/hyprutils/' in p for p in report['dependencies'])}
 report['passed']=True
except Exception as error:report['error']=repr(error)
shutil.copy2(__file__,OUT/'inputs/characterize.py')
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
