// Isolated qualification candidate: exact implemented operation negotiation.
Elm::Placement::Rect placementRect(const CBox& box) {return {box.x,box.y,box.w,box.h};}
struct GeometryScope {
    Elm::Placement::Scope scope;
    PHLWORKSPACE workspace;
    PHLMONITOR output;
    uint64_t outputDependency;
};
std::optional<GeometryScope> geometryScope(const PHLWINDOW& window) {
    const auto workspace=window->m_workspace;const auto output=window->m_monitor.lock();
    if(!workspace || !workspace->m_space || !output || output->m_id<0) return {};
    const auto wg=geometryWorkspaces.bind(workspace),og=geometryOutputs.bind(output);
    const auto area=geometryWorkAreaRevision(wg,og,geometryRect(workspace->m_space->workArea(true)));
    const auto scope=Elm::Placement::Scope::fromNative(workspace->m_id,wg,static_cast<uint64_t>(output->m_id),og,area);
    if(!scope) return {};
    return GeometryScope{*scope,workspace,output,outputGeneration};
}
bool geometryTargetEligible(const PHLWINDOW& window,int protocol) {
    const auto target=window->layoutTarget();const auto workspace=window->m_workspace;
    const auto modes=Fullscreen::controller()->getFullscreenModes(window);
    if(!target || !workspace || !workspace->m_space || !window->m_isMapped || window->parent() || window->m_group || window->m_isX11 || !window->m_xdgSurface || !window->m_xdgSurface->m_toplevel || !target->floating() || window->m_pinned || window->isHidden() || Desktop::WindowPolicy::isMinimized(window) || !workspace->isVisible() || window->onSpecialWorkspace() || !window->m_monitor.lock() || target->workspace()!=workspace || modes.internal!=modes.client || modes.internal==Fullscreen::FSMODE_FULLSCREEN || Fullscreen::controller()->layoutManagedFS(window)) return false;
    if(g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || g_layoutManager->dragController()->target()) return false;
    const auto family=nativeFamily(window);if(!family || family->size()!=1) return false;
    if(protocol==1) {
    const auto raw=window->m_xdgSurface->m_toplevel->m_current;
    if(!std::isfinite(raw.minSize.x) || !std::isfinite(raw.minSize.y) || !std::isfinite(raw.maxSize.x) || !std::isfinite(raw.maxSize.y) || raw.minSize.x<0 || raw.minSize.y<0 || raw.maxSize.x<0 || raw.maxSize.y<0 || raw.maxSize.x>0 || raw.maxSize.y>0 || raw.minSize.x>1 || raw.minSize.y>1) return false;
    const auto minimum=target->minSize(),maximum=target->maxSize();
    if((minimum && (minimum->x>1 || minimum->y>1)) || (maximum && (maximum->x<std::numeric_limits<double>::max() || maximum->y<std::numeric_limits<double>::max()))) return false;
    } else if(protocol==2) {
        const auto input=geometryInput(window,Elm::ProspectiveGeometry::Operation::Maximize,CBox{0,0,1,1},{});
        if(!input || geometryPolicyInputs(window)=="null" || input->xdgGeometryOrigin!=Vector2D{0,0})return false;
    } else return false;
    for(const auto& peer:Desktop::windowState()->windows()) if(peer!=window && peer->m_isMapped && peer->m_workspace==workspace) {
        const auto other=Fullscreen::controller()->getFullscreenModes(peer);
        if(other.internal!=Fullscreen::FSMODE_NONE || other.client!=Fullscreen::FSMODE_NONE) return false;
    }
    return true;
}
// Exact peer state/readback includes identity, placement and input protection.
std::string geometryPeers(const PHLWINDOW& excluded) {
    std::string result;
    for(const auto& window:Desktop::windowState()->windows()) if(window!=excluded && window->m_isMapped) {
        const auto scope=geometryScope(window);const auto modes=Fullscreen::controller()->getFullscreenModes(window);
        if(!scope || !window->layoutTarget()) throw std::runtime_error("Peer scope unavailable");
        result+=identityOf(window)+":"+identityOf(window->parent())+":"+std::to_string(scope->workspace->m_id)+":"+std::to_string(scope->output->m_id)+":"+std::to_string(geometryWorkspaces.bind(scope->workspace))+":"+std::to_string(geometryOutputs.bind(scope->output))+":"+std::to_string(geometryWorkAreaRevision(geometryWorkspaces.bind(scope->workspace),geometryOutputs.bind(scope->output),geometryRect(scope->workspace->m_space->workArea(true))))+":"+geometryMode(modes.internal)+":"+geometryMode(modes.client)+":"+geometryRect(window->layoutTarget()->position())+":"+geometryRect(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL))+":"+(Desktop::WindowPolicy::isMinimized(window)?"1":"0")+":"+(window->m_pinned?"1":"0")+":"+(window->isHidden()?"1":"0")+";";
    }
    return result;
}
std::string performGeometryEffect(Session& session,JsonObject* object) {
    const auto intent=objectMember(object,"intent");
    if(!intent || !fields(intent,{"request","generation","incarnation","operation","context"})) return error("effect-schema");
    const auto request=counter(intent,"request"),generation=counter(intent,"generation"),targetId=counter(intent,"incarnation");
    const auto context=objectMember(intent,"context");
    if(!request || !generation || !targetId || !context || !fields(context,{"lifetime","epoch","output","revision"})) return error("effect-schema");
    const auto native=counter(context,"lifetime"),epoch=counter(context,"epoch"),output=counter(context,"output"),expected=counter(context,"revision");
    const auto op=json_object_get_member(intent,"operation");
    if(!native || !epoch || !output || !expected || !op || !JSON_NODE_HOLDS_VALUE(op) || json_node_get_value_type(op)!=G_TYPE_STRING) return error("effect-schema");
    const std::string operation=json_node_get_string(op);
    gchar* raw=json_to_string(json_object_get_member(object,"intent"),FALSE);const std::string encoded(raw);g_free(raw);
    const auto reply=[&](const char* status,const char* reason){return effectOutcome(session,encoded,status,reason,2);};
    if(!session.geometryEnabled || session.geometryFrontend!=session.frontend || !session.geometryOperations.contains(operation)) return reply("Refused","geometry-operation-not-negotiated");
    const std::string fingerprint="2:"+quote(operation)+":"+std::to_string(*request)+":"+std::to_string(*generation)+":"+std::to_string(*targetId)+":"+std::to_string(*native)+":"+std::to_string(*epoch)+":"+std::to_string(*output)+":"+std::to_string(*expected);
    if(*native!=lifetime || *epoch!=session.frontend) return reply("Refused","authority-mismatch");
    if(*request==session.effectRequest) return fingerprint==session.lastPayload ? session.lastReply : reply("Refused","request-reuse");
    if(*request<session.effectRequest || *generation<=session.generation) return reply("Refused","operation-order");
    session.effectRequest=*request;session.generation=*generation;session.lastPayload=fingerprint;
    session.lastReply=reply("Unknown","effect-unproven");
    const auto reject=[&](const char* reason){session.lastReply=reply("Refused",reason);return session.lastReply;};
    if(operation!="maximize" && operation!="restore-geometry") return reject("unsupported-operation");
    refreshGeometryFacts();
    if(*output!=outputGeneration || *expected!=geometryRevision) return reject("dependency-mismatch");
    const auto member=std::ranges::find_if(members,[&](const Member& entry){return entry.id==*targetId;});
    if(member==members.end() || !member->window.lock()) return reject("stale-incarnation");
    const auto window=member->window.lock();const Elm::Geometry::Target barrier{lifetime,*targetId};
    if(effectBarriers.blocked(barrier)) return reject("native-operation-unresolved");
    if(!geometryTargetEligible(window,session.geometryProtocol)) return reject("geometry-ineligible");
    const auto scope=geometryScope(window);const auto key=Elm::Placement::Identity::fromNative(lifetime,*targetId);
    if(!scope || !key) return reject("geometry-scope");
    const auto modes=Fullscreen::controller()->getFullscreenModes(window);
    auto original=geometryPlacements.read(*key,key,scope->scope);
    const bool maximize=operation=="maximize";
    if(maximize && modes.internal==Fullscreen::FSMODE_NONE && original) {
        const Elm::Placement::Original current{placementRect(window->layoutTarget()->position()),placementRect(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL))};
        if(!(current==*original)) return reject("ordinary-placement-external-change");
    }
    if(maximize && modes.internal==Fullscreen::FSMODE_MAXIMIZED && !original) return reject("ordinary-placement-unavailable");
    if(!maximize && modes.internal==Fullscreen::FSMODE_MAXIMIZED && !original) return reject("ordinary-placement-unavailable");
    // Desired-state duplicate is a read-only operation, never a recapture.
    if((maximize && modes.internal==Fullscreen::FSMODE_MAXIMIZED) || (!maximize && modes.internal==Fullscreen::FSMODE_NONE)) {
        if(!maximize && original) {
            const Elm::Placement::Original current{placementRect(window->layoutTarget()->position()),placementRect(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL))};
            if(!(current==*original)) return reject("ordinary-placement-external-change");
            geometryPlacements.retire(*key);refreshGeometryFacts();notifyEffectChange();
        }
        session.lastReply=reply("Committed","already-applied");return session.lastReply;
    }
    const auto prospective=geometryProspective(window,maximize,original);
    const auto conversion=geometryPolicyInputs(window);
    if(session.geometryProtocol==2 && (!prospective || conversion=="null"))return reject("geometry-size-infeasible");
    const auto oldFocus=Desktop::focusState()->window();const auto oldKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
    const auto oldPointer=g_pSeatManager->m_state.pointerFocus.lock();const auto peers=geometryPeers(window);
    if(!effectBarriers.begin(barrier)) return reject("native-operation-bound");
    if(maximize) {
        const Elm::Placement::Original capture{placementRect(window->layoutTarget()->position()),placementRect(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL))};
        const auto result=geometryPlacements.capture(*key,key,scope->scope,capture);
        original=geometryPlacements.read(*key,key,scope->scope);
        if((result!=Elm::Placement::Capture::Captured && result!=Elm::Placement::Capture::Duplicate) || !original) {
            effectBarriers.definitive(barrier);return reject("ordinary-placement-bound-or-incompatible");
        }
    }
    try {
        const auto desired=maximize?Fullscreen::FSMODE_MAXIMIZED:Fullscreen::FSMODE_NONE;
        Fullscreen::controller()->setFullscreenMode(window,desired,desired,false);
        refreshFacts();refreshGeometryFacts();notifyEffectChange();
        // Callbacks may replace identity/owners. Reacquire exact native member.
        const auto live=std::ranges::find_if(members,[&](const Member& entry){return entry.id==*targetId && entry.window.lock()==window;});
        if(live==members.end() || !geometryTargetEligible(window,session.geometryProtocol)) return session.lastReply;
        const auto currentScope=geometryScope(window);const auto actual=Fullscreen::controller()->getFullscreenModes(window);
        if(!currentScope || !(currentScope->scope==scope->scope) || currentScope->workspace!=scope->workspace || currentScope->output!=scope->output || currentScope->outputDependency!=scope->outputDependency || actual.internal!=desired || actual.client!=desired || Desktop::focusState()->window()!=oldFocus || g_pSeatManager->m_state.keyboardFocus.lock()!=oldKeyboard || g_pSeatManager->m_state.pointerFocus.lock()!=oldPointer || geometryPeers(window)!=peers) return session.lastReply;
        const auto known=geometryPlacements.read(*key,key,currentScope->scope);if(!known) return session.lastReply;
        if(session.geometryProtocol==2) {
            const auto fresh=geometryProspective(window,maximize,known);
            if(!fresh || geometryPolicyInputs(window)!=conversion || fresh->logical!=prospective->logical || fresh->real!=prospective->real || fresh->configure!=prospective->configure || window->layoutTarget()->position()!=prospective->logical || window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)!=prospective->real || window->m_pendingReportedSize!=prospective->real.size() || window->m_pendingReportedSize.floor()!=prospective->configure)return session.lastReply;
        }
        if(maximize) {
            if(geometryRect(window->layoutTarget()->position())!=geometryRect(scope->workspace->m_space->workArea(true))) return session.lastReply;
        } else {
            const Elm::Placement::Original restored{placementRect(window->layoutTarget()->position()),placementRect(window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL))};
            if(!(restored==*known)) return session.lastReply;
            geometryPlacements.retire(*key);
        }
        effectBarriers.definitive(barrier);session.lastReply=reply("Committed","applied");
    } catch(...) {notifyEffectChange();} // No retries, no recapture, no fabricated rollback.
    return session.lastReply;
}
