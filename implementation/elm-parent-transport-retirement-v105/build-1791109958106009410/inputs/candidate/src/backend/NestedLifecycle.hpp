#pragma once
#include <string_view>
#include "NestedPresentation.hpp"
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
    Presentation presentation;
    void stageSize(int w, int h, bool fullscreen = false, bool maximized = false) {
        if (destroyed) return;
        presentation.stage(w, h, fullscreen, maximized);
    }
    bool acknowledge() {
        if (destroyed || !presentation.acknowledge()) return false;
        acknowledged = true;
        width = presentation.acked.width; height = presentation.acked.height;
        return true;
    }
    bool announce() {
        if (!acknowledged || announced || destroyed) return false;
        announced = true;
        return true;
    }
    bool bufferAllowed() const { return acknowledged && announced && !destroyed && presentation.current(presentation.acked.generation); }
    void destroy() { destroyed = true; presentation.destroy(); }
};
}
