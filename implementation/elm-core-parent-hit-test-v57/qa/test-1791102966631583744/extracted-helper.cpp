void scheduleParentHitTest(CPointerManager* manager) {
    const auto position = parentPositionFor(manager);
    if (!g_pEventLoopManager || !position->normalized.point || position->hitTestQueued)
        return;
    position->hitTestQueued = true;
    const std::weak_ptr<ParentPointerPosition> weak = position;
    g_pEventLoopManager->doLater([weak] {
        const auto position = weak.lock();
        if (!position) return;
        position->hitTestQueued = false;
        if (!g_pCompositor || g_pCompositor->m_isShuttingDown || !g_pInputManager ||
            !position->normalized.point || position->dispatching)
            return;
        auto& manager = Pointer::mgr();
        if (!manager || parentPositionFor(manager.get()) != position)
            return;
        const auto device = position->device.lock();
        const auto output = position->output.lock();
        const auto source = device ? device->aq() : nullptr;
        if (!device || !output || !source || Aquamarine::parentPointerInputStatus(source.get(), output.get()) != Aquamarine::ParentInputStatus::Ready)
            return;
        const auto& monitors = State::monitorState()->monitors();
        const auto monitor = std::ranges::find_if(monitors, [output](const auto& m) {
            return m->m_enabled && !m->isMirror() && m->m_output == output;
        });
        if (monitor == monitors.end() || (*monitor)->logicalBox() != position->appliedBox)
            return;
        // Monitor layout listeners also move workspace surfaces. Pick the live
        // surface after that dispatch completes, even if cursor pixels did not
        // change. No stored coordinate, raw owner, or button is queued here.
        g_pInputManager->simulateMouseMovement();
    });
}