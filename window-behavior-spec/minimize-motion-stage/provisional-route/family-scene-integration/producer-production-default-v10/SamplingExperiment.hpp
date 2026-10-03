#pragma once
#include <GLES2/gl2.h>
#include <stdexcept>
#include <string>

namespace OwnedSampling {
inline constexpr const char* policy = "four-nearest-centers-highp-bilinear-v1";
inline constexpr const char* linearFragment = "precision highp float;uniform highp sampler2D atlas;varying highp vec2 tex;void main(){gl_FragColor=texture2D(atlas,tex);}";
inline constexpr const char* manualFragment = R"GLSL(
precision highp float;
uniform highp sampler2D atlas;
uniform highp vec2 atlasSize;
varying highp vec2 tex;
highp vec4 center(highp vec2 i) {
    highp vec2 clamped = clamp(i, vec2(0.0), atlasSize - vec2(1.0));
    return texture2D(atlas, (clamped + vec2(0.5)) / atlasSize);
}
void main() {
    highp vec2 s = tex * atlasSize - vec2(0.5);
    highp vec2 i = floor(s);
    highp vec2 f = s - i;
    highp vec4 c00 = center(i);
    highp vec4 c10 = center(i + vec2(1.0, 0.0));
    highp vec4 c01 = center(i + vec2(0.0, 1.0));
    highp vec4 c11 = center(i + vec2(1.0, 1.0));
    gl_FragColor = c00 * ((1.0-f.x)*(1.0-f.y))
                + c10 * (f.x*(1.0-f.y))
                + c01 * ((1.0-f.x)*f.y)
                + c11 * (f.x*f.y);
}
)GLSL";
struct Texture {
    int width = 0, height = 0, controlIndex = -1;
    std::string digest;
    bool announced = false;
};
inline void requireDiagnostic(bool enabled, bool raster, bool causal, bool readback) {
    if (enabled && (!raster || !causal || !readback))
        throw std::invalid_argument("manual bilinear experiment requires raster causal readback");
}
inline void requireExtent(const Texture& t) {
    if (t.width < 1 || t.height < 1 || t.width > 8192 || t.height > 8192)
        throw std::invalid_argument("manual sampler lacks actual immutable upload extent");
}
inline void requireState(const Texture& t, int min, int mag, int wrapS, int wrapT,
                         float uniformWidth, float uniformHeight, unsigned error) {
    requireExtent(t);
    if (min != GL_NEAREST || mag != GL_NEAREST || wrapS != GL_CLAMP_TO_EDGE ||
        wrapT != GL_CLAMP_TO_EDGE || uniformWidth != t.width || uniformHeight != t.height ||
        error != GL_NO_ERROR)
        throw std::runtime_error("manual sampler actual filter/extent uniform disagrees");
}
}
