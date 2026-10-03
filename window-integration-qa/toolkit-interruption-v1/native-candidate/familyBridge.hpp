#pragma once
struct lua_State;
int luaWindowFamilies(lua_State* state);
int luaModalFocusBridgeAvailable(lua_State* state);
void initFamilyBridge();
void exitFamilyBridge();
