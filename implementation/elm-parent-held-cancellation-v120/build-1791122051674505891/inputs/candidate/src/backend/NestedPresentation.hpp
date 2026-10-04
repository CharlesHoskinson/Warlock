#pragma once
#include "BufferDimensions.hpp"
#include <array>
#include <cstdint>
#include <limits>
namespace Aquamarine::NestedPolicy {
// Private policy: ACKed parent logical geometry is distinct from child mode pixels.
struct Presentation {
    struct Snapshot { uint64_t generation = 0; int width = 1280, height = 720; bool fullscreen = false, maximized = false; };
    Snapshot pending, acked, committed;
    bool staged = false, destroyed = false, exhausted = false, invalid = false;
    int pixelWidth = 0, pixelHeight = 0;
    void stage(int w, int h, bool fullscreen = false, bool maximized = false) {
        if (destroyed || exhausted || invalid) return;
        if (w < 0 || h < 0) { invalid = true; staged = true; return; }
        pending = acked;
        pending.width = w > 0 ? w : acked.width;
        pending.height = h > 0 ? h : acked.height;
        pending.fullscreen = fullscreen; pending.maximized = maximized;
        staged = true;
    }
    bool acknowledge() {
        if (destroyed || exhausted || invalid) return false;
        if (acked.generation == std::numeric_limits<uint64_t>::max()) { exhausted = true; return false; }
        pending.generation = acked.generation + 1;
        acked = pending; staged = false;
        return true;
    }
    bool current(uint64_t generation) const { return !destroyed && !exhausted && !invalid && !staged && generation != 0 && generation == acked.generation; }
    bool preflight(double mw, double mh, bool hasBuffer, double bw, double bh, bool explicitNull, bool formatValid, bool viewport) const {
        return current(acked.generation) && viewport && formatValid && validPixelDimensions(mw, mh) &&
            validPixelDimensions(acked.width, acked.height) && !explicitNull && (!hasBuffer || bufferMatchesMode(bw, bh, mw, mh));
    }
    bool queueCommit(uint64_t generation, int width, int height) {
        if (!current(generation) || !validPixelDimensions(width, height)) return false;
        committed = acked; pixelWidth = width; pixelHeight = height; return true;
    }
    bool inputAllowed() const { return current(committed.generation); }
    bool identityMapping() const { return inputAllowed() && pixelWidth == committed.width && pixelHeight == committed.height; }
    void destroy() { destroyed = true; committed.generation = 0; }
};
// Paired releases remain deliverable while geometry is fenced. No synthesized presses.
struct BalancedButtons {
    std::array<uint32_t, 32> held{};
    bool admit(uint32_t button, bool pressed, bool mappingReady) {
        if (!button) return false;
        for (auto& value : held) {
            if (value != button) continue;
            if (pressed) return false;
            value = 0; return true;
        }
        if (!pressed || !mappingReady) return false;
        for (auto& value : held) if (!value) { value = button; return true; }
        return false;
    }
};
}
