#pragma once
#include <cstdint>
#include <limits>
class CWLSurfaceResource;
namespace Warlock {
class AppliedRevision {
    uint64_t revision_=0;bool exhausted_=false;
public:
    explicit AppliedRevision(uint64_t initial=0):revision_(initial){}
    uint64_t value()const noexcept{return exhausted_?0:revision_;}
    bool apply()noexcept{if(exhausted_ || revision_==std::numeric_limits<uint64_t>::max()){exhausted_=true;return false;}++revision_;return true;}
};
// Native read-only fact: after actual state/texture application, including a
// synchronized child which does not emit its ordinary commit notification.
// Zero means uncommitted, unavailable or exhausted; it never grants authority.
uint64_t appliedSurfaceRevision(const CWLSurfaceResource* surface) noexcept;
}
