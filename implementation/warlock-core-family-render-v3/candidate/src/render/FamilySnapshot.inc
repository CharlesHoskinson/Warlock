// The caller names only a native root. All contributors and paint passes are
// selected inside the owning compositor; no caller-supplied member list exists.
SP<IFramebuffer> IHyprRenderer::makeFamilySnapshotFB(PHLWINDOW root) {
    if (!root || root->parent() || !validMapped(root) || !root->m_workspace || root->onSpecialWorkspace() ||
        m_bRenderingSnapshot || warlockSnapshotFamily || m_currentPass || m_renderData.currentFB || m_renderData.mainFB ||
        m_renderData.outFB || !m_usedAsyncBuffers.empty())
        return nullptr;
    const auto monitor = root->m_monitor.lock();
    if (!monitor || !monitor->m_output || monitor->m_pixelSize.x <= 0 || monitor->m_pixelSize.y <= 0 ||
        monitor->m_pixelSize.x > 4096 || monitor->m_pixelSize.y > 4096)
        return nullptr;
    const auto& desktop = Desktop::windowState()->windows();
    if (desktop.empty() || desktop.size() > 256 || std::ranges::find(desktop, root) == desktop.end())
        return nullptr;
    std::vector<PHLWINDOW> family;
    for (const auto& candidate : desktop) {
        std::vector<PHLWINDOW> ancestors;
        auto cursor = candidate;
        while (cursor && cursor != root) {
            if (ancestors.size() == 256 || std::ranges::find(ancestors, cursor) != ancestors.end())
                return nullptr;
            ancestors.push_back(cursor);
            cursor = cursor->parent();
        }
        if (cursor != root || !candidate->m_isMapped)
            continue;
        if (candidate->m_monitor.lock() != monitor || candidate->m_workspace != root->m_workspace ||
            candidate->isHidden() || !shouldRenderWindow(candidate, monitor))
            return nullptr;
        family.push_back(candidate);
    }
    if (family.empty() || std::ranges::find(family, root) == family.end())
        return nullptr;

    // Snapshot and feedback flags, renderer references and GL bindings are
    // restored on every exit. Async client buffers stay held until glFinish.
    GLint read = 0, drawFB = 0, pack = 4;
    std::array<GLint, 4> viewport{};
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &read);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &drawFB);
    glGetIntegerv(GL_PACK_ALIGNMENT, &pack);
    glGetIntegerv(GL_VIEWPORT, viewport.data());
    const auto oldData = m_renderData;
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
        warlockSnapshotFamily = nullptr;
        m_renderData = oldData;
        m_bRenderingSnapshot = oldSnapshot;
        m_bBlockSurfaceFeedback = oldFeedback;
        glBindFramebuffer(GL_READ_FRAMEBUFFER, read);
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, drawFB);
        glPixelStorei(GL_PACK_ALIGNMENT, pack);
        glViewport(viewport[0], viewport[1], viewport[2], viewport[3]);
    });
    const auto fb = createFB("Warlock native family snapshot");
    if (!fb)
        return nullptr;
    fb->alloc(monitor->m_pixelSize.x, monitor->m_pixelSize.y, DRM_FORMAT_ABGR8888);
    fb->setImageDescription(monitor->workBufferImageDescription());
    if (!fb->isAllocated() || fb->m_size != monitor->m_pixelSize || glGetError() != GL_NO_ERROR)
        return nullptr;
    CRegion damage{0, 0, static_cast<int>(monitor->m_transformedSize.x), static_cast<int>(monitor->m_transformedSize.y)};
    if (!beginFullFakeRender(monitor, damage, fb))
        return nullptr;
    started = issued = true;
    m_bRenderingSnapshot = m_bBlockSurfaceFeedback = true;
    warlockSnapshotFamily = &family;
    draw(CClearPassElement::SClearData{CHyprColor(0, 0, 0, 0)});
    startRenderPass();
    const auto now = Time::steadyNow();
    // Preserve the owning renderer's tiled/floating/fullscreen pass selection.
    // renderWindow restricts contributors; layer surfaces/background/fadeouts
    // are never invoked as captured family members.
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
    return fb;
}
