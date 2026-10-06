#include "warlock/family_crop.hpp"
#include "warlock/popup_tree.hpp"
#include "warlock/screen_shader.hpp"
#include "warlock/shader_plane.hpp"

namespace {
class WarlockAppliedShaderPass final : public IPassElement {
    SP<ITexture> texture_;
    CBox box_;
    bool& completed_;
public:
    WarlockAppliedShaderPass(SP<ITexture> texture, const CBox& box, bool& completed) : texture_(std::move(texture)), box_(box), completed_(completed) {}
    std::vector<UP<IPassElement>> draw() override {
        completed_ = Render::GL::g_pHyprOpenGL->renderFamilyScreenShader(texture_, box_);
        return {};
    }
    bool needsLiveBlur() override { return false; }
    bool needsPrecomputeBlur() override { return false; }
    const char* passName() override { return "Warlock owned cropped screen shader"; }
    ePassElementType type() override { return EK_CUSTOM; }
    bool undiscardable() override { return true; }
    bool disableSimplification() override { return true; }
};
struct WarlockNativeFamilyCrop {
    PHLMONITOR monitor;
    std::vector<PHLWINDOW> family;
    CBox pixels;
};
std::optional<WarlockNativeFamilyCrop> warlockNativeFamilyCrop(PHLWINDOW root, bool observeStopped = false) {
    if (!root || root->parent() || !validMapped(root) || !root->m_workspace || (!observeStopped && !root->m_workspace->isVisible()) || root->onSpecialWorkspace())
        return {};
    const auto monitor = root->m_monitor.lock();
    if (!monitor || !monitor->m_output || monitor->m_transform != WL_OUTPUT_TRANSFORM_NORMAL)
        return {};
    const auto& desktop = Desktop::windowState()->windows();
    if (desktop.empty() || desktop.size() > 256 || std::ranges::find(desktop, root) == desktop.end())
        return {};
    WarlockNativeFamilyCrop result{monitor, {}, {}};
    std::vector<preview::capture::CropRect> rects;
    size_t surfaces = 0;
    for (const auto& candidate : desktop) {
        std::vector<PHLWINDOW> ancestors;
        auto cursor = candidate;
        while (cursor && cursor != root) {
            if (ancestors.size() == 256 || std::ranges::find(ancestors, cursor) != ancestors.end())
                return {};
            ancestors.push_back(cursor);
            cursor = cursor->parent();
        }
        if (cursor != root || !candidate->m_isMapped)
            continue;
        if (candidate->m_monitor.lock() != monitor || candidate->m_workspace != root->m_workspace || !candidate->m_transformers.empty() ||
            (!observeStopped && (candidate->isHidden() || Desktop::WindowPolicy::isMinimized(candidate) || !g_pHyprRenderer->shouldRenderWindow(candidate))))
            return {};
        const auto tree = preview::capture::rootPopupTree(candidate);
        if (!tree || tree->rows.size() > 256 - surfaces)
            return {};
        surfaces += tree->rows.size();
        const auto offset = (candidate->m_pinned ? Vector2D{} : candidate->m_workspace->m_renderOffset->value()) + candidate->m_floatingOffset - monitor->m_position;
        const auto full = candidate->getFullWindowBoundingBox().translate(offset);
        rects.push_back({full.x, full.y, full.w, full.h});
        const auto position = candidate->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT) + offset;
        for (const auto& row : tree->rows) {
            if (!row.sampled)
                continue;
            const auto point = position + row.local;
            const auto size = row.surface->m_current.size;
            rects.push_back({point.x, point.y, size.x, size.y});
        }
        result.family.push_back(candidate);
    }
    if (result.family.empty() || std::ranges::find(result.family, root) == result.family.end())
        return {};
    const auto crop = preview::capture::familyCropPlan(rects, monitor->m_scale);
    if (!crop)
        return {};
    result.pixels = {static_cast<double>(crop->pixelX), static_cast<double>(crop->pixelY), static_cast<double>(crop->image.width), static_cast<double>(crop->image.height)};
    return result;
}
}

std::optional<CBox> IHyprRenderer::familyCropBounds(PHLWINDOW root) {
    if (warlockSnapshotFamily || warlockCropPixelBounds || m_bRenderingSnapshot)
        return {};
    const auto plan = warlockNativeFamilyCrop(root);
    return plan ? std::optional<CBox>{plan->pixels} : std::nullopt;
}

