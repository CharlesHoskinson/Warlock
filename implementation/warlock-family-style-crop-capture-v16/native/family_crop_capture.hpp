#pragma once
#include "preview_capture.hpp"
namespace preview::capture {
// Native bounds are outputs only. Reserve the actual PNG/framebuffer/readback
// plan before the owning renderer allocates and re-derives its contributors.
inline std::unique_ptr<const OwnedPng> captureOwnedFamilyCrop(PHLWINDOW window,Budget& budget,uint64_t deadline,const std::function<bool()>& current,CBox* pixelBounds){
    if(!pixelBounds)return {};
    *pixelBounds={};
    auto valid=[&]{return nativeNow()<deadline && current();};
    if(!current || !window || !g_pHyprRenderer || !Render::GL::g_pHyprOpenGL || !valid())return {};
    const auto monitor=window->m_monitor.lock();const auto bounds=g_pHyprRenderer->familyCropBounds(window);if(!monitor || !bounds)return {};
    const auto p=plan(static_cast<uint32_t>(bounds->w),static_cast<uint32_t>(bounds->h));if(!p)return {};
    const auto peak=g_pHyprRenderer->familyCapturePeakBytes(window,p->peak);if(!peak || *peak<p->peak)return {};
    auto reservation=budget.reserve(*peak);if(!reservation)return {};
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();if(glGetError()!=GL_NO_ERROR || !valid())return {};
    GLint read=0,draw=0,pack=4;std::array<GLint,4> viewport{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);glGetIntegerv(GL_VIEWPORT,viewport.data());
    struct Restore {GLint read,draw,pack;std::array<GLint,4> viewport;~Restore(){glBindFramebuffer(GL_READ_FRAMEBUFFER,read);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glPixelStorei(GL_PACK_ALIGNMENT,pack);glViewport(viewport[0],viewport[1],viewport[2],viewport[3]);}} restore{read,draw,pack,viewport};
    if(g_pHyprRenderer->familyCapturePeakBytes(window,p->peak)!=peak || !valid())return {};
    CBox actual{};auto fb=g_pHyprRenderer->makeFamilyCropFB(window,&actual);
    if(!fb || actual!=*bounds || !fb->isAllocated() || !dynamic_cast<Render::GL::CGLFramebuffer*>(fb.get()) || fb->m_size!=bounds->size() || fb->m_drmFormat!=DRM_FORMAT_ABGR8888 || glGetError()!=GL_NO_ERROR || !valid())return {};
    auto pixels=makeShared<Readback>(*p);if(!fb->readPixels(CHLBufferReference{pixels}) || glGetError()!=GL_NO_ERROR || !valid())return {};
    // RPT_EXPORT uses the same native positive-Y output projection as the
    // monitor. Preserve framebuffer row order; native pixels must qualify it.
    auto encoded=encodeRgba(pixels->pixels,p->width,p->height,p->stride,false,true);if(!valid())return {};
    pixels.reset();fb.reset();*pixelBounds=actual;
    return std::make_unique<const OwnedPng>(std::move(*reservation),std::move(encoded),p->width,p->height);
}
}
