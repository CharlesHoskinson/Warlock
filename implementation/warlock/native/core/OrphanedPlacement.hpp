#pragma once
#include <cmath>

namespace WarlockPlacement {
// An orphan has no trustworthy old output origin. Wrap its logical coordinate
// into the destination extent, then anchor it to that output's actual origin.
// Keep size, workspace and ordinary existing-monitor translation unchanged.
inline double orphanedCoordinate(double coordinate, double origin, double extent) {
    if (!std::isfinite(coordinate) || !std::isfinite(extent) || extent <= 0)
        return origin;
    const double remainder = std::fmod(coordinate, extent);
    const double relative = remainder < 0 ? remainder + extent : remainder;
    // Adding an extremely small negative remainder can round to the upper
    // boundary. That boundary belongs to the next output, so wrap it to zero.
    return origin + (relative < extent ? relative : 0);
}
}
