// Typed workspace identity; never substitute a window incarnation.
struct WorkspaceNavigationRecord {
    std::string bound, fingerprint, intent, status, reason;
    uint64_t request, generation;
};
std::vector<WorkspaceNavigationRecord> workspaceNavigationRecords;
bool workspaceNavigationBlocked() {
    return std::ranges::any_of(workspaceNavigationRecords,[](const auto& r){return r.status=="Unknown";});
}
bool workspaceNavigationRow(JsonObject* row) {
    if(!row || !fields(row,{"identity","generation","monitor","outputOwnershipGeneration"}))return false;
    const auto id=counter(row,"identity");
    return id && *id<=static_cast<uint64_t>(std::numeric_limits<int64_t>::max()) && counter(row,"generation") && counter(row,"monitor",true) && counter(row,"outputOwnershipGeneration");
}
std::string workspaceNavigationFingerprint(JsonObject* intent) {
    if(!intent || !fields(intent,{"request","generation","source","destination","context"}) || !counter(intent,"request") || !counter(intent,"generation"))throw std::runtime_error("workspace-navigation-intent");
    const auto source=objectMember(intent,"source"),destination=objectMember(intent,"destination"),context=objectMember(intent,"context");
    if(!workspaceNavigationRow(source) || !workspaceNavigationRow(destination) || !context || !fields(context,{"lifetime","epoch","output","revision"}))throw std::runtime_error("workspace-navigation-scope");
    std::string result;
    for(const auto name:{"request","generation"})result+=":"+std::to_string(*counter(intent,name));
    for(const auto row:{source,destination})for(const auto name:{"identity","generation","monitor","outputOwnershipGeneration"})result+=":"+std::to_string(*counter(row,name,std::string(name)=="monitor"));
    for(const auto name:{"lifetime","epoch","output","revision"}){const auto value=counter(context,name);if(!value)throw std::runtime_error("workspace-navigation-context");result+=":"+std::to_string(*value);}
    return result;
}
PHLWORKSPACE workspaceNavigationResolve(JsonObject* row) {
    for(const auto& ref:State::workspaceState()->workspaces()) {
        const auto workspace=ref.lock();
        if(!workspace || workspace->m_id<=0 || workspace->m_isSpecialWorkspace || !workspace->m_space || static_cast<uint64_t>(workspace->m_id)!=*counter(row,"identity"))continue;
        const auto monitor=workspace->m_monitor.lock();
        if(monitor && monitor->m_enabled && monitor->m_id>=0 && static_cast<uint64_t>(monitor->m_id)==*counter(row,"monitor",true) && geometryWorkspaces.bind(workspace)==*counter(row,"generation") && geometryOutputs.bind(monitor)==*counter(row,"outputOwnershipGeneration"))return workspace;
    }
    return nullptr;
}
std::string workspaceNavigationEncoded(const WorkspaceNavigationRecord& record) {
    return "{\"schema\":1,\"binding\":"+record.bound+",\"intent\":"+record.intent+",\"status\":"+quote(record.status)+",\"reason\":"+quote(record.reason)+"}";
}
std::string workspaceNavigationReply(const WorkspaceNavigationRecord& record) {
    return "{\"protocolVersion\":3,\"kind\":\"workspace-navigation-outcome\",\"workspaceProtocol\":1,\"binding\":"+record.bound+",\"intent\":"+record.intent+",\"status\":"+quote(record.status)+",\"reason\":"+quote(record.reason)+"}";
}
std::string applyWorkspaceNavigation(Session& session,JsonObject* object) {
    const auto intent=objectMember(object,"intent");const auto fingerprint=workspaceNavigationFingerprint(intent);
    gchar* raw=json_to_string(json_object_get_member(object,"intent"),FALSE);std::string encoded(raw);g_free(raw);
    const auto scope=binding(session);const auto request=*counter(intent,"request"),generation=*counter(intent,"generation");
    WorkspaceNavigationRecord proposed{scope,fingerprint,encoded,"Unknown","effect-unproven",request,generation};
    auto found=std::ranges::find_if(workspaceNavigationRecords,[&](const auto& r){return r.bound==scope;});
    if(found!=workspaceNavigationRecords.end()) {
        if(request==found->request)return fingerprint==found->fingerprint?workspaceNavigationReply(*found):error("workspace-navigation-request-reuse");
        if(request<found->request || generation<=found->generation)return error("workspace-navigation-order");
    } else if(workspaceNavigationRecords.size()>=64)return error("workspace-navigation-history-bound");
    if(workspaceNavigationBlocked())return error("workspace-navigation-unresolved");
    if(found==workspaceNavigationRecords.end()){workspaceNavigationRecords.push_back(proposed);found=std::prev(workspaceNavigationRecords.end());}else *found=proposed;
    auto& record=*found;
    const auto reject=[&](const char* reason){record.status="Refused";record.reason=reason;return workspaceNavigationReply(record);};
    const auto context=objectMember(intent,"context");
    if(*counter(context,"lifetime")!=lifetime || *counter(context,"epoch")!=session.frontend)return reject("authority-mismatch");
    if(!session.geometryEnabled || session.geometryProtocol!=3 || session.geometryFrontend!=session.frontend)return reject("workspace-observation-required");
    refreshFacts();refreshGeometryFacts(3);
    if(*counter(context,"output")!=outputGeneration || *counter(context,"revision")!=geometryRevision)return reject("dependency-mismatch");
    for(const auto& member:members)if(effectBarriers.blocked({lifetime,member.id}))return reject("native-operation-unresolved");
    if(g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || g_layoutManager->dragController()->target())return reject("input-blocked");
    const auto source=workspaceNavigationResolve(objectMember(intent,"source")),destination=workspaceNavigationResolve(objectMember(intent,"destination"));
    if(!source || !destination)return reject("workspace-owner-mismatch");
    if(source==destination)return reject("workspace-already-active");
    const auto sourceMonitor=source->m_monitor.lock(),destinationMonitor=destination->m_monitor.lock();
    if(Desktop::focusState()->monitor()!=sourceMonitor || sourceMonitor->m_activeWorkspace!=source || sourceMonitor->m_activeSpecialWorkspace || destinationMonitor->m_activeSpecialWorkspace)return reject("source-workspace-mismatch");
    // Existing ordinary empty destinations only. No creation or family transfer.
    for(const auto& window:Desktop::windowState()->windows())if(window->m_isMapped && (window->m_workspace==destination || window->m_pinned))return reject("destination-not-empty");
    const auto membership=[&](){std::string value;for(const auto& window:Desktop::windowState()->windows())if(window->m_isMapped){const auto workspace=window->m_workspace;const auto monitor=window->m_monitor.lock();value+=identityOf(window)+":"+(workspace?std::to_string(workspace->m_id):"null")+":"+(monitor?std::to_string(monitor->m_id):"null")+":"+(Desktop::WindowPolicy::isMinimized(window)?"1":"0")+":"+(window->m_pinned?"1":"0")+";";}return value;};
    const auto before=membership();const auto output=outputGeneration;
    try {
        destinationMonitor->changeWorkspace(destination,false,true,true);
        Desktop::focusState()->rawMonitorFocus(destinationMonitor);
        Desktop::focusState()->fullWindowFocus(nullptr,Desktop::FOCUS_REASON_DESKTOP_STATE_CHANGE);
        refreshFacts();refreshGeometryFacts(3);notifyEffectChange();
        if(destinationMonitor->m_activeWorkspace!=destination || !destination->isVisible() || Desktop::focusState()->monitor()!=destinationMonitor || Desktop::focusState()->window() || g_pSeatManager->m_state.keyboardFocus.lock() || workspaceNavigationResolve(objectMember(intent,"destination"))!=destination || output!=outputGeneration || membership()!=before || g_pSessionLockManager->isSessionLocked() || !g_pInputManager->m_exclusiveLSes.empty() || g_pSeatManager->m_seatGrab || g_layoutManager->dragController()->target())return workspaceNavigationReply(record);
        record.status="Committed";record.reason="applied";
    }catch(...){notifyEffectChange();} // Mutation may have happened: retain Unknown.
    return workspaceNavigationReply(record);
}
std::string readWorkspaceNavigation(Session& session,JsonObject* object) {
    const auto queried=objectMember(object,"record");
    if(!queried || !fields(queried,{"binding","intent"}))throw std::runtime_error("workspace-navigation-query");
    const auto bound=objectMember(queried,"binding"),intent=objectMember(queried,"intent");
    if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !counter(bound,"lifetime") || !counter(bound,"session") || !counter(bound,"frontend") || *counter(bound,"lifetime")!=lifetime)throw std::runtime_error("workspace-navigation-query-binding");
    const auto fingerprint=workspaceNavigationFingerprint(intent);
    gchar* raw=json_to_string(json_object_get_member(queried,"binding"),FALSE);gchar* iraw=json_to_string(json_object_get_member(queried,"intent"),FALSE);
    // Compare numeric scope, independent of JSON object order.
    const auto found=std::ranges::find_if(workspaceNavigationRecords,[&](const auto& r){
        auto parser=json_parser_new();const bool parsed=json_parser_load_from_data(parser,r.bound.c_str(),-1,nullptr);
        const auto stored=parsed?json_node_get_object(json_parser_get_root(parser)):nullptr;
        const bool equal=stored && *counter(stored,"lifetime")==*counter(bound,"lifetime") && *counter(stored,"session")==*counter(bound,"session") && *counter(stored,"frontend")==*counter(bound,"frontend") && r.fingerprint==fingerprint;g_object_unref(parser);return equal;
    });
    WorkspaceNavigationRecord absent{raw,fingerprint,iraw,"Unknown","native-record-unavailable",*counter(intent,"request"),*counter(intent,"generation")};g_free(raw);g_free(iraw);
    return "{\"protocolVersion\":3,\"kind\":\"workspace-navigation-state\",\"workspaceProtocol\":1,\"binding\":"+binding(session)+",\"requestId\":"+quote(std::to_string(*counter(object,"requestId")))+",\"record\":"+workspaceNavigationEncoded(found==workspaceNavigationRecords.end()?absent:*found)+"}";
}
