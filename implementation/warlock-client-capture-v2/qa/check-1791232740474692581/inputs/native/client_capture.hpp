#pragma once
#include "preview_capture.hpp"
#include "client_plan.hpp"
#include <hyprland/src/render/pass/ClearPassElement.hpp>
namespace preview::capture {
inline std::optional<ClientPlan> clientLayout(PHLWINDOW window) {
    if(!window || !window->m_isMapped || !window->wlSurface() || !window->wlSurface()->resource() || !window->m_workspace)return {};
    const auto monitor=window->m_monitor.lock();if(!monitor || !monitor->m_output)return {};
    const auto size=window->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
    return clientPlan(size.x,size.y,monitor->m_pixelSize.x,monitor->m_pixelSize.y,monitor->m_scale,monitor->m_transform!=WL_OUTPUT_TRANSFORM_NORMAL,window->m_floatingOffset!=Vector2D{},!window->m_transformers.empty());
}
// A new source: isolated root client surface tree. No desktop/monitor snapshot
// is captured or promoted. Unsupported geometry remains a refusal.
inline std::unique_ptr<const OwnedPng> captureOwnedClient(PHLWINDOW window,Budget& budget,uint64_t deadline,const std::function<bool()>& current) {
    if(!current || !window || !g_pHyprRenderer || !Render::GL::g_pHyprOpenGL || g_pHyprRenderer->m_bRenderingSnapshot || g_pHyprRenderer->m_renderData.currentFB || g_pHyprRenderer->m_renderData.mainFB || g_pHyprRenderer->m_renderData.outFB || !g_pHyprRenderer->m_usedAsyncBuffers.empty())return {};
    auto valid=[&]{return nativeNow()<deadline && current();};if(!valid())return {};
    const auto plan=clientLayout(window);const auto monitor=window->m_monitor.lock();if(!plan || !monitor)return {};
    auto reservation=budget.reserve(plan->peak);if(!reservation)return {};
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();if(glGetError()!=GL_NO_ERROR || !valid())return {};
    GLint read=0,draw=0,pack=4;std::array<GLint,4> viewport{};glGetIntegerv(GL_VIEWPORT,viewport.data());glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);
    struct Restore {
        GLint read,draw,pack;std::array<GLint,4> viewport;bool snapshot;Render::SRenderData previous;bool started=false;bool issued=false;
        ~Restore(){
            if(started)g_pHyprRenderer->endRender();
            if(issued){glFinish();g_pHyprRenderer->m_usedAsyncBuffers.clear();g_pHyprRenderer->m_renderPass.clear();}
            g_pHyprRenderer->m_renderData=std::move(previous);g_pHyprRenderer->m_bRenderingSnapshot=snapshot;
            glBindFramebuffer(GL_READ_FRAMEBUFFER,read);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glPixelStorei(GL_PACK_ALIGNMENT,pack);glViewport(viewport[0],viewport[1],viewport[2],viewport[3]);
        }
    } restore{read,draw,pack,viewport,g_pHyprRenderer->m_bRenderingSnapshot,g_pHyprRenderer->m_renderData};
    auto fb=g_pHyprRenderer->createFB("Warlock isolated client");if(!fb)return {};
    fb->alloc(plan->canvas.width,plan->canvas.height,DRM_FORMAT_ABGR8888);fb->setImageDescription(monitor->workBufferImageDescription());
    auto glfb=dynamic_cast<Render::GL::CGLFramebuffer*>(fb.get());
    if(!glfb || !fb->isAllocated() || fb->m_size!=monitor->m_pixelSize || glGetError()!=GL_NO_ERROR || !valid())return {};
    CRegion damage{0,0,static_cast<double>(plan->canvas.width),static_cast<double>(plan->canvas.height)};
    if(!g_pHyprRenderer->beginFullFakeRender(monitor,damage,fb))return {};
    restore.started=true;restore.issued=true;g_pHyprRenderer->m_bRenderingSnapshot=true;
    g_pHyprRenderer->draw(CClearPassElement::SClearData{CHyprColor(0,0,0,0)});g_pHyprRenderer->startRenderPass();
    // ignorePosition puts the root at the monitor's canvas origin. Standalone
    // disables decoration, rounding, blur, workspace fading and window alpha.
    g_pHyprRenderer->renderWindow(window,monitor,Time::steadyNow(),false,Render::RENDER_PASS_MAIN,true,true);
    g_pHyprRenderer->endRender();restore.started=false;
    // FULL_FAKE returns before the core's ordinary async-buffer drain. Wait
    // for this render before releasing sampled client buffers; the original
    // deadline is checked again and is never renewed.
    glFinish();g_pHyprRenderer->m_usedAsyncBuffers.clear();g_pHyprRenderer->m_renderPass.clear();restore.issued=false;
    if(glGetError()!=GL_NO_ERROR || !valid())return {};
    auto pixels=makeShared<Readback>(plan->client);
    glBindFramebuffer(GL_READ_FRAMEBUFFER,glfb->getFBID());glPixelStorei(GL_PACK_ALIGNMENT,1);
    // GL starts at the bottom; the isolated client starts at the canvas top.
    glReadPixels(0,plan->canvas.height-plan->client.height,plan->client.width,plan->client.height,GL_RGBA,GL_UNSIGNED_BYTE,pixels->pixels.data());
    if(glGetError()!=GL_NO_ERROR || !valid())return {};
    auto encoded=encodeRgba(pixels->pixels,plan->client.width,plan->client.height,plan->client.stride,true,true);
    if(!valid())return {};
    pixels.reset();fb.reset();
    return std::make_unique<const OwnedPng>(std::move(*reservation),std::move(encoded),plan->client.width,plan->client.height);
}
}
