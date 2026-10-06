#pragma once
#include <cstdint>
#include <limits>
namespace preview {
class SourceEpoch {
    uint64_t value_;
    bool exhausted_{false};
public:
    explicit SourceEpoch(uint64_t value=1):value_(value){if(!value)exhausted_=true;}
    uint64_t value()const noexcept{return value_;}
    bool available()const noexcept{return !exhausted_ && value_>0;}
    bool commit()noexcept {
        if(!available() || value_==std::numeric_limits<uint64_t>::max()){exhausted_=true;return false;}
        ++value_;return true;
    }
};
}
