#include "MaintenanceLua.hpp"
#include "production_runtime.hpp"
#include <cassert>
#include <iostream>
using namespace OmarchyA11yMaintenance;
bool quiet=false,watch=true,grab=true,retired=false;unsigned commits=0,reads=0;
Context context{"abc_1_2","reviewed-v2",std::string(64,'a'),[]{return ":1.5";},[](const std::string& client){++reads;return Status{retired,quiet,quiet,client==":1.7",!grab&&client==":1.7"};},[]{++reads;return quiet;},[]{retired=true;watch=grab=false;++commits;}};
int prepare(lua_State* L){return OmarchyA11yMaintenance::prepare(L,context);}
int identity(lua_State* L){return OmarchyA11yMaintenance::identity(L,context);}
int capability(lua_State* L){return OmarchyA11yMaintenance::capability(L,context);}
int main(){
 auto* L=luaL_newstate();assert(L);luaL_openlibs(L);
 for(auto row:{std::pair<const char*,lua_CFunction>{"prepare",::prepare},std::pair<const char*,lua_CFunction>{"identity",::identity},std::pair<const char*,lua_CFunction>{"capability",::capability}}){lua_pushcfunction(L,row.second);lua_setglobal(L,row.first);}
 const std::string tokens="'abc_1_2','reviewed-v2','"+std::string(64,'a')+"'";
 auto run=[&](const std::string& code,bool pass){lua_settop(L,0);const auto status=luaL_dostring(L,code.c_str());assert((status==LUA_OK)==pass);return status==LUA_OK?std::string(lua_tostring(L,-1)):std::string();};
 assert(run("return prepare("+tokens+")",true).find("\"ready\":false")!=std::string::npos);assert(watch&&grab&&!retired&&commits==0);
 const auto before=reads;
 for(const auto& code:std::initializer_list<std::string>{"return prepare('other','reviewed-v2','"+std::string(64,'a')+"')","return prepare('abc_1_2','reviewed-v2','stale')",std::string("return prepare(123,'reviewed-v2','nonce')"),"return prepare("+tokens+",'extra')"})run(code,false);
 assert(reads==before&&commits==0&&watch&&grab);
 assert(run("return capability("+tokens+",':1.7')",true).find("\"callerPreReplay\":false")!=std::string::npos);
 grab=false;assert(run("return capability("+tokens+",':1.7')",true).find("\"callerPreReplay\":true")!=std::string::npos);assert(!retired&&commits==0);
 assert(run("return capability("+tokens+",':1.8')",true).find("\"registered\":false")!=std::string::npos);
 run("return capability("+tokens+",'invalid')",false);
 quiet=true;assert(run("return prepare("+tokens+")",true).find("\"ready\":true")!=std::string::npos);assert(retired&&!watch&&!grab&&commits==1);
 assert(run("return identity()",true).find(std::string(64,'a'))!=std::string::npos);
 context.incarnation=std::string(64,'b');quiet=false;retired=false;watch=grab=true;const auto beforeReload=reads;
 run("return prepare("+tokens+")",false);assert(reads==beforeReload&&commits==1&&!retired&&watch&&grab);
 run("return identity(1)",false);
 const auto a=ProductionRuntime::nonce(),b=ProductionRuntime::nonce();assert(a.size()==64&&b.size()==64&&a!=b);
 assert(!ProductionRuntime::allowed("/tmp/not-a-session",nullptr));assert(!ProductionRuntime::allowed("/run/user/0",nullptr,getuid()));
 assert(quote("\"\n")=="\"\\\"\\u000a\"");
 assert(ProductionRuntime::scopeAllowed("0::/user.slice/qa-harness.slice/qa-harness-real_12.scope\n"));
 assert(!ProductionRuntime::scopeAllowed("0::/qa-harness.slice/qa-harness-real.scope-extra\n"));
 assert(!ProductionRuntime::scopeAllowed("0::/qa-harnessXslice/qa-harness-real.scope\n"));
 assert(!ProductionRuntime::scopeAllowed("0::/user.slice/ordinary.scope\n"));
 const std::string bus="unix:path=/run/user/1000/bus";
 assert(ProductionRuntime::busAddressAllowed(bus,bus));
 assert(ProductionRuntime::busAddressAllowed(bus+",guid="+std::string(32,'a'),bus));
 assert(!ProductionRuntime::busAddressAllowed(bus+";unix:path=/tmp/other",bus));
 assert(!ProductionRuntime::busAddressAllowed(bus+",guid=bad",bus));
 assert(!ProductionRuntime::busAddressAllowed(bus+",guid="+std::string(32,'a')+";unix:path=/tmp/other",bus));
 assert(!ProductionRuntime::busAddressAllowed("unix:path=/run/user/1000/other",bus));
 lua_close(L);std::cout<<"actual Lua ABI + fresh nonce/runtime: 24 scenarios PASS\n";
}
