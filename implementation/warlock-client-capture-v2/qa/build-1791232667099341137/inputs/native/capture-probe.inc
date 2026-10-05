// QA-only producer observation. The binding is authenticated by the native peer
// registry. Request JSON can name a current incarnation, but cannot attest pixels,
// clocks, output generation, source liveness, locks or completion.
std::string previewProbe(pid_t peer,const std::string& start,const std::string& operation,JsonObject* object) {
    const bool scoped=operation=="preview-capture-probe-scoped-request";
    const bool scope=operation=="preview-capture-probe-scope-request";
    const bool capture=operation=="preview-capture-probe-request" || scoped;
    const bool clock=operation=="preview-capture-probe-clock-request";
    const bool state=operation=="preview-capture-probe-state-request";
    const bool retire=operation=="preview-capture-probe-retire-request";
    if(!(capture || scope || clock || state || retire) || !(scoped?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs","context"}):scope?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation"}):capture?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs"}):
        fields(object,{"protocolVersion","kind","binding","requestId"}))) return error("preview-probe-schema");
    const auto bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");
    if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId) return error("preview-probe-schema");
    const auto native=counter(bound,"lifetime"),session=counter(bound,"session"),frontend=counter(bound,"frontend");
    auto found=sessions.find(peer);
    if(!native || !session || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || found->second.id!=*session || found->second.frontend!=*frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{*native,*session,*frontend})) return error("binding-mismatch");
    const auto& active=found->second;
    auto envelope=[&](const char* kind) {return "{\"protocolVersion\":3,\"kind\":"+quote(kind)+",\"binding\":"+binding(active)+",\"requestId\":"+quote(std::to_string(*requestId));};
    if(clock) return envelope("preview-capture-probe-clock")+",\"clock\":"+quote(std::to_string(lifetime))+",\"nowNs\":"+quote(std::to_string(preview::capture::nativeNow()))+"}";
    // Privacy and output invalidation remove all completed probe pixels. Source
    // stop is deliberately not a retirement event for independently owned RAM.
    refreshOutputs();
    const bool locked=!g_pSessionLockManager || g_pSessionLockManager->isSessionLocked();
    for(auto& [pid,item]:captureProbes) if(locked || item.output!=outputGeneration)item.revoked=true;
    if(locked) return error("preview-probe-locked");
    if(scope) {
        const auto subject=counter(object,"subjectIncarnation");if(!subject)return error("preview-scope-subject");
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& row){return row.id==*subject;});
        const auto window=member==members.end()?PHLWINDOW{}:member->window.lock();
        const auto context=previewContext(window,*subject);if(!context || !window->m_isMapped)return error("preview-scope-source-unavailable");
        const auto monitor=window->m_monitor.lock();if(!monitor || !monitor->m_output)return error("preview-scope-output-unavailable");
        const auto dimensions=monitor->m_pixelSize;
        if(!std::isfinite(dimensions.x) || !std::isfinite(dimensions.y) || dimensions.x<1 || dimensions.y<1 || dimensions.x>4096 || dimensions.y>4096 || std::floor(dimensions.x)!=dimensions.x || std::floor(dimensions.y)!=dimensions.y)return error("preview-scope-dimensions");
        const auto plan=preview::capture::plan(static_cast<uint32_t>(dimensions.x),static_cast<uint32_t>(dimensions.y));if(!plan)return error("preview-scope-dimensions");
        if(previewObservation==std::numeric_limits<uint64_t>::max())return error("preview-scope-observation-exhausted");
        const bool live=!Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer && g_pHyprRenderer->shouldRenderWindow(window);
        const bool gpu=g_pHyprRenderer && Render::GL::g_pHyprOpenGL;
        return envelope("preview-capture-probe-scope")+",\"scope\":{\"binding\":"+binding(active)+",\"context\":"+contextJSON(*context)+",\"observation\":"+quote(std::to_string(++previewObservation))+",\"clock\":"+quote(std::to_string(lifetime))+",\"now\":"+quote(std::to_string(preview::capture::nativeNow()))+",\"present\":true,\"sourceLive\":"+(live?"true":"false")+",\"locked\":false,\"gpuReady\":"+(gpu?"true":"false")+"},\"maximumTransferBytes\":"+quote(std::to_string((plan->png+4095)&~uint64_t{4095}))+",\"previewEligible\":false,\"scopeKind\":\"root-surface-commit-monitor-plane-unqualified\"}";
    }
    if(retire) {
        if(auto held=captureProbes.find(peer);held!=captureProbes.end() && held->second.exported)return error("preview-probe-import-outstanding");
        captureProbes.erase(peer);
        return envelope("preview-capture-probe-retired")+",\"ownedBytes\":\"0\"}";
    }
    if(capture) {
        const auto subject=counter(object,"subjectIncarnation"),deadline=counter(object,"deadlineNs");
        const uint64_t now=preview::capture::nativeNow();
        if(!subject || !deadline || *deadline<=now || *deadline-now>2000000000ULL) return error("preview-probe-deadline");
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==*subject;});
        if(member==members.end()) return error("preview-probe-subject");
        const auto window=member->window.lock();
        if(!window || !window->m_isMapped || Desktop::WindowPolicy::isMinimized(window)) return error("preview-probe-source-unavailable");
        const auto monitor=window->m_monitor.lock();
        if(!monitor || !monitor->m_output) return error("preview-probe-output-unavailable");
        if(captureProbes.contains(peer)) return error("preview-probe-retire-required");
        const auto stamp=previewContext(window,*subject);if(!stamp)return error("preview-probe-source-epoch-unavailable");
        if(scoped && requestedContext(objectMember(object,"context"))!=stamp)return error("preview-probe-context-stale");
        const uint64_t generation=outputGeneration;
        const auto pixels=monitor->m_pixelSize;
        auto current=[&] {
            refreshOutputs();
            const auto owner=sessions.find(peer);
            const auto memberNow=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==*subject && value.window.lock()==window;});
            return owner!=sessions.end() && owner->second.id==*session && owner->second.frontend==*frontend && startTime(peer)==start && memberNow!=members.end() &&
                g_pSessionLockManager && !g_pSessionLockManager->isSessionLocked() && outputGeneration==generation && window->m_monitor.lock()==monitor && monitor->m_output && monitor->m_pixelSize==pixels &&
                window->m_isMapped && previewContext(window,*subject)==stamp && !Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer && g_pHyprRenderer->shouldRenderWindow(window);
        };
        auto image=preview::capture::captureOwnedPlane(window,*captureBudget,*deadline,current);
        if(!image) return error("preview-probe-capture-unavailable");
        const auto checksum=preview::capture::crc(image->png());
        if(preview::capture::nativeNow()>=*deadline || !current()) return error("preview-probe-expired");
        refreshFacts();
        if(previewContext(window,*subject)!=stamp)return error("preview-probe-context-stale");
        auto [inserted,ok]=captureProbes.emplace(peer,CaptureProbe{*session,*frontend,*subject,*requestId,generation,preview::capture::nativeNow(),checksum,std::move(image)});
        if(!ok)return error("preview-probe-capture-unavailable");
        inserted->second.privacy=previewPrivacy;inserted->second.rendering=previewRendering;inserted->second.scene=stamp->scene.value;inserted->second.content=stamp->content.value;inserted->second.deadline=*deadline;
    }
    const auto probe=captureProbes.find(peer);
    if(probe==captureProbes.end() || probe->second.client || probe->second.revoked || probe->second.session!=*session || probe->second.frontend!=*frontend) return error("preview-probe-unavailable");
    const auto& held=probe->second;
    return envelope("preview-capture-probe-owned")+",\"subjectIncarnation\":"+quote(std::to_string(held.incarnation))+",\"captureRequest\":"+quote(std::to_string(held.request))+
        ",\"outputGeneration\":"+quote(std::to_string(held.output))+",\"completedNs\":"+quote(std::to_string(held.completed))+
        ",\"width\":"+std::to_string(held.image->width)+",\"height\":"+std::to_string(held.image->height)+",\"encodedBytes\":"+quote(std::to_string(held.image->png().size()))+
        ",\"ownedBytes\":"+quote(std::to_string(held.image->charge()))+",\"crc32\":"+quote(std::to_string(held.checksum))+
        ",\"encoding\":\"PNG-RGBA8-straight\",\"planeSpace\":\"monitor-physical-unqualified\",\"previewEligible\":false}";
}
