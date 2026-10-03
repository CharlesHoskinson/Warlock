"""Actual Hyprutils unique/weak ABI + Lua VM, extracted retirement source only."""
from pathlib import Path
import hashlib, json, resource, shlex, subprocess, sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope

B = Path(__file__).resolve().parent

def block(source, prefix):
    start = source.index(prefix); cursor = source.index('{', start); depth = 1; end = cursor + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}'); end += 1
    return source[start:end]

SHIM = r'''
#include <hyprutils/memory/WeakPtr.hpp>
#include <hyprutils/memory/SharedPtr.hpp>
#include <hyprutils/memory/UniquePtr.hpp>
#include <format>
#include <functional>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}
template<class T> using SP=Hyprutils::Memory::CSharedPointer<T>;
template<class T> using WP=Hyprutils::Memory::CWeakPointer<T>;
using Hyprutils::Memory::makeShared;
using Hyprutils::Memory::makeUnique;
unsigned checks=0,scenarios=0;
void check(bool p){if(!p)throw std::runtime_error("check "+std::to_string(checks+1));++checks;}
struct Owner {uint64_t m_stableID;bool mapped=true,hidden=false;explicit Owner(uint64_t id):m_stableID(id){}bool isHidden(){return hidden;}};
using PHLWINDOW=SP<Owner>;using PHLWINDOWREF=WP<Owner>;
bool validMapped(const PHLWINDOW& owner){return owner&&owner->mapped;}
struct CBox{double x=0,y=0,width=0,height=0;};
struct Vector2D{double x=0,y=0;};
enum eMouseBindMode{MBIND_INVALID,MBIND_MOVE,MBIND_RESIZE};constexpr uint32_t BTN_LEFT=272;
namespace Layout {struct ITarget {PHLWINDOW owner;explicit ITarget(PHLWINDOW w):owner(w){}PHLWINDOW window(){return owner;}};}
struct Controller{SP<Layout::ITarget> current;SP<Layout::ITarget> target(){return current;}};
bool keepCurrentGeometry=false;uint32_t releasedButton=BTN_LEFT;
struct Manager{Controller controller;int ends=0;bool keepObserved=false;std::function<void()> onEnd;
 Controller* dragController(){return &controller;}
 void endDragTarget(){++ends;keepObserved=keepCurrentGeometry;controller.current.reset();if(onEnd)onEnd();}};
auto g_layoutManager=makeUnique<Manager>();
struct WindowState{std::vector<PHLWINDOW> list;const auto& windows(){return list;}};
WindowState windows;
namespace Desktop{WindowState* windowState(){return &windows;}}
struct CHyprBar {
 PHLWINDOW owner;bool m_bDragPending=false,m_bDraggingThis=false,m_bTouchEv=false,m_bCancelledDown=true;int m_touchId=0;Vector2D m_captionPress;
 std::function<void()> destroying;explicit CHyprBar(PHLWINDOW w):owner(w){}~CHyprBar(){if(destroying)destroying();}
 PHLWINDOW getOwner(){return owner;}bool retireCaptionIntent();
};
struct Globals{std::vector<WP<CHyprBar>> bars;};auto g_pGlobalState=makeUnique<Globals>();
'''

