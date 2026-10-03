#pragma once
#include <hyprland/src/desktop/view/Window.hpp>
#include <string>

struct lua_State;
// Strong owning handle, resolved before any action. No address/active fallback.
bool toggleCapturedPin(const PHLWINDOW& owner, std::string& reason);
int luaPinCapturedWindow(lua_State* state);
