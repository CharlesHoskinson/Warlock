#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>
#include <vector>

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
        for(const auto& origin:origins){
            for(size_t i=0;i<4;++i)
                if(!std::isfinite(origin.rectangle[i])||!std::isfinite(origin.velocity[i])||!std::isfinite(origin.target[i])
                    ||std::abs(origin.rectangle[i])>400000||std::abs(origin.target[i])>400000||std::abs(origin.velocity[i])>1e9)
                    throw std::invalid_argument("finite bounded trajectory material required");
            for(size_t i=2;i<4;++i){
                if(origin.rectangle[i]<=0||origin.target[i]<=0)throw std::invalid_argument("positive dimensions required");
                // h10(t)=t(1-t)^2 is nonnegative and at most 4/27.
                // The zero-tangent base is a convex blend of the endpoints.
                // Thus this bound retains at least half the smaller dimension.
                if(origin.velocity[i]<0)
                    duration=std::min(duration,std::min(origin.rectangle[i],origin.target[i])*27/(-8*origin.velocity[i]));
            }
        }
        if(!std::isfinite(duration)||duration<1e-9)throw std::invalid_argument("trajectory duration cannot be represented safely");
    }
    double seconds()const{return duration;}
    size_t size()const{return origins.size();}
    Sample sample(size_t index,double elapsedSeconds)const{
        if(index>=origins.size()||!std::isfinite(elapsedSeconds)||elapsedSeconds<0)
            throw std::invalid_argument("bounded family sample required");
        const auto& o=origins[index];
        if(elapsedSeconds==0)return {o.rectangle,o.velocity};
        if(elapsedSeconds>=duration)return {o.target,{0,0,0,0}};
        const double t=elapsedSeconds/duration,t2=t*t,t3=t2*t;
        const double a=2*t3-3*t2+1,v=t3-2*t2+t,b=-2*t3+3*t2;
        const double da=(6*t2-6*t)/duration,dv=3*t2-4*t+1,db=(-6*t2+6*t)/duration;
        Sample result;
        for(size_t i=0;i<4;++i){
            result.rectangle[i]=a*o.rectangle[i]+v*duration*o.velocity[i]+b*o.target[i];
            result.velocity[i]=da*o.rectangle[i]+dv*o.velocity[i]+db*o.target[i];
            if(!std::isfinite(result.rectangle[i])||!std::isfinite(result.velocity[i]))throw std::runtime_error("nonfinite trajectory sample");
        }
        if(result.rectangle[2]<=0||result.rectangle[3]<=0)throw std::runtime_error("trajectory exhausted positive dimension");
        return result;
    }
};
}
