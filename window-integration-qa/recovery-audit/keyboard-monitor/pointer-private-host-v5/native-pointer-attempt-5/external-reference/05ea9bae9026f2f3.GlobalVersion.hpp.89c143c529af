#pragma once
#include <algorithm>
#include <cstdint>

namespace Aquamarine::RegistryVersion {
constexpr uint32_t negotiate(uint32_t advertised, uint32_t supported, uint32_t required) {
    const auto common = std::min(advertised, supported);
    return common >= required ? common : 0;
}
}
