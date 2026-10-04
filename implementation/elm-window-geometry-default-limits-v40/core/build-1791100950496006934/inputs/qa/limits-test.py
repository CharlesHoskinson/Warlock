"""Actual default declarations, commit callback, layout accessors and Window normalization."""
import hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('limits-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
HEADER=ROOT/'candidate/src/protocols/XDGShell.hpp';XDG=ROOT/'candidate/src/protocols/XDGShell.cpp';WINDOW=ROOT/'candidate/src/desktop/view/Window.cpp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=1;end=opening+1
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]
h=HEADER.read_text();start=h.index('    struct {\n        Vector2D minSize');end=h.index('    } m_pending, m_current;',start)+len('    } m_pending, m_current;');decl=h[start:end]
x=XDG.read_text();w=WINDOW.read_text();layout=block(x,'Vector2D CXDGToplevelResource::layoutMinSize()')+'\n'+block(x,'Vector2D CXDGToplevelResource::layoutMaxSize()')
callback=block(x,'m_listeners.surfaceCommit = m_surface->m_events.commit.listen([this] ');callback=callback[callback.index('{')+1:-1]
normal=block(w,'std::optional<Vector2D> CWindow::minSize()')+'\n'+block(w,'std::optional<Vector2D> CWindow::maxSize()')
fixture=r'''
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>
#include <memory>
#include <optional>
struct Vector2D {double x=0,y=0;Vector2D()=default;Vector2D(double a,double b):x(a),y(b){};Vector2D clamp(Vector2D low)const{return {std::max(x,low.x),std::max(y,low.y)};}bool operator==(const Vector2D&)const=default;};
struct Box {Vector2D xy;Vector2D pos()const{return xy;}};
struct Owner {struct {Box geometry;} m_current;};
struct CXDGToplevelResource {std::shared_ptr<Owner>m_owner;Vector2D layoutMinSize();Vector2D layoutMaxSize();
// DECLARATION
};
struct Property {std::optional<Vector2D>value_;bool hasValue(){return value_.has_value();}Vector2D value(){return *value_;}};
struct Boolean {bool v=false;bool valueOrDefault(){return v;}};
struct Rules {Property low,high;Boolean noMax;Property&minSize(){return low;}Property&maxSize(){return high;}Boolean&noMaxSize(){return noMax;}};
struct Xdg {std::shared_ptr<CXDGToplevelResource>m_toplevel;};
struct Hints {int min_width=0,min_height=0,max_width=0,max_height=0;};
struct Xwayland {std::shared_ptr<Hints>m_sizeHints=std::make_shared<Hints>();};
struct CWindow {std::shared_ptr<Rules>m_ruleApplicator=std::make_shared<Rules>();std::shared_ptr<Xdg>m_xdgSurface=std::make_shared<Xdg>();std::shared_ptr<Xwayland>m_xwaylandSurface=std::make_shared<Xwayland>();bool m_isX11=false;std::optional<Vector2D>minSize();std::optional<Vector2D>maxSize();};
#define UNLIKELY(x) (x)
struct Surface {struct {bool texture=false,buffer=false;}m_current,m_pending;void map(){}void unmap(){}};
struct Resource {void error(int,const char*){}};
struct Event {void emit(){}};
struct Commit {struct {int v=0;}m_current,m_pending;std::shared_ptr<CXDGToplevelResource>m_toplevel;std::shared_ptr<Surface>m_surface=std::make_shared<Surface>();std::shared_ptr<Resource>m_resource=std::make_shared<Resource>();bool m_initialCommit=false,m_mapped=false;struct {Event map,unmap,commit;}m_events;void run();};
'''
main=r'''
int main(){unsigned checks=0;auto verify=[&](bool v,const char*n){++checks;if(!v)std::fprintf(stderr,"FAIL %s\n",n);return v;};constexpr double unlimited=std::numeric_limits<double>::max();
 auto top=std::make_shared<CXDGToplevelResource>();CWindow window;window.m_xdgSurface->m_toplevel=top;Commit commit;commit.m_toplevel=top;
 if(!verify(top->m_pending.minSize==Vector2D{0,0}&&top->m_pending.maxSize==Vector2D{0,0}&&top->m_current.minSize==Vector2D{0,0}&&top->m_current.maxSize==Vector2D{0,0},"never-set protocol defaults unspecified"))return 1;
 if(!verify(window.minSize()==Vector2D{1,1}&&window.maxSize()==Vector2D{unlimited,unlimited},"never-set normalized limits"))return 1;
 for(Vector2D minimum: {Vector2D{0,0},Vector2D{60,0},Vector2D{0,70},Vector2D{60,70}})for(Vector2D maximum:{Vector2D{0,0},Vector2D{600,0},Vector2D{0,700},Vector2D{600,700}}){
  auto oldMin=top->m_current.minSize,oldMax=top->m_current.maxSize;top->m_pending.minSize=minimum;top->m_pending.maxSize=maximum;
  if(!verify(top->m_current.minSize==oldMin&&top->m_current.maxSize==oldMax,"pending does not change committed hints"))return 1;
  commit.run();
  if(!verify(top->m_current.minSize==minimum&&top->m_current.maxSize==maximum,"actual surface commit applies hints"))return 1;
  auto expectedMin=Vector2D{minimum.x>1?minimum.x:0,minimum.y>1?minimum.y:0};auto expectedMax=Vector2D{maximum.x>1?maximum.x:0,maximum.y>1?maximum.y:0};
  if(!verify(top->layoutMinSize()==expectedMin&&top->layoutMaxSize()==expectedMax,"independent unspecified axes and explicit limits preserved"))return 1;
  if(!verify(window.minSize()==Vector2D{std::max(1.,expectedMin.x),std::max(1.,expectedMin.y)}&&window.maxSize()==Vector2D{expectedMax.x<5?unlimited:expectedMax.x,expectedMax.y<5?unlimited:expectedMax.y},"Window per-axis unspecified normalization"))return 1;
 }
 top->m_pending.minSize={120,80};top->m_pending.maxSize={120,80};commit.run();
 if(!verify(window.minSize()==Vector2D{120,80}&&window.maxSize()==Vector2D{120,80},"explicit fixed-size hints preserved"))return 1;
 top->m_pending.minSize={0,0};top->m_pending.maxSize={0,0};commit.run();
 if(!verify(window.minSize()==Vector2D{1,1}&&window.maxSize()==Vector2D{unlimited,unlimited},"explicit zero reset equals never-set"))return 1;
 top->m_owner=std::make_shared<Owner>();top->m_owner->m_current.geometry.xy={3,4};top->m_pending.minSize={60,0};top->m_pending.maxSize={600,0};commit.run();
 if(!verify(top->layoutMinSize()==Vector2D{63,0}&&top->layoutMaxSize()==Vector2D{603,0},"existing explicit geometry-offset policy retained"))return 1;
 window.m_ruleApplicator->low.value_=Vector2D{90,95};window.m_ruleApplicator->high.value_=Vector2D{800,805};
 if(!verify(window.minSize()==Vector2D{90,95}&&window.maxSize()==Vector2D{800,805},"window rule overrides retained"))return 1;
 window.m_ruleApplicator->high.value_.reset();window.m_ruleApplicator->noMax.v=true;
 if(!verify(!window.maxSize(),"no-max-size rule retained"))return 1;
 std::printf("checks %u\n",checks);return 0;
}
'''
variants=[('actual',decl,layout),('previous-finite-defaults',decl.replace('{0, 0}','{1337420, 694200}'),layout),('unsafe-discard-explicit-limits',decl,layout.replace('if (m_current.maxSize.x > 1)','if (false)').replace('if (m_current.maxSize.y > 1)','if (false)'))]
inputs={str(p):sha(p) for p in [HEADER,XDG,WINDOW,Path(__file__)]};checks=[]
for p in [HEADER,XDG,WINDOW,Path(__file__)]:shutil.copy2(p,OUT/p.name)
(OUT/'report.json').write_text(json.dumps({'passed':False,'inputs':inputs,'scope':'Incomplete CPU attempt; inspect logs'},indent=2)+'\n')
for name,d,l in variants:
 src=OUT/(name+'.cpp');src.write_text(fixture.replace('// DECLARATION',d)+'\n'+l+'\n'+normal+'\nvoid Commit::run(){\n'+callback+'\n}\n'+main);binary=OUT/name
 p=subprocess.run(['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(src),'-o',str(binary)],capture_output=True,text=True,timeout=60);(OUT/(name+'-compile.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5);(OUT/(name+'-run.log')).write_text(p.stdout+p.stderr);checks.append({'name':name,'passed':p.returncode==(0 if name=='actual' else 1),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
assert all(sha(p)==wanted for p,wanted in inputs.items())
r={'passed':all(c['passed'] for c in checks),'nativeAcceptance':False,'scope':'Actual defaults/commit/layout/Window limits; hints>5 and existing rule/offset policy, no broad protocol conformance or GUI','inputs':inputs,'checks':checks};r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='report.json'}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json')}),flush=True);raise SystemExit(not r['passed'])
