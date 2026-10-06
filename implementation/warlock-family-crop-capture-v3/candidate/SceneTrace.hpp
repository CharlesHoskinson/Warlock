#pragma once
#include "desktop/DesktopTypes.hpp"
#include <cstdint>
#include <vector>
#include <array>
class CWLSurfaceResource;
namespace Render::SceneTrace {
    struct Draw { PHLWINDOWREF window; uint64_t authority=0, incarnation=0; bool hadWindow=false, main=false, popup=false; uint64_t surface=0; std::array<double,4> box{}; double alpha=0; std::vector<std::array<int32_t,4>> input; };
    struct Frame { int64_t monitor=-1; uint64_t serial=0; bool complete=false, overflow=false, committed=false; std::array<double,5> output{}; int transform=0; uint64_t outputGeneration=0; std::vector<Draw> draws; };
    // Experimental draw-dispatch evidence only. Commit is not presentation.
    bool bind(const PHLWINDOW& window,uint64_t authority,uint64_t incarnation) noexcept;
    void forget(const PHLWINDOW& window) noexcept;
    void clearBindings() noexcept;
    void begin(const PHLMONITOR& monitor) noexcept;
    void draw(const PHLMONITOR& monitor,const PHLWINDOW& window,bool main,bool popup,const SP<CWLSurfaceResource>& surface,const std::array<double,4>& box,double alpha,const std::vector<std::array<int32_t,4>>& input) noexcept;
    void invalidate(const PHLMONITOR& monitor) noexcept;
    void finish(const PHLMONITOR& monitor,bool committed) noexcept;
    std::vector<Frame> snapshots();
}
