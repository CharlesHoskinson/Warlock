#pragma once
#include <hyprutils/math/Box.hpp>
#include <hyprutils/math/Vector2D.hpp>
#include <cmath>
#include <stdexcept>
namespace AtlasCoordinates {
using namespace Hyprutils::Math;
inline Vector2D logicalPosition(const Vector2D& globalPosition,const Vector2D& pixelOffset,double scale) {
 if(!std::isfinite(scale) || scale<=0 || !std::isfinite(pixelOffset.x) || !std::isfinite(pixelOffset.y))throw std::runtime_error("invalid atlas coordinate scale/offset");
 return globalPosition-pixelOffset/scale;
}
inline CBox pixelBox(const CBox& outputBox,const Vector2D& pixelOffset) {return outputBox.copy().translate(-pixelOffset);}
// Renderer shader boxes currently inverse-transform against monitor geometry
// even for export. Recover the untransformed canonical box using the original
// output pixel dimensions. This changes shader metadata, never monitor fields.
inline CBox canonicalShaderBox(const CBox& transformedBox,int outputTransform,const Vector2D& outputPixelSize) {
 if(outputTransform<0 || outputTransform>7 || outputPixelSize.x<=0 || outputPixelSize.y<=0)throw std::runtime_error("invalid atlas output transform");
 return transformedBox.copy().transform(static_cast<eTransform>(outputTransform),outputPixelSize.x,outputPixelSize.y);
}
}
