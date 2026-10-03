#include "atlasRenderer.hpp"
#include "atlasAdapter.hpp"
#include <hyprutils/utils/ScopeGuard.hpp>
#include <hyprland/src/render/OpenGL.hpp>
#include <hyprland/src/output/Monitor.hpp>
#include <hyprland/src/render/Shader.hpp>
#include <hyprland/src/desktop/view/Window.hpp>
#include <stdexcept>
#include <array>
#include <string_view>

namespace {
// Legal protected member access, using base pointer-to-member types. No cast
// of the actual renderer object to a derived type and no private layout access.
struct Access : Render::IHyprRenderer {
    static constexpr auto window() {return &Access::renderWindow;}
    static constexpr auto mode() {return &Access::m_renderMode;}
};
struct GLState {
    GLint blendSrcRGB,blendDstRGB,blendSrcAlpha,blendDstAlpha,equationRGB,equationAlpha;
    GLint stencilClear,arrayBuffer,renderbuffer;
    GLboolean colorMask[4];
    struct Stencil {GLint function,reference,valueMask,writeMask,fail,depthFail,pass;};
    std::array<Stencil,2> stencils;
    struct Texture {GLint unit,texture2D,texture3D,external;};
    std::array<Texture,4> textures;
    GLint active;bool externalAvailable=false;
    GLState() {
        glGetIntegerv(GL_BLEND_SRC_RGB,&blendSrcRGB);glGetIntegerv(GL_BLEND_DST_RGB,&blendDstRGB);
        glGetIntegerv(GL_BLEND_SRC_ALPHA,&blendSrcAlpha);glGetIntegerv(GL_BLEND_DST_ALPHA,&blendDstAlpha);
        glGetIntegerv(GL_BLEND_EQUATION_RGB,&equationRGB);glGetIntegerv(GL_BLEND_EQUATION_ALPHA,&equationAlpha);
        glGetIntegerv(GL_STENCIL_CLEAR_VALUE,&stencilClear);glGetBooleanv(GL_COLOR_WRITEMASK,colorMask);
        glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&arrayBuffer);glGetIntegerv(GL_RENDERBUFFER_BINDING,&renderbuffer);
        for(int i=0;i<2;i++) {
            auto& s=stencils[i];
            glGetIntegerv(i?GL_STENCIL_BACK_FUNC:GL_STENCIL_FUNC,&s.function);
            glGetIntegerv(i?GL_STENCIL_BACK_REF:GL_STENCIL_REF,&s.reference);
            glGetIntegerv(i?GL_STENCIL_BACK_VALUE_MASK:GL_STENCIL_VALUE_MASK,&s.valueMask);
            glGetIntegerv(i?GL_STENCIL_BACK_WRITEMASK:GL_STENCIL_WRITEMASK,&s.writeMask);
            glGetIntegerv(i?GL_STENCIL_BACK_FAIL:GL_STENCIL_FAIL,&s.fail);
            glGetIntegerv(i?GL_STENCIL_BACK_PASS_DEPTH_FAIL:GL_STENCIL_PASS_DEPTH_FAIL,&s.depthFail);
            glGetIntegerv(i?GL_STENCIL_BACK_PASS_DEPTH_PASS:GL_STENCIL_PASS_DEPTH_PASS,&s.pass);
        }
        GLint count=0;glGetIntegerv(GL_NUM_EXTENSIONS,&count);
        for(GLint i=0;i<count;i++)if(std::string_view(reinterpret_cast<const char*>(glGetStringi(GL_EXTENSIONS,i)))=="GL_OES_EGL_image_external")externalAvailable=true;
        glGetIntegerv(GL_ACTIVE_TEXTURE,&active);
        // Audited renderer uses0,1,2 and8 for surfaces/blur/mattes/LUTs.
        int i=0;for(const GLint unit:{0,1,2,8}) {
            auto& t=textures[i++];t.unit=unit;glActiveTexture(GL_TEXTURE0+unit);
            glGetIntegerv(GL_TEXTURE_BINDING_2D,&t.texture2D);glGetIntegerv(GL_TEXTURE_BINDING_3D,&t.texture3D);
            t.external=0;if(externalAvailable)glGetIntegerv(GL_TEXTURE_BINDING_EXTERNAL_OES,&t.external);
        }
        glActiveTexture(active);
    }
    void restore()const {
        glBlendFuncSeparate(blendSrcRGB,blendDstRGB,blendSrcAlpha,blendDstAlpha);glBlendEquationSeparate(equationRGB,equationAlpha);
        glClearStencil(stencilClear);glColorMask(colorMask[0],colorMask[1],colorMask[2],colorMask[3]);
        for(int i=0;i<2;i++) {
            const auto& s=stencils[i];const GLenum face=i?GL_BACK:GL_FRONT;
            glStencilFuncSeparate(face,s.function,s.reference,s.valueMask);glStencilMaskSeparate(face,s.writeMask);
            glStencilOpSeparate(face,s.fail,s.depthFail,s.pass);
        }
        glBindBuffer(GL_ARRAY_BUFFER,arrayBuffer);glBindRenderbuffer(GL_RENDERBUFFER,renderbuffer);
        for(const auto& t:textures) {
            glActiveTexture(GL_TEXTURE0+t.unit);glBindTexture(GL_TEXTURE_2D,t.texture2D);glBindTexture(GL_TEXTURE_3D,t.texture3D);
            if(externalAvailable)glBindTexture(GL_TEXTURE_EXTERNAL_OES,t.external);
        }
        glActiveTexture(active);
    }
};

}

