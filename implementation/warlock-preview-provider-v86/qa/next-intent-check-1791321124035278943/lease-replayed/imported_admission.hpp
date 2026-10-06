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
    friend class ImportedClients;
    Binding owner_;
    size_t limit_;
    std::map<uint64_t,NativeStartIdentity> intents_;
    // At most one predecessor per actor; issued request floors live in Broker.
    std::map<uint64_t,NativeStartIdentity> predecessors_;
    bool canForgetRetired(uint64_t entry,const Binding& owner,Id<Incarnation> subject)const {
        for(const auto* records:{&intents_,&predecessors_}) {
            const auto record=records->find(entry);
            if(record!=records->end() && (record->second.binding!=owner || record->second.subject!=subject))return false;
        }
        return true;
    }
    void forgetRetired(uint64_t entry)noexcept {intents_.erase(entry);predecessors_.erase(entry);}
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
        if(intent.deadline<=nativeNow)return Admission::Expired;
        if(prior==intents_.end()) {
            if(intents_.size()>=limit_)return Admission::Capacity;
            intents_.emplace(entry,intent);
        }
        return Admission::Admitted;
    }
    const NativeStartIdentity& original(uint64_t entry)const{return intents_.at(entry);}
    Admission advance(uint64_t entry,const NativeStartIdentity& intent,uint64_t nativeNow) {
        if(!entry || intent.binding!=owner_ || !intent.subject.value || !intent.clock.value ||
           !intent.publication || !intent.lease || !intent.deadline || !nativeNow ||
           nativeNow>UINT64_MAX-2000000000ULL || intent.deadline<=nativeNow ||
           intent.deadline>nativeNow+2000000000ULL)return Admission::Invalid;
        auto prior=intents_.find(entry);
        if(prior==intents_.end())return Admission::Invalid;
        const auto& old=prior->second;
        // An explicit new picker lease cannot replace pending work or replay
        // an older intent. Only an expired, unissued enrollment calls this API.
        if(old.binding!=intent.binding || old.subject!=intent.subject || old.clock!=intent.clock ||
           old.deadline>nativeNow || intent.publication<=old.publication || false)
            return Admission::Conflict;
        predecessors_.insert_or_assign(entry,old);prior->second=intent;
        return Admission::Admitted;
    }
    std::optional<NativeStartIdentity> predecessor(uint64_t entry)const {
        auto found=predecessors_.find(entry);
        return found==predecessors_.end()?std::nullopt:std::optional{found->second};
    }
    size_t predecessorCount()const noexcept{return predecessors_.size();}
    std::optional<NativeStartIdentity> find(uint64_t entry)const {
        auto found=intents_.find(entry);
        return found==intents_.end()?std::nullopt:std::optional{found->second};
    }
    size_t size()const noexcept{return intents_.size();}
};
struct ImportedStartAttempt {
    ImportedIntentLedger::Admission intent{ImportedIntentLedger::Admission::Invalid};
    demand::Attempt native;
    std::string events{"[]"};
    // Presentation feedback never enters the job/terminal-proof stream.
    std::string feedback{"[]"};
};
}
