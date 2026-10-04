
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

void CWindow::requests(std::optional<bool> requestsMX){
    if (requestsMX.has_value() && !(m_suppressedEvents & SUPPRESS_MAXIMIZE)) {
        if (m_isMapped) {
            auto window = m_self.lock();

            if (window->m_suppressNextMaximize) {
                window->m_suppressNextMaximize = false;
                return;
            }

            const auto CLIENT_STATE = Fullscreen::controller()->getFullscreenModes(window).client;
            // Client requests express a desired state, not a toggle. Repeated
            // set/unset requests must preserve the already requested state.
            if (requestsMX.value() && CLIENT_STATE == Fullscreen::FSMODE_NONE)
                Fullscreen::controller()->setFullscreenMode(window, std::nullopt, Fullscreen::FSMODE_MAXIMIZED);
            else if (!requestsMX.value() && CLIENT_STATE == Fullscreen::FSMODE_MAXIMIZED)
                Fullscreen::controller()->setFullscreenMode(window, std::nullopt, Fullscreen::FSMODE_NONE);
        }
    }
}
bool CWindow::acceptsInput() const {
    return !Desktop::WindowPolicy::isMinimized(m_self.lock()) && !isHidden() && !isInputBlocked();
}
void CFullscreenController::setWindowFullscreenModeClient(const PHLWINDOW window, const eFullscreenMode mode, bool layoutAware) {
    if (!window)
        return;

    const auto FS_HANDLER = getFsHandler(window, layoutAware);
    if (!FS_HANDLER) {
        Log::logger->log(Log::ERR, "window {} doesn't have FS handler assinged. This should never happen", window->m_title);
        return;
    }

    FS_HANDLER->setTargetFullscreenModeClient(window->m_target, mode);

    g_pXWaylandManager->setWindowFullscreen(window, mode == FSMODE_FULLSCREEN);
}

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
