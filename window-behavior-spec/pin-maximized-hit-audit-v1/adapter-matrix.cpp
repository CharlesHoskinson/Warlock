#include <hyprutils/math/Box.hpp>
#include <hyprutils/math/Vector2D.hpp>
#include <cassert>
#include <cmath>
#include <iostream>
#include <map>
#include <memory>
#include <ranges>
#include <string>
#include <vector>
using Hyprutils::Math::CBox;using Hyprutils::Math::Vector2D;
using WORKSPACEID=int;
struct Window;struct Workspace;struct Monitor;
using PHLWINDOW=std::shared_ptr<Window>;
using PHLWORKSPACE=std::shared_ptr<Workspace>;
using PHLMONITOR=std::shared_ptr<Monitor>;
struct Rule {struct Value {bool value=false;bool valueOrDefault(){return value;}};Value focus;Value noFocus(){return focus;}};
struct XDG {struct Top {bool modal=false;bool anyChildModal(){return modal;}};std::shared_ptr<Top> m_toplevel=std::make_shared<Top>();};
struct XWay {bool wants=true;bool wantsFocus(){return wants;}};
struct Space {CBox workArea(){return {0,0,1000,1000};}};
struct Workspace {int id=1;std::shared_ptr<Space> m_space=std::make_shared<Space>();bool visible=true;bool isVisible(){return visible;}};
struct Monitor {PHLWORKSPACE m_activeSpecialWorkspace;int m_layerSurfaceLayers[4]{};Vector2D m_position{0,0},m_size{1000,1000};int activeWorkspaceID(){return 1;}int activeSpecialWorkspaceID(){return -1;}};
struct Window {
 std::string name;bool m_isFloating=false,m_isMapped=true,m_X11ShouldntFocus=false,m_isX11=false,protectedFamily=false,input=true,priority=false,overrideRedirect=false,popup=false,allowed=true;
 int mode=0;PHLWORKSPACE m_workspace;std::weak_ptr<Monitor> m_monitor;std::shared_ptr<Rule> m_ruleApplicator=std::make_shared<Rule>();std::shared_ptr<XDG> m_xdgSurface;std::shared_ptr<XWay> m_xwaylandSurface=std::make_shared<XWay>();CBox box{0,0,1000,1000};
 bool priorityFocus(){return priority;}bool acceptsInput(){return input;}bool isX11OverrideRedirect(){return overrideRedirect;}bool hasPopupAt(const Vector2D&){return popup;}bool onSpecialWorkspace(){return m_workspace&&m_workspace->id<0;}bool isAllowedOverFullscreen(){return allowed;}CBox getWindowBoxUnified(uint16_t){return box;}CBox layoutBox(){return box;}int workspaceID(){return m_workspace?m_workspace->id:0;}
};
namespace Config{using INTEGER=int;}
std::map<std::string,int> options;
template<class T> struct CConfigValue {std::string key;CConfigValue(const char*k):key(k){}T operator*()const{return options[key];}};
namespace Math {enum eDirection {DIRECTION_LEFT,DIRECTION_RIGHT,DIRECTION_UP,DIRECTION_DOWN};}
PHLMONITOR monitor=std::make_shared<Monitor>();PHLWORKSPACE workspace=std::make_shared<Workspace>();PHLWINDOW fs,currentFocus;
namespace State {
 struct MQ {MQ& vec(const Vector2D&){return *this;}PHLMONITOR run(){return monitor;}};struct MS {MQ query(){return {};}};MS*monitorState(){static MS s;return &s;}
 struct WQ {int selected=1;WQ&id(int id){selected=id;return *this;}PHLWORKSPACE run(){return workspace;}};struct WS {WQ query(){return {};}};WS*workspaceState(){static WS s;return &s;}
 struct Layout {bool reserved=false;bool isPointOnReservedArea(const Vector2D&,PHLMONITOR){return reserved;}};Layout*monitorLayoutController(){static Layout l;return &l;}
}
namespace Fullscreen {enum {FSMODE_NONE=0,FSMODE_MAXIMIZED=1,FSMODE_FULLSCREEN=2};struct Modes {int internal=0;};struct Controller {
 bool hasFullscreen(PHLWORKSPACE){return bool(fs);}PHLWINDOW getFullscreenWindow(PHLWORKSPACE){return fs;}bool isFullscreen(PHLWINDOW w,int mode){return w&&w->mode==mode;}Modes getFullscreenModes(PHLWORKSPACE){return {fs?fs->mode:0};}
 };Controller*controller(){static Controller c;return &c;}}
