#pragma once
#include <hyprutils/math/Box.hpp>
#include <cmath>
#include <climits>
#include <limits>
#include <optional>
#include <algorithm>
namespace Elm::ProspectiveGeometry {
using Hyprutils::Math::CBox;
using Hyprutils::Math::Vector2D;
using Hyprutils::Math::SBoxExtents;
enum class Operation { Maximize, RestoreOrdinary };
struct Bounds { Vector2D minimum, maximum; };
struct Input {
    Operation operation;
    CBox logical, visual;
    SBoxExtents reserved;
    Vector2D xdgGeometryOrigin;
    double monitorScale;
    Bounds raw, layout;
};
struct Projection { CBox logical, visual, real; Vector2D configure; };
inline bool finite(Vector2D x) { return std::isfinite(x.x) && std::isfinite(x.y); }
inline bool nonnegative(Vector2D x) { return finite(x) && x.x>=0 && x.y>=0; }
inline bool supportedBox(CBox x) {
    return finite(x.pos()) && nonnegative(x.size()) && x.rot==0 &&
           std::abs(x.x)<=INT_MAX && std::abs(x.y)<=INT_MAX && x.w<=INT_MAX && x.h<=INT_MAX;
}
inline bool positiveBox(CBox x) { return supportedBox(x) && x.w>0 && x.h>0; }
inline bool axis(double value,double lower,double upper,bool raw) {
    return value>=lower && ((raw && upper==0) || value<=upper);
}
inline bool validBounds(Bounds x,bool raw) {
    if(!nonnegative(x.minimum) || !nonnegative(x.maximum))return false;
    for(int a=0;a<2;++a) {
        const double lo=a?x.minimum.y:x.minimum.x, hi=a?x.maximum.y:x.maximum.x;
        if(raw && hi==0)continue;
        if(hi<=0 || lo>=hi)return false; // fixed either axis remains excluded
    }
    return true;
}
// Experimental profile guard only: layout dimensions are real-valued while
// raw dimensions constrain floor(real). Do not intersect those spaces directly.
inline bool variableConfigureAxis(double rawMinimum,double rawMaximum,double layoutMinimum,double layoutMaximum) {
    const double lower=std::max({1.0,std::ceil(rawMinimum),std::floor(layoutMinimum)});
    const double upper=std::min({static_cast<double>(INT_MAX),
                                rawMaximum==0?static_cast<double>(INT_MAX):std::floor(rawMaximum),
                                std::floor(layoutMaximum)});
    // Strict inequality rejects empty and singleton integer intervals alike.
    // No floating-point endpoint is converted to int before it is range-bounded.
    return lower<upper;
}
inline std::optional<Projection> project(Input input) {
    if((input.operation!=Operation::Maximize && input.operation!=Operation::RestoreOrdinary) ||
       !positiveBox(input.logical) || !supportedBox(input.visual) ||
       !nonnegative(input.reserved.topLeft) || !nonnegative(input.reserved.bottomRight) ||
       !finite(input.xdgGeometryOrigin) || input.xdgGeometryOrigin!=Vector2D{0,0} ||
       !std::isfinite(input.monitorScale) || input.monitorScale<=0 ||
       !validBounds(input.raw,true) || !validBounds(input.layout,false))return std::nullopt;
    if(!variableConfigureAxis(input.raw.minimum.x,input.raw.maximum.x,input.layout.minimum.x,input.layout.maximum.x) ||
       !variableConfigureAxis(input.raw.minimum.y,input.raw.maximum.y,input.layout.minimum.y,input.layout.maximum.y))return std::nullopt;
    input.logical.round(); input.visual.round();
    if(!positiveBox(input.logical))return std::nullopt;
    CBox real=input.logical;
    if(input.operation==Operation::Maximize) {
        const CBox selected=input.visual.empty()?input.logical:input.visual;
        real=CBox{selected.pos()+input.reserved.topLeft,
                  selected.size()-(input.reserved.topLeft+input.reserved.bottomRight)};
    }
    if(!positiveBox(real) || real.w>INT_MAX || real.h>INT_MAX)return std::nullopt;
    // Wayland sendConfigure receives positive doubles converted to signed integers.
    const Vector2D configure{std::floor(real.w),std::floor(real.h)};
    if(configure.x<1 || configure.y<1)return std::nullopt;
    if(!axis(real.w,input.raw.minimum.x,input.raw.maximum.x,true) ||
       !axis(configure.y,input.raw.minimum.y,input.raw.maximum.y,true) ||
       !axis(real.w,input.layout.minimum.x,input.layout.maximum.x,false) ||
       !axis(real.h,input.layout.minimum.y,input.layout.maximum.y,false))return std::nullopt;
    return Projection{input.logical,input.visual,real,configure};
}
}