SP<Render::IFramebuffer> makeCanonicalAtlas(PHLWINDOW window,PHLMONITOR monitor,const Vector2D& offset,const Vector2D& size) {
    using namespace Render;
    auto* renderer=g_pHyprRenderer.get();
    auto* gl=GL::g_pHyprOpenGL.get();
    if(renderer->m_renderData.pMonitor)throw std::runtime_error("atlas cannot nest active render");
    // Preserve the compositor's shader cache through its public useShader API.
    GLint program=0;glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    SP<CShader> priorShader;
    if(gl->m_shaders)for(const auto& variants:gl->m_shaders->fragVariants)for(const auto& [features,shader]:variants)
        if(shader && shader->program()==static_cast<GLuint>(program))priorShader=shader;
    if(!priorShader)throw std::runtime_error("atlas cannot restore unknown shader program");
    const auto priorData=renderer->m_renderData;
    const auto priorMode=renderer->*Access::mode();
    const auto priorSnapshot=renderer->m_bRenderingSnapshot;
    const bool priorSurfaceFeedback=renderer->m_bBlockSurfaceFeedback;
    const bool priorBlurNeeded=monitor->m_blurFBShouldRender;
    auto priorPass=std::move(renderer->m_renderPass);
    GLint viewport[4],scissor[4],vao=0,activeTexture=0;
    glGetIntegerv(GL_VIEWPORT,viewport);glGetIntegerv(GL_SCISSOR_BOX,scissor);
    glGetIntegerv(GL_VERTEX_ARRAY_BINDING,&vao);glGetIntegerv(GL_ACTIVE_TEXTURE,&activeTexture);
    const GLState priorGL;
    const bool blend=glIsEnabled(GL_BLEND),stencil=glIsEnabled(GL_STENCIL_TEST),scissoring=glIsEnabled(GL_SCISSOR_TEST);
    struct Restore {
        IHyprRenderer* r;GL::CHyprOpenGLImpl* gl;SRenderData data;eRenderMode mode;bool snapshot;bool surfaceFeedback;
        CRenderPass pass;SP<CShader> shader;PHLMONITOR monitor;bool blurNeeded;GLint* viewport;GLint* scissor;GLint vao,texture;GLState state;bool blend,stencil,scissoring;bool begun=false;
        ~Restore() {
            if(begun) {try {r->endRender();}catch(...) {}}
            r->m_renderPass=std::move(pass);r->m_renderData.pMonitor=monitor;
            gl->setViewport(viewport[0],viewport[1],viewport[2],viewport[3]);
            gl->scissor(scissor[0],scissor[1],scissor[2],scissor[3],false);
            gl->blend(blend);gl->setCapStatus(GL_STENCIL_TEST,stencil);gl->setCapStatus(GL_SCISSOR_TEST,scissoring);
            gl->useShader(shader);glBindVertexArray(vao);state.restore();glActiveTexture(texture);
            r->m_renderData=data;r->*Access::mode()=mode;r->m_bRenderingSnapshot=snapshot;r->m_bBlockSurfaceFeedback=surfaceFeedback;monitor->m_blurFBShouldRender=blurNeeded;
        }
    } restore{renderer,gl,priorData,priorMode,priorSnapshot,priorSurfaceFeedback,std::move(priorPass),priorShader,monitor,priorBlurNeeded,viewport,scissor,vao,activeTexture,priorGL,blend,stencil,scissoring};
    const auto fb=renderer->createFB("canonical decorated motion atlas");
    fb->alloc(size.x,size.y,DRM_FORMAT_ABGR8888);fb->setImageDescription(monitor->workBufferImageDescription());
    CRegion damage{CBox{0,0,size.x,size.y}};
    if(!renderer->beginFullFakeRender(monitor,damage,fb))throw std::runtime_error("atlas fake render unavailable");
    restore.begun=true;
    renderer->m_bRenderingSnapshot=true;
    renderer->m_bBlockSurfaceFeedback=true;
    renderer->m_renderData.fbSize=size;
    renderer->setProjectionType(RPT_EXPORT);
    renderer->setViewport(0,0,size.x,size.y);
    renderer->m_renderData.transformDamage=false;
    renderer->m_renderData.noSimplify=true;
    renderer->m_renderData.renderModif={};
    beginAtlasCoordinates(offset,monitor);
    Hyprutils::Utils::CScopeGuard coordinates{[]{endAtlasCoordinates();}};
    renderer->pushMonitorTransformEnabled(false);
    Hyprutils::Utils::CScopeGuard transform{[&]{renderer->popMonitorTransformEnabled();}};
    renderer->draw(CClearPassElement::SClearData{CHyprColor(0,0,0,0)});
    (renderer->*Access::window())(window,monitor,Time::steadyNow(),!window->m_X11DoesntWantBorders,RENDER_PASS_ALL,false,false);
    renderer->endRender();restore.begun=false;
    validateAtlasCoordinates();
    return fb;
}
