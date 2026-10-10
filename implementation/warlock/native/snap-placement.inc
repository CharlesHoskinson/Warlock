// Negotiated geometry operation; syntax alone never admits a native mutation.
struct SnapSubmission {
    std::string region;
    CBox geometry;
    uint64_t monitor, output, area, workspace;
};
std::optional<SnapSubmission> snapSubmission(JsonObject* intent) {
    const auto p=objectMember(intent,"placement");
    if(!p || !fields(p,{"region","geometry","monitor","outputOwnershipGeneration","workAreaRevision","workspaceGeneration"}))return {};
    const auto name=json_object_get_member(p,"region");
    if(!name || !JSON_NODE_HOLDS_VALUE(name) || json_node_get_value_type(name)!=G_TYPE_STRING)return {};
    const std::string region=json_node_get_string(name);
    if(region!="left-half" && region!="right-half" && region!="top-left" && region!="top-right" && region!="bottom-left" && region!="bottom-right")return {};
    const auto monitor=counter(p,"monitor",true),output=counter(p,"outputOwnershipGeneration"),area=counter(p,"workAreaRevision"),workspace=counter(p,"workspaceGeneration");
    const auto node=json_object_get_member(p,"geometry");
    if(!monitor || !output || !area || !workspace || !node || !JSON_NODE_HOLDS_ARRAY(node))return {};
    const auto values=json_node_get_array(node);if(json_array_get_length(values)!=4)return {};
    double rect[4];
    for(unsigned i=0;i<4;i++){
        const auto value=json_array_get_element(values,i);if(!JSON_NODE_HOLDS_VALUE(value))return {};
        const auto type=json_node_get_value_type(value);if(type!=G_TYPE_INT64 && type!=G_TYPE_DOUBLE)return {};
        rect[i]=json_node_get_double(value);if(!std::isfinite(rect[i]) || std::abs(rect[i])>INT_MAX || (i>=2 && rect[i]<=0))return {};
    }
    return SnapSubmission{region,CBox{rect[0],rect[1],rect[2],rect[3]},*monitor,*output,*area,*workspace};
}
std::string snapFingerprint(const SnapSubmission& p) {
    return quote(p.region)+":"+geometryRect(p.geometry)+":"+std::to_string(p.monitor)+":"+std::to_string(p.output)+":"+std::to_string(p.area)+":"+std::to_string(p.workspace);
}
CBox snapRegion(const CBox& area,const std::string& region) {
    const bool right=region=="right-half" || region=="top-right" || region=="bottom-right";
    const bool quarter=region!="left-half" && region!="right-half";
    const bool bottom=region=="bottom-left" || region=="bottom-right";
    return {area.x+(right?area.w/2:0),area.y+(bottom?area.h/2:0),area.w/2,quarter?area.h/2:area.h};
}
template<class Reply,class Reject>
std::string performSnapEffect(Session& session,const SnapSubmission& placement,uint64_t targetId,const PHLWINDOW& window,
    const Elm::Geometry::Target& barrier,const GeometryScope& scope,const Elm::Placement::Identity& key,Reply reply,Reject reject) {
    // Protocol 3 retains negotiated snap support alongside pin/unpin.
    if(session.geometryProtocol!=2 && session.geometryProtocol!=3)return reject("snap-protocol");
    const auto modes=Fullscreen::controller()->getFullscreenModes(window);
    if(modes.internal!=Fullscreen::FSMODE_NONE || modes.client!=Fullscreen::FSMODE_NONE)return reject("snap-mode");
    if(geometryPlacements.read(key,key,scope.scope))return reject("ordinary-placement-reserved");
    const auto wg=geometryWorkspaces.bind(scope.workspace),og=geometryOutputs.bind(scope.output);
    const auto workArea=scope.workspace->m_space->workArea(true);
    const auto revision=geometryWorkAreaRevision(wg,og,geometryRect(workArea));
    if(placement.monitor!=static_cast<uint64_t>(scope.output->m_id) || placement.output!=og || placement.area!=revision || placement.workspace!=wg)return reject("snap-scope-mismatch");
    const auto desired=snapRegion(workArea,placement.region);
    if(std::abs(desired.x-placement.geometry.x)>1e-6 || std::abs(desired.y-placement.geometry.y)>1e-6 || std::abs(desired.w-placement.geometry.w)>1e-6 || std::abs(desired.h-placement.geometry.h)>1e-6)return reject("snap-region-mismatch");
    const auto input=geometryInput(window,Elm::ProspectiveGeometry::Operation::RestoreOrdinary,desired,{});
    const auto projected=input?Elm::ProspectiveGeometry::project(*input):std::nullopt;
    const auto conversion=geometryPolicyInputs(window);
    if(!projected || conversion=="null")return reject("snap-size-infeasible");
    if(!WarlockGestureEnd::canRememberSnap(window->layoutTarget()))return reject("caption-placement-capacity");
    const auto ordinaryCaptionBox=window->layoutTarget()->position();
    const auto oldFocus=Desktop::focusState()->window();const auto oldKeyboard=g_pSeatManager->m_state.keyboardFocus.lock();
    const auto oldPointer=g_pSeatManager->m_state.pointerFocus.lock();const auto peers=geometryPeers(window);
    if(!effectBarriers.begin(barrier))return reject("native-operation-bound");
    try {
        window->layoutTarget()->setPositionGlobal(projected->logical);
        refreshFacts();refreshGeometryFacts();notifyEffectChange();
        const auto live=std::ranges::find_if(members,[&](const Member& entry){return entry.id==targetId && entry.window.lock()==window;});
        if(live==members.end() || !geometryTargetEligible(window,session.geometryProtocol))return session.lastReply;
        const auto current=geometryScope(window);const auto actual=Fullscreen::controller()->getFullscreenModes(window);
        if(!current || !(current->scope==scope.scope) || current->workspace!=scope.workspace || current->output!=scope.output || current->outputDependency!=scope.outputDependency || actual.internal!=Fullscreen::FSMODE_NONE || actual.client!=Fullscreen::FSMODE_NONE || Desktop::focusState()->window()!=oldFocus || g_pSeatManager->m_state.keyboardFocus.lock()!=oldKeyboard || g_pSeatManager->m_state.pointerFocus.lock()!=oldPointer || geometryPeers(window)!=peers)return session.lastReply;
        const auto freshInput=geometryInput(window,Elm::ProspectiveGeometry::Operation::RestoreOrdinary,desired,{});
        const auto fresh=freshInput?Elm::ProspectiveGeometry::project(*freshInput):std::nullopt;
        if(!fresh || geometryPolicyInputs(window)!=conversion || fresh->logical!=projected->logical || fresh->real!=projected->real || fresh->configure!=projected->configure || window->layoutTarget()->position()!=projected->logical || window->geometricBox(Desktop::View::IGeometric::GEOMETRIC_GOAL)!=projected->real || window->m_pendingReportedSize!=projected->real.size() || window->m_pendingReportedSize.floor()!=projected->configure)return session.lastReply;
        WarlockGestureEnd::rememberSnap(window->layoutTarget(),ordinaryCaptionBox,ordinaryCaptionBox);
        effectBarriers.definitive(barrier);session.lastReply=reply("Committed","applied");
    }catch(...){notifyEffectChange();} // Retain Unknown, never replay or invent rollback.
    return session.lastReply;
}
