#pragma once
#include <string_view>
namespace Aquamarine::NestedPolicy {
enum class Selection { Unspecified, Wayland, Invalid };
inline Selection selection(const char* value) {
    if (!value) return Selection::Unspecified;
    return std::string_view(value) == "wayland" ? Selection::Wayland : Selection::Invalid;
}
struct ConfigureLifecycle {
    bool acknowledged = false;
    bool announced = false;
    bool destroyed = false;
    int width = 1280, height = 720;
    void stageSize(int w, int h) {
        if (destroyed) return;
        width = w > 0 ? w : 1280;
        height = h > 0 ? h : 720;
    }
    bool acknowledge() {
        if (destroyed) return false;
        acknowledged = true;
        return true;
    }
    bool announce() {
        if (!acknowledged || announced || destroyed) return false;
        announced = true;
        return true;
    }
    bool bufferAllowed() const { return acknowledged && announced && !destroyed; }
    void destroy() { destroyed = true; }
};
}
