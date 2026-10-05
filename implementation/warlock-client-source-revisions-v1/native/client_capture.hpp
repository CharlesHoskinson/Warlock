#pragma once
#include "preview_capture.hpp"
#include "client_plan.hpp"
#include "surface_tree.hpp"
#include <hyprland/src/render/pass/ClearPassElement.hpp>
#include <hyprland/src/protocols/core/Compositor.hpp>
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
    const auto projection=monitor->getScaleMatrix().getMatrix();
    if(!(projection[0]>0 && projection[4]>0) || projection[1]!=0 || projection[3]!=0)return {};
    auto reservation=budget.reserve(plan->peak);if(!reservation)return {};
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();if(glGetError()!=GL_NO_ERROR || !valid())return {};
    GLint read=0,draw=0,pack=4;std::array<GLint,4> viewport{};glGetIntegerv(GL_VIEWPORT,viewport.data());glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);
    struct Restore {
        GLint read,draw,pack;std::array<GLint,4> viewport;bool snapshot;bool feedback;Render::SRenderData previous;bool started=false;bool issued=false;bool restored=false;
        void reset(){
            if(restored)return;
            restored=true;
            if(started)g_pHyprRenderer->endRender();
            if(issued){glFinish();g_pHyprRenderer->m_usedAsyncBuffers.clear();g_pHyprRenderer->m_renderPass.clear();}
            g_pHyprRenderer->m_renderData=std::move(previous);g_pHyprRenderer->m_bRenderingSnapshot=snapshot;g_pHyprRenderer->m_bBlockSurfaceFeedback=feedback;
            glBindFramebuffer(GL_READ_FRAMEBUFFER,read);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glPixelStorei(GL_PACK_ALIGNMENT,pack);glViewport(viewport[0],viewport[1],viewport[2],viewport[3]);
        }
        ~Restore(){reset();}
    } restore{read,draw,pack,viewport,g_pHyprRenderer->m_bRenderingSnapshot,g_pHyprRenderer->m_bBlockSurfaceFeedback,g_pHyprRenderer->m_renderData};
    auto fb=g_pHyprRenderer->createFB("Warlock isolated client");if(!fb)return {};
    fb->alloc(plan->canvas.width,plan->canvas.height,DRM_FORMAT_ABGR8888);fb->setImageDescription(monitor->workBufferImageDescription());
    auto glfb=dynamic_cast<Render::GL::CGLFramebuffer*>(fb.get());
    if(!glfb || !fb->isAllocated() || fb->m_size!=monitor->m_pixelSize || glGetError()!=GL_NO_ERROR || !valid())return {};
    CRegion damage{0,0,static_cast<double>(plan->canvas.width),static_cast<double>(plan->canvas.height)};
    if(!g_pHyprRenderer->beginFullFakeRender(monitor,damage,fb))return {};
    restore.started=true;restore.issued=true;g_pHyprRenderer->m_bRenderingSnapshot=true;g_pHyprRenderer->m_bBlockSurfaceFeedback=true;
    g_pHyprRenderer->draw(CClearPassElement::SClearData{CHyprColor(0,0,0,0)});g_pHyprRenderer->startRenderPass();
    // Use the owning renderer's public surface-pass boundary. The protected
    // whole-window renderer is deliberately not exposed or bypassed. Only the
    // enrolled root tree contributes pass elements; no popup/decor/plugin hook.
    CSurfacePassElement::SRenderData data{};data.pMonitor=monitor;data.when=Time::steadyNow();
    data.pos=monitor->m_position;data.w=plan->client.width;data.h=plan->client.height;data.pWindow=window;
    data.dontRound=true;data.decorate=false;data.blur=false;data.alpha=1;data.fadeAlpha=1;
    const auto root=window->wlSurface()->resource();const auto tree=surfaceTree(root);if(!tree)return {};
    for(const auto index:tree->paint){const auto& row=tree->rows[index];const auto surface=row.surface;
        if(!surface->m_current.texture || surface->m_current.size.x<1 || surface->m_current.size.y<1)continue;
        data.localPos=row.local;data.texture=surface->m_current.texture;data.surface=surface;data.mainSurface=surface==root;
        g_pHyprRenderer->addPassElement(makeUnique<CSurfacePassElement>(data));++data.surfaceCounter;
    }
    g_pHyprRenderer->endRender();restore.started=false;
    // FULL_FAKE returns before the core's ordinary async-buffer drain. Wait
    // for this render before releasing sampled client buffers; the original
    // deadline is checked again and is never renewed.
    glFinish();g_pHyprRenderer->m_usedAsyncBuffers.clear();g_pHyprRenderer->m_renderPass.clear();restore.issued=false;
    if(glGetError()!=GL_NO_ERROR || !valid())return {};
    auto pixels=makeShared<Readback>(plan->client);
    glBindFramebuffer(GL_READ_FRAMEBUFFER,glfb->getFBID());glPixelStorei(GL_PACK_ALIGNMENT,1);
    // The owning monitor projection maps logical Y=0 to GL Y=0, with
    // positive Y. Read the client rectangle at that origin and preserve row
    // order. A generic negative-Y/top-of-framebuffer assumption is incorrect.
    glReadPixels(0,0,plan->client.width,plan->client.height,GL_RGBA,GL_UNSIGNED_BYTE,pixels->pixels.data());
    if(glGetError()!=GL_NO_ERROR || !valid())return {};
    auto encoded=encodeRgba(pixels->pixels,plan->client.width,plan->client.height,plan->client.stride,false,true);
    if(!valid())return {};
    pixels.reset();fb.reset();restore.reset();
    GLint restoredRead=0,restoredDraw=0,restoredPack=0;std::array<GLint,4> restoredViewport{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&restoredRead);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&restoredDraw);glGetIntegerv(GL_PACK_ALIGNMENT,&restoredPack);glGetIntegerv(GL_VIEWPORT,restoredViewport.data());
    if(restoredRead!=read || restoredDraw!=draw || restoredPack!=pack || restoredViewport!=viewport || glGetError()!=GL_NO_ERROR || !valid())return {};
    return std::make_unique<const OwnedPng>(std::move(*reservation),std::move(encoded),plan->client.width,plan->client.height);
}
}
