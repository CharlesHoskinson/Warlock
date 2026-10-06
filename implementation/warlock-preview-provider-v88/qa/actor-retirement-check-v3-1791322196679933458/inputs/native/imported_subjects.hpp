#pragma once
#include "preview_broker.hpp"
#include <initializer_list>

namespace preview::bridge {
// Native C membership, independent of vector position. Issuance never resets;
// the future aggregate retirement transaction must erase every owner together.
// No removal API is exposed until that transaction and Elm settlement exist.
class ImportedSubjects {
    friend class ImportedClients;
    std::map<uint64_t,Id<Incarnation>> active_;
    size_t limit_;
    uint64_t issuedThrough_{};
    void forgetRetired(uint64_t entry)noexcept {active_.erase(entry);}
public:
    struct Pending { uint64_t entry;Id<Incarnation> subject;std::map<uint64_t,Id<Incarnation>>::node_type node; };
    explicit ImportedSubjects(size_t limit,std::initializer_list<Id<Incarnation>> subjects):limit_(limit) {
        if(!limit || limit>256)throw std::invalid_argument("Bounded native active subjects");
        for(auto subject:subjects)append(subject);
    }
    std::optional<uint64_t> find(Id<Incarnation> subject)const {
        for(const auto& [entry,owned]:active_)if(owned==subject)return entry;
        return {};
    }
    bool exhausted()const noexcept{return issuedThrough_==UINT64_MAX;}
    Pending stage(Id<Incarnation> subject)const {
        if(!subject.value || find(subject) || active_.size()>=limit_ || exhausted())
            throw std::invalid_argument("Distinct staged native subject and bounded nonreused serial");
        std::map<uint64_t,Id<Incarnation>> staged;
        const auto entry=issuedThrough_+1;staged.emplace(entry,subject);
        return {entry,subject,staged.extract(entry)};
    }
    void commit(Pending&& pending) {
        if(exhausted() || pending.entry!=issuedThrough_+1 || !pending.subject.value ||
           active_.size()>=limit_ || find(pending.subject) || pending.node.empty() ||
           pending.node.key()!=pending.entry || pending.node.mapped()!=pending.subject)
            throw std::invalid_argument("Exact staged native membership commit");
        active_.insert(std::move(pending.node));issuedThrough_=pending.entry;
    }
    uint64_t append(Id<Incarnation> subject) {
        if(!subject.value || find(subject) || active_.size()>=limit_ || exhausted())
            throw std::invalid_argument("Distinct native subject and nonreused bounded serial");
        auto pending=stage(subject);const auto entry=pending.entry;commit(std::move(pending));return entry;
    }
    size_t size()const noexcept{return active_.size();}
    uint64_t issuedThrough()const noexcept{return issuedThrough_;}
    const auto& active()const noexcept{return active_;}
};
}