CASES = r'''
std::pair<bool,bool> invoke(lua_State* L,const PHLWINDOW& owner,const std::string& stable=""){
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);
 const auto address=std::format("0x{:x}",reinterpret_cast<uintptr_t>(owner.get()));
 const auto id=stable.empty()?std::format("{:x}",owner->m_stableID):stable;
 lua_pushlstring(L,address.data(),address.size());lua_pushlstring(L,id.data(),id.size());
 check(lua_pcall(L,2,2,0)==LUA_OK);check(lua_gettop(L)==2&&lua_isboolean(L,1)&&lua_isboolean(L,2));++scenarios;
 return {bool(lua_toboolean(L,1)),bool(lua_toboolean(L,2))};
}
int main(int argc,char**){
 auto* L=luaL_newstate();check(L!=nullptr);
 auto owner=makeShared<Owner>(0xa1),peer=makeShared<Owner>(0xb2);windows.list={owner,peer};
 auto bar=makeUnique<CHyprBar>(owner);auto other=makeUnique<CHyprBar>(peer);
 g_pGlobalState->bars={WP<CHyprBar>{bar},WP<CHyprBar>{other}};
 const auto ref=WP<CHyprBar>{bar};check(!ref.expired()&&ref.get()==bar.get());
 check((invoke(L,owner)==std::pair{true,false}));check(ref==bar&&bar->m_bCancelledDown);
 if(argc>1){lua_close(L);return 0;}
 bar->m_bDragPending=true;other->m_bDragPending=true;
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDragPending&&other->m_bDragPending&&bar->m_bCancelledDown);
 bar->m_bDraggingThis=true;bar->m_bTouchEv=true;bar->m_touchId=7;
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDraggingThis&&!bar->m_bTouchEv&&bar->m_touchId==0);
 bar->m_bDragPending=true;check((invoke(L,owner,"a2")==std::pair{false,false}));check(bar->m_bDragPending);
 owner->hidden=true;check((invoke(L,owner)==std::pair{false,false}));check(bar->m_bDragPending);owner->hidden=false;
 owner->mapped=false;check((invoke(L,owner)==std::pair{false,false}));check(bar->m_bDragPending);owner->mapped=true;
 bar->m_bDragPending=false;auto target=makeShared<Layout::ITarget>(owner);gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_MOVE,BTN_LEFT};
 g_layoutManager->controller.current=target;
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==1&&g_layoutManager->keepObserved&&!keepCurrentGeometry&&!gesture&&!g_layoutManager->controller.current&&releasedButton==0);
 gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_RESIZE,BTN_LEFT};g_layoutManager->controller.current=target;
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==2&&g_layoutManager->keepObserved);
 const auto foreign=makeShared<Layout::ITarget>(peer);g_layoutManager->controller.current=foreign;
 check((invoke(L,owner)==std::pair{true,false}));check(g_layoutManager->controller.current==foreign&&g_layoutManager->ends==2);
 g_layoutManager->controller.current.reset();
 bool destructorQueried=false;bar->m_bDragPending=true;
 bar->destroying=[&]{destructorQueried=true;check(ref.expired()&&ref.get()!=nullptr);check((invoke(L,owner)==std::pair{true,false}));};
 bar.reset();check(destructorQueried&&ref.expired()&&ref.get()==nullptr);
 check((invoke(L,owner)==std::pair{true,false}));
 // A new uniquely owned bar never becomes reachable through an old weak handle.
 bar=makeUnique<CHyprBar>(owner);bar->m_bDragPending=true;
 check((invoke(L,owner)==std::pair{true,false}));check(bar->m_bDragPending&&ref.get()==nullptr);
 g_pGlobalState->bars.push_back(WP<CHyprBar>{bar});
 check((invoke(L,owner)==std::pair{true,true}));check(!bar->m_bDragPending);
 // Delegated core callbacks may destroy decorations before the borrowing loop.
 gesture=GestureCapture{owner,target,owner->m_stableID,{},MBIND_MOVE,BTN_LEFT};g_layoutManager->controller.current=target;
 g_layoutManager->onEnd=[&]{bar.reset();};
 check((invoke(L,owner)==std::pair{true,true}));check(g_layoutManager->ends==3&&!bar);g_layoutManager->onEnd={};
 check((invoke(L,peer)==std::pair{true,true}));check(!other->m_bDragPending);
 // Invalid Lua shape/type preserves the ordinary two-boolean refusal contract.
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);check(lua_pcall(L,0,2,0)==LUA_OK);
 check(!lua_toboolean(L,1)&&!lua_toboolean(L,2));++scenarios;
 lua_settop(L,0);lua_pushcfunction(L,luaRetireGestureCurrent);lua_pushinteger(L,1);lua_pushstring(L,"a1");check(lua_pcall(L,2,2,0)==LUA_OK);
 check(!lua_toboolean(L,1)&&!lua_toboolean(L,2));++scenarios;
 lua_close(L);std::cout<<checks<<" assertions / "<<scenarios<<" actual unique-weak ABI Lua scenarios PASS\n";
}
'''

def extracted(text, caption):
    return (block(text,'struct GestureCapture')+';\nstd::optional<GestureCapture> gesture;\n'+
            block(text,'bool sameGesture')+'\n'+block(text,'void retireCapturedGesture')+'\n'+
            block(caption,'bool CHyprBar::retireCaptionIntent')+'\n'+block(text,'int luaRetireGestureCurrent'))

def main():
    scope=require_qa_scope();out=B/'ownership-build';out.mkdir(exist_ok=False)
    source=B/'native-candidate/dragBridge.cpp';caption=B/'native-candidate/barDeco.cpp'
    exact=extracted(source.read_text(),caption.read_text())
    oldsource=B.parent/'toolkit-interruption-v4/native-candidate/dragBridge.cpp'
    old=extracted(oldsource.read_text(),caption.read_text())
    flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','hyprutils','lua'],text=True))
    records=[];deps={}
    for label,text,args in [('corrected',exact,[]),('frozen-v20-counterexample',old,['--idle'])]:
        cpp=out/(label+'.cpp');cpp.write_text(SHIM+text+CASES);binary=out/label
        command=['g++','-std=c++23','-O1','-g','-MD','-MF',str(out/(label+'.d')),str(cpp),'-o',str(binary),*flags]
        built=subprocess.run(command,capture_output=True,text=True)
        run=subprocess.run([str(binary),*args],capture_output=True,text=True) if built.returncode==0 else None
        records.append({'label':label,'exactSourceSHA256':hashlib.sha256(text.encode()).hexdigest(),
            'compile':{'command':command,'exitCode':built.returncode,'stdout':built.stdout,'stderr':built.stderr},
            'execute':None if run is None else {'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}})
        if (out/(label+'.d')).exists():
            for item in (out/(label+'.d')).read_text().replace('\\\n',' ').split(':',1)[1].split():
                p=Path(item)
                if p.is_file():deps[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
    result=(all(r['compile']['exitCode']==0 for r in records) and
            records[0]['execute']['exitCode']==0 and records[1]['execute']['exitCode']==-6 and
            'tried to lock a CWeakPointer over a CUniquePointer' in records[1]['execute']['stderr'])
    report={'result':'pass' if result else 'fail','records':records,'dependencies':deps,'scope':scope,
        'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),
        'candidateSourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'frozenV20SourceSHA256':hashlib.sha256(oldsource.read_bytes()).hexdigest(),
        'nativeGUIExecuted':False,'mainLoaded':False,
        'boundary':'Actual Hyprutils unique/weak ABI and Lua VM; exact extracted source, mocked core/window/decoration lifecycle; actual compositor acceptance remains pending'}
    (B/'ownership-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'corrected':records[0]['execute'],'counterexample':records[1]['execute'],'boundary':report['boundary']}))
    raise SystemExit(0 if result else 1)

if __name__=='__main__':main()
