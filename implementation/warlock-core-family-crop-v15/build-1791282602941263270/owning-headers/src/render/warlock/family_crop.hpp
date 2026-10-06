#pragma once
#include "preview_png.hpp"
#include <cmath>
#include <limits>
namespace preview::capture {
struct CropRect {double x,y,width,height;};
struct FamilyCropPlan {int64_t pixelX,pixelY;double scale;Plan image;};
// Call only with compositor-owned contributor extents. This pure planner does
// not authenticate membership, attest style/fidelity or confer pixel authority.
inline std::optional<FamilyCropPlan> familyCropPlan(std::span<const CropRect> rects,double scale) {
    if(rects.empty() || rects.size()>512 || !std::isfinite(scale) || scale<=0)return {};
    double left=std::numeric_limits<double>::infinity(),top=left,right=-left,bottom=-left;
    for(const auto& rect:rects) {
        if(!std::isfinite(rect.x) || !std::isfinite(rect.y) || !std::isfinite(rect.width) || !std::isfinite(rect.height) || rect.width<=0 || rect.height<=0)return {};
        const double x=rect.x*scale,y=rect.y*scale,r=(rect.x+rect.width)*scale,b=(rect.y+rect.height)*scale;
        for(double value:{x,y,r,b})if(!std::isfinite(value) || std::abs(value)>INT32_MAX)return {};
        left=std::min(left,x);top=std::min(top,y);right=std::max(right,r);bottom=std::max(bottom,b);
    }
    const double x=std::floor(left),y=std::floor(top),r=std::ceil(right),b=std::ceil(bottom),width=r-x,height=b-y;
    if(width<1 || height<1 || width>4096 || height>4096)return {};
    const auto image=plan(static_cast<uint32_t>(width),static_cast<uint32_t>(height));if(!image)return {};
    return FamilyCropPlan{static_cast<int64_t>(x),static_cast<int64_t>(y),scale,*image};
}
}
