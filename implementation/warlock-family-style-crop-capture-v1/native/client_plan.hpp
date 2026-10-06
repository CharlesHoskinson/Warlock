#pragma once
#include "preview_png.hpp"
#include <cmath>
namespace preview::capture {
struct ClientPlan {Plan client,canvas;uint64_t peak;};
inline std::optional<ClientPlan> clientPlan(double width,double height,double canvasWidth,double canvasHeight,double scale,bool transformed,bool offset,bool customTransformer) {
    auto whole=[](double value){return std::isfinite(value) && value>=1 && value<=4096 && std::floor(value)==value;};
    if(scale!=1 || transformed || offset || customTransformer || !whole(width) || !whole(height) || !whole(canvasWidth) || !whole(canvasHeight) || width>canvasWidth || height>canvasHeight)return {};
    auto client=plan(static_cast<uint32_t>(width),static_cast<uint32_t>(height)),canvas=plan(static_cast<uint32_t>(canvasWidth),static_cast<uint32_t>(canvasHeight));
    if(!client || !canvas)return {};
    return ClientPlan{*client,*canvas,canvas->pixels+client->pixels+client->png};
}
}
