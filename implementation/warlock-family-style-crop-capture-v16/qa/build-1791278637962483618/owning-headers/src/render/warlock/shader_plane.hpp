#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <optional>
namespace warlock {
struct ShaderPlanePlan { uint32_t width, height; uint64_t peakBytes; };
// Value-only nominal storage admission; no authority or measured driver claim.
inline std::optional<ShaderPlanePlan> shaderPlanePlan(double width, double height, double x, double y, double cropWidth, double cropHeight, uint64_t encodedPeak) {
    auto dimension=[](double v){return std::isfinite(v) && v>=1 && v<=4096 && std::floor(v)==v;};
    if (!dimension(width) || !dimension(height) || !dimension(cropWidth) || !dimension(cropHeight) || !std::isfinite(x) || !std::isfinite(y) || x<0 || y<0 || std::floor(x)!=x || std::floor(y)!=y || x+cropWidth>width || y+cropHeight>height)
        return {};
    const auto planeBytes=uint64_t(width)*uint64_t(height)*4;
    const auto cropBytes=uint64_t(cropWidth)*uint64_t(cropHeight)*4;
    if (encodedPeak<cropBytes)return {};
    // Source+shader destination; after source retirement, destination+crop;
    // after shader destination retirement, original crop/readback/PNG plan.
    return ShaderPlanePlan{uint32_t(width),uint32_t(height),std::max({planeBytes*2,planeBytes+cropBytes,encodedPeak})};
}
}
