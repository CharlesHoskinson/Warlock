#pragma once

#include "../../DesktopTypes.hpp"
#include "../../../layout/target/Target.hpp"
#include "../../../managers/fullscreen/FullscreenController.hpp"
#include "NativePinPolicy.hpp"
#include <cstdint>
#include <functional>
#include <optional>
#include <unordered_map>
#include <vector>
#include <string_view>
#include <unordered_set>
#include "../../../helpers/signal/Signal.hpp"

namespace Layout {
    class CAlgorithm;
}

namespace Desktop::Pin {
    struct SNativeMaxRestore {
        PHLWINDOWREF              owner;
        WP<Desktop::View::CGroup> group;
        std::vector<PHLWINDOWREF> members;
        WP<Layout::ITarget>       nativeTarget;
        WP<Layout::ITarget>       layoutTarget;
        WP<Layout::CSpace>        space;
        PHLMONITORREF             output;
        Vector2D                  outputOrigin;
        Layout::STargetBox        box;
        bool                      floating      = false;
        bool                      pinOrigin     = false;
        bool                      pinManaged    = false;
        bool                      restoreUsable = true;
        bool                      layoutHandled = false;
        uint64_t                  generation    = 0;
    };

    struct SNativeMaxTransfer {
        PHLWINDOW                          owner;
        SP<Layout::ITarget>                target;
        SP<Layout::ITarget>                nativeTarget;
        SP<Layout::CSpace>                 sourceSpace;
        SP<Layout::CSpace>                 destination;
        SNativeMaxRestore                  restore;
        Fullscreen::SFullscreenMode        modes;
        SP<Layout::CAlgorithm>             sourceAlgorithm;
        WP<Fullscreen::IFullscreenHandler> sourceHandler;
        uint64_t                           operation = 0;
    };

    struct SNativeTransferOutcome {
        uint64_t                    operation        = 0;
        uint64_t                    generation       = 0;
        bool                        accepted         = false;
        bool                        actualModesKnown = false;
        Fullscreen::SFullscreenMode before;
        Fullscreen::SFullscreenMode actual;
        uintptr_t                   target = 0, space = 0, workspace = 0, output = 0;
        std::string                 reason;
    };

    struct SNativeMaxProjection {
        bool               valid         = false;
        bool               pinOrigin     = false;
        bool               pinManaged    = false;
        bool               floating      = false;
        bool               layoutHandled = false;
        uint64_t           generation    = 0;
        uintptr_t          target        = 0;
        uintptr_t          layoutTarget  = 0;
        uintptr_t          space         = 0;
        Layout::STargetBox box;
    };

    class CNativePinState {
      public:
        CNativePinState();
        bool                                  capture(PHLWINDOW window, bool layoutHandled);
        SNativeMaxProjection                  snapshot(PHLWINDOW window) const;
        bool                                  admits(PHLWINDOW window) const;
        bool                                  maxOrigin(PHLWINDOW window) const;
        bool                                  ownedUnpinReady(PHLWINDOW window) const;
        std::optional<SNativeTransferOutcome> transferOutcome(PHLWINDOW window) const;
        void                                  setOrigin(PHLWINDOW window, bool pinned);
        bool                                  restore(PHLWINDOW window);
        void                                  rebind(PHLWINDOW window, const SNativeMaxRestore& record);
        std::optional<SNativeMaxRestore>      record(PHLWINDOW window) const;
        void                                  retire(PHLWINDOW window);
        bool                                  live(PHLWINDOW window) const;
        void                                  refreshFamily();
        void                                  invalidateReturn(PHLWINDOW window);
        std::optional<SNativeMaxTransfer>     beginTransfer(PHLWINDOW window, const SP<Layout::CSpace>& destination);
        bool                                  finishTransfer(const SNativeMaxTransfer& transfer);
        bool                                  transferring(PHLWINDOW window) const;
        bool                                  rebaseOutput(PHLWINDOW window);
        bool                                  synchronize(PHLWINDOW window);

      private:
        CHyprSignalListener                                        m_open, m_close, m_pin, m_floating, m_fullscreen, m_workspace;
        std::unordered_set<PHLWINDOWREF>                           m_protected;
        bool                                                       m_refreshing = false;
        std::unordered_set<PHLWINDOWREF>                           m_closed;
        uint64_t                                                   m_nextGeneration = 1;
        std::unordered_map<WP<Layout::ITarget>, SNativeMaxRestore> m_records;
        std::unordered_map<PHLWINDOWREF, uint64_t>                 m_transferring;
        std::unordered_map<PHLWINDOWREF, SNativeTransferOutcome>   m_transferOutcomes;
        uint64_t                                                   m_nextOperation = 1;
        void                                                       reap();
    };

    UP<CNativePinState>&   state();
    uint32_t               capabilityVersion();
    std::string_view       policyBuildIdentity();
    bool                   eligible(PHLWINDOW window);
    bool                   effective(PHLWINDOW window);
    bool                   effective(PHLWINDOWREF window);
    bool                   familyEdge(PHLWINDOW child, PHLWINDOW parent);
    std::vector<PHLWINDOW> band();
    PHLWINDOW              deepestModal(PHLWINDOW owner);
}
