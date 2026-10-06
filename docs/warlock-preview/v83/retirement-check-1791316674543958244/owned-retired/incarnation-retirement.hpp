#pragma once
#include <cstdint>
#include <stdexcept>

namespace preview::retirement {
enum class State { Active, Retired, Future };

// Owner-thread membership and the lifetime's monotonic issuance frontier are
// native facts. Unmapped/minimized/suspended members are still Active. This
// observation says nothing about independent capture/storage/ACK obligations.
inline State observe(uint64_t subject, uint64_t issued, bool owned) {
    if (!subject || (owned && subject > issued))
        throw std::invalid_argument("Coherent native incarnation retirement facts");
    if (subject > issued) return State::Future;
    return State::Retired;
}
inline const char* name(State state) {
    switch (state) {
        case State::Active: return "Active";
        case State::Retired: return "Retired";
        case State::Future: return "Future";
    }
    throw std::invalid_argument("Native incarnation retirement state");
}
}
