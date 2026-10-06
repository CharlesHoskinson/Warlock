#pragma once
#include "preview_png.hpp"
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/render/OpenGL.hpp>
#include <hyprland/src/render/gl/GLFramebuffer.hpp>
#include <hyprland/src/protocols/types/Buffer.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <chrono>
#include <cmath>

namespace preview::capture {
inline uint64_t nativeNow() {
    return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch()).count());
}
class Readback final:public IHLBuffer {
    uint32_t stride_;
public:
    std::vector<uint8_t> pixels;
    explicit Readback(const Plan& p):stride_(p.stride),pixels(p.pixels) {
        size=Vector2D{static_cast<int>(p.width),static_cast<int>(p.height)};
        if(pixels.capacity()>p.pixels) throw std::runtime_error("Readback capacity exceeds plan");
    }
    Aquamarine::eBufferCapability caps() override {return Aquamarine::BUFFER_CAPABILITY_DATAPTR;}
    Aquamarine::eBufferType type() override {return Aquamarine::BUFFER_TYPE_SHM;}
    void update(const CRegion&) override {}
    bool isSynchronous() override {return true;}
    bool good() override {return true;}
    Aquamarine::SSHMAttrs shm() override {return {.success=true,.fd=-1,.format=DRM_FORMAT_ABGR8888,.size=size,.stride=static_cast<int>(stride_),.offset=0};}
    std::tuple<uint8_t*,uint32_t,size_t> beginDataPtr(uint32_t) override {return {pixels.data(),DRM_FORMAT_ABGR8888,pixels.size()};}
    void endDataPtr() override {}
    // Internal readback has no client wl_buffer. The inherited release method
    // dereferences m_resource; reference unlock must terminate here instead.
    // Synchronous CPU pixels have no client release or explicit-sync points.
    void sendRelease() override {}
};
// Native callback must derive lock, lifetime/incarnation, output and actor facts
// from current compositor state. It cannot be supplied by web/JSON authority.
// Guard/deadline refusal retains no accepted buffer. glReadPixels is synchronous
// readback; this API does not make it interruptible or prove presentation.
inline std::unique_ptr<const OwnedPng> captureOwnedPlane(PHLWINDOW window,Budget& budget,uint64_t deadline,const std::function<bool()>& current,bool family=false) {
    auto valid=[&] {return nativeNow()<deadline && current();};
    if(!window || !g_pHyprRenderer || !Render::GL::g_pHyprOpenGL || !current || !valid() || g_pHyprRenderer->m_bRenderingSnapshot) return {};
    const auto monitor=window->m_monitor.lock();
    if(!monitor || !monitor->m_output || !g_pHyprRenderer->shouldRenderWindow(window)) return {};
    const auto dimensions=monitor->m_pixelSize;
    if(!std::isfinite(dimensions.x) || !std::isfinite(dimensions.y) || dimensions.x<1 || dimensions.y<1 || dimensions.x>4096 || dimensions.y>4096 || std::floor(dimensions.x)!=dimensions.x || std::floor(dimensions.y)!=dimensions.y) return {};
    auto p=plan(static_cast<uint32_t>(dimensions.x),static_cast<uint32_t>(dimensions.y));
    auto reservation=budget.reserve(p->peak);
    if(!reservation) return {};
    // Ask the owning renderer to select its EGL context; refuse any pre-existing
    // GL error, and do not accept readPixels' boolean as proof of GL success.
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();
    if(glGetError()!=GL_NO_ERROR || !valid()) return {};
    GLint readFB=0,drawFB=0,pack=4;
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&readFB);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&drawFB);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);
    struct Restore {
        GLint read,draw,pack;
        ~Restore() {glBindFramebuffer(GL_READ_FRAMEBUFFER,read);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glPixelStorei(GL_PACK_ALIGNMENT,pack);}
    } restore{readFB,drawFB,pack};
    auto fb=family?g_pHyprRenderer->makeFamilySnapshotFB(window):g_pHyprRenderer->makeSnapshotFB(window);
    if(!fb || !fb->isAllocated() || !dynamic_cast<Render::GL::CGLFramebuffer*>(fb.get()) || fb->m_size!=dimensions || fb->m_drmFormat!=DRM_FORMAT_ABGR8888 || glGetError()!=GL_NO_ERROR || !valid()) return {};
    auto readback=makeShared<Readback>(*p);
    if(!fb->readPixels(CHLBufferReference{readback}) || glGetError()!=GL_NO_ERROR || !valid()) return {};
    auto encoded=encodeRgba(readback->pixels,p->width,p->height,p->stride,!family,true);
    if(!valid()) return {};
    // Readback and framebuffer references are dropped before publishing the
    // independently owned encoded result. The conservative reservation stays.
    readback.reset();fb.reset();
    return std::make_unique<const OwnedPng>(std::move(*reservation),std::move(encoded),p->width,p->height);
}
}
