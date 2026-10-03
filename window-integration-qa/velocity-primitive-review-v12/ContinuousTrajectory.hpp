#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <vector>
#include <utility>

namespace ContinuousMotion {
using Vector=std::array<double,4>; // x, y, width, height, or derivatives thereof
struct Origin {Vector rectangle,velocity,target;};
struct Sample {Vector rectangle,velocity;};
class FamilyTrajectory {
    std::vector<Origin> origins;
    double duration=0;
public:
    FamilyTrajectory(std::vector<Origin> values,double nominalSeconds):origins(std::move(values)),duration(nominalSeconds) {
        if(origins.empty()||origins.size()>64||!std::isfinite(duration)||duration<=0||duration>4)
            throw std::invalid_argument("complete bounded family and positive duration required");
        double minimum=1e-9;
        for(const auto& origin:origins){
            for(size_t i=0;i<4;++i){
                const double a=origin.rectangle[i],b=origin.target[i],v=origin.velocity[i];
                if(!std::isfinite(a)||!std::isfinite(v)||!std::isfinite(b)
                    ||std::abs(a)>400000||std::abs(b)>400000||std::abs(v)>1e9)
                    throw std::invalid_argument("finite bounded trajectory material required");
                if(i>=2&&(a<=0||b<=0))throw std::invalid_argument("positive dimensions required");
                // Cubic geometry Bezier controls: a, a+T*v/3, b, b.
                if(v>0)duration=std::min(duration,3*(400000-a)/v);
                if(v<0)duration=std::min(duration,i>=2?1.5*a/(-v):3*(a+400000)/(-v));
                // Derivative Bezier controls: v, 3*(b-a)/T-v, 0.
                const double delta=b-a;
                if(delta!=0){
                    const double headroom=delta>0?1e9+v:1e9-v;
                    if(headroom<=0)throw std::invalid_argument("endpoint has no bounded derivative duration");
                    minimum=std::max(minimum,3*std::abs(delta)/headroom);
                }
            }
        }
        if(!std::isfinite(duration)||duration<minimum)throw std::invalid_argument("no common bounded family duration");
        for(const auto& origin:origins)for(size_t i=0;i<4;++i){
            const double control=origin.rectangle[i]+duration*origin.velocity[i]/3;
            const double tangent=3*(origin.target[i]-control)/duration;
            if(!std::isfinite(control)||std::abs(control)>400000||(i>=2&&control<=0)
                ||!std::isfinite(tangent)||std::abs(tangent)>1e9)
                throw std::invalid_argument("actual floating control leaves admitted bounds");
        }
    }
    double seconds()const{return duration;}
    size_t size()const{return origins.size();}
    Sample sample(size_t index,double elapsedSeconds)const{
        if(index>=origins.size()||!std::isfinite(elapsedSeconds)||elapsedSeconds<0)
            throw std::invalid_argument("bounded family sample required");
        const auto& o=origins[index];
        if(elapsedSeconds==0)return {o.rectangle,o.velocity};
        if(elapsedSeconds>=duration)return {o.target,{0,0,0,0}};
        const double t=elapsedSeconds/duration;
        Sample result;
        for(size_t i=0;i<4;++i){
            const double control=o.rectangle[i]+duration*o.velocity[i]/3;
            const double tangent=3*(o.target[i]-control)/duration;
            // std::lerp keeps each de Casteljau value within its finite hull.
            const double a=std::lerp(o.rectangle[i],control,t),b=std::lerp(control,o.target[i],t);
            result.rectangle[i]=std::lerp(std::lerp(a,b,t),std::lerp(b,o.target[i],t),t);
            result.velocity[i]=std::lerp(std::lerp(o.velocity[i],tangent,t),std::lerp(tangent,0.0,t),t);
            if(!std::isfinite(result.rectangle[i])||!std::isfinite(result.velocity[i])
                ||std::abs(result.rectangle[i])>400000||std::abs(result.velocity[i])>1e9)
                throw std::runtime_error("trajectory sample leaves admitted bounds");
        }
        if(result.rectangle[2]<=0||result.rectangle[3]<=0)throw std::runtime_error("trajectory exhausted positive dimension");
        return result;
    }
};
}
