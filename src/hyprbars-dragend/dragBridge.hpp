#pragma once
#include <hyprland/src/helpers/math/Math.hpp>
#include <hyprland/src/desktop/view/Window.hpp>

void initDragBridge();
void exitDragBridge();
struct lua_State;
int luaDragBridgeAvailable(lua_State* state);
int luaFileDragActive(lua_State* state);
bool startCaptionDrag(const PHLWINDOW& owner, const Vector2D& press);
