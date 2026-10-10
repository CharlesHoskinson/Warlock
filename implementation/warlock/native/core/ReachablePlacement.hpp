#pragma once
#include <algorithm>
#include <cmath>

namespace WarlockPlacement {
// Preserve size and already reachable placement. Recover the top-left input
// region when a usable output area changes; oversized windows keep their size.
inline double reachableCoordinate(double coordinate, double origin, double extent, double windowExtent) {
    if (!std::isfinite(coordinate) || !std::isfinite(origin) || !std::isfinite(extent) || !std::isfinite(windowExtent) || extent <= 0 || windowExtent <= 0)
        return coordinate;
    const double visible = std::min({windowExtent, 32.0, extent});
    return std::clamp(coordinate, origin, origin + extent - visible);
}
}
