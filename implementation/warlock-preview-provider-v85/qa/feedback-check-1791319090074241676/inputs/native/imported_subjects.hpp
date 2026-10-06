#pragma once
#include "preview_broker.hpp"
#include <initializer_list>

namespace preview::bridge {
// Native C membership, independent of vector position. Issuance never resets;
// the future aggregate retirement transaction must erase every owner together.
// No removal API is exposed until that transaction and Elm settlement exist.
class ImportedSubjects {
    std::map<uint64_t,Id<Incarnation>> active_;
    size_t limit_;
    uint64_t issuedThrough_{};
public:
    explicit ImportedSubjects(size_t limit,std::initializer_list<Id<Incarnation>> subjects):limit_(limit) {
        if(!limit || limit>256)throw std::invalid_argument("Bounded native active subjects");
        for(auto subject:subjects)append(subject);
    }
    std::optional<uint64_t> find(Id<Incarnation> subject)const {
        for(const auto& [entry,owned]:active_)if(owned==subject)return entry;
        return {};
    }
    bool exhausted()const noexcept{return issuedThrough_==UINT64_MAX;}
    uint64_t append(Id<Incarnation> subject) {
        if(!subject.value || find(subject) || active_.size()>=limit_ || exhausted())
            throw std::invalid_argument("Distinct native subject and nonreused bounded serial");
        const auto entry=issuedThrough_+1;
        active_.emplace(entry,subject);issuedThrough_=entry;return entry;
    }
    size_t size()const noexcept{return active_.size();}
    uint64_t issuedThrough()const noexcept{return issuedThrough_;}
    const auto& active()const noexcept{return active_;}
};
}
