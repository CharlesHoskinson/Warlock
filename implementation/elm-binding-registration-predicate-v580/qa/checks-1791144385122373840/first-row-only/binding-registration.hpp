#pragma once
#include <cstdint>
namespace Elm::Registration {
// Conservatively count retained records, including peers whose liveness is unknown.
template<class Sessions> bool contains(const Sessions& sessions, uint64_t id, uint64_t frontend) {
    for (const auto& entry : sessions)
        return entry.second.id == id && entry.second.frontend == frontend;
    return false;
}
}
