#pragma once
#include <GLES2/gl2.h>
#include <cstdint>
#include <stdexcept>
namespace OwnedOver {
inline constexpr const char* policy="per-layer-explicit-over-nearest-rgba8-v1";
inline constexpr const char* fragment=R"GLSL(
precision highp float;
uniform highp sampler2D atlas;
uniform highp sampler2D prefix;
uniform highp vec2 atlasSize;
uniform highp vec2 outputSize;
uniform highp vec4 coverageBounds;
uniform highp vec4 sampleRect;
highp vec4 center(highp vec2 i) {
    highp vec2 c=clamp(i,vec2(0.0),atlasSize-vec2(1.0));
    return texture2D(atlas,(c+vec2(0.5))/atlasSize);
}
void main() {
    highp vec4 previous=texture2D(prefix,gl_FragCoord.xy/outputSize);
    highp vec2 point=vec2(gl_FragCoord.x,outputSize.y-gl_FragCoord.y);
    highp vec2 pixel=floor(point);
    if(pixel.x<coverageBounds.x||pixel.y<coverageBounds.y||pixel.x>=coverageBounds.z||pixel.y>=coverageBounds.w){
        gl_FragColor=previous;return;
    }
    highp vec2 tex=(point-sampleRect.xy)/sampleRect.zw;
    highp vec2 s=tex*atlasSize-vec2(0.5);
    highp vec2 i=floor(s), f=s-i;
    highp vec4 source=center(i)*((1.0-f.x)*(1.0-f.y))
        +center(i+vec2(1.0,0.0))*(f.x*(1.0-f.y))
        +center(i+vec2(0.0,1.0))*((1.0-f.x)*f.y)
        +center(i+vec2(1.0,1.0))*(f.x*f.y);
    highp vec4 over=clamp(source+previous*(1.0-source.a),0.0,1.0);
    gl_FragColor=floor(over*255.0+vec4(0.5))/255.0;
}
)GLSL";
inline constexpr const char* copyVertex="precision highp float;attribute highp vec2 position;void main(){gl_Position=vec4(position,0.,1.);}";
inline constexpr const char* copyFragment="precision highp float;uniform highp sampler2D prefix;uniform highp vec2 outputSize;void main(){gl_FragColor=texture2D(prefix,gl_FragCoord.xy/outputSize);}";
inline void requireDiagnostic(bool enabled,bool raster,bool causal,bool readback) {
    if(enabled&&(!raster||!causal||!readback))throw std::invalid_argument("quantized over experiment requires raster causal readback");
}
inline void requireBuffers(uint64_t generation,int width,int height,GLuint readTexture,GLuint writeTexture,GLuint writeFramebuffer){
    if(!generation||width<=0||height<=0||width>16384||height>16384||uint64_t(width)*height*8>256*1024*1024
        ||!readTexture||!writeTexture||readTexture==writeTexture||!writeFramebuffer)
        throw std::runtime_error("separate bounded current-generation prefix attachments required");
}
inline void requireState(GLint boundFramebuffer,GLint expectedFramebuffer,GLint attachedTexture,GLuint expectedTexture,
        GLint attachmentType,bool blend,const int* bits,int samples,int min,int mag,int wrapS,int wrapT,
        int sourceUnit,int prefixUnit,float width,float height,int expectedWidth,int expectedHeight,unsigned error){
    if(boundFramebuffer!=expectedFramebuffer||attachedTexture<=0||GLuint(attachedTexture)!=expectedTexture||attachmentType!=GL_TEXTURE
        ||blend||bits[0]!=8||bits[1]!=8||bits[2]!=8||bits[3]!=8||samples!=0||min!=GL_NEAREST||mag!=GL_NEAREST
        ||wrapS!=GL_CLAMP_TO_EDGE||wrapT!=GL_CLAMP_TO_EDGE||sourceUnit!=0||prefixUnit!=1
        ||width!=expectedWidth||height!=expectedHeight||error!=GL_NO_ERROR)
        throw std::runtime_error("actual quantized over framebuffer/sampler/blend/extent state disagrees");
}
}
