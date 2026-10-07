#pragma once
#include "preview_retirement.hpp"

namespace preview::bridge {
// Native transport bookkeeping only. ImportedClients must validate physical
// and terminal-proof settlement under its Endpoint lock before committing a
// prepared completion. Neither a ready JSON field nor a delivery ACK grants
// cleanup. All access stays serialized with the original receiver epoch.
class RetirementJournal {
    struct Row {
        IncarnationRetirement observation;
        std::optional<ActorRetired> completion;
        uint64_t ordinal{};
        std::string wire;
        bool readyAccepted{};
        std::string acceptedReady{};
    };
    Binding owner_;
    const uint64_t popup_,epoch_;
    const size_t limit_;
    std::map<uint64_t,Row> rows_;
    uint64_t issued_{},acknowledged_{},pollAfter_{};
    void receiver(uint64_t popup,uint64_t epoch,Binding binding) const {
        require(popup==popup_ && epoch==epoch_ && binding==owner_,
            "Original retirement delivery receiver, epoch and binding");
    }
    bool valid(const IncarnationRetirement& value) const {
        return value.binding==owner_ && value.clock.value==owner_.lifetime.value &&
            value.subject.value && value.request && value.sequence && value.now &&
            value.subject.value<=value.issuedThrough && value.state==IncarnationState::Retired;
    }
public:
    class Prepared {
        friend class RetirementJournal;
        RetirementJournal* owner_;
        uint64_t entry_,ordinal_;
        ActorRetired fact_;
        std::string wire_;
        Prepared(RetirementJournal* owner,uint64_t entry,uint64_t ordinal,
                ActorRetired fact,std::string wire):owner_(owner),entry_(entry),ordinal_(ordinal),
                fact_(fact),wire_(std::move(wire)){}
    public:
        Prepared(const Prepared&)=delete;
        Prepared& operator=(const Prepared&)=delete;
        Prepared(Prepared&& value)noexcept:owner_(std::exchange(value.owner_,nullptr)),
            entry_(value.entry_),ordinal_(value.ordinal_),fact_(value.fact_),wire_(std::move(value.wire_)){}
        Prepared& operator=(Prepared&& value)noexcept {
            if(this!=&value) {
                owner_=std::exchange(value.owner_,nullptr);entry_=value.entry_;
                ordinal_=value.ordinal_;fact_=value.fact_;wire_=std::move(value.wire_);
            }
            return *this;
        }
        const std::string& wire()const noexcept{return wire_;}
    };
    RetirementJournal(Binding binding,uint64_t popup,uint64_t epoch,size_t limit=256):
        owner_(binding),popup_(popup),epoch_(epoch),limit_(limit) {
        require(binding.lifetime.value && binding.session.value && binding.frontend.value &&
            popup && epoch && limit>0 && limit<=256,"Bounded own retirement delivery journal");
    }
    RetirementJournal(const RetirementJournal&)=delete;
    RetirementJournal& operator=(const RetirementJournal&)=delete;
    size_t size()const noexcept{return rows_.size();}
    uint64_t issued()const noexcept{return issued_;}
    uint64_t acknowledged()const noexcept{return acknowledged_;}
    bool hasReadiness()const noexcept {for(const auto& [entry,row]:rows_){(void)entry;if(row.readyAccepted && !row.completion)return true;}return false;}
    // Caller has already checked the original live C/ImportedClients entry.
    // A transport record alone must never enroll a native subject or actor.
    bool retain(uint64_t popup,uint64_t epoch,uint64_t entry,
            const IncarnationRetirement& observation) {
        receiver(popup,epoch,observation.binding);
        require(entry && valid(observation),"Exact permanent retirement observation");
        auto prior=rows_.find(entry);
        if(prior!=rows_.end()) {
            const auto& old=prior->second.observation;
            require(old.subject==observation.subject && old.request==observation.request &&
                old.sequence==observation.sequence && old.now==observation.now &&
                old.issuedThrough==observation.issuedThrough,"Retain original observation correlation");
            return true;
        }
        if(rows_.size()>=limit_ || issued_==UINT64_MAX)return false;
        auto wire=encodeIncarnationRetirement(observation);
        rows_.emplace(entry,Row{observation,{},0,std::move(wire)});
        return true;
    }
    const IncarnationRetirement* observation(uint64_t popup,uint64_t epoch,
            Binding binding,uint64_t entry)const {
        receiver(popup,epoch,binding);
        auto row=rows_.find(entry);return row==rows_.end()?nullptr:&row->second.observation;
    }
    bool ready(uint64_t popup,uint64_t epoch,uint64_t entry,std::string_view raw)const {
        // Receiver validation precedes even command decoding or cache lookup.
        receiver(popup,epoch,owner_);
        Json message(raw);auto object=message.object();
        Json::fields(object,{"kind","binding","subject","observationRequest","observationSequence"});
        require(std::string_view(Json::text(object,"kind"))=="retire-ready" &&
            decodeBinding(Json::child(object,"binding"))==owner_,"Typed own retirement readiness");
        auto row=rows_.find(entry);if(row==rows_.end())return false;
        const auto& original=row->second.observation;
        return message.counter("subject")==original.subject.value &&
            message.counter("observationRequest")==original.request &&
            message.counter("observationSequence")==original.sequence;
    }
    bool acceptReady(uint64_t popup,uint64_t epoch,uint64_t entry,std::string_view raw) {
        require(!raw.empty() && raw.size()<=4096,"Bounded immutable original retirement readiness");
        if(!ready(popup,epoch,entry,raw))return false;
        auto row=rows_.find(entry);
        require(row!=rows_.end() && !row->second.completion,"Pending original readiness row");
        if(!row->second.readyAccepted) {
            // Allocate before publishing acceptance. Polling must carry these
            // exact bytes; reconstructed JSON can invalidate its native ticket.
            std::string retained(raw);row->second.acceptedReady=std::move(retained);
            row->second.readyAccepted=true;
        }
        return true;
    }
    struct Readiness {uint64_t entry;Id<Incarnation> subject;std::string wire;};
    std::optional<Readiness> nextReadiness(uint64_t popup,uint64_t epoch,Binding binding) {
        receiver(popup,epoch,binding);
        if(rows_.empty())return {};
        auto row=rows_.upper_bound(pollAfter_);
        for(size_t examined=0;examined<rows_.size();++examined) {
            if(row==rows_.end())row=rows_.begin();
            if(row->second.readyAccepted && !row->second.completion) {
                const auto& original=row->second.observation;
                require(!row->second.acceptedReady.empty(),"Original immutable accepted readiness bytes");
                auto wire=row->second.acceptedReady;
                // Construct the retry before advancing transport selection.
                Readiness result{row->first,original.subject,std::move(wire)};
                pollAfter_=row->first;return result;
            }
            ++row;
        }
        return {};
    }
    std::vector<Readiness> pendingReadiness(uint64_t popup,uint64_t epoch,Binding binding)const {
        receiver(popup,epoch,binding);std::vector<Readiness> result;
        for(const auto& [entry,row]:rows_) {
            if(!row.readyAccepted || row.completion)continue;
            const auto& original=row.observation;
            require(!row.acceptedReady.empty(),"Original immutable accepted readiness bytes");
            auto wire=row.acceptedReady;
            result.push_back({entry,original.subject,std::move(wire)});
        }
        return result;
    }
    // Allocate the final envelope before native all-map removal. There is no
    // issued ordinal or journal mutation until commit, so aborted preparation
    // cannot create a delivery gap or strand existing observations.
    std::optional<Prepared> prepare(uint64_t popup,uint64_t epoch,uint64_t entry,
            const ActorRetired& fact) {
        receiver(popup,epoch,fact.native.binding);
        const auto row=rows_.find(entry);
        require(row!=rows_.end() && !row->second.completion,"Retained pending retirement observation");
        const auto& old=row->second.observation;const auto& next=fact.native;
        require(valid(next) && fact.entry==entry && entry<=fact.entryIssuedThrough &&
            next.subject==old.subject && next.request>old.request && next.sequence>old.sequence &&
            next.now>=old.now && next.issuedThrough>=old.issuedThrough,
            "Exact later native completion of original observed actor");
        if(issued_==UINT64_MAX)return {};
        const auto ordinal=issued_+1;
        auto wire="{\"kind\":\"native-actor-retirement-delivery\",\"deliveryOrdinal\":\""+
            std::to_string(ordinal)+"\",\"fact\":"+encodeActorRetired(fact)+"}";
        return Prepared(this,entry,ordinal,fact,std::move(wire));
    }
    // Under the Endpoint lock, commit immediately before the already validated
    // noexcept erasures. A stale prepared value fails without consuming a gap.
    bool commit(Prepared&& value)noexcept {
        auto row=rows_.find(value.entry_);
        if(value.owner_!=this || row==rows_.end() || row->second.completion ||
            issued_==UINT64_MAX || value.ordinal_!=issued_+1)return false;
        row->second.completion=value.fact_;
        row->second.ordinal=value.ordinal_;
        row->second.wire=std::move(value.wire_);
        issued_=value.ordinal_;value.owner_=nullptr;
        return true;
    }
    const std::string* nextCompletion(uint64_t popup,uint64_t epoch,Binding binding)const {
        receiver(popup,epoch,binding);
        if(acknowledged_==issued_)return nullptr;
        for(const auto& [entry,row]:rows_) {
            (void)entry;
            if(row.completion && row.ordinal==acknowledged_+1)return &row.wire;
        }
        return nullptr;
    }
    // Pure inspection for the native ticket issuer. The effectful acknowledge
    // method remains the sole processing-prefix advance and row erasure.
    std::optional<ActorRetired> completionForAcknowledgment(uint64_t popup,
            uint64_t epoch,std::string_view raw)const {
        receiver(popup,epoch,owner_);
        Json message(raw);auto object=message.object();
        Json::fields(object,{"kind","binding","deliveryOrdinal"});
        require(std::string_view(Json::text(object,"kind"))=="retire-delivery-ack" &&
            decodeBinding(Json::child(object,"binding"))==owner_,"Original typed actor processing acknowledgment");
        const auto ordinal=message.counter("deliveryOrdinal");
        if(acknowledged_==UINT64_MAX || ordinal!=acknowledged_+1 || ordinal>issued_)return {};
        for(const auto& [entry,row]:rows_) {
            (void)entry;if(row.completion && row.ordinal==ordinal)return row.completion;
        }
        return {};
    }
    bool acknowledge(uint64_t popup,uint64_t epoch,std::string_view raw) {
        receiver(popup,epoch,owner_);
        Json message(raw);auto object=message.object();
        Json::fields(object,{"kind","binding","deliveryOrdinal"});
        require(std::string_view(Json::text(object,"kind"))=="retire-delivery-ack" &&
            decodeBinding(Json::child(object,"binding"))==owner_,"Exact own completion delivery acknowledgment");
        const auto ordinal=message.counter("deliveryOrdinal");
        if(ordinal<=acknowledged_)return true;
        if(acknowledged_==UINT64_MAX || ordinal!=acknowledged_+1 || ordinal>issued_)return false;
        for(auto row=rows_.begin();row!=rows_.end();++row) {
            if(row->second.completion && row->second.ordinal==ordinal) {
                rows_.erase(row);acknowledged_=ordinal;return true;
            }
        }
        return false;
    }
};
}
