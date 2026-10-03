#include "snapshotBridge.hpp"
#include "atlasRenderer.hpp"
#include <hyprland/src/desktop/state/WindowState.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <hyprland/src/desktop/rule/windowRule/WindowRuleApplicator.hpp>
#include <hyprland/src/render/Renderer.hpp>
#include <hyprland/src/render/OpenGL.hpp>
#include <hyprland/src/render/gl/GLFramebuffer.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <cairo/cairo.h>
#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fcntl.h>
#include <format>
#include <regex>
#include <vector>
#include <unistd.h>
extern "C" {
#include <lua.h>
#include <lauxlib.h>
}

namespace {
int result(lua_State* state, std::string value) {
    lua_pushlstring(state,value.data(),value.size());
    return 1;
}
cairo_status_t writePng(void* closure,const unsigned char* bytes,unsigned int length) {
    const int fd=*static_cast<int*>(closure);
    while(length) {
        const ssize_t written=write(fd,bytes,length);
        if(written<0 && errno==EINTR)continue;
        if(written<=0)return CAIRO_STATUS_WRITE_ERROR;
        length-=written;bytes+=written;
    }
    return CAIRO_STATUS_SUCCESS;
}
}

static int snapshot(lua_State* state,bool atlas) {
    const std::string address=luaL_checkstring(state,1);
    const std::string stable=luaL_checkstring(state,2);
    const auto pid=luaL_checkinteger(state,3);
    const std::filesystem::path output=luaL_checkstring(state,4);
    const std::string captureEpoch=atlas?luaL_checkstring(state,5):"";
    auto fail=[&](const char* reason) {return result(state,std::format(R"({{"ok":false,"reason":"{}"}})",reason));};
    try {
    if(atlas && (!std::regex_match(captureEpoch,std::regex("[a-f0-9]{12}-[0-9]+")) || output.filename()!=captureEpoch+".png"))return fail("invalid capture epoch ownership");
    if(!std::regex_match(address,std::regex("0x[0-9a-fA-F]+")) || !std::regex_match(stable,std::regex("[0-9a-fA-F]+")) || pid<=0)
        return fail("invalid identity");
    const char* runtime=getenv("XDG_RUNTIME_DIR");
    if(!runtime)return fail("no runtime directory");
    const auto parent=std::filesystem::weakly_canonical(output.parent_path());
    const auto root=std::filesystem::weakly_canonical(std::filesystem::path(runtime)/"hypr-window-motion");
    if(!parent.string().starts_with(root.string()+"/") || !std::regex_match(output.filename().string(),std::regex("[a-z0-9-]+\\.png")))
        return fail("output is outside private motion runtime");
    PHLWINDOW window;
    for(const auto& candidate:Desktop::windowState()->windows()) {
        if(candidate && std::format("0x{:x}",reinterpret_cast<uintptr_t>(candidate.get()))==address &&
            std::format("{:x}",candidate->m_stableID)==stable && candidate->getPID()==pid) {window=candidate;break;}
    }
    if(!window || !window->m_isMapped || window->isHidden())return fail("window unavailable");
    if(window->m_ruleApplicator && window->m_ruleApplicator->noScreenShare().valueOrDefault())return fail("window capture denied");
    const auto monitor=window->m_monitor.lock();
    if(!monitor || (!atlas && monitor->m_transform!=WL_OUTPUT_TRANSFORM_NORMAL))return fail("output transform unsupported");
    if(g_pHyprRenderer->type()!=Render::IHyprRenderer::RT_GL)return fail("non-GL renderer unsupported");
    // Public compositor snapshot API renders only this window plus its own
    // native decorations into transparent pixels, independently of occluders.
    // It writes no at/size/alpha/workspace or other live window state.
    const auto nativePosition=window->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
    const auto nativeSize=window->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);
    const auto box=window->getFullWindowBoundingBox();
    const double scale=monitor->m_scale;
    // A snapped/maximized client may fit exactly while its border/shadow
    // extends off-output. Capture the entire visible frame; never clip a
    // client that itself spans outputs or belongs to a different output.
    const double clientX=(nativePosition.x-monitor->m_position.x)*scale;
    const double clientY=(nativePosition.y-monitor->m_position.y)*scale;
    if(!atlas && (clientX<0 || clientY<0 || clientX+nativeSize.x*scale>monitor->m_pixelSize.x || clientY+nativeSize.y*scale>monitor->m_pixelSize.y))
        return fail("client bounds span outputs");
    const int x=atlas?static_cast<int>(std::floor((box.x-monitor->m_position.x)*scale)):std::max(0,static_cast<int>(std::floor((box.x-monitor->m_position.x)*scale)));
    const int y=atlas?static_cast<int>(std::floor((box.y-monitor->m_position.y)*scale)):std::max(0,static_cast<int>(std::floor((box.y-monitor->m_position.y)*scale)));
    const int right=atlas?static_cast<int>(std::ceil((box.x+box.w-monitor->m_position.x)*scale)):std::min(static_cast<int>(monitor->m_pixelSize.x),static_cast<int>(std::ceil((box.x+box.w-monitor->m_position.x)*scale)));
    const int bottom=atlas?static_cast<int>(std::ceil((box.y+box.h-monitor->m_position.y)*scale)):std::min(static_cast<int>(monitor->m_pixelSize.y),static_cast<int>(std::ceil((box.y+box.h-monitor->m_position.y)*scale)));
    const int width=right-x,height=bottom-y;
    if(width<=0 || height<=0 || width>8192 || height>8192 || static_cast<uint64_t>(width)*height>33554432)return fail("empty visible decorated bounds");
    // Lua IPC can run with no current GL context, unlike a render callback.
    // Match the compositor's CGLFramebuffer::readPixels context acquisition,
    // preserving the caller's EGL context/surfaces after our framebuffer dies.
    struct RestoreEGL {
        EGLDisplay display=eglGetCurrentDisplay();
        EGLContext context=eglGetCurrentContext();
        EGLSurface draw=eglGetCurrentSurface(EGL_DRAW),read=eglGetCurrentSurface(EGL_READ);
        ~RestoreEGL() {
            if(display!=EGL_NO_DISPLAY)eglMakeCurrent(display,draw,read,context);
            else eglMakeCurrent(Render::GL::g_pHyprOpenGL->m_eglDisplay,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);
        }
    } restoreEGL;
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();
    GLint previousDraw=0,previousRead=0,previousPack=4;
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&previousDraw);
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&previousRead);
    glGetIntegerv(GL_PACK_ALIGNMENT,&previousPack);
    struct RestoreGL {
        GLint draw,read,pack;
        ~RestoreGL() {
            glPixelStorei(GL_PACK_ALIGNMENT,pack);
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);
            glBindFramebuffer(GL_READ_FRAMEBUFFER,read);
        }
    } restoreGL{previousDraw,previousRead,previousPack};
    const auto framebuffer=atlas?makeCanonicalAtlas(window,monitor,Vector2D{x,y},Vector2D{width,height}):g_pHyprRenderer->makeSnapshotFB(window);
    if(!framebuffer)return fail("compositor snapshot unavailable");
    if(framebuffer->m_size!=(atlas?Vector2D{width,height}:monitor->m_pixelSize))return fail("snapshot framebuffer dimensions differ");
    Render::GL::g_pHyprOpenGL->makeEGLCurrent();
    // Allocated CGLFramebuffer::bind() binds DRAW only. Explicitly bind READ
    // just as the compositor readPixels helper does, without altering viewport.
    glBindFramebuffer(GL_READ_FRAMEBUFFER,static_cast<Render::GL::CGLFramebuffer*>(framebuffer.get())->getFBID());
    if(glCheckFramebufferStatus(GL_READ_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)return fail("snapshot read framebuffer incomplete");
    // Attribute errors to our readback, rather than earlier compositor draws.
    for(int i=0;i<16 && glGetError()!=GL_NO_ERROR;i++) {}
    glPixelStorei(GL_PACK_ALIGNMENT,1);
    std::vector<unsigned char> rgba(static_cast<size_t>(width)*height*4);
    // Full fake-render framebuffer uses compositor top-left coordinates,
    // matching CGLFramebuffer::readPixels offsets; do not invert monitor Y.
    glReadPixels(atlas?0:x,atlas?0:y,width,height,GL_RGBA,GL_UNSIGNED_BYTE,rgba.data());
    const auto error=glGetError();
    if(error!=GL_NO_ERROR)return result(state,std::format(R"({{"ok":false,"reason":"snapshot readback failed","glError":{}}})",error));
    if(!window->m_isMapped || window->isHidden() || window->getPID()!=pid || std::format("{:x}",window->m_stableID)!=stable)return fail("native identity changed during snapshot");
    if(window->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=nativePosition || window->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=nativeSize)
        return fail("native geometry changed during snapshot");
    // Hyprland GL uses ONE / ONE_MINUS_SRC_ALPHA: the returned RGBA is
    // already premultiplied. Cairo ARGB32 requires those same premultiplied
    // channels, packed in native-endian words; do not multiply alpha twice.
    const int stride=cairo_format_stride_for_width(CAIRO_FORMAT_ARGB32,width);
    std::vector<uint32_t> pixels(static_cast<size_t>(stride/4)*height);
    for(int row=0;row<height;row++)for(int col=0;col<width;col++) {
        const auto src=(static_cast<size_t>(row)*width+col)*4;
        pixels[static_cast<size_t>(row)*(stride/4)+col]=(static_cast<uint32_t>(rgba[src+3])<<24)|(static_cast<uint32_t>(rgba[src])<<16)|(static_cast<uint32_t>(rgba[src+1])<<8)|rgba[src+2];
    }
    int fd=open(output.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    if(fd<0)return fail("private PNG creation failed");
    auto surface=cairo_image_surface_create_for_data(reinterpret_cast<unsigned char*>(pixels.data()),CAIRO_FORMAT_ARGB32,width,height,stride);
    const auto status=cairo_surface_write_to_png_stream(surface,writePng,&fd);
    cairo_surface_destroy(surface);close(fd);
    if(status!=CAIRO_STATUS_SUCCESS) {unlink(output.c_str());return fail("PNG encoding failed");}
    const double logicalX=monitor->m_position.x+x/scale,logicalY=monitor->m_position.y+y/scale;
    return result(state,std::format(R"({{"ok":true,"whole":true,"canonical":{},"captureEpoch":"{}","stableId":"{}","pid":{},"rect":{{"x":{},"y":{},"width":{},"height":{}}},"insets":{{"left":{},"top":{},"right":{},"bottom":{}}},"pixels":[{},{}]}})",
        atlas,captureEpoch,stable,pid,logicalX,logicalY,width/scale,height/scale,nativePosition.x-logicalX,nativePosition.y-logicalY,
        logicalX+width/scale-nativePosition.x-nativeSize.x,logicalY+height/scale-nativePosition.y-nativeSize.y,width,height));
    } catch(const std::exception&) {
        return fail("snapshot exception");
    } catch(...) {
        return fail("snapshot failed");
    }
}

int luaWholeWindowSnapshot(lua_State* state) {return snapshot(state,false);}
int luaWindowAtlas(lua_State* state) {return snapshot(state,true);}
