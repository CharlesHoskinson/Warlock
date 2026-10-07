#pragma once
#include "preview_broker.hpp"

namespace preview::demand {
struct Policy { Limits limits; Id<Lifetime> lifetime; Id<Clock> clock; uint64_t minimumInterval; };
struct NativeDemand {
    uint64_t entry, lease;
    Scope scope;
    Id<Origin> origin;
    uint64_t cost;
    bool visible;
};
struct Version { uint64_t lease; Id<Origin> origin; Context context; auto operator<=>(const Version&) const = default; };
struct Slot {
    NativeDemand latest;
    bool open;
    std::optional<Version> requested;
    std::optional<Job> capture;
};
struct Attempt {
    enum class Status { Started, NotReady, Capacity, Exhausted, NativeRejected } status{Status::NotReady};
    std::optional<Job> job;
    Result native;
};
// This class is native provider state, never a JSON authority or UI policy model.
// The caller supplies authenticated native observations and retains every broker
// control receipt until exact acknowledgement. nativeBroker() is allocator-only.
class Coordinator {
    friend class bridge::ImportedClients;
    Policy policy_;
    std::unique_ptr<Broker> ownedBroker_;
    Broker& broker_;
    std::map<uint64_t,Slot> slots_;
    bool canForgetRetired(uint64_t entry,const Binding& owner,Id<Incarnation> subject)const {
        const auto slot=slots_.find(entry);
        return slot==slots_.end() || (slot->second.latest.scope.binding==owner && slot->second.latest.scope.context.incarnation==subject);
    }
    void forgetRetired(uint64_t entry)noexcept {slots_.erase(entry);}
    uint64_t observedNow_{};
    std::optional<uint64_t> lastAttempt_;
    bool valid(const NativeDemand& d) const {
        const auto& s=d.scope; const auto& b=s.binding; const auto& c=s.context;
        return d.entry && d.lease && d.origin.value && d.cost && d.cost<=policy_.limits.bytes &&
            b.lifetime==policy_.lifetime && c.lifetime==policy_.lifetime && s.clock==policy_.clock &&
            b.session.value && b.frontend.value && c.incarnation.value && c.output.value &&
            c.privacy.value && c.rendering.value && c.scene.value && c.content.value &&
            s.now && s.now>=observedNow_;
    }
    static bool eligible(const NativeDemand& d) {
        return d.visible && d.scope.present && d.scope.sourceLive && !d.scope.locked && d.scope.gpuReady;
    }
    std::vector<Receipt> cancelOwned(uint64_t entry) {
        std::vector<Receipt> result;
        for(const auto& r:broker_.inspect()) {
            if(r.entry!=entry || r.terminal) continue;
            auto outcome=broker_.cancel(entry,r.job.binding,r.job);
            result.insert(result.end(),outcome.receipts.begin(),outcome.receipts.end());
        }
        return result;
    }
public:
    explicit Coordinator(Policy policy):policy_(policy),ownedBroker_(std::make_unique<Broker>(policy.limits)),broker_(*ownedBroker_) {
        if(!policy.lifetime.value || !policy.clock.value || !policy.minimumInterval)
            throw std::invalid_argument("Explicit native clock and positive pacing policy");
    }
    // The URI endpoint owns the physical Broker. It must outlive this scheduler.
    // Borrowing never copies ownership, capacity counters or replay history.
    Coordinator(Policy policy,Broker& broker):policy_(policy),broker_(broker) {
        const auto limits=broker.limits();
        if(!policy.lifetime.value || !policy.clock.value || !policy.minimumInterval ||
           policy.limits.entries!=limits.entries || policy.limits.records!=limits.records ||
           policy.limits.items!=limits.items || policy.limits.bytes!=limits.bytes)
            throw std::invalid_argument("Demand policy must match the shared native broker");
    }
    Coordinator(const Coordinator&)=delete;
    Coordinator& operator=(const Coordinator&)=delete;
    Coordinator(Coordinator&&)=delete;
    Coordinator& operator=(Coordinator&&)=delete;
    struct Observation { bool accepted; std::vector<Receipt> receipts; };
    Observation observe(const NativeDemand& d) {
        if(!valid(d)) return {false,{}};
        auto old=slots_.find(d.entry);
        if(old!=slots_.end()) {
            const auto& s=old->second;
            if(d.lease<s.latest.lease ||
               (d.lease==s.latest.lease && ((!s.open && d.visible) ||
                d.scope.binding!=s.latest.scope.binding || d.origin!=s.latest.origin ||
                d.scope.context.incarnation!=s.latest.scope.context.incarnation))) return {false,{}};
        } else if(slots_.size()>=policy_.limits.entries) return {false,{}};
        if(!broker_.enroll(d.entry,d.scope,d.cost)) {
            if(old!=slots_.end()) old->second.open=false;
            return {false,cancelOwned(d.entry)};
        }
        observedNow_=d.scope.now;
        if(old==slots_.end()) old=slots_.emplace(d.entry,Slot{d,d.visible,{}, {}}).first;
        else { old->second.latest=d; old->second.open=d.visible; }
        auto receipts=eligible(d) ? std::vector<Receipt>{} : cancelOwned(d.entry);
        poll();
        return {true,std::move(receipts)};
    }
    // Producer completion unlocks scheduling, not physical charge or ownership.
    // Only trusted Broker state is used, never frontend flags or elapsed timers.
    void poll() {
        const auto records=broker_.inspect();
        for(auto& [entry,slot]:slots_) {
            if(!slot.capture) continue;
            bool retained=false;
            for(const auto& r:records) {
                if(r.entry==entry && r.job==*slot.capture) {
                    retained=true;
                    if(r.producerDone) slot.capture.reset();
                    break;
                }
            }
            // Broker erases an admitted record only after physical destruction
            // and exact terminal acknowledgement. This native absence is that
            // retirement proof, not a frontend flag or process disappearance.
            if(!retained) slot.capture.reset();
        }
    }
    Attempt start(uint64_t entry,uint64_t originalDeadline) {
        poll();
        auto it=slots_.find(entry);
        if(it==slots_.end()) return {};
        auto& slot=it->second; const auto& d=slot.latest;
        const Version wanted{d.lease,d.origin,d.scope.context};
        if(!slot.open || !eligible(d) || slot.capture || slot.requested==wanted ||
           originalDeadline<=d.scope.now || d.scope.now!=observedNow_) return {};
        if(lastAttempt_ && (d.scope.now<*lastAttempt_ || false)) return {};
        // capacity is scheduling feedback, never a fabricated operation outcome.
        if(broker_.recordCount()>=policy_.limits.records || broker_.activeItems()>=policy_.limits.items ||
           d.cost>policy_.limits.bytes-broker_.charge()) return {Attempt::Status::Capacity,{}, {}};
        const uint64_t floor=broker_.requestFloor(entry);
        if(floor==UINT64_MAX) return {Attempt::Status::Exhausted,{}, {}};
        const Job job{d.scope.binding,d.scope.context,{floor+1},d.origin,d.scope.clock,originalDeadline};
        auto result=broker_.acquire(entry,d.scope.binding,job);
        lastAttempt_=d.scope.now;
        if(result.status==Result::Status::Admitted) {
            slot.requested=wanted; slot.capture=job;
            return {Attempt::Status::Started,job,std::move(result)};
        }
        if(result.status==Result::Status::Refused) slot.requested=wanted;
        return {Attempt::Status::NativeRejected,job,std::move(result)};
    }
    Broker& nativeBroker() { return broker_; }
    const Broker& nativeBroker() const { return broker_; }
    const Slot& inspect(uint64_t entry) const { return slots_.at(entry); }
    uint64_t now() const { return observedNow_; }
    size_t slotCount()const noexcept{return slots_.size();}
    std::optional<uint64_t> lastAttempt() const { return lastAttempt_; }
};
}
