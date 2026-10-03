#pragma once
#include <lua.hpp>
#include <functional>
#include <string>
namespace OmarchyA11yMaintenance {
inline std::string quote(const std::string& v) {
 std::string out="\"";
 for(unsigned char c:v) {if(c=='"'||c=='\\'){out+='\\';out+=c;}else if(c<32){const char* h="0123456789abcdef";out+="\\u00";out+=h[c>>4];out+=h[c&15];}else out+=c;}
 return out+'"';
}
struct Status {bool retiring=false,quiescent=false,unloadQuiescent=false,registered=false,preReplay=false;};
struct Context {
 std::string signature,packageID,incarnation;
 std::function<std::string()> owner;
 std::function<Status(const std::string&)> status;
 std::function<bool()> quiescent;
 std::function<void()> retire;
};
inline std::string identityJSON(const Context& c) {
 return "{\"instance\":"+quote(c.signature)+",\"packageID\":"+quote(c.packageID)+",\"incarnation\":"+quote(c.incarnation)+",\"managerOwner\":"+quote(c.owner())+"}";
}
inline int identity(lua_State* L,const Context& c) {
 if(lua_gettop(L)!=0)return luaL_error(L,"identity requires no arguments");
 const auto v=identityJSON(c);lua_pushlstring(L,v.data(),v.size());return 1;
}
inline bool matches(lua_State* L,const Context& c,int count) {
 if(lua_gettop(L)!=count)return false;
 const std::string* values[]={&c.signature,&c.packageID,&c.incarnation};
 for(int i=1;i<=3;++i){if(lua_type(L,i)!=LUA_TSTRING)return false;size_t size=0;const char* value=lua_tolstring(L,i,&size);if(std::string(value,size)!=*values[i-1])return false;}
 return true;
}
inline int prepare(lua_State* L,const Context& c) {
 if(!matches(L,c,3))return luaL_error(L,"maintenance target/incarnation mismatch");
 const bool ready=c.quiescent();if(ready)c.retire();
 auto v=identityJSON(c);v.pop_back();v+=",\"ready\":";v+=ready?"true}":"false}";
 lua_pushlstring(L,v.data(),v.size());return 1;
}
inline int capability(lua_State* L,const Context& c) {
 if(!matches(L,c,4)||lua_type(L,4)!=LUA_TSTRING)return luaL_error(L,"capability target/incarnation mismatch");
 size_t size=0;const char* value=lua_tolstring(L,4,&size);const std::string client(value,size);
 // Unique bus names contain no escapes; actual registration check remains native.
 if(client.empty()||client.front()!=':'||client.size()>255||client.find_first_not_of(":0123456789.")!=std::string::npos)return luaL_error(L,"invalid unique client");
 const auto s=c.status(client);auto v=identityJSON(c);v.pop_back();
 const auto b=[](bool flag){return flag?"true":"false";};
 v+=",\"retiring\":"+std::string(b(s.retiring))+",\"quiescent\":"+b(s.quiescent)+",\"unloadQuiescent\":"+b(s.unloadQuiescent)+",\"registered\":"+b(s.registered)+",\"callerPreReplay\":"+b(s.preReplay)+"}";
 lua_pushlstring(L,v.data(),v.size());return 1;
}
}
