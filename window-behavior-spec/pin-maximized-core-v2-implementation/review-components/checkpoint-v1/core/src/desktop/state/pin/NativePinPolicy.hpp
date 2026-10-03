#pragma once

#include <cstdint>
#include <cstddef>
#include <optional>
#include <vector>

namespace Desktop::Pin {
    constexpr uint32_t NATIVE_PIN_POLICY_VERSION = 1;

    struct SAdmission {
        bool live          = false;
        bool visible       = false;
        bool normalSpace   = false;
        bool restoreKnown  = false;
        bool restoreOrigin = false;
        bool targetExact   = false;
        int  internalMode  = 0;
        int  clientMode    = 0;
    };

    constexpr bool admitsNative(const SAdmission& state) {
        return state.live && state.visible && state.normalSpace && state.restoreKnown && state.targetExact && state.clientMode >= 0 && state.clientMode <= 1 &&
            (state.internalMode == 1 || (state.internalMode == 0 && state.restoreOrigin));
    }

    constexpr bool retainsMaxPin(bool pinned, int oldMode, int newMode, int clientMode) {
        return pinned && oldMode >= 0 && oldMode <= 1 && newMode >= 0 && newMode <= 1 && clientMode >= 0 && clientMode <= 1;
    }

    constexpr bool preservesProtectedPeer(bool peerPinnedMax, int requestedMode) {
        return peerPinnedMax && requestedMode == 1;
    }

    struct SBandNode {
        uintptr_t key = 0;
        int parent = -1;
    };

    // The owning renderer and hit tester consume this same bottom-to-top order.
    std::optional<std::vector<size_t>> orderBand(const std::vector<SBandNode>& nodes);

    struct SFocusAcceptance {
        bool coreOwnerExact   = false;
        bool coreSurfaceExact = false;
        bool seatSurfaceExact = false;
        bool keyboardPresent  = false;
        bool guardsCurrent    = false;
        bool ownerCurrent     = false;
    };

    constexpr bool acceptsFocus(const SFocusAcceptance& state) {
        return state.coreOwnerExact && state.coreSurfaceExact && state.seatSurfaceExact && state.keyboardPresent && state.guardsCurrent && state.ownerCurrent;
    }
}
