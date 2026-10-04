"""Compile actual native callbacks against independent behavioral fixtures."""
import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('callbacks-'+str(time.time_ns()));OUT.mkdir()
OWNER=ROOT.parents[2]/'implementation/maximized-stack-v1/native-core-v2'
window=ROOT/'candidate/src/desktop/view/Window.cpp';controller=ROOT/'candidate/src/managers/fullscreen/FullscreenController.cpp'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def block(text,marker):
 start=text.index(marker);opening=text.index('{',start);depth=1;i=opening+1
 while depth:
  depth+=int(text[i]=='{')-int(text[i]=='}');i+=1
 return text[start:i]
def pieces(w,c):
 return block(w,'    if (requestsMX.has_value()'),block(w,'bool CWindow::acceptsInput() const'),block(c,'void CFullscreenController::setWindowFullscreenModeClient(')
current=pieces(window.read_text(),controller.read_text());prior=pieces((OWNER/'src/desktop/view/Window.cpp').read_text(),(OWNER/'src/managers/fullscreen/FullscreenController.cpp').read_text())
fixture=r'''
#include <memory>
#include <optional>
#include <string>
#include <vector>
#include <cstdio>
struct CWindow; using PHLWINDOW=std::shared_ptr<CWindow>;
namespace Desktop::WindowPolicy { bool isMinimized(const PHLWINDOW&); }
namespace Fullscreen {
 enum eFullscreenMode { FSMODE_NONE=0,FSMODE_MAXIMIZED=1,FSMODE_FULLSCREEN=2 };
 struct Modes {eFullscreenMode client;};
 struct Handler { void setTargetFullscreenModeClient(int,eFullscreenMode){} };
 class CFullscreenController { public:
  std::vector<eFullscreenMode> requests;
  std::shared_ptr<Handler> handler=std::make_shared<Handler>();
  std::shared_ptr<Handler> getFsHandler(PHLWINDOW,bool) {return handler;}
  Modes getFullscreenModes(PHLWINDOW);
  void setFullscreenMode(PHLWINDOW,std::optional<eFullscreenMode>,std::optional<eFullscreenMode>);
  void setWindowFullscreenModeClient(PHLWINDOW,eFullscreenMode,bool);
 };
 CFullscreenController* controller();
}
struct Toplevel { std::vector<bool> maxFlags;void setMaximized(bool b){maxFlags.push_back(b);} };
struct Xdg {std::shared_ptr<Toplevel> m_toplevel=std::make_shared<Toplevel>();};
struct CWindow {
 std::weak_ptr<CWindow> m_self; bool m_isMapped=true,m_suppressNextMaximize=false,m_isX11=false;
 int m_suppressedEvents=0,m_target=1; std::string m_title="probe";
 bool hidden=false,blocked=false,minimized=false;
 std::shared_ptr<Xdg> m_xdgSurface=std::make_shared<Xdg>();
 Fullscreen::eFullscreenMode client=Fullscreen::FSMODE_NONE;
 bool isHidden()const{return hidden;} bool isInputBlocked()const{return blocked;}
 bool acceptsInput()const;
 void requests(std::optional<bool> requestsMX);
};
constexpr int SUPPRESS_MAXIMIZE=1;
namespace Desktop::WindowPolicy {bool isMinimized(const PHLWINDOW&w){return w && w->minimized;}}
namespace Fullscreen {
 CFullscreenController engine; CFullscreenController*controller(){return &engine;}
 Modes CFullscreenController::getFullscreenModes(PHLWINDOW w){return {w->client};}
 void CFullscreenController::setFullscreenMode(PHLWINDOW w,std::optional<eFullscreenMode>,std::optional<eFullscreenMode>c){requests.push_back(c.value());w->client=c.value();}
}
namespace Log { enum {ERR};struct Logger{template<class...T>void log(T...){} };Logger obj;Logger*logger=&obj;}
struct XManager {std::vector<bool>flags;void setWindowFullscreen(PHLWINDOW,bool b){flags.push_back(b);} } xm;
auto*g_pXWaylandManager=&xm;
using namespace Fullscreen;
'''
main=r'''
int main(){unsigned checks=0;
 auto verify=[&](bool value,const char*name){++checks;if(!value){std::fprintf(stderr,"FAIL %s\n",name);return false;}return true;};
 auto fresh=[](){auto w=std::make_shared<CWindow>();w->m_self=w;return w;};
 for(auto mode:{FSMODE_NONE,FSMODE_MAXIMIZED,FSMODE_FULLSCREEN})for(int desired:{-1,0,1})for(bool mapped:{false,true})for(bool suppressed:{false,true}){
  auto w=fresh();w->client=mode;w->m_isMapped=mapped;w->m_suppressedEvents=suppressed?SUPPRESS_MAXIMIZE:0;engine.requests.clear();
  w->requests(desired<0?std::optional<bool>{}:std::optional<bool>{desired==1});
  bool changes=desired>=0 && mapped && !suppressed && ((desired==1&&mode==FSMODE_NONE)||(desired==0&&mode==FSMODE_MAXIMIZED));
  auto expected=changes?(desired==1?FSMODE_MAXIMIZED:FSMODE_NONE):mode;
  if(!verify(w->client==expected && engine.requests.size()==(changes?1u:0u),"explicit desired mode/guard"))return 1;
 }
 auto w=fresh();engine.requests.clear();w->requests(true);w->requests(true);w->requests(false);w->requests(false);
 if(!verify(engine.requests==std::vector<eFullscreenMode>{FSMODE_MAXIMIZED,FSMODE_NONE},"repeated set/unset idempotent"))return 1;
 w=fresh();w->m_suppressNextMaximize=true;engine.requests.clear();w->requests(true);
 if(!verify(!w->m_suppressNextMaximize&&engine.requests.empty(),"one-shot suppression retained"))return 1;
 for(bool mini:{false,true})for(bool hidden:{false,true})for(bool blocked:{false,true}){
  w=fresh();w->minimized=mini;w->hidden=hidden;w->blocked=blocked;
  if(!verify(w->acceptsInput()==(!mini&&!hidden&&!blocked),"minimized/hidden/blocked input exclusion preserved"))return 1;
 }
 for(auto mode:{FSMODE_NONE,FSMODE_MAXIMIZED,FSMODE_FULLSCREEN}){
  w=fresh();xm.flags.clear();engine.setWindowFullscreenModeClient(w,mode,false);
  if(!verify(w->m_xdgSurface->m_toplevel->maxFlags==std::vector<bool>{mode==FSMODE_MAXIMIZED}&&xm.flags==std::vector<bool>{mode==FSMODE_FULLSCREEN},"distinct MAX/FULL configure flags"))return 1;
 }
 for(int shape:{0,1,2}){w=fresh();auto top=w->m_xdgSurface->m_toplevel;
  if(shape==0)w->m_isX11=true;else if(shape==1)w->m_xdgSurface=nullptr;else w->m_xdgSurface->m_toplevel=nullptr;
  xm.flags.clear();engine.setWindowFullscreenModeClient(w,FSMODE_MAXIMIZED,false);
  if(!verify(top->maxFlags.empty()&&xm.flags==std::vector<bool>{false},"absent/X11 XDGShell guarded"))return 1;
 }
 w=fresh();engine.handler=nullptr;xm.flags.clear();engine.setWindowFullscreenModeClient(w,FSMODE_MAXIMIZED,false);
 if(!verify(xm.flags.empty()&&w->m_xdgSurface->m_toplevel->maxFlags.empty(),"missing handler no configure"))return 1;
 xm.flags.clear();engine.setWindowFullscreenModeClient(nullptr,FSMODE_MAXIMIZED,false);
 if(!verify(xm.flags.empty(),"null target no configure"))return 1;
 std::printf("checks %u\n",checks);return 0;
}
'''
checks=[]
for name,parts in [('actual',current),('previous-toggle',(prior[0],current[1],current[2])),('previous-no-max-configure',(current[0],current[1],prior[2])),('unsafe-raw-owner-input',(current[0],prior[1],current[2]))]:
 text=fixture+'\nvoid CWindow::requests(std::optional<bool> requestsMX){\n'+parts[0]+'\n}\n'+parts[1]+'\n'+parts[2]+'\n'+main
 source=OUT/(name+'.cpp');source.write_text(text);binary=OUT/name
 p=subprocess.run(['/usr/bin/c++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(binary)],capture_output=True,text=True,timeout=60)
 (OUT/(name+'-compile.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(binary)],capture_output=True,text=True,timeout=5);(OUT/(name+'-run.log')).write_text(p.stdout+p.stderr)
 checks.append({'name':name,'passed':p.returncode==(0 if name=='actual' else 1),'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
for p in [window,controller,Path(__file__)]:shutil.copy2(p,OUT/p.name)
r={'passed':all(c['passed'] for c in checks),'scope':'Actual extracted callbacks with independent request/configure/input oracles; no native window acceptance','inputs':{str(p):sha(p) for p in [window,controller,Path(__file__)]},'checks':checks}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json')}));raise SystemExit(not r['passed'])
