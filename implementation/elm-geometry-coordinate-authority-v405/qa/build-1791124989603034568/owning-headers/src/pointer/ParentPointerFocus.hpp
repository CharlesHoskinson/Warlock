#pragma once
#include <hyprutils/memory/SharedPtr.hpp>
namespace Desktop::View { class CWindow; }
namespace Pointer {
void refreshParentHitTest(const Hyprutils::Memory::CSharedPointer<Desktop::View::CWindow>& window);
}
