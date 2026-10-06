// QA-only producer observation. The binding is authenticated by the native peer
// registry. Request JSON can name a current incarnation, but cannot attest pixels,
// clocks, output generation, source liveness, locks or completion.
std::string clientProbe(pid_t peer,const std::string& start,const std::string& operation,JsonObject* object) {
    const bool scoped=operation=="preview-client-scoped-request";
    const bool popupScope=operation=="preview-popup-scope-request";
    const bool styleCropScope=operation=="preview-family-style-crop-scope-request";
    const bool styleScope=operation=="preview-family-style-scope-request" || styleCropScope;
    const bool familyScope=operation=="preview-family-scope-request" || styleScope;
    const bool scope=operation=="preview-client-scope-request" || popupScope || familyScope;
    const bool capture=operation=="preview-client-request" || scoped;
    const bool clock=operation=="preview-client-clock-request";
    const bool state=operation=="preview-client-state-request";
    const bool retire=operation=="preview-client-retire-request";
    if(!(capture || scope || clock || state || retire) || !(scoped?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs","context"}):scope?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation"}):capture?
        fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs"}):
        fields(object,{"protocolVersion","kind","binding","requestId"}))) return error("preview-client-schema");
    const auto bound=objectMember(object,"binding");const auto requestId=counter(object,"requestId");
    if(!bound || !fields(bound,{"lifetime","session","frontend"}) || !requestId) return error("preview-client-schema");
    const auto native=counter(bound,"lifetime"),session=counter(bound,"session"),frontend=counter(bound,"frontend");
    auto found=sessions.find(peer);
    if(!native || !session || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || found->second.id!=*session || found->second.frontend!=*frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{*native,*session,*frontend})) return error("binding-mismatch");
    const auto& active=found->second;
    auto envelope=[&](const char* kind) {return "{\"protocolVersion\":3,\"kind\":"+quote(kind)+",\"binding\":"+binding(active)+",\"requestId\":"+quote(std::to_string(*requestId));};
    if(clock) return envelope("preview-client-clock")+",\"clock\":"+quote(std::to_string(lifetime))+",\"nowNs\":"+quote(std::to_string(preview::capture::nativeNow()))+"}";
    // Privacy and output invalidation remove all completed probe pixels. Source
    // stop is deliberately not a retirement event for independently owned RAM.
    refreshOutputs();
    const bool locked=!g_pSessionLockManager || g_pSessionLockManager->isSessionLocked();
    for(auto& [pid,item]:captureProbes) if(locked || item.output!=outputGeneration)item.revoked=true;
    if(locked) return error("preview-client-locked");
    if(scope) {
        const auto subject=counter(object,"subjectIncarnation");if(!subject)return error("preview-client-scope-subject");
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& row){return row.id==*subject;});
        const auto window=member==members.end()?PHLWINDOW{}:member->window.lock();
        const auto family=familyScope?familyContext(window,*subject):std::optional<FamilyObservation>{};
        const auto styled=styleScope?familyStyleContext(window,*subject):std::optional<FamilyStyleObservation>{};
        if(styleScope && !styled)return error("preview-family-style-source-unavailable");
        const auto context=styleScope?std::optional<preview::Context>{styled->context}:familyScope?(family?std::optional<preview::Context>{family->context}:std::nullopt):popupScope?popupContext(window,*subject):clientContext(window,*subject);if(!context || !window->m_isMapped)return error("preview-client-scope-source-unavailable");
        const auto monitor=window->m_monitor.lock();if(!monitor || !monitor->m_output)return error("preview-client-scope-output-unavailable");
        const auto layout=preview::capture::clientLayout(window);if(!layout)return error("preview-client-layout-unsupported");
        const auto monitorPlan=preview::capture::plan(static_cast<uint32_t>(monitor->m_pixelSize.x),static_cast<uint32_t>(monitor->m_pixelSize.y));
        if((popupScope || familyScope) && !monitorPlan)return error("preview-popup-layout-unsupported");
        const auto cropBounds=styleCropScope?g_pHyprRenderer->familyObservationCropBounds(window):std::optional<CBox>{};
        const auto croppedPlan=cropBounds?preview::capture::plan(static_cast<uint32_t>(cropBounds->w),static_cast<uint32_t>(cropBounds->h)):std::nullopt;
        if(styleCropScope && !croppedPlan)return error("preview-family-style-crop-unavailable");
        const auto plan=styleCropScope?*croppedPlan:(popupScope || familyScope)?*monitorPlan:layout->client;
        if(previewObservation==std::numeric_limits<uint64_t>::max())return error("preview-client-scope-observation-exhausted");
        const bool live=!Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer && g_pHyprRenderer->shouldRenderWindow(window);
        const bool gpu=g_pHyprRenderer && Render::GL::g_pHyprOpenGL;
        return envelope(styleCropScope?"preview-family-style-crop-scope":styleScope?"preview-family-style-scope":familyScope?"preview-family-scope":popupScope?"preview-popup-scope":"preview-client-scope")+",\"scope\":{\"binding\":"+binding(active)+",\"context\":"+contextJSON(*context)+",\"observation\":"+quote(std::to_string(++previewObservation))+",\"clock\":"+quote(std::to_string(lifetime))+",\"now\":"+quote(std::to_string(preview::capture::nativeNow()))+",\"present\":true,\"sourceLive\":"+(live?"true":"false")+",\"locked\":false,\"gpuReady\":"+(gpu?"true":"false")+"},\"maximumTransferBytes\":"+quote(std::to_string((plan.png+4095)&~uint64_t{4095}))+",\"previewEligible\":false,\"scopeKind\":"+quote(styleCropScope?"native-family-style-crop-channels-unqualified":styleScope?"native-family-style-channels-unqualified":familyScope?"isolated-root-popup-modal-unqualified":popupScope?"isolated-root-popup-unqualified":"isolated-root-client-unqualified")+(family?",\"members\":"+familyMembersJSON(*family):"")+(styled?",\"styles\":"+familyStylesJSON(*styled):"")+(cropBounds?",\"crop\":{\"pixelX\":"+quote(std::to_string(static_cast<int64_t>(cropBounds->x)))+",\"pixelY\":"+quote(std::to_string(static_cast<int64_t>(cropBounds->y)))+",\"width\":"+std::to_string(plan.width)+",\"height\":"+std::to_string(plan.height)+",\"scale\":"+std::format("{:.17g}",monitor->m_scale)+"}":"")+"}";
    }
    if(retire) {
        if(auto held=captureProbes.find(peer);held!=captureProbes.end() && (held->second.popup || held->second.family || held->second.crop))return error("preview-client-plane-mismatch");
        if(auto held=captureProbes.find(peer);held!=captureProbes.end() && held->second.exported)return error("preview-client-import-outstanding");
        captureProbes.erase(peer);
        return envelope("preview-client-retired")+",\"ownedBytes\":\"0\"}";
    }
    if(capture) {
        const auto subject=counter(object,"subjectIncarnation"),deadline=counter(object,"deadlineNs");
        const uint64_t now=preview::capture::nativeNow();
        if(!subject || !deadline || *deadline<=now || *deadline-now>2000000000ULL) return error("preview-client-deadline");
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==*subject;});
        if(member==members.end()) return error("preview-client-subject");
        const auto window=member->window.lock();
        if(!window || !window->m_isMapped || Desktop::WindowPolicy::isMinimized(window)) return error("preview-client-source-unavailable");
        const auto monitor=window->m_monitor.lock();
        if(!monitor || !monitor->m_output) return error("preview-client-output-unavailable");
        if(captureProbes.contains(peer)) return error("preview-client-retire-required");
        const auto stamp=clientContext(window,*subject);if(!stamp)return error("preview-client-source-epoch-unavailable");
        if(scoped && requestedContext(objectMember(object,"context"))!=stamp)return error("preview-client-context-stale");
        const uint64_t generation=outputGeneration;
        const auto pixels=monitor->m_pixelSize;
        auto current=[&] {
            refreshOutputs();
            const auto owner=sessions.find(peer);
            const auto memberNow=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==*subject && value.window.lock()==window;});
            return owner!=sessions.end() && owner->second.id==*session && owner->second.frontend==*frontend && startTime(peer)==start && memberNow!=members.end() &&
                g_pSessionLockManager && !g_pSessionLockManager->isSessionLocked() && outputGeneration==generation && window->m_monitor.lock()==monitor && monitor->m_output && monitor->m_pixelSize==pixels &&
                window->m_isMapped && clientContext(window,*subject)==stamp && !Desktop::WindowPolicy::isMinimized(window) && g_pHyprRenderer && g_pHyprRenderer->shouldRenderWindow(window);
        };
        auto image=preview::capture::captureOwnedClient(window,*captureBudget,*deadline,current);
        if(!image) return error("preview-client-capture-unavailable");
        const auto checksum=preview::capture::crc(image->png());
        if(preview::capture::nativeNow()>=*deadline || !current()) return error("preview-client-expired");
        refreshFacts();
        if(clientContext(window,*subject)!=stamp)return error("preview-client-context-stale");
        auto [inserted,ok]=captureProbes.emplace(peer,CaptureProbe{*session,*frontend,*subject,*requestId,generation,preview::capture::nativeNow(),checksum,std::move(image)});
        if(!ok)return error("preview-client-capture-unavailable");
        inserted->second.client=true;inserted->second.privacy=previewPrivacy;inserted->second.rendering=previewRendering;inserted->second.scene=stamp->scene.value;inserted->second.content=stamp->content.value;inserted->second.deadline=*deadline;
    }
    const auto probe=captureProbes.find(peer);
    if(probe==captureProbes.end() || !probe->second.client || probe->second.revoked || probe->second.session!=*session || probe->second.frontend!=*frontend) return error("preview-client-unavailable");
    const auto& held=probe->second;
    return envelope("preview-client-owned")+",\"subjectIncarnation\":"+quote(std::to_string(held.incarnation))+",\"captureRequest\":"+quote(std::to_string(held.request))+
        ",\"outputGeneration\":"+quote(std::to_string(held.output))+",\"completedNs\":"+quote(std::to_string(held.completed))+
        ",\"width\":"+std::to_string(held.image->width)+",\"height\":"+std::to_string(held.image->height)+",\"encodedBytes\":"+quote(std::to_string(held.image->png().size()))+
        ",\"ownedBytes\":"+quote(std::to_string(held.image->charge()))+",\"crc32\":"+quote(std::to_string(held.checksum))+
        ",\"encoding\":\"PNG-RGBA8-straight\",\"planeSpace\":\"client-logical-unqualified\",\"previewEligible\":false}";
}
