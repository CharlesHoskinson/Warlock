#pragma once
#include <algorithm>
#include <cmath>
#include <optional>
namespace Pointer::ParentPolicy {
struct Point { double x, y; bool operator==(const Point&) const = default; };
struct Box { double x, y, width, height; };
struct NormalizedPosition {
    std::optional<Point> point;
    void clear() { point.reset(); }
    bool remember(double x, double y) {
        clear();
        if (!std::isfinite(x) || !std::isfinite(y)) return false;
        point = Point{std::clamp(x,0.0,1.0),std::clamp(y,0.0,1.0)};
        return true;
    }
    std::optional<Point> project(Box box) const {
        if (!point || !std::isfinite(box.x) || !std::isfinite(box.y) ||
            !std::isfinite(box.width) || !std::isfinite(box.height) || box.width<=0 || box.height<=0) return std::nullopt;
        const Point result{point->x,point->y};
        if (!std::isfinite(result.x) || !std::isfinite(result.y)) return std::nullopt;
        return result;
    }
};
}
