#pragma once
#include <array>
#include <cmath>
#include <stdexcept>

namespace OwnedCoverage {
inline constexpr const char* policy="top-left-half-open-pixel-centers-v1";
struct Geometry {
    std::array<int,4> bounds;
    std::array<float,4> sample;
};
inline int first(double edge,double origin,double logical,int pixels) {
    int low=0,high=pixels;
    while(low<high){
        const int middle=low+(high-low)/2;
        const double center=origin+(double(middle)+0.5)*logical/pixels;
        if(center<edge)low=middle+1;else high=middle;
    }
    return low;
}
inline Geometry geometry(double x,double y,double width,double height,
        double ox,double oy,double logicalWidth,double logicalHeight,int pixelsWidth,int pixelsHeight){
    for(const auto value:{x,y,width,height,ox,oy,logicalWidth,logicalHeight,x+width,y+height,ox+logicalWidth,oy+logicalHeight})
        if(!std::isfinite(value))throw std::runtime_error("finite coverage geometry required");
    if(width<=0||height<=0||logicalWidth<=0||logicalHeight<=0||pixelsWidth<=0||pixelsHeight<=0||pixelsWidth>16384||pixelsHeight>16384)
        throw std::runtime_error("bounded positive coverage dimensions required");
    Geometry result{{first(x,ox,logicalWidth,pixelsWidth),first(y,oy,logicalHeight,pixelsHeight),
        first(x+width,ox,logicalWidth,pixelsWidth),first(y+height,oy,logicalHeight,pixelsHeight)},
        {float((x-ox)*pixelsWidth/logicalWidth),float((y-oy)*pixelsHeight/logicalHeight),
         float(width*pixelsWidth/logicalWidth),float(height*pixelsHeight/logicalHeight)}};
    for(const auto value:result.sample)if(!std::isfinite(value))throw std::runtime_error("finite representable coverage sample rectangle required");
    if(result.sample[2]<=0||result.sample[3]<=0)throw std::runtime_error("positive representable coverage sample extent required");
    return result;
}
inline void requireUniforms(const Geometry& expected,const float* bounds,const float* sample,unsigned error){
    if(error)throw std::runtime_error("actual coverage uniform query failed");
    for(unsigned i=0;i<4;++i)if(bounds[i]!=float(expected.bounds[i])||sample[i]!=expected.sample[i])
        throw std::runtime_error("actual coverage/sample uniforms differ from exact member geometry");
}
}
