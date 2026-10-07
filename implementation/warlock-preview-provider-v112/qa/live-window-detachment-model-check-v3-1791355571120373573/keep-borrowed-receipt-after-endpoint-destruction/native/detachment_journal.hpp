#pragma once
#include "preview_wire.hpp"

namespace preview::bridge {
// A scoped preview completion never says that a native window is Retired.
struct ActorDetached {
    Binding binding;Id<Incarnation> subject;
    uint64_t epoch{},entry{},entryIssuedThrough{},requestFloor{};
};
class DetachmentJournal {
    struct Row {ActorDetached fact;std::string ready;bool complete{};uint64_t ordinal{};std::string wire;};
    Binding owner_;const uint64_t popup_,epoch_;const size_t limit_;
    std::map<uint64_t,Row> rows_;uint64_t issued_{},acknowledged_{},pollAfter_{};
    void receiver(uint64_t popup,uint64_t epoch)const {
        require(popup==popup_ && epoch==epoch_,"Original scoped detachment receiver and epoch");
    }
    static uint64_t floor(JsonObject* object){const std::string_view text=Json::text(object,"requestFloor");return text=="0"?0:decimal(text);}
    bool matches(const ActorDetached& fact)const {
        return fact.binding==owner_ && fact.epoch==epoch_ && fact.subject.value && fact.entry && fact.entry<=fact.entryIssuedThrough;
    }
    uint64_t ackOrdinal(uint64_t popup,uint64_t epoch,std::string_view raw)const {
        receiver(popup,epoch);Json message(raw);auto object=message.object();
        Json::fields(object,{"kind","binding","receiverEpoch","deliveryOrdinal"});
        require(std::string_view(Json::text(object,"kind"))=="detach-delivery-ack" &&
            decodeBinding(Json::child(object,"binding"))==owner_ && message.counter("receiverEpoch")==epoch_,
            "Distinct typed scoped detachment processing acknowledgment");
        return message.counter("deliveryOrdinal");
    }
public:
    class Prepared {
        friend class DetachmentJournal;DetachmentJournal* owner_;uint64_t entry_,ordinal_;std::string wire_;
        Prepared(DetachmentJournal* owner,uint64_t entry,uint64_t ordinal,std::string wire):owner_(owner),entry_(entry),ordinal_(ordinal),wire_(std::move(wire)){}
    public:
        Prepared(const Prepared&)=delete;Prepared& operator=(const Prepared&)=delete;
        Prepared(Prepared&& other)noexcept:owner_(std::exchange(other.owner_,nullptr)),entry_(other.entry_),ordinal_(other.ordinal_),wire_(std::move(other.wire_)){}
        const std::string& wire()const noexcept{return wire_;}
    };
    DetachmentJournal(Binding owner,uint64_t popup,uint64_t epoch,size_t limit=256):owner_(owner),popup_(popup),epoch_(epoch),limit_(limit){
        require(owner.lifetime.value && owner.session.value && owner.frontend.value && popup && epoch && limit && limit<=256,
            "Bounded original native scoped detachment journal");
    }
    DetachmentJournal(const DetachmentJournal&)=delete;DetachmentJournal& operator=(const DetachmentJournal&)=delete;
    size_t size()const noexcept{return rows_.size();}
    uint64_t issued()const noexcept{return issued_;}
    uint64_t acknowledged()const noexcept{return acknowledged_;}
    bool hasReadiness()const noexcept {for(const auto& [entry,row]:rows_){(void)entry;if(!row.complete)return true;}return false;}
    bool ready(const ActorDetached& fact,std::string_view raw)const {
        require(matches(fact),"Exact native actor before scoped readiness decoding");
        Json message(raw);auto object=message.object();
        Json::fields(object,{"kind","binding","receiverEpoch","subject","entry","entryIssuedThrough","requestFloor"});
        return std::string_view(Json::text(object,"kind"))=="detach-ready" && decodeBinding(Json::child(object,"binding"))==owner_ &&
            message.counter("receiverEpoch")==epoch_ && message.counter("subject")==fact.subject.value &&
            message.counter("entry")==fact.entry && message.counter("entryIssuedThrough")==fact.entryIssuedThrough && floor(object)==fact.requestFloor;
    }
    // The C issuer/dispatcher validates the canonical original native purpose.
    // This journal retains its input; it supplies no physical cleanup authority.
    bool acceptReady(uint64_t popup,uint64_t epoch,const ActorDetached& fact,std::string_view raw){
        receiver(popup,epoch);require(!raw.empty() && raw.size()<=4096,"Bounded original scoped readiness");
        if(!ready(fact,raw))return false;
        auto old=rows_.find(fact.entry);
        if(old!=rows_.end())return !old->second.complete && old->second.ready==raw;
        if(rows_.size()>=limit_)return false;
        rows_.emplace(fact.entry,Row{fact,std::string(raw),false,0,{}});return true;
    }
    struct Readiness {ActorDetached fact;std::string wire;};
    std::optional<Readiness> nextReadiness(uint64_t popup,uint64_t epoch){
        receiver(popup,epoch);if(rows_.empty())return {};
        auto row=rows_.upper_bound(pollAfter_);
        for(size_t examined=0;examined<rows_.size();++examined){
            if(row==rows_.end())row=rows_.begin();
            if(!row->second.complete){Readiness result{row->second.fact,row->second.ready};pollAfter_=row->first;return result;}
            ++row;
        }
        return {};
    }
    // Trusted ImportedClients preflight must establish native quarantine and
    // every physical/backend/reader/proof/receiver/control barrier first.
    std::optional<Prepared> prepare(uint64_t popup,uint64_t epoch,const ActorDetached& fact){
        receiver(popup,epoch);require(matches(fact),"Exact original scoped completion");auto row=rows_.find(fact.entry);
        require(row!=rows_.end() && !row->second.complete && ready(fact,row->second.ready),"Original retained scoped readiness before completion");
        if(issued_==UINT64_MAX)return {};
        auto wire=Wire().integer("detachProtocol",1).text("kind","native-preview-binding-detach-delivery")
            .begin("binding").binding(owner_).end().counter("receiverEpoch",epoch_).counter("deliveryOrdinal",issued_+1)
            .begin("event").text("kind","native-preview-actor-detached").text("identity","family:"+std::to_string(fact.subject.value))
            .counter("subject",fact.subject.value).counter("entry",fact.entry).counter("entryIssuedThrough",fact.entryIssuedThrough)
            .text("requestFloor",std::to_string(fact.requestFloor)).end().finish();
        return Prepared(this,fact.entry,issued_+1,std::move(wire));
    }
    bool commit(Prepared&& prepared)noexcept {
        auto row=rows_.find(prepared.entry_);
        if(prepared.owner_!=this || row==rows_.end() || row->second.complete || issued_==UINT64_MAX || prepared.ordinal_!=issued_+1)return false;
        row->second.ordinal=prepared.ordinal_;row->second.wire=std::move(prepared.wire_);row->second.complete=true;
        issued_=prepared.ordinal_;prepared.owner_=nullptr;return true;
    }
    const std::string* nextCompletion(uint64_t popup,uint64_t epoch)const {
        receiver(popup,epoch);if(acknowledged_==issued_)return nullptr;
        for(const auto& [entry,row]:rows_){(void)entry;if(row.complete && row.ordinal==acknowledged_+1)return &row.wire;}
        return nullptr;
    }
    std::optional<ActorDetached> completionForAcknowledgment(uint64_t popup,uint64_t epoch,std::string_view raw)const {
        const auto ordinal=ackOrdinal(popup,epoch,raw);
        if(acknowledged_==UINT64_MAX || ordinal!=acknowledged_+1 || ordinal>issued_)return {};
        for(const auto& [entry,row]:rows_){(void)entry;if(row.complete && row.ordinal==ordinal)return row.fact;}
        return {};
    }
    bool acknowledge(uint64_t popup,uint64_t epoch,std::string_view raw){
        const auto ordinal=ackOrdinal(popup,epoch,raw);if(ordinal<=acknowledged_)return true;
        if(!completionForAcknowledgment(popup,epoch,raw))return false;
        for(auto row=rows_.begin();row!=rows_.end();++row)if(row->second.complete && row->second.ordinal==ordinal){rows_.erase(row);acknowledged_=ordinal;return true;}
        return false;
    }
};
}
