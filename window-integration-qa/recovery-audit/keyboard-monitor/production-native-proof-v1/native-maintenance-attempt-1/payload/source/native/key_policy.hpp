#pragma once

// Staged local policy. No D-Bus calls, compositor calls, or state publication.
#include <cstdint>
#include <map>
#include <optional>
#include <set>
#include <string>
#include <utility>

namespace KeyboardMonitor {
struct Client {
    bool watch = false, full = false;
    std::set<uint32_t> modifiers;
    std::set<std::pair<uint32_t,uint32_t>> strokes;
};
struct Route {
    bool consumed = false;
    uint32_t sym = 0;
    std::set<std::string> recipients;
};
struct Result {
    bool consumed = false;
    uint32_t sym = 0;
    std::set<std::string> recipients;
};
class Policy {
    using Key = std::pair<uintptr_t,uint32_t>;
    struct Tap { uint32_t sym=0; uint64_t time=0; bool armed=false; };
    std::map<Key,Route> held;
    std::map<uintptr_t,Tap> taps;
public:
    std::map<std::string,Client> clients;
    void resetTaps() { taps.clear(); }
    void drop(const std::string& id) { clients.erase(id); resetTaps(); }
    void stop() { clients.clear(); resetTaps(); }
    void removeDevice(uintptr_t device) {
        for (auto it=held.begin();it!=held.end();) {
            if(it->first.first==device) it=held.erase(it); else ++it;
        }
        taps.erase(device);
    }
    bool quiescent() const {
        for(const auto& [key,route]:held) if(route.consumed) return false;
        return true;
    }
    bool captured(uintptr_t device,uint32_t key) const {
        const auto it=held.find({device,key});
        return it!=held.end() && it->second.consumed;
    }
    bool known(uintptr_t device,uint32_t key) const { return held.contains({device,key}); }
    std::set<uint32_t> capturedKeys(uintptr_t device) const {
        std::set<uint32_t> keys;
        for(const auto& [identity,route]:held)if(identity.first==device&&route.consumed)keys.insert(identity.second);
        return keys;
    }
    Result key(uintptr_t device,uint32_t key,uint32_t sym,uint32_t state,bool press,uint64_t now,uint32_t delay,bool alreadyNativePressed=false,bool allowed=true) {
        const Key identity{device,key};
        if(!allowed)resetTaps();
        if(press) {auto& tap=taps[device];if(tap.armed&&tap.sym!=sym)tap.armed=false;}
        auto previous=held.find(identity);
        // Routes retain suppression and original keysym even after policy/layout changes.
        if(previous!=held.end()) {
            Result result{previous->second.consumed,previous->second.sym,{}};
            for(const auto& [id,c]:clients) {
                if(!allowed)continue;
                if(c.watch || c.full || previous->second.recipients.contains(id)) result.recipients.insert(id);
            }
            if(!press) held.erase(previous);
            return result;
        }
        Result result{false,sym,{}};
        if(!allowed) {
            if(press)held.emplace(identity,Route{false,sym,{}});
            return result;
        }
        // Preexisting native presses/releases keep their original delivery route.
        if(!press || alreadyNativePressed) {
            for(const auto& [id,c]:clients) if(c.watch) result.recipients.insert(id);
            if(press) held.emplace(identity,Route{false,sym,result.recipients});
            return result;
        }
        bool modifier=false, chord=false, full=false,exactStroke=false;
        for(const auto& [id,c]:clients) {
            full |= c.full;
            exactStroke |= c.strokes.contains({sym,state});
            modifier |= c.modifiers.contains(sym);
            bool customHeld=false;
            for(const auto& [k,r]:held) if(k.first==device && c.modifiers.contains(r.sym) && r.sym!=sym) customHeld=true;
            bool claim=c.full || c.modifiers.contains(sym) || customHeld || c.strokes.contains({sym,state});
            if(c.watch || claim) result.recipients.insert(id);
            result.consumed |= claim;
            chord |= customHeld;
        }
        auto& tap=taps[device];
        const bool second=modifier && !full && !chord && !exactStroke && tap.armed && tap.sym==sym && now>=tap.time && now-tap.time<=delay;
        if(second) { result.consumed=false; tap.armed=false; }
        else if(modifier && !full && !chord && result.consumed) tap={sym,now,true};
        else if(chord) tap.armed=false;
        held.emplace(identity,Route{result.consumed,sym,result.recipients});
        return result;
    }
};

struct Mask { uint32_t depressed=0,latched=0,locked=0,group=0; };
// Explicit virtual-mask policy. Accepted/raw lock differences are retained after
// grabs end. The caller supplies per-packet suppressed lock/depressed masks from
// actual XKB key routes. Ambiguous batched modifier attribution remains a gate.
class VirtualMaskGuard {
    uint32_t correction=0;
public:
    void remapCorrection(uint32_t next) { correction=next; }
    Mask filter(Mask raw,Mask accepted,uint32_t suppressedDepressed,uint32_t controlledLocks,bool fullGrab,std::optional<uint32_t> expectedLocks=std::nullopt) {
        const auto mask=fullGrab ? UINT32_MAX : controlledLocks;
        correction=(correction & ~mask) | ((raw.locked ^ expectedLocks.value_or(accepted.locked)) & mask);
        return {raw.depressed & ~suppressedDepressed,raw.latched,raw.locked ^ correction,raw.group};
    }
    uint32_t parity() const { return correction; }
};
}
