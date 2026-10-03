
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
static int windowEq(lua_State* L) {
    const auto* lhs = sc<PHLWINDOWREF*>(luaL_checkudata(L, 1, MT));
    const auto* rhs = sc<PHLWINDOWREF*>(luaL_checkudata(L, 2, MT));

    lua_pushboolean(L, lhs->lock() == rhs->lock());
    return 1;
}
void Objects::CLuaWindow::push(lua_State* L, PHLWINDOWREF w) {
    new (lua_newuserdata(L, sizeof(PHLWINDOWREF))) PHLWINDOWREF(w ? w->m_self : nullptr);
    luaL_getmetatable(L, MT);
    lua_setmetatable(L, -2);
}
int luaWindowLifetime(lua_State* state) {
    // Use the public native Lua wrapper/equality, never its userdata layout.
    // Close emits before mapped is cleared; do not recover by string address.
    if (lua_gettop(state) != 1 || lua_type(state, 1) != LUA_TUSERDATA || !lua_getmetatable(state, 1)) {
        lua_pushnil(state); return 1;
    }
    const int suppliedMetatable = lua_gettop(state);
    for (const auto& owner : Desktop::windowState()->windows()) {
        if (!owner)
            continue;
        Config::Lua::Objects::CLuaWindow::push(state, owner);
        const int candidate = lua_gettop(state);
        if (!lua_getmetatable(state, candidate)) {
            lua_pop(state, 1);
            continue;
        }
        const bool nativeMetatable = lua_rawequal(state, suppliedMetatable, -1);
        lua_pop(state, 1);
        const bool exactNativeObject = nativeMetatable && lua_compare(state, 1, candidate, LUA_OPEQ);
        lua_pop(state, 1);
        if (!exactNativeObject)
            continue;
        const auto address = std::format("0x{:x}", reinterpret_cast<uintptr_t>(owner.get()));
        const auto stableID = std::format("{:x}", owner->m_stableID);
        lua_pushlstring(state, address.data(), address.size());
        lua_pushlstring(state, stableID.data(), stableID.size());
        lua_pushinteger(state, owner->getPID());
        return 3;
    }
    lua_pushnil(state);
    return 1;
}
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
