// Explicit desired ordinary workspace; never a dispatcher string or scratchpad.
struct TransferSubmission {int64_t source,destination;uint64_t sourceGeneration;};
std::optional<TransferSubmission> transferSubmission(JsonObject* intent) {
    const auto p=objectMember(intent,"transfer");
    if(!p || !fields(p,{"source","sourceGeneration","destination"}))return {};
    const auto source=counter(p,"source"),generation=counter(p,"sourceGeneration"),destination=counter(p,"destination");
    if(!source || !generation || !destination || *source>INT64_MAX || *destination>INT64_MAX || *source==*destination)return {};
    return TransferSubmission{static_cast<int64_t>(*source),static_cast<int64_t>(*destination),*generation};
}
std::string transferFingerprint(const TransferSubmission& p) {
    return std::to_string(p.source)+":"+std::to_string(p.sourceGeneration)+":"+std::to_string(p.destination);
}
template<class Reply,class Reject>
std::string performTransferEffect(Session& session,const TransferSubmission& p,uint64_t rootId,const PHLWINDOW& root,const Elm::Geometry::Target& barrier,Reply reply,Reject reject) {
    if(g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || g_layoutManager->dragController()->target())return reject("transfer-input-blocked");
    const auto source=root->m_workspace;const auto sourceMonitor=root->m_monitor.lock();
    if(!source || source->m_id!=p.source || source->m_isSpecialWorkspace || geometryWorkspaces.bind(source)!=p.sourceGeneration || !sourceMonitor || !sourceMonitor->m_enabled || root->parent())return reject("transfer-source-changed");
    const auto family=nativeFamily(root);
    if(!family || family->empty())return reject("transfer-family-unavailable");
    std::vector<Elm::Geometry::Target> reserved;
    std::vector<bool> minimized;
    for(const auto& window:*family) {
        if(!window->m_isMapped || window->m_workspace!=source || window->m_monitor.lock()!=sourceMonitor || window->m_pinned || window->m_group || window->isHidden())return reject("transfer-family-ineligible");
        const auto identity=std::ranges::find_if(members,[&](const Member& m){return m.window.lock()==window;});
        if(identity==members.end() || effectBarriers.blocked({lifetime,identity->id}))return reject("transfer-family-unresolved");
        reserved.push_back({lifetime,identity->id});minimized.push_back(Desktop::WindowPolicy::isMinimized(window));
    }
    PHLWORKSPACE destination=nullptr;
    for(const auto& workspace:State::workspaceState()->workspaces())if(workspace->m_id==p.destination){destination=workspace.lock();break;}
    if(destination && (destination->m_isSpecialWorkspace || !destination->m_monitor || !destination->m_monitor->m_enabled))return reject("transfer-destination-ineligible");
    // Reserve every family member before creating a workspace or moving windows.
    std::vector<Elm::Geometry::Target> admitted;
    for(const auto& id:reserved) {
        if(!effectBarriers.begin(id)){for(const auto& old:admitted)effectBarriers.definitive(old);return reject("transfer-family-bound");}
        admitted.push_back(id);
    }
    const auto oldFocus=Desktop::focusState()->window();
    const auto outputDependency=outputGeneration;
    try {
        if(!destination)destination=State::workspaceState()->create(p.destination,sourceMonitor->m_id);
        if(!destination || !destination->m_monitor)return session.lastReply;
        const auto destinationMonitor=destination->m_monitor.lock();
        const auto destinationGeneration=geometryWorkspaces.bind(destination);
        for(const auto& window:*family) {
            const auto identity=std::ranges::find_if(members,[&](const Member& m){return m.window.lock()==window;});
            if(identity==members.end() || window->m_workspace!=source || window->m_pinned || window->m_group || outputGeneration!=outputDependency)return session.lastReply;
            g_pHyprRenderer->damageWindow(window,true);
            Desktop::globalWindowController()->moveWindowToWorkspace(window,destination);
            g_pHyprRenderer->damageWindow(window,true);
        }
        // Native policy replaces a recipient moved out of the visible workspace.
        // The Elm view never calls focus or follows the destination implicitly.
        if(oldFocus && std::ranges::find(*family,oldFocus)!=family->end() && !destination->isVisible()) {
            PHLWINDOW fallback=nullptr;
            for(const auto& candidate:Desktop::windowState()->windows()) {
                if(std::ranges::find(*family,candidate)!=family->end() || !candidate->m_isMapped || !candidate->m_workspace || !candidate->m_workspace->isVisible() || candidate->isHidden() || Desktop::WindowPolicy::isMinimized(candidate) || !candidate->acceptsInput() || candidate->m_ruleApplicator->noFocus().valueOrDefault())continue;
                const auto recipient=SceneModal::focusRecipient(candidate);
                if(recipient && *recipient==candidate){fallback=candidate;break;}
            }
            Desktop::focusState()->fullWindowFocus(fallback,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE);
        }
        geometryPlacements.retire(*Elm::Placement::Identity::fromNative(lifetime,rootId));
        refreshFacts();refreshGeometryFacts();notifyEffectChange();
        if(outputGeneration!=outputDependency || geometryWorkspaces.bind(destination)!=destinationGeneration || destination->m_monitor.lock()!=destinationMonitor || !destinationMonitor->m_enabled)return session.lastReply;
        for(size_t i=0;i<family->size();++i) {
            const auto& window=(*family)[i];
            const auto identity=std::ranges::find_if(members,[&](const Member& m){return m.id==reserved[i].incarnation && m.window.lock()==window;});
            if(identity==members.end() || !window->m_isMapped || window->m_workspace!=destination || window->m_monitor.lock()!=destinationMonitor || Desktop::WindowPolicy::isMinimized(window)!=minimized[i])return session.lastReply;
        }
        for(const auto& id:reserved)effectBarriers.definitive(id);
        session.lastReply=reply("Committed","workspace-transferred");
    } catch(...) {notifyEffectChange();} // Retain Unknown custody; no retry/rollback.
    return session.lastReply;
}
