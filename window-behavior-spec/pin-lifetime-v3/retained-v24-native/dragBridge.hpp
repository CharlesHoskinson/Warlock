#pragma once
#include <hyprland/src/helpers/math/Math.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/state/FocusState.hpp>

void initDragBridge();
void exitDragBridge();
struct lua_State;
int luaDragBridgeAvailable(lua_State* state);
int luaFileDragActive(lua_State* state);
int luaRetireGestureCurrent(lua_State* state);
int luaWindowLifetime(lua_State* state);
bool startCaptionDrag(const PHLWINDOW& owner, const Vector2D& press);

bool preserveCapturedGestureFocus(const PHLWINDOW& owner, const PHLWINDOW& independentlyFocused, Desktop::eFocusReason reason);
