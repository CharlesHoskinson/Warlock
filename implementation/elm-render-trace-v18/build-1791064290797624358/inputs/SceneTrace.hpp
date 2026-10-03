#pragma once
#include "desktop/DesktopTypes.hpp"
#include <cstdint>
#include <vector>
namespace Render::SceneTrace {
    struct Draw { PHLWINDOWREF window; bool hadWindow=false, main=false, popup=false; };
    struct Frame { int64_t monitor=-1; uint64_t serial=0; bool complete=false, overflow=false, committed=false; std::vector<Draw> draws; };
    // Experimental draw-dispatch evidence only. Commit is not presentation.
    void begin(const PHLMONITOR& monitor) noexcept;
    void draw(const PHLMONITOR& monitor,const PHLWINDOW& window,bool main,bool popup) noexcept;
    void finish(const PHLMONITOR& monitor,bool committed) noexcept;
    std::vector<Frame> snapshots();
}
