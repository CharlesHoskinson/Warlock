"""Actual staged getter + official push/equality text in real Lua VM, mocked windows."""
from pathlib import Path
import hashlib,json,resource,shlex,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent

def block(source,prefix):
 start=source.index(prefix);brace=source.index('{',start);depth=1;end=brace+1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[start:end]

def main():
 scope=require_qa_scope();out=B/'lua-lifetime-build';out.mkdir(exist_ok=False)
 native=(B/'native-candidate/dragBridge.cpp').read_text();official=(B/'primary/LuaWindow.cpp').read_text()
 exact=block(official,'static int windowEq')+'\n'+block(official,'void Objects::CLuaWindow::push')+'\n'+block(native,'int luaWindowLifetime')
 shim=r'''
#include <cassert>
#include <memory>
#include <format>
#include <vector>
#include <iostream>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}
struct Owner;
struct Ref{std::weak_ptr<Owner> ref;Ref(std::nullptr_t=nullptr){}Ref(std::shared_ptr<Owner> w):ref(w){}std::shared_ptr<Owner> lock()const{return ref.lock();}operator bool()const{return !ref.expired();}Owner*operator->()const{return lock().get();}};
using PHLWINDOWREF=Ref;
struct Owner{uint64_t m_stableID;int pid;Ref m_self;int getPID(){return pid;}};
template<class R,class T>R sc(T value){return static_cast<R>(value);}
constexpr const char* MT="HL.Window";
namespace Desktop{struct State{std::vector<std::shared_ptr<Owner>> current;auto& windows(){return current;}};State storage;State*windowState(){return &storage;}}
namespace Config::Lua::Objects{struct CLuaWindow{static void push(lua_State*,PHLWINDOWREF);};}
using namespace Config::Lua;
'''
 cases=r'''
int gcRef(lua_State* L){static_cast<Ref*>(lua_touserdata(L,1))->~Ref();return 0;}
int main(){
 auto* L=luaL_newstate();luaL_newmetatable(L,MT);lua_pushcfunction(L,windowEq);lua_setfield(L,-2,"__eq");lua_pushcfunction(L,gcRef);lua_setfield(L,-2,"__gc");lua_pop(L,1);
 auto owner=std::make_shared<Owner>(Owner{0xabc,123});owner->m_self=owner;Desktop::storage.current={owner};
 auto call=[&](const Ref& w){lua_settop(L,0);lua_pushcfunction(L,luaWindowLifetime);Objects::CLuaWindow::push(L,w);assert(lua_pcall(L,1,LUA_MULTRET,0)==LUA_OK);};
 call(owner);assert(lua_gettop(L)==3);assert(std::string(lua_tostring(L,2))=="abc");assert(lua_tointeger(L,3)==123);assert(std::string(lua_tostring(L,1))==std::format("0x{:x}",reinterpret_cast<uintptr_t>(owner.get())));
 auto replacement=std::make_shared<Owner>(Owner{0xdef,123});replacement->m_self=replacement;Desktop::storage.current={replacement};
 call(owner);assert(lua_gettop(L)==1&&lua_isnil(L,1));
 Ref expired=owner;owner.reset();call(expired);assert(lua_gettop(L)==1&&lua_isnil(L,1));
 call(replacement);assert(lua_gettop(L)==3&&std::string(lua_tostring(L,2))=="def");
 lua_settop(L,0);lua_pushcfunction(L,luaWindowLifetime);lua_pushstring(L,"0xbeef");assert(lua_pcall(L,1,LUA_MULTRET,0)==LUA_OK&&lua_isnil(L,1));
 lua_settop(L,0);lua_pushcfunction(L,luaWindowLifetime);lua_newuserdata(L,1);luaL_newmetatable(L,"foreign");lua_setmetatable(L,-2);assert(lua_pcall(L,1,LUA_MULTRET,0)==LUA_OK&&lua_isnil(L,1));
 lua_settop(L,0);lua_pushcfunction(L,luaWindowLifetime);lua_newuserdata(L,1);assert(lua_pcall(L,1,LUA_MULTRET,0)==LUA_OK&&lua_isnil(L,1));
 lua_settop(L,0);lua_pushcfunction(L,luaWindowLifetime);assert(lua_pcall(L,0,LUA_MULTRET,0)==LUA_OK&&lua_isnil(L,1));
 lua_close(L);std::cout<<"8 actual Lua VM getter scenarios PASS\n";
}
'''
 (out/'test.cpp').write_text(shim+exact+cases)
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','lua'],text=True))
 command=['g++','-std=c++23','-O1','-MD','-MF',str(out/'test.d'),str(out/'test.cpp'),'-o',str(out/'test'),*flags]
 built=subprocess.run(command,capture_output=True,text=True);run=subprocess.run([str(out/'test')],capture_output=True,text=True) if built.returncode==0 else None
 deps={}
 if (out/'test.d').exists():
  for item in (out/'test.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(item)
   if p.is_file():deps[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
 report={'result':'pass' if run and run.returncode==0 else 'fail','scenarios':8,'scope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'exactSourceSHA256':hashlib.sha256(exact.encode()).hexdigest(),'compile':{'command':command,'exitCode':built.returncode,'stdout':built.stdout,'stderr':built.stderr},'run':None if run is None else {'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr},'dependencies':deps,'nativeExecuted':False,'boundary':'Real Lua stack/metatable/API behavior, actual getter/official equality+push text, mocked native WindowState; native close timing awaits actual fixture'}
 (B/'lua-lifetime-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('result','scenarios','scope','boundary')}));raise SystemExit(0 if report['result']=='pass' else 1)
if __name__=='__main__':main()