// Geometry observation does not attest or render pixels and cannot relax capture.
std::optional<CBox> IHyprRenderer::familyObservationCropBounds(PHLWINDOW root) {
    if (warlockSnapshotFamily || warlockCropPixelBounds || m_bRenderingSnapshot)
        return {};
    const auto plan = warlockNativeFamilyCrop(root, true);
    return plan ? std::optional<CBox>{plan->pixels} : std::nullopt;
}

const CBox* IHyprRenderer::familyCropPixelBounds() const {
    return warlockCropPixelBounds;
}

std::optional<uint64_t> IHyprRenderer::familyCapturePeakBytes(PHLWINDOW root, uint64_t encodedPeak) {
    if (warlockSnapshotFamily || warlockCropPixelBounds || m_bRenderingSnapshot)
        return {};
    const auto plan = warlockNativeFamilyCrop(root);
    const auto shader = warlock::appliedScreenShader();
    if (!plan || !shader.complete || shader.contextualUniforms || !encodedPeak)
        return {};
    if (!shader.enabled)
        return encodedPeak;
    const auto& bounds = plan->pixels;
    const auto dimensions = plan->monitor->m_pixelSize;
    const auto storage = warlock::shaderPlanePlan(dimensions.x, dimensions.y, bounds.x, bounds.y, bounds.w, bounds.h, encodedPeak);
    return storage ? std::optional<uint64_t>{storage->peakBytes} : std::nullopt;
}

