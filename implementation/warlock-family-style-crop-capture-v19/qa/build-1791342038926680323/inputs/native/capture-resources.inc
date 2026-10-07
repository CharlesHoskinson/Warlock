std::string clientResources(pid_t peer,const std::string& start,const std::string& operation,JsonObject* object) {
    using namespace preview::resources;
    if(!fields(object,{"protocolVersion","kind","binding","requestId","captureRequest","subjectIncarnation","transfer"}))return error("client-resource-schema");
    const auto bound=objectMember(object,"binding");
    if(!bound || !fields(bound,{"lifetime","session","frontend"}))return error("client-resource-schema");
    const auto native=counter(bound,"lifetime"),session=counter(bound,"session"),frontend=counter(bound,"frontend");
    const auto request=counter(object,"requestId"),capture=counter(object,"captureRequest"),subject=counter(object,"subjectIncarnation"),transfer=counter(object,"transfer",true);
    if(!native || !session || !frontend || !request || !capture || !subject || !transfer)return error("client-resource-schema");
    auto owner=sessions.find(peer);
    if(owner==sessions.end() || owner->second.start!=start || *native!=lifetime || owner->second.id!=*session || owner->second.frontend!=*frontend ||
        !grantRegistry->callerMatches(verifiedPeer(peer,start),{*native,*session,*frontend}))return error("client-resource-binding");
    const auto action=operation=="preview-client-resource-state-request"?Operation::Observe:
        operation=="preview-client-resource-release-request"?Operation::ReleaseExport:Operation::RetireProducer;
    const bool locked=!g_pSessionLockManager || g_pSessionLockManager->isSessionLocked();
    return execute(captureProbes,peer,Binding{*native,*session,*frontend},Target{*capture,*subject},*request,
        preview::capture::nativeNow(),locked,action,*transfer,captureResourceSequence,wire);
}
