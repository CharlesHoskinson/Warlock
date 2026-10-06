#pragma once
#include "source_epoch.hpp"
#include <array>
#include <cmath>
#include <set>
#include <vector>
namespace preview {
enum StyleChannel:size_t {FadeAlpha,ActiveAlpha,FullscreenAlpha,LayoutAlpha,MoveToAlpha,MoveFromAlpha,WorkspaceAlpha,DimPercent,AnrTint,Rounding,RoundingPower,BorderSize,BorderFade,BorderAngle,ShadowFade,ShadowAngle,GlowFade,GlowAngle,StyleChannelCount};
struct StyleGradient {
    std::vector<std::array<double,4>> rgba;
    std::vector<double> shader;
    double angle=0;
    bool operator==(const StyleGradient&)const=default;
};
struct WindowStyle {
    uint64_t id=0,flags=0;
    std::array<double,StyleChannelCount> channels{};
    // current/previous border, shadow, glow. Retain the shader's exact inputs,
    // rather than trusting a lossy hash or the upstream RGBA cache alone.
    std::array<StyleGradient,6> gradients{};
    bool operator==(const WindowStyle&)const=default;
};
class StyleRevision {
    SourceEpoch epoch_;
    uint64_t root_=0,family_=0;
    std::vector<WindowStyle> members_;
    bool complete_=false;
public:
    explicit StyleRevision(uint64_t initial=1):epoch_(initial){}
    bool observe(uint64_t root,uint64_t family,std::vector<WindowStyle> members,bool complete=true){
        if(!root || !family || members.empty() || members.size()>256)complete=false;
        std::set<uint64_t> seen;
        for(const auto& member:members){
            if(!member.id || !seen.insert(member.id).second)complete=false;
            for(double value:member.channels)if(!std::isfinite(value))complete=false;
            for(const auto& gradient:member.gradients){
                if(!std::isfinite(gradient.angle) || gradient.shader.size()!=gradient.rgba.size()*4)complete=false;
                for(const auto& color:gradient.rgba)for(double value:color)if(!std::isfinite(value))complete=false;
                for(double value:gradient.shader)if(!std::isfinite(value))complete=false;
            }
        }
        if(!seen.contains(root))complete=false;
        // Canonical unavailable state makes repeated malformed observations
        // stable. Recovery must obtain a later epoch; old validity cannot leak.
        if(!complete){root=family=0;members.clear();}
        if(root!=root_ || family!=family_ || members!=members_ || complete!=complete_){epoch_.commit();root_=root;family_=family;members_=std::move(members);complete_=complete;}
        return complete_ && epoch_.available();
    }
    uint64_t value()const noexcept{return complete_ && epoch_.available()?epoch_.value():0;}
    void unavailable(){observe(0,0,{},false);}
};
}
