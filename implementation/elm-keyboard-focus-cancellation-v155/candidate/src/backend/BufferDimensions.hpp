#pragma once
#include <cmath>
#include <limits>
namespace Aquamarine::NestedPolicy {
inline bool validPixelDimensions(double width, double height) {
    return std::isfinite(width) && std::isfinite(height) &&
           width > 0 && height > 0 &&
           width <= std::numeric_limits<int>::max() && height <= std::numeric_limits<int>::max() &&
           width == std::floor(width) && height == std::floor(height);
}
inline bool bufferMatchesMode(double bw, double bh, double mw, double mh) {
    return validPixelDimensions(mw, mh) && validPixelDimensions(bw, bh) && bw == mw && bh == mh;
}
}
