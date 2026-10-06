// QA-only producer observation. The binding is authenticated by the native peer
// registry. Request JSON can name a current incarnation, but cannot attest pixels,
// clocks, output generation, source liveness, locks or completion.
std::string previewProbe(pid_t peer,const std::string& start,const std::string& incomingOperation,JsonObject* object) {
    const bool styled=incomingOperation=="preview-family-style-crop-scoped-request" || incomingOperation=="preview-family-style-crop-state-request" || incomingOperation=="preview-family-style-crop-retire-request";
    const auto planeOperation=styled?std::string("preview-family-crop-")+incomingOperation.substr(std::string("preview-family-style-crop-").size()):incomingOperation;
    const bool crop=planeOperation=="preview-family-crop-scoped-request" || planeOperation=="preview-family-crop-state-request" || planeOperation=="preview-family-crop-retire-request";
    const auto operation=crop?std::string("preview-family-")+planeOperation.substr(std::string("preview-family-crop-").size()):planeOperation;
    const bool family=operation=="preview-family-scoped-request" || operation=="preview-family-state-request" || operation=="preview-family-retire-request";
    const bool popup=operation=="preview-popup-scoped-request" || operation=="preview-popup-state-request" || operation=="preview-popup-retire-request";
    const bool scoped=operation=="preview-capture-probe-scoped-request" || operation=="preview-popup-scoped-request" || operation=="preview-family-scoped-request";
    const bool scope=operation=="preview-capture-probe-scope-request";
    const bool capture=operation=="preview-capture-probe-request" || scoped;
    const bool clock=operation=="preview-capture-probe-clock-request";
    const bool state=operation=="preview-capture-probe-state-request" || operation=="preview-popup-state-request" || operation=="preview-family-state-request";
    const bool retire=operation=="preview-capture-probe-retire-request" || operation=="preview-popup-retire-request" || operation=="preview-family-retire-request";
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
        if(auto held=captureProbes.find(peer);held!=captureProbes.end() && (held->second.popup!=popup || held->second.family!=family || held->second.crop!=crop || held->second.styled!=styled))return error("preview-probe-plane-mismatch");
        if(auto held=captureProbes.find(peer);held!=captureProbes.end() && held->second.exported)return error("preview-probe-import-outstanding");
        captureProbes.erase(peer);
        return envelope(styled?"preview-family-style-crop-retired":crop?"preview-family-crop-retired":family?"preview-family-retired":popup?"preview-popup-retired":"preview-capture-probe-retired")+",\"ownedBytes\":\"0\"}";
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
        if((popup || family) && !preview::capture::clientLayout(window))return error("preview-popup-layout-unsupported");
        const auto familyObservation=family?familyContext(window,*subject):std::optional<FamilyObservation>{};
        auto sourceStamp=[&]() -> std::optional<preview::Context> {
            if(styled){const auto observed=familyStyleContext(window,*subject);if(!observed)return {};return observed->context;}
            if(family){const auto observed=familyContext(window,*subject);if(!observed)return {};return observed->context;}
            return popup?popupContext(window,*subject):previewContext(window,*subject);
        };
        if(family && (!familyObservation || std::ranges::any_of(familyObservation->members,[&](const auto& row){return (row.flags&1) || (row.flags&8) || !(row.flags&(crop?16:32));})))return error("preview-family-source-unavailable");
        const auto stamp=sourceStamp();if(!stamp)return error("preview-probe-source-epoch-unavailable");
        if(scoped && requestedContext(objectMember(object,"context"))!=stamp)return error("preview-probe-context-stale");
        const uint64_t generation=outputGeneration;
        const auto pixels=monitor->m_pixelSize;
        auto current=[&] {
            refreshOutputs();
            const auto owner=sessions.find(peer);
            const auto memberNow=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==*subject && value.window.lock()==window;});
            return owner!=sessions.end() && owner->second.id==*session && owner->second.frontend==*frontend && startTime(peer)==start && memberNow!=members.end() &&
                g_pSessionLockManager && !g_pSessionLockManager->isSessionLocked() && outputGeneration==generation && window->m_monitor.lock()==monitor && monitor->m_output && monitor->m_pixelSize==pixels &&
                window->m_isMapped && sourceStamp()==stamp && !Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer && g_pHyprRenderer->shouldRenderWindow(window);
        };
        CBox cropBounds{};
        auto image=crop?preview::capture::captureOwnedFamilyCrop(window,*captureBudget,*deadline,current,&cropBounds):preview::capture::captureOwnedPlane(window,*captureBudget,*deadline,current,family);
        if(!image) return error("preview-probe-capture-unavailable");
        const auto checksum=preview::capture::crc(image->png());
        if(preview::capture::nativeNow()>=*deadline || !current()) return error("preview-probe-expired");
        refreshFacts();
        if(sourceStamp()!=stamp)return error("preview-probe-context-stale");
        auto [inserted,ok]=captureProbes.emplace(peer,CaptureProbe{*session,*frontend,*subject,*requestId,generation,preview::capture::nativeNow(),checksum,std::move(image)});
        if(!ok)return error("preview-probe-capture-unavailable");
        inserted->second.popup=popup;inserted->second.family=family;inserted->second.crop=crop;inserted->second.styled=styled;if(crop){inserted->second.cropBounds=cropBounds;inserted->second.cropScale=monitor->m_scale;}if(familyObservation)inserted->second.capturedMembers=familyObservation->members;inserted->second.privacy=previewPrivacy;inserted->second.rendering=previewRendering;inserted->second.scene=stamp->scene.value;inserted->second.content=stamp->content.value;inserted->second.deadline=*deadline;
    }
    const auto probe=captureProbes.find(peer);
    if(probe==captureProbes.end() || probe->second.client || probe->second.popup!=popup || probe->second.family!=family || probe->second.crop!=crop || probe->second.styled!=styled || probe->second.revoked || probe->second.session!=*session || probe->second.frontend!=*frontend) return error("preview-probe-unavailable");
    const auto& held=probe->second;
    const auto cropMetadata=crop?",\"pixelX\":"+quote(std::to_string(static_cast<int64_t>(held.cropBounds.x)))+",\"pixelY\":"+quote(std::to_string(static_cast<int64_t>(held.cropBounds.y)))+",\"pixelScale\":"+std::to_string(held.cropScale):std::string{};
    return envelope(styled?"preview-family-style-crop-owned":crop?"preview-family-crop-owned":family?"preview-family-owned":popup?"preview-popup-owned":"preview-capture-probe-owned")+",\"subjectIncarnation\":"+quote(std::to_string(held.incarnation))+",\"captureRequest\":"+quote(std::to_string(held.request))+
        ",\"outputGeneration\":"+quote(std::to_string(held.output))+",\"completedNs\":"+quote(std::to_string(held.completed))+
        ",\"width\":"+std::to_string(held.image->width)+",\"height\":"+std::to_string(held.image->height)+",\"encodedBytes\":"+quote(std::to_string(held.image->png().size()))+
        ",\"ownedBytes\":"+quote(std::to_string(held.image->charge()))+",\"crc32\":"+quote(std::to_string(held.checksum))+
        ",\"encoding\":\"PNG-RGBA8-straight\",\"planeSpace\":"+quote(styled?"native-family-style-cropped-pixels-unqualified":crop?"native-family-cropped-pixels-unqualified":family?"root-popup-modal-monitor-unqualified":popup?"root-popup-monitor-unqualified":"monitor-physical-unqualified")+cropMetadata+",\"previewEligible\":false}";
}