namespace Desktop {
 namespace View {enum eGetWindowProperties:uint16_t {WINDOW_ONLY=0,RESERVED_EXTENTS=1<<0,INPUT_EXTENTS=1<<1,FULL_EXTENTS=1<<2,FLOATING_ONLY=1<<3,ALLOW_FLOATING=1<<4,USE_PROP_TILED=1<<5,SKIP_FULLSCREEN_PRIORITY=1<<6,FOCUS_PRIORITY=1<<7,FOLLOW_MOUSE_CHECK=1<<8};}
 struct Focus {PHLWINDOW window(){return currentFocus;}};Focus*focusState(){static Focus f;return &f;}
 namespace Pin {std::vector<PHLWINDOW> protectedBand;std::vector<PHLWINDOW>band(){return protectedBand;}bool effective(PHLWINDOW w){return w&&w->protectedFamily;}}
 struct Tracker {std::vector<PHLWINDOW> entries;const std::vector<PHLWINDOW>&windows()const{return entries;}};
 class CViewHitTester {const Tracker&m_tracker;public:CViewHitTester(const Tracker&t):m_tracker(t){}PHLWINDOW windowAt(const Vector2D&,uint16_t,PHLWINDOW=nullptr)const;};
}
using namespace Desktop;using namespace Desktop::View;
#if defined(PROPOSED_CORRECTION)
#include "intended/windowAt.cpp.inc"
#else
#include "windowAt-exact.cpp.inc"
#endif
struct Layer {bool present=false;};using PHLLS=std::shared_ptr<Layer>;
constexpr int ZWLR_LAYER_SHELL_V1_LAYER_BOTTOM=1;
namespace Desktop {struct HitAdapter {bool layerSurfaceAt(const Vector2D&,int*,Vector2D*,PHLLS*){return false;}};struct ViewAdapter {HitAdapter hitTest(){return {};}};ViewAdapter*viewState(){static ViewAdapter v;return &v;}}
PHLWINDOW pointerSelection(PHLWINDOW ideal){
 auto PMONITOR=monitor;auto PWORKSPACE=workspace;PHLWINDOW pFoundWindow;bool foundSurface=false;PHLLS pFoundLayerSurface;Vector2D mouseCoords{50,50},surfaceCoords;
 auto getWindowIdeal=[&]() -> const PHLWINDOW&{return ideal;};
#if defined(PROPOSED_CORRECTION)
#include "intended/max-pointer-selection.cpp.inc"
#else
#include "max-pointer-selection-exact.cpp.inc"
#endif
 return pFoundWindow;
}
int main(){
 Tracker tracker;auto p=std::make_shared<Window>();p->name="protected-MAX";p->m_workspace=workspace;p->m_monitor=monitor;p->mode=1;p->protectedFamily=true;
 auto ordinary=std::make_shared<Window>();ordinary->name="ordinary-tiled";ordinary->m_workspace=workspace;ordinary->m_monitor=monitor;tracker.entries={ordinary,p};fs=p;Pin::protectedBand={p};CViewHitTester hit(tracker);Vector2D point{50,50};
 auto row=[&](const char*name,PHLWINDOW result){std::cout<<name<<":"<<(result?result->name:"null")<<"\n";};
 auto hitrow=[&](const char*name,uint16_t flags=ALLOW_FLOATING,PHLWINDOW ignored=nullptr){row(name,hit.windowAt(point,flags,ignored));};
 hitrow("protected-hit");hitrow("protected-ignored",ALLOW_FLOATING,p);
 p->input=false;hitrow("protected-no-input");p->input=true;
 p->box={200,200,100,100};hitrow("protected-outside");p->box={0,0,1000,1000};
 p->m_ruleApplicator->focus.value=true;hitrow("protected-nofocus");p->m_ruleApplicator->focus.value=false;
 hitrow("priority-only",FOCUS_PRIORITY);
 ordinary->input=false;hitrow("ignored-with-ordinary-no-input",ALLOW_FLOATING,p);ordinary->input=true;
 ordinary->m_ruleApplicator->focus.value=true;hitrow("ignored-with-ordinary-nofocus",ALLOW_FLOATING,p);ordinary->m_ruleApplicator->focus.value=false;
 hitrow("skip-fullscreen",ALLOW_FLOATING|SKIP_FULLSCREEN_PRIORITY,p);
 hitrow("floating-only",ALLOW_FLOATING|FLOATING_ONLY);
 fs.reset();hitrow("no-fullscreen-ignored",ALLOW_FLOATING,p);fs=p;
 row("protected-MAX-pointer-ordinary-tiled",pointerSelection(ordinary));row("protected-MAX-pointer-null",pointerSelection(nullptr));
 auto another=std::make_shared<Window>();another->name="another-protected-tiled";another->protectedFamily=true;another->m_workspace=workspace;another->m_monitor=monitor;
 row("protected-MAX-pointer-protected-tiled",pointerSelection(another));
 Pin::protectedBand.push_back(another);tracker.entries.push_back(another);hitrow("distinct-protected-band-winner");Pin::protectedBand.pop_back();tracker.entries.pop_back();
 monitor->m_activeSpecialWorkspace=std::make_shared<Workspace>();monitor->m_activeSpecialWorkspace->id=-1;
 row("special-workspace-protected-normal-ideal",pointerSelection(another));row("special-workspace-null-ideal",pointerSelection(nullptr));monitor->m_activeSpecialWorkspace.reset();
 p->protectedFamily=false;Pin::protectedBand.clear();hitrow("ordinary-MAX");hitrow("ordinary-MAX-outside-ignore",ALLOW_FLOATING,p);
 row("ordinary-MAX-pointer-protected-tiled",pointerSelection(another));row("ordinary-MAX-pointer-ordinary-tiled",pointerSelection(ordinary));row("ordinary-MAX-pointer-null",pointerSelection(nullptr));
 ordinary->m_isFloating=true;row("ordinary-MAX-pointer-allowed-floating",pointerSelection(ordinary));ordinary->m_isFloating=false;
 p->mode=2;hitrow("ordinary-exclusive");row("exclusive-block-non-MAX-ideal",pointerSelection(another));
 p->protectedFamily=true;hitrow("protected-exclusive-old-refusal");
}
