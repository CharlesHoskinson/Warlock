#pragma once
#include <cmath>
#include <algorithm>
#include <initializer_list>
#include <limits>
#include <optional>
namespace Pointer::BufferPolicy {
struct PixelSize { int width, height; bool operator==(const PixelSize&) const = default; };
// Allocate for the rendered cursor, including image/output scaling and rotation.
// Finite planes retain their required size; unlimited planes use the full extent.
inline std::optional<PixelSize> cursorBufferSize(double width, double height, double imageScale,
                                                double outputScale, int transform, double capWidth, double capHeight) {
    for (const double v : {width, height, imageScale, outputScale})
        if (!std::isfinite(v) || v <= 0) return std::nullopt;
    if (transform < 0 || transform > 7) return std::nullopt;
    long double w = std::ceil(static_cast<long double>(width) / imageScale * outputScale);
    long double h = std::ceil(static_cast<long double>(height) / imageScale * outputScale);
    if (transform % 2) std::swap(w, h);
    constexpr auto limit = std::numeric_limits<int>::max();
    if (!std::isfinite(w) || !std::isfinite(h) || w < 1 || h < 1 || w > limit || h > limit)
        return std::nullopt;
    if (capWidth == -1 && capHeight == -1) return PixelSize{static_cast<int>(w), static_cast<int>(h)};
    if (!std::isfinite(capWidth) || !std::isfinite(capHeight) || capWidth < 1 || capHeight < 1 ||
        capWidth > limit || capHeight > limit || std::floor(capWidth) != capWidth || std::floor(capHeight) != capHeight ||
        w > capWidth || h > capHeight) return std::nullopt;
    return PixelSize{static_cast<int>(capWidth), static_cast<int>(capHeight)};
}
}
