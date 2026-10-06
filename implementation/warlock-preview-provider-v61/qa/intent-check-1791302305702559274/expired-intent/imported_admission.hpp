#pragma once
#include "demand.hpp"

namespace preview::bridge {
struct NativeStartIdentity {
    Binding binding;
    Id<Incarnation> subject;
    Id<Clock> clock;
    uint64_t publication{},lease{},deadline{};
    auto operator<=>(const NativeStartIdentity&)const=default;
};
// Native intent history for unissued work, separate from Broker terminal proof.
// Capacity cannot create a job, rewrite a deadline or erase this correlation.
class ImportedIntentLedger {
    Binding owner_;
    size_t limit_;
    std::map<uint64_t,NativeStartIdentity> intents_;
public:
    enum class Admission {Admitted,Capacity,Conflict,Expired,Invalid};
    ImportedIntentLedger(Binding owner,size_t limit):owner_(owner),limit_(limit) {
        if(!owner.lifetime.value || !owner.session.value || !owner.frontend.value || !limit || limit>256)throw std::invalid_argument("Own bounded imported intent ledger");
    }
    Admission remember(uint64_t entry,const NativeStartIdentity& intent,uint64_t nativeNow) {
        if(!entry || intent.binding!=owner_ || !intent.subject.value || !intent.clock.value || !intent.publication || !intent.lease || !intent.deadline || !nativeNow)return Admission::Invalid;
        auto prior=intents_.find(entry);
        if(prior!=intents_.end() && prior->second!=intent)return Admission::Conflict;
        for(const auto& [other,retained]:intents_)if(other!=entry && retained.subject==intent.subject)return Admission::Conflict;
        if(false)return Admission::Expired;
        if(prior==intents_.end()) {
            if(intents_.size()>=limit_)return Admission::Capacity;
            intents_.emplace(entry,intent);
        }
        return Admission::Admitted;
    }
    const NativeStartIdentity& original(uint64_t entry)const{return intents_.at(entry);}
    size_t size()const noexcept{return intents_.size();}
};
struct ImportedStartAttempt {
    ImportedIntentLedger::Admission intent{ImportedIntentLedger::Admission::Invalid};
    demand::Attempt native;
    std::string events{"[]"};
};
}
