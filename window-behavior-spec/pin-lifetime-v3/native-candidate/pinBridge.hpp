#pragma once
#include <hyprland/src/desktop/view/Window.hpp>
#include <string>
struct lua_State;
// All actions retain the exact strong native owner; there is no active fallback.
void initPinBridge();
void exitPinBridge();
void reloadPinBridge();
bool toggleCapturedPin(const PHLWINDOW& owner,std::string& reason);
float pinFeedbackAlpha(const PHLWINDOW& owner);
int luaPinCapturedWindow(lua_State*);
int luaPinIdentity(lua_State*);
int luaPinRequest(lua_State*);
int luaPinEvents(lua_State*);
int luaPinFeedbackEnabled(lua_State*);
// Called only after an owning core raise or a live-state event. No focus/input.
void repairPinStacking() noexcept;
int luaPinStackState(lua_State*);
int luaPinCapture(lua_State*);
int luaPinBarState(lua_State*);
