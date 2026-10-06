#pragma once
#include "source_epoch.hpp"
#include "applied_shader.hpp"
#include <array>
#include <bit>
#include <cmath>
#include <set>
#include <string>
#include <vector>
namespace preview {
enum StyleChannel:size_t {FadeAlpha,ActiveAlpha,FullscreenAlpha,LayoutAlpha,MoveToAlpha,MoveFromAlpha,WorkspaceAlpha,DimPercent,AnrTint,Rounding,RoundingPower,BorderSize,BorderFade,BorderAngle,ShadowFade,ShadowAngle,GlowFade,GlowAngle,StyleChannelCount};
struct StyleGradient {
    std::vector<std::array<double,4>> rgba;
    std::vector<double> shader;
    double angle=0;
    bool operator==(const StyleGradient&)const=default;
};
enum RenderInteger:size_t {ShadowEnabled,ShadowRange,ShadowPower,ShadowSharp,GlowEnabled,GlowRange,GlowPower,BlurEnabled,BlurSize,BlurPasses,BlurNewOptimizations,BlurXray,BlurIgnoreOpacity,BlurPopups,BlurInputMethods,BlurBlend,CMEnabled,CMAutoHDR,NonShaderCM,NonShaderCMInterop,SendContentType,XpMode,XwaylandNearestNeighbor,RenderIntegerCount};
enum RenderFloating:size_t {ShadowScale,ShadowOffsetX,ShadowOffsetY,DimAround,BlurBrightness,BlurContrast,BlurVibrancy,BlurVibrancyDarkness,BlurNoise,PopupIgnoreAlpha,InputMethodIgnoreAlpha,RenderFloatingCount};
struct RenderConfiguration {
    std::array<int64_t,RenderIntegerCount> integers{};
    std::array<double,RenderFloatingCount> floating{};
    std::string screenShader;
    preview::shader::AppliedScreenShader appliedShader;
    bool operator==(const RenderConfiguration& other)const {
        if(integers!=other.integers || screenShader!=other.screenShader || appliedShader!=other.appliedShader)return false;
        for(size_t i=0;i<floating.size();++i)if(std::bit_cast<uint64_t>(floating[i])!=std::bit_cast<uint64_t>(other.floating[i]))return false;
        return true;
    }
};
struct SurfaceBackground {
    uint64_t id=0;bool hasEffect=false;std::vector<std::array<int32_t,4>> blurRegion;
    bool operator==(const SurfaceBackground&)const=default;
};
struct WindowStyle {
    uint64_t id=0,flags=0,effectFlags=0;
    // Identities are scoped to each window native tree, independent of object addresses.
    uint64_t rootSurfaceId=1;std::vector<SurfaceBackground> surfaceEffects;
    std::array<double,StyleChannelCount> channels{};
    // Value-owned normalized native protocol blur rectangles; flag10 records effect presence.
    std::vector<std::array<int32_t,4>> blurRegion;
    // current/previous border, shadow, glow. Retain the shader's exact inputs,
    // rather than trusting a lossy hash or the upstream RGBA cache alone.
    std::array<StyleGradient,6> gradients{};
    bool operator==(const WindowStyle&)const=default;
};
class StyleRevision {
    SourceEpoch epoch_;
    uint64_t root_=0,family_=0;
    std::vector<WindowStyle> members_;
    RenderConfiguration configuration_;
    bool complete_=false;
public:
    explicit StyleRevision(uint64_t initial=1):epoch_(initial){}
    bool observe(uint64_t root,uint64_t family,std::vector<WindowStyle> members,bool complete=true,RenderConfiguration configuration={}){
        if(!root || !family || members.empty() || members.size()>256)complete=false;
        const auto& shader=configuration.appliedShader;
        if(!shader.complete || shader.contextualUniforms || (!shader.enabled && (!shader.vertex.empty() || !shader.fragment.empty())) ||
           (shader.enabled && (shader.vertex.empty() || shader.fragment.empty())) || shader.vertex.size()>preview::shader::ScreenShaderSourceBudget ||
           shader.fragment.size()>preview::shader::ScreenShaderSourceBudget-std::min(shader.vertex.size(),preview::shader::ScreenShaderSourceBudget))complete=false;
        for(double value:configuration.floating)if(!std::isfinite(value))complete=false;
        std::set<uint64_t> seen;size_t blurRectangles=0,surfaceFacts=0;
        for(const auto& member:members){
            if(!member.id || !seen.insert(member.id).second)complete=false;
            if(!(member.effectFlags&(uint64_t{1}<<10)) && !member.blurRegion.empty())complete=false;
            if(member.blurRegion.size()>4096 || blurRectangles>4096-member.blurRegion.size())complete=false;
            else blurRectangles+=member.blurRegion.size();
            for(const auto& rectangle:member.blurRegion)if(rectangle[2]<=rectangle[0] || rectangle[3]<=rectangle[1])complete=false;
            if(!member.rootSurfaceId || member.surfaceEffects.size()>255 || surfaceFacts>256-(1+member.surfaceEffects.size()))complete=false;
            else surfaceFacts+=1+member.surfaceEffects.size();
            std::set<uint64_t> surfaceIDs{member.rootSurfaceId};
            for(const auto& surface:member.surfaceEffects){
                if(!surface.id || !surfaceIDs.insert(surface.id).second || (!surface.hasEffect && !surface.blurRegion.empty()))complete=false;
                if(surface.blurRegion.size()>4096 || blurRectangles>4096-surface.blurRegion.size())complete=false;
                else blurRectangles+=surface.blurRegion.size();
                for(const auto& rectangle:surface.blurRegion)if(rectangle[2]<=rectangle[0] || rectangle[3]<=rectangle[1])complete=false;
            }
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
        if(!complete){root=family=0;members.clear();configuration={};}
        if(root!=root_ || family!=family_ || members!=members_ || configuration!=configuration_ || complete!=complete_){epoch_.commit();root_=root;family_=family;members_=std::move(members);configuration_=std::move(configuration);complete_=complete;}
        return complete_ && epoch_.available();
    }
    uint64_t value()const noexcept{return complete_ && epoch_.available()?epoch_.value():0;}
    void unavailable(){observe(0,0,{},false);}
};
}
