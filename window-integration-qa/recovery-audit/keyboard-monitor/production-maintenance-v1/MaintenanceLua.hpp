#pragma once
#include <lua.hpp>
#include <functional>
#include <string>
namespace OmarchyA11yMaintenance {
struct Context {
 std::string signature,packageID;
 std::function<bool()> quiescent;
 std::function<void()> retire;
};
inline int identity(lua_State* L,const Context& context) {
 const auto value="{\"instance\":\""+context.signature+"\",\"packageID\":\""+context.packageID+"\"}";
 lua_pushlstring(L,value.data(),value.size());return 1;
}
inline int prepare(lua_State* L,const Context& context) {
 // Two exact tokens, no coercion of Lua numbers or inferred session fallback.
 if(lua_gettop(L)!=2||lua_type(L,1)!=LUA_TSTRING||lua_type(L,2)!=LUA_TSTRING)
  return luaL_error(L,"prepare_unload requires exact instance and package strings");
 size_t firstLength=0,secondLength=0;
 const auto* first=lua_tolstring(L,1,&firstLength);const auto* second=lua_tolstring(L,2,&secondLength);
 if(std::string(first,firstLength)!=context.signature||std::string(second,secondLength)!=context.packageID)
  return luaL_error(L,"maintenance target identity mismatch");
 const bool ready=context.quiescent();
 if(ready)context.retire(); // actual bridge atomically stops policy + pointer work
 const auto value="{\"instance\":\""+context.signature+"\",\"packageID\":\""+context.packageID+"\",\"ready\":"+(ready?"true":"false")+"}";
 lua_pushlstring(L,value.data(),value.size());return 1;
}
}
