/* Cosmetic profile only: never changes eligibility, custody or focus policy. */
void settleReducedMotion(const std::vector<PHLWINDOW>& family,const PHLWORKSPACE& previous,const PHLWORKSPACE& destination) {
    for(const auto& workspace : {previous,destination}) {
        if(!workspace) continue;
        if(workspace->m_renderOffset) workspace->m_renderOffset->warp(false);
        if(workspace->m_alpha) workspace->m_alpha->warp(false);
    }
    for(const auto& window : Desktop::windowState()->windows()) {
        if(!window || !window->m_isMapped || (std::ranges::find(family,window)==family.end() && window->m_workspace!=previous && window->m_workspace!=destination)) continue;
        window->finishAnimation();
        window->alpha().warp(false);
        g_pHyprRenderer->damageWindow(window,true);
    }
}

void motionTransitionObserved(const Session& session,const std::string& intent,const std::vector<PHLWINDOW>& family,const PHLWORKSPACE& previous,const PHLWORKSPACE& destination) {
    if(!session.motionRequest || !g_pEventManager) return;
    bool settled=true;
    for(const auto& window : family) settled=settled && window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_CURRENT)==window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL) && !window->alpha().isBeingAnimated();
    for(const auto& workspace : {previous,destination}) if(workspace) settled=settled && (!workspace->m_renderOffset || !workspace->m_renderOffset->isBeingAnimated()) && (!workspace->m_alpha || !workspace->m_alpha->isBeingAnimated());
    g_pEventManager->postEvent(SHyprIPCEvent{"warlockmotion","{\"binding\":"+binding(session)+",\"intent\":"+intent+",\"profile\":"+quote(session.reducedMotion?"reduced":"full")+",\"settled\":"+(settled?"true":"false")+"}"});
}

// Only surfaces of a live owning host process inherit its Elm-selected profile.
// Names/titles are never used to identify an owner. This does not grant input.
bool hostReducedMotion(const SP<CWLSurfaceResource>& resource) {
    if(!resource || !resource->client()) return false;
    pid_t pid=0;uid_t uid=0;gid_t gid=0;wl_client_get_credentials(resource->client(),&pid,&uid,&gid);
    if(uid!=getuid() || pid<=0) return false;
    const auto identity=startTime(pid);
    return !identity.empty() && std::ranges::any_of(sessions,[&](const auto& entry){
        const auto& session=entry.second;
        return session.reducedMotion && session.presentationPid==pid && session.presentationStart==identity && startTime(entry.first)==session.start;
    });
}
void settleShellMotion() {
    const auto layers=Desktop::layerState()->layers();
    for(const auto& layer : layers) {
        if(!layer || !layer->wlSurface() || !hostReducedMotion(layer->wlSurface()->resource())) continue;
        layer->finishAnimation();layer->alpha().warp();
    }
    const auto windows=Desktop::windowState()->windows();
    for(const auto& window : windows) {
        if(!window || !window->wlSurface() || !hostReducedMotion(window->wlSurface()->resource())) continue;
        window->finishAnimation();window->alpha().warp();
    }
}
