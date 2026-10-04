#pragma once
#include <algorithm>
#include <cmath>
#include <limits>
#include <optional>
namespace Elm::SizeBounds {
struct Size { double width,height; };
struct Raw { Size minimum,maximum; };
struct Layout { std::optional<Size> minimum,maximum; };
struct Axis {
    double minimum;
    std::optional<double> maximum;
    bool fixed() const { return maximum && minimum>0 && minimum==*maximum; }
    bool admits(double value) const { return std::isfinite(value) && value>0 && value>=minimum && (!maximum || value<=*maximum); }
};
struct Bounds {
    Axis horizontal,vertical;
    bool resizable() const { return !horizontal.fixed() && !vertical.fixed(); }
    bool admits(Size size) const { return resizable() && horizontal.admits(size.width) && vertical.admits(size.height); }
};
inline bool valid(Size size) { return std::isfinite(size.width) && std::isfinite(size.height) && size.width>=0 && size.height>=0; }
inline std::optional<Axis> intersect(double rawMin,double rawMax,double layoutMin,double layoutMax) {
    const double minimum=std::max(rawMin,layoutMin);
    const double rawUpper=rawMax==0?std::numeric_limits<double>::max():rawMax;
    const double upper=std::min(rawUpper,layoutMax);
    if(upper<=0 || minimum>upper)return std::nullopt;
    return Axis{minimum,upper==std::numeric_limits<double>::max()?std::nullopt:std::optional<double>{upper}};
}
inline std::optional<Bounds> derive(Raw raw,Layout layout) {
    if(!valid(raw.minimum) || !valid(raw.maximum) || (layout.minimum && !valid(*layout.minimum)) || (layout.maximum && !valid(*layout.maximum)))return std::nullopt;
    const Size minimum=layout.minimum.value_or(Size{0,0});
    const Size maximum=layout.maximum.value_or(Size{std::numeric_limits<double>::max(),std::numeric_limits<double>::max()});
    auto x=intersect(raw.minimum.width,raw.maximum.width,minimum.width,maximum.width);
    auto y=intersect(raw.minimum.height,raw.maximum.height,minimum.height,maximum.height);
    if(!x || !y)return std::nullopt;
    return Bounds{*x,*y};
}
}
