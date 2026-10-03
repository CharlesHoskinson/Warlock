#pragma once
#include <algorithm>
#include <cstdint>
#include <map>
#include <string>

namespace PointerLocator {
// Integration state only: the authoritative coordinate/one-shot State is unchanged.
class NotificationFence {
public:
    static constexpr std::size_t MAX_NOTES=512, MAX_CALLS=16;
    static constexpr std::uint64_t DEADLINE_MS=1500;
    struct Note {
        std::string sender,name;
        std::uint64_t epoch=0,deadline=0;
        enum Phase {Queued,InFlight,Ready} phase=Queued;
        std::string snapshotOwner;
    };
    std::map<std::uint64_t,Note> notes;
    std::uint64_t nextId=0,refused=0,discarded=0,emitted=0;
    bool retired=false;
    std::size_t activeCount=0;
    bool reserve(std::size_t armed,std::size_t queries) const {
        return !retired && notes.size()+armed+queries<MAX_NOTES;
    }
    bool capture(const std::string& sender,std::uint64_t epoch,const std::string& name,std::uint64_t now) {
        if(retired||notes.size()>=MAX_NOTES||sender.empty()||name.empty()||!epoch){++refused;return false;}
        notes.emplace(++nextId,Note{sender,name,epoch,now+DEADLINE_MS,Note::Queued,{}});return true;
    }
    std::size_t active() const {return activeCount;}
    bool start(std::uint64_t id) {
        const auto it=notes.find(id);
        if(retired||it==notes.end()||it->second.phase!=Note::Queued||active()>=MAX_CALLS)return false;
        it->second.phase=Note::InFlight;++activeCount;return true;
    }
    bool complete(std::uint64_t id,const std::string& snapshotOwner) {
        const auto it=notes.find(id);
        if(retired||it==notes.end()||it->second.phase!=Note::InFlight)return false;
        it->second.phase=Note::Ready;it->second.snapshotOwner=snapshotOwner;--activeCount;return true;
    }
    bool valid(std::uint64_t id,std::uint64_t currentEpoch,const std::string& currentOwner,bool backlog,std::uint64_t now) const {
        const auto it=notes.find(id);
        if(retired||it==notes.end()||backlog)return false;
        const auto& n=it->second;
        return now<n.deadline&&n.phase==Note::Ready&&n.epoch==currentEpoch
               &&currentOwner==n.sender&&n.snapshotOwner==n.sender;
    }
    bool erase(std::uint64_t id) {
        const auto it=notes.find(id);if(it==notes.end())return false;
        if(it->second.phase==Note::InFlight)--activeCount;
        notes.erase(it);return true;
    }
    void drop(std::uint64_t id){if(erase(id))++discarded;}
    void sent(std::uint64_t id){if(erase(id))++emitted;}
    void retire(){retired=true;discarded+=notes.size();notes.clear();activeCount=0;}
};
}
