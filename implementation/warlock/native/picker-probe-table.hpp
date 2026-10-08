#pragma once
#include <cstdint>
#include <sys/types.h>
#include <tuple>

// The owner thread selects a product incarnation only for the duration of one
// authenticated IPC/descriptor callback. Zero retains the frozen QA namespace.
struct CaptureKey {
    inline static thread_local uint64_t selected=0;
    pid_t peer;
    uint64_t subject;
    CaptureKey(pid_t peer):peer(peer),subject(selected) {}
    CaptureKey(pid_t peer,uint64_t subject):peer(peer),subject(subject) {}
    bool operator<(const CaptureKey& other) const {return std::tie(peer,subject)<std::tie(other.peer,other.subject);}
};
class CaptureSelection {
    const uint64_t previous=CaptureKey::selected;
public:
    explicit CaptureSelection(uint64_t subject) {CaptureKey::selected=subject;}
    ~CaptureSelection() {CaptureKey::selected=previous;}
    CaptureSelection(const CaptureSelection&)=delete;
    CaptureSelection& operator=(const CaptureSelection&)=delete;
};
