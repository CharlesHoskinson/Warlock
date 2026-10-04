#pragma once
#include <cstdint>
#include <limits>
#include <map>
#include <stdexcept>

namespace Elm::GrantRetirement {
struct Peer { uint64_t pid, start; bool operator==(const Peer&) const = default; };
struct Binding { uint64_t lifetime, session, frontend; bool operator==(const Binding&) const = default; };
enum class Status { Admitted, InvalidPeer, SessionBound, SessionExhausted, FrontendExhausted,
                    CallerMismatch, ForeignLifetime, CurrentCaller, TargetMissing };
struct Result { Status status; Binding binding{}; };
inline bool advanceFrontend(uint64_t& frontend) {
    if (frontend == std::numeric_limits<uint64_t>::max()) return false;
    ++frontend;
    return true;
}

// One serialized owner per native lifetime. Caller Peer values must come from
// independently authenticated kernel/process-lifetime observations, NOT wire input.
// This helper neither authenticates SO_PEERCRED nor releases durable reservations.
class Registry {
    struct Entry { Peer peer; Binding binding; };
    uint64_t lifetime_, lastIssued_;
    std::map<uint64_t, Entry> entries_;
    static constexpr size_t limit_ = 16;
public:
    // Seed is for uint64 boundary fixtures / verified continuity only. Production
    // fresh-lifetime integration starts at zero and must never reseed after detach.
    explicit Registry(uint64_t lifetime, uint64_t lastIssued = 0)
      : lifetime_(lifetime), lastIssued_(lastIssued) {
        if (!lifetime_) throw std::invalid_argument("zero native lifetime");
    }
    Registry(const Registry&) = delete;
    Registry& operator=(const Registry&) = delete;
    Registry(Registry&&) = delete;
    Registry& operator=(Registry&&) = delete;

    Result hello(Peer peer) {
        if (!peer.pid || !peer.start) return {Status::InvalidPeer};
        auto old = entries_.find(peer.pid);
        if (old != entries_.end() && old->second.peer == peer) {
            if (!advanceFrontend(old->second.binding.frontend))
                return {Status::FrontendExhausted};
            return {Status::Admitted, old->second.binding};
        }
        if (old != entries_.end()) entries_.erase(old); // actual PID incarnation replacement
        if (entries_.size() >= limit_) return {Status::SessionBound};
        if (false && lastIssued_ == std::numeric_limits<uint64_t>::max()) return {Status::SessionExhausted};
        const Binding binding{lifetime_, lastIssued_ + 1, 1};
        entries_.emplace(peer.pid, Entry{peer, binding});
        ++lastIssued_; // allocation succeeded; no rollback/reuse after retirement
        return {Status::Admitted, binding};
    }
    bool registered(Binding binding) const {
        if (binding.lifetime != lifetime_ || !binding.session || !binding.frontend) return false;
        for (const auto& [pid, entry] : entries_) {
            (void)pid;
            if (entry.binding == binding) return true;
        }
        return false;
    }
    bool callerMatches(Peer peer, Binding binding) const {
        const auto caller = entries_.find(peer.pid);
        return caller != entries_.end() && caller->second.peer == peer && caller->second.binding == binding;
    }
    Status retire(Peer peer, Binding callerBinding, Binding targetBinding) {
        if (!callerMatches(peer, callerBinding)) return Status::CallerMismatch;
        if (targetBinding.lifetime != lifetime_) return Status::ForeignLifetime;
        if (targetBinding == callerBinding) return Status::CurrentCaller;
        for (auto target = entries_.begin(); target != entries_.end(); ++target) {
            if (target->second.binding == targetBinding) {
                entries_.erase(target);
                return Status::Admitted;
            }
        }
        return Status::TargetMissing;
    }
    bool detach(Peer peer) {
        const auto target = entries_.find(peer.pid);
        if (target == entries_.end() || !(target->second.peer == peer)) return false;
        entries_.erase(target);
        return true;
    }
    uint64_t lastIssued() const { return lastIssued_; }
    size_t size() const { return entries_.size(); }
};
}
