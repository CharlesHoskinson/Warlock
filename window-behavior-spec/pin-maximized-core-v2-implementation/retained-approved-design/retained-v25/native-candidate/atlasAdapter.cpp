#include "atlasAdapter.hpp"
#include "atlasCoordinates.hpp"
#include "globals.hpp"
#include <hyprland/src/plugins/HookSystem.hpp>
#include <hyprland/src/render/ElementRenderer.hpp>
#include <hyprland/src/render/Shader.hpp>
#include <hyprland/src/render/pass/RectPassElement.hpp>
#include <hyprland/src/render/pass/SurfacePassElement.hpp>
#include <hyprland/src/render/pass/BorderPassElement.hpp>
#include <hyprland/src/render/pass/TexPassElement.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <hyprutils/utils/ScopeGuard.hpp>
#include <unordered_map>
#include <stdexcept>
namespace {
CFunctionHook *elementHook=nullptr,*uniformHook=nullptr;
struct Context {
 bool active=false,shaderCoordinates=true;
 int surfaceDepth=0,directNativeDepth=0;
 Vector2D offset,pixels;
 double scale=1;
 int transform=0;
 std::unordered_map<CShader*,Vector2D> pendingTopLeft;
} context;
using Draw=void(*)(Render::IElementRenderer*,WP<IPassElement>,const CRegion&);
using Uniform=void(*)(CShader*,eShaderUniform,GLfloat,GLfloat);
void uniform(CShader* shader,eShaderUniform key,GLfloat x,GLfloat y) {
 const auto original=reinterpret_cast<Uniform>(uniformHook->m_original);
 if(!context.active || !context.shaderCoordinates){original(shader,key,x,y);return;}
 if(key==SHADER_TOP_LEFT) {
  if(context.pendingTopLeft.contains(shader))throw std::runtime_error("atlas unmatched shader top-left pair");
  context.pendingTopLeft[shader]={x,y};return;
 }
 if(key==SHADER_FULL_SIZE) {
  const auto pending=context.pendingTopLeft.find(shader);
  if(pending==context.pendingTopLeft.end())throw std::runtime_error("atlas full-size without shader top-left");
  const auto box=AtlasCoordinates::canonicalShaderBox(CBox{pending->second.x,pending->second.y,x,y},context.transform,context.pixels);
  context.pendingTopLeft.erase(pending);
  original(shader,SHADER_TOP_LEFT,box.x,box.y);original(shader,key,box.w,box.h);return;
 }
 original(shader,key,x,y);
}
void element(Render::IElementRenderer* renderer,WP<IPassElement> value,const CRegion& damage) {
 const auto original=reinterpret_cast<Draw>(elementHook->m_original);
 if(!context.active || !value){original(renderer,value,damage);return;}
 auto& data=g_pHyprRenderer->m_renderData;
 const auto previousModif=data.renderModif;
 const bool previousShader=context.shaderCoordinates;
 Hyprutils::Utils::CScopeGuard restore{[&]{data.renderModif=previousModif;context.shaderCoordinates=previousShader;}};
 data.renderModif={};context.shaderCoordinates=true;
 const bool innerSurface=context.surfaceDepth>0;
 switch(value->type()) {
  case EK_CLEAR: original(renderer,value,damage);return;
  case EK_SURFACE: {
   const auto e=dynamicPointerCast<CSurfacePassElement>(value);const auto previous=e->m_data;
   if(innerSurface)throw std::runtime_error("atlas nested surface normalization unsupported");
   e->m_data.pos=AtlasCoordinates::logicalPosition(e->m_data.pos,context.offset,context.scale);
   if(!e->m_data.clipBox.empty())e->m_data.clipBox.translate(-context.offset);
   ++context.surfaceDepth;
   Hyprutils::Utils::CScopeGuard undo{[&]{e->m_data=previous;--context.surfaceDepth;}};
   original(renderer,value,damage);return;
  }
  case EK_RECT: {
   const auto e=dynamicPointerCast<CRectPassElement>(value);const auto previous=e->m_data;
   if(!innerSurface){e->m_data.box.translate(-context.offset);if(!e->m_data.clipBox.empty())e->m_data.clipBox.translate(-context.offset);}
   CRegion drawDamage=damage;if(context.directNativeDepth>0 && !innerSurface)drawDamage.translate(-context.offset);
   Hyprutils::Utils::CScopeGuard undo{[&]{e->m_data=previous;}};original(renderer,value,drawDamage);return;
  }
  case EK_TEXTURE: {
   const auto e=dynamicPointerCast<CTexPassElement>(value);const auto previous=e->m_data;
   if(e->m_data.blur || e->m_data.motionBlur.enabled || e->m_data.useMirrorProjection)throw std::runtime_error("atlas blur/motion/mirror texture path unsupported");
   if(!innerSurface){e->m_data.box.translate(-context.offset);if(!e->m_data.clipBox.empty())e->m_data.clipBox.translate(-context.offset);if(!e->m_data.clipRegion.empty())e->m_data.clipRegion.translate(-context.offset);}
   Hyprutils::Utils::CScopeGuard undo{[&]{e->m_data=previous;}};original(renderer,value,damage);return;
  }
  case EK_BORDER: {
   const auto e=dynamicPointerCast<CBorderPassElement>(value);const auto previous=e->m_data;
   e->m_data.box.translate(-context.offset);
   Hyprutils::Utils::CScopeGuard undo{[&]{e->m_data=previous;}};original(renderer,value,damage);return;
  }
  case EK_SHADOW:case EK_INNER_GLOW: {
   // These shaders use local rounding coordinates. Their real window cutout
   // applies renderModif too, so retain one translation for this direct path.
   context.shaderCoordinates=false;
   data.renderModif.modifs.emplace_back(Render::SRenderModifData::RMOD_TYPE_TRANSLATE,-context.offset);
   ++context.directNativeDepth;
   Hyprutils::Utils::CScopeGuard depth{[]{--context.directNativeDepth;}};
   original(renderer,value,damage);return;
  }
  case EK_CUSTOM:
   if(std::string(value->passName())!="CBarPassElement")throw std::runtime_error("atlas unknown custom decoration path");
   original(renderer,value,damage);return;
  default:throw std::runtime_error("atlas unsupported render element path");
 }
}
CFunctionHook* install(const char* name,const char* exactSymbol,const void* replacement) {
 auto found=HyprlandAPI::findFunctionsByName(PHANDLE,name);
 std::erase_if(found,[&](const auto& match){return match.signature!=exactSymbol;});
 if(found.size()!=1)throw std::runtime_error("atlas exact compositor function unavailable");
 auto* hook=HyprlandAPI::createFunctionHook(PHANDLE,found.front().address,replacement);
 if(!hook || !hook->hook())throw std::runtime_error("atlas function hook unavailable");return hook;
}
}
void initAtlasAdapter() {
 try {
  elementHook=install("drawElement","_ZN6Render16IElementRenderer11drawElementEN9Hyprutils6Memory12CWeakPointerI12IPassElementEERKNS1_4Math7CRegionE",reinterpret_cast<void*>(element));
  uniformHook=install("setUniformFloat2","_ZN7CShader16setUniformFloat2E14eShaderUniformff",reinterpret_cast<void*>(uniform));
 }catch(...){exitAtlasAdapter();throw;}
}
void exitAtlasAdapter() {
 context={};if(uniformHook){uniformHook->unhook();uniformHook=nullptr;}if(elementHook){elementHook->unhook();elementHook=nullptr;}
}
void beginAtlasCoordinates(const Vector2D& offset,PHLMONITOR monitor) {
 if(!elementHook || !uniformHook || context.active)throw std::runtime_error("atlas normalization unavailable or already active");
 context={};context.active=true;context.offset=offset;context.scale=monitor->m_scale;context.transform=monitor->m_transform;context.pixels=monitor->m_pixelSize;
}
void endAtlasCoordinates(){context={};}
void validateAtlasCoordinates(){if(!context.pendingTopLeft.empty())throw std::runtime_error("atlas incomplete shader coordinate pair");}
CBox atlasCaptionClip(const CBox& box){return context.active?box.copy().translate(-context.offset):box;}