SP<IFramebuffer> IHyprRenderer::makeFamilyCropFB(PHLWINDOW root, CBox* pixelBounds) {
    if (!pixelBounds)
        return nullptr;
    *pixelBounds = {};
    if (m_bRenderingSnapshot || warlockSnapshotFamily || warlockCropPixelBounds || m_currentPass || m_renderData.currentFB || m_renderData.mainFB ||
        m_renderData.outFB || !m_usedAsyncBuffers.empty())
        return nullptr;
    const auto plan = warlockNativeFamilyCrop(root);
    if (!plan)
        return nullptr;
    const auto& monitor = plan->monitor;
    const auto& family = plan->family;
    const auto& bounds = plan->pixels;
    GLint read = 0, drawFB = 0, pack = 4;
    std::array<GLint, 4> viewport{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &read);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &drawFB);
    glGetIntegerv(GL_PACK_ALIGNMENT, &pack);
    glGetIntegerv(GL_VIEWPORT, viewport.data());
    const auto oldData = m_renderData;
    const auto oldMode = m_renderMode;
    const bool oldSnapshot = m_bRenderingSnapshot, oldFeedback = m_bBlockSurfaceFeedback;
    bool started = false, issued = false;
    const auto restore = makeUnique<CScopeGuard>([&] {
        if (started)
            endRender();
        if (issued) {
            glFinish();
            m_usedAsyncBuffers.clear();
            m_renderPass.clear();
        }
        warlockCropPixelBounds = nullptr;
        warlockSnapshotFamily = nullptr;
        m_renderData = oldData;
        m_renderMode = oldMode;
        m_bRenderingSnapshot = oldSnapshot;
        m_bBlockSurfaceFeedback = oldFeedback;
        glBindFramebuffer(GL_READ_FRAMEBUFFER, read);
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, drawFB);
        glPixelStorei(GL_PACK_ALIGNMENT, pack);
        glViewport(viewport[0], viewport[1], viewport[2], viewport[3]);
    });
    const auto appliedShader = warlock::appliedScreenShader();
    if (!appliedShader.complete || appliedShader.contextualUniforms)
        return nullptr;
    // A native screen program interpolates screen-global UV and observes
    // full output framebuffer coordinates and texture dimensions. Never
    // rescale that program to a crop. Only family contributors are rendered.
    CBox renderBounds = bounds;
    if (appliedShader.enabled) {
        const auto dimensions = monitor->m_pixelSize;
        const auto storage = warlock::shaderPlanePlan(dimensions.x, dimensions.y, bounds.x, bounds.y, bounds.w, bounds.h, uint64_t(bounds.w) * uint64_t(bounds.h) * 4);
        if (!storage)
            return nullptr;
        renderBounds = {0, 0, double(storage->width), double(storage->height)};
    }
    auto fb = createFB("Warlock native cropped family");
    if (!fb)
        return nullptr;
    fb->alloc(renderBounds.w, renderBounds.h, DRM_FORMAT_ABGR8888);
    fb->setImageDescription(monitor->workBufferImageDescription());
    if (!fb->isAllocated() || fb->m_size != renderBounds.size() || glGetError() != GL_NO_ERROR)
        return nullptr;
    CRegion damage{renderBounds};
    if (!beginFullFakeRender(monitor, damage, fb))
        return nullptr;
    started = issued = true;
    m_renderData.fbSize = fb->m_size;
    setProjectionType(RPT_EXPORT);
    m_renderData.noSimplify = true;
    m_renderData.transformDamage = false;
    m_bRenderingSnapshot = m_bBlockSurfaceFeedback = true;
    warlockSnapshotFamily = &family;
    warlockCropPixelBounds = &renderBounds;
    glViewport(0, 0, renderBounds.w, renderBounds.h);
    draw(CClearPassElement::SClearData{CHyprColor(0, 0, 0, 0)});
    startRenderPass();
    const auto now = Time::steadyNow();
    if (Fullscreen::controller()->hasFullscreen(root->m_workspace))
        renderWorkspaceWindowsFullscreen(monitor, root->m_workspace, now);
    else
        renderWorkspaceWindows(monitor, root->m_workspace, now);
    for (const auto& candidate : family) {
        if (candidate->m_pinned && candidate->m_isFloating)
            renderWindow(candidate, monitor, now, true, RENDER_PASS_ALL);
    }
    endRender();
    started = false;
    glFinish();
    m_usedAsyncBuffers.clear();
    m_renderPass.clear();
    issued = false;
    if (glGetError() != GL_NO_ERROR)
        return nullptr;
    if (appliedShader.enabled) {
        auto finalFB = createFB("Warlock owned cropped screen shader output");
        if (!finalFB)
            return nullptr;
        finalFB->alloc(renderBounds.w, renderBounds.h, DRM_FORMAT_ABGR8888);
        finalFB->setImageDescription(monitor->workBufferImageDescription());
        if (!finalFB->isAllocated() || finalFB->m_size != renderBounds.size() || glGetError() != GL_NO_ERROR)
            return nullptr;
        if (!beginFullFakeRender(monitor, damage, finalFB))
            return nullptr;
        started = issued = true;
        m_renderData.fbSize = finalFB->m_size;
        setProjectionType(RPT_EXPORT);
        m_renderData.noSimplify = true;
        m_renderData.transformDamage = false;
        glViewport(0, 0, renderBounds.w, renderBounds.h);
        draw(CClearPassElement::SClearData{CHyprColor(0, 0, 0, 0)});
        bool shaderCompleted = false;
        m_renderPass.add(makeUnique<WarlockAppliedShaderPass>(fb->getTexture(), renderBounds, shaderCompleted));
        endRender();
        started = false;
        glFinish();
        m_usedAsyncBuffers.clear();
        m_renderPass.clear();
        issued = false;
        if (!shaderCompleted || glGetError() != GL_NO_ERROR || warlock::appliedScreenShader() != appliedShader)
            return nullptr;
        // The sampled source is no longer needed after completed draw.
        // Retire it before allocating the independently owned exported crop.
        fb.reset();
        auto croppedFB = createFB("Warlock owned crop of native shader plane");
        if (!croppedFB)
            return nullptr;
        croppedFB->alloc(bounds.w, bounds.h, DRM_FORMAT_ABGR8888);
        croppedFB->setImageDescription(monitor->workBufferImageDescription());
        if (!croppedFB->isAllocated() || croppedFB->m_size != bounds.size() || glGetError() != GL_NO_ERROR)
            return nullptr;
        glBindFramebuffer(GL_READ_FRAMEBUFFER, GLFB(finalFB)->getFBID());
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, GLFB(croppedFB)->getFBID());
        issued = true;
        glBlitFramebuffer(bounds.x, bounds.y, bounds.x + bounds.w, bounds.y + bounds.h, 0, 0, bounds.w, bounds.h, GL_COLOR_BUFFER_BIT, GL_NEAREST);
        glFinish();
        issued = false;
        if (glGetError() != GL_NO_ERROR || warlock::appliedScreenShader() != appliedShader)
            return nullptr;
        finalFB.reset();
        fb = std::move(croppedFB);
    }
    *pixelBounds = bounds;
    return fb;
}
