#pragma once
#include "ContinuousTrajectory.hpp"
#include <cstdint>
#include <map>
#include <string>

namespace ContinuousMotion {
// A pure plan: it never mutates tokens, source identities or presentation state.
struct CommonTrajectoryPlan {
    std::map<std::string,FamilyTrajectory> curves;
    double durationSeconds=0;
    explicit CommonTrajectoryPlan(const std::map<std::string,std::vector<Origin>>& outputs,double nominalSeconds) {
        if(outputs.empty()||outputs.size()>64||!std::isfinite(nominalSeconds)||nominalSeconds<=0||nominalSeconds>4)
            throw std::invalid_argument("bounded complete output duration plan required");
        double lower=1e-9,upper=nominalSeconds;
        size_t memberCount=0;
        for(const auto& [name,origins]:outputs){
            if(name.empty()||origins.empty()||origins.size()>64||(memberCount&&memberCount!=origins.size()))
                throw std::invalid_argument("complete same-size bounded output families required");
            memberCount=origins.size();
            for(const auto& origin:origins)for(size_t i=0;i<4;++i){
                const auto a=origin.rectangle[i],b=origin.target[i],v=origin.velocity[i];
                if(!std::isfinite(a)||!std::isfinite(b)||!std::isfinite(v)||std::abs(a)>400000||std::abs(b)>400000||std::abs(v)>1e9||(i>=2&&(a<=0||b<=0)))
                    throw std::invalid_argument("bounded output trajectory material required");
                // Same control constraints as the unchanged V12 primitive.
                if(v>0)upper=std::min(upper,3*(400000-a)/v);
                if(v<0)upper=std::min(upper,i>=2?1.5*a/(-v):3*(a+400000)/(-v));
                const auto delta=b-a;
                if(delta!=0){
                    const auto room=delta>0?1e9+v:1e9-v;
                    if(room<=0)throw std::invalid_argument("output derivative duration has no headroom");
                    lower=std::max(lower,3*std::abs(delta)/room);
                }
            }
        }
        if(!std::isfinite(upper)||upper<lower||!std::isfinite(upper*1e9)||upper*1e9<1)
            throw std::invalid_argument("no common representable bounded duration");
        durationSeconds=upper;
        for(const auto& [name,origins]:outputs){
            FamilyTrajectory curve(origins,durationSeconds);
            if(curve.seconds()!=durationSeconds)throw std::invalid_argument("output curve changed common planned duration");
            curves.emplace(name,std::move(curve));
        }
    }
};
inline double elapsedSeconds(uint64_t now,uint64_t start) {
    if(!now||!start||now<start||now-start>9007199254740991ULL)
        throw std::invalid_argument("nonmonotonic or unrepresentable sample timestamp");
    return double(now-start)/1e9;
}
}
