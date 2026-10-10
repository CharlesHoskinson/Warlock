// Shared native preflight; no independent shell/modal policy.
#pragma once
#include "core/ModalRecipient.hpp"
namespace WarlockNavigationModal {
inline constexpr uint16_t INCLUDE_BLOCKED_PARENT = WarlockModal::INCLUDE_BLOCKED_PARENT;
using WarlockModal::focusRecipient;
}
