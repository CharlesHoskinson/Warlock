/* Cosmetic profile only: never changes eligibility, custody or focus policy. */
void settleReducedMotion(const std::vector<PHLWINDOW>& family,const PHLWORKSPACE& previous,const PHLWORKSPACE& destination) {
    for(const auto& workspace : {previous,destination}) {
        if(!workspace) continue;
        if(workspace->m_renderOffset && workspace->m_renderOffset->isBeingAnimated()) workspace->m_renderOffset->warp(false);
        if(workspace->m_alpha && workspace->m_alpha->isBeingAnimated()) workspace->m_alpha->warp(false);
    }
    for(const auto& window : Desktop::windowState()->windows()) {
        if(!window || !window->m_isMapped || (std::ranges::find(family,window)==family.end() && window->m_workspace!=previous && window->m_workspace!=destination)) continue;
        if(std::ranges::find(family,window)!=family.end()) {
            if(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)) window->finishAnimation();
            if(window->alpha().isBeingAnimated()) window->alpha().warp(false);
        }
        g_pHyprRenderer->damageWindow(window,true);
    }
}
void motionTransitionObserved(const Session&,const std::string&,const std::vector<PHLWINDOW>&,const PHLWORKSPACE&,const PHLWORKSPACE&);

// Retain only an accepted effect's current native goals. Weak identities do not
// keep retired windows/workspaces alive or confer permission to replay an effect.
void retainAcceptedMotion(Session& session,const std::string& intent,const std::vector<PHLWINDOW>& family,const PHLWORKSPACE& previous,const PHLWORKSPACE& destination) {
    session.motion={};
    if(session.reducedMotion) return;
    auto& motion=session.motion;
    motion.output=outputGeneration;motion.intent=intent;
    for(const auto& window : family) {
        const auto member=std::ranges::find_if(members,[&](const Member& entry){return entry.window.lock()==window;});
        if(member==members.end()) {motion={};return;}
        motion.windows.push_back({*member,window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL),window->m_workspace,window->alpha().goal()});
    }
    for(const auto& workspace : {previous,destination}) {
        if(!workspace || std::ranges::any_of(motion.workspaces,[&](const MotionWorkspace& item){return item.workspace.lock()==workspace;})) continue;
        motion.workspaces.push_back({workspace,workspace->m_renderOffset ? workspace->m_renderOffset->goal() : Vector2D{},workspace->m_alpha ? workspace->m_alpha->goal() : 1.F});
    }
}

void settleAcceptedMotion() {
    for(auto& [peer,session] : sessions) {
        auto& motion=session.motion;
        if(motion.windows.empty()) continue;
        bool valid=startTime(peer)==session.start && motion.output==outputGeneration && !g_pSessionLockManager->isSessionLocked();
        bool running=false;
        std::vector<PHLWINDOW> family;
        for(const auto& item : motion.windows) {
            const auto window=item.member.window.lock();
            valid=valid && window && window->m_isMapped && window->m_workspace==item.workspace.lock() &&
                std::ranges::any_of(members,[&](const Member& member){return member.id==item.member.id && member.window.lock()==window;});
            if(!valid) break;
            valid=window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)==item.goal && window->alpha().goal()==item.alpha;
            running=running || window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=item.goal || window->alpha().isBeingAnimated();
            family.push_back(window);
        }
        for(const auto& item : motion.workspaces) {
            const auto workspace=item.workspace.lock();
            if(!workspace) {valid=false;break;}
            valid=valid && (!workspace->m_renderOffset || workspace->m_renderOffset->goal()==item.goal) && (!workspace->m_alpha || workspace->m_alpha->goal()==item.alpha);
            running=running || (workspace->m_renderOffset && workspace->m_renderOffset->isBeingAnimated()) || (workspace->m_alpha && workspace->m_alpha->isBeingAnimated());
        }
        if(!valid || !running) {motion={};continue;}
        if(!motion.settle || !session.reducedMotion) continue;
        const auto previous=motion.workspaces.empty() ? PHLWORKSPACE{} : motion.workspaces.front().workspace.lock();
        const auto destination=motion.workspaces.empty() ? PHLWORKSPACE{} : motion.workspaces.back().workspace.lock();
        settleReducedMotion(family,previous,destination);
        motionTransitionObserved(session,motion.intent,family,previous,destination);
        motion={};
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
        if(layer->geometricBox(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=layer->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)) layer->finishAnimation();
        if(layer->alpha().isBeingAnimated()) layer->alpha().warp();
    }
    const auto windows=Desktop::windowState()->windows();
    for(const auto& window : windows) {
        if(!window || !window->wlSurface() || !hostReducedMotion(window->wlSurface()->resource())) continue;
        if(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_CURRENT)!=window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)) window->finishAnimation();
        if(window->alpha().isBeingAnimated()) window->alpha().warp();
    }
}
