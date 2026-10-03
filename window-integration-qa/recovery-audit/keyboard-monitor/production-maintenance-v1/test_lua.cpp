#include "MaintenanceLua.hpp"
#include <cassert>
#include <iostream>
using namespace OmarchyA11yMaintenance;
bool quiet=false,subscribed=true,retired=false;unsigned commits=0;
Context context{"abc_1_2","reviewed-v1",[]{return quiet;},[]{retired=true;subscribed=false;++commits;}};
int prepare(lua_State* L){return OmarchyA11yMaintenance::prepare(L,context);}
int identity(lua_State* L){return OmarchyA11yMaintenance::identity(L,context);}
int main(){
 auto* L=luaL_newstate();assert(L);
 lua_pushcfunction(L,prepare);lua_setglobal(L,"prepare");lua_pushcfunction(L,identity);lua_setglobal(L,"identity");
 assert(luaL_dostring(L,"return prepare('abc_1_2','reviewed-v1')")==LUA_OK);assert(std::string(lua_tostring(L,-1)).find("\"ready\":false")!=std::string::npos);assert(subscribed&&!retired&&commits==0);lua_settop(L,0);
 assert(luaL_dostring(L,"return prepare('other','reviewed-v1')")!=LUA_OK);assert(subscribed&&commits==0);lua_settop(L,0);
 assert(luaL_dostring(L,"return prepare(123,'reviewed-v1')")!=LUA_OK);assert(commits==0);lua_settop(L,0);
 assert(luaL_dostring(L,"return prepare('abc_1_2','reviewed-v1','extra')")!=LUA_OK);assert(commits==0);lua_settop(L,0);
 quiet=true;assert(luaL_dostring(L,"return prepare('abc_1_2','reviewed-v1')")==LUA_OK);assert(std::string(lua_tostring(L,-1)).find("\"ready\":true")!=std::string::npos);assert(retired&&!subscribed&&commits==1);lua_settop(L,0);
 assert(luaL_dostring(L,"return identity()") == LUA_OK);assert(std::string(lua_tostring(L,-1)).find("reviewed-v1")!=std::string::npos);
 lua_close(L);std::cout<<"actual Lua ABI callback: 6 scenarios PASS\n";
}
