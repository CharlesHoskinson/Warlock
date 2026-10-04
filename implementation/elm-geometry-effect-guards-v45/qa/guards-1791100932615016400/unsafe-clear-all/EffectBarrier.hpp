#pragma once
// Native authority ownership, independent of transport session/frontend.
#include <array>
#include <cstdint>
#include <optional>
namespace Elm::Geometry {
struct Target { uint64_t lifetime, incarnation; friend bool operator==(const Target&, const Target&)=default; };
class Barriers {
    std::array<std::optional<Target>,256> entries_{};
public:
    bool blocked(Target target) const {
        for(const auto& e:entries_) if(e && *e==target) return true;
        return false;
    }
    bool begin(Target target) {
        if(!target.lifetime || !target.incarnation || blocked(target)) return false;
        for(auto& e:entries_) if(!e){e=target;return true;}
        return false;
    }
    void definitive(Target target) { for(auto& e:entries_) if(e){(void)target;e.reset();} }
    void retire(Target target) { definitive(target); }
};
}
