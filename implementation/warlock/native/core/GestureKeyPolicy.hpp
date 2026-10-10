#pragma once

namespace WarlockGesture {
// Ordinary keyboard traffic does not end a captured native pointer gesture.
// Escape press is explicit cancellation; its release cannot end another one.
inline bool cancelKey(bool active, bool pressed, bool escape) {
    return active && pressed && escape;
}
}
