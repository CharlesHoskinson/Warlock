// Offline type check only. This object contains no plugin entry point or hooks.
#include <hyprland/src/devices/IKeyboard.hpp>
#include <hyprland/src/managers/input/InputManager.hpp>
#include <type_traits>

struct ExposedKeyboardABI : IKeyboard { using IKeyboard::updatePressed; };
static_assert(std::is_same_v<decltype(&ExposedKeyboardABI::updatePressed),bool (IKeyboard::*)(uint32_t,bool)>);
static_assert(std::is_same_v<decltype(&IKeyboard::updateModifiers),void (IKeyboard::*)(uint32_t,uint32_t,uint32_t,uint32_t)>);
static_assert(std::is_same_v<decltype(&IKeyboard::updateXkbStateWithKey),void (IKeyboard::*)(uint32_t,bool)>);
static_assert(std::is_same_v<decltype(&CInputManager::onKeyboardKey),void (CInputManager::*)(const IKeyboard::SKeyEvent&,SP<IKeyboard>)>);
static_assert(std::is_same_v<decltype(&CInputManager::onKeyboardMod),void (CInputManager::*)(SP<IKeyboard>)>);

using UpdatePressedFn=bool (*)(IKeyboard*,uint32_t,bool);
using UpdateModifiersFn=void (*)(IKeyboard*,uint32_t,uint32_t,uint32_t,uint32_t);
using OnKeyboardKeyFn=void (*)(CInputManager*,const IKeyboard::SKeyEvent&,SP<IKeyboard>);
using OnKeyboardModFn=void (*)(CInputManager*,SP<IKeyboard>);
