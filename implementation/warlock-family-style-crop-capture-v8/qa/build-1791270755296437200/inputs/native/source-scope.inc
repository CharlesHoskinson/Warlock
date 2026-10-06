std::optional<preview::Context> previewContext(PHLWINDOW window,uint64_t subject) {
    const auto source=previewSources.find(subject);
    if(!window || source==previewSources.end() || source->second->dead || !source->second->epoch.available() || source->second->surface.lock()!=window->resource())return {};
    refreshFacts();
    if(!outputGeneration || !factsRevision || !previewPrivacy || !previewRendering)return {};
    return preview::Context{{lifetime},{subject},{outputGeneration},{previewPrivacy},{previewRendering},{factsRevision},{source->second->epoch.value()}};
}
std::optional<preview::Context> requestedContext(JsonObject* object) {
    if(!object || !fields(object,{"lifetime","incarnation","output","privacy","rendering","scene","content"}))return {};
    const auto native=counter(object,"lifetime"),subject=counter(object,"incarnation"),output=counter(object,"output"),privacy=counter(object,"privacy"),rendering=counter(object,"rendering"),scene=counter(object,"scene"),content=counter(object,"content");
    if(!native || !subject || !output || !privacy || !rendering || !scene || !content)return {};
    return preview::Context{{*native},{*subject},{*output},{*privacy},{*rendering},{*scene},{*content}};
}
std::string contextJSON(const preview::Context& context) {
    return "{\"lifetime\":"+quote(std::to_string(context.lifetime.value))+",\"incarnation\":"+quote(std::to_string(context.incarnation.value))+",\"output\":"+quote(std::to_string(context.output.value))+",\"privacy\":"+quote(std::to_string(context.privacy.value))+",\"rendering\":"+quote(std::to_string(context.rendering.value))+",\"scene\":"+quote(std::to_string(context.scene.value))+",\"content\":"+quote(std::to_string(context.content.value))+"}";
}

std::optional<preview::Context> clientContext(PHLWINDOW window,uint64_t subject) {
    auto context=previewContext(window,subject);if(!context)return {};
    auto& tracker=clientTrees[subject];
    const auto tree=preview::capture::surfaceTree(window->resource());if(!tree){tracker.unavailable();return {};}
    const auto content=tracker.observe(*tree);if(!content)return {};
    context->content={content};return context;
}

std::optional<preview::Context> popupContext(PHLWINDOW window,uint64_t subject) {
    auto context=previewContext(window,subject);if(!context)return {};
    auto& tracker=popupTrees[subject];
    const auto tree=preview::capture::rootPopupTree(window);if(!tree){tracker.unavailable();return {};}
    const auto content=tracker.observe(*tree);if(!content)return {};
    context->content={content};return context;
}

struct FamilyObservation {preview::Context context;std::vector<preview::FamilyNode> members;};
std::optional<FamilyObservation> familyContext(PHLWINDOW window,uint64_t subject) {
    auto base=previewContext(window,subject);if(!base || window->parent())return {};
    auto& state=familySources[subject];
    auto refused=[&]()->std::optional<FamilyObservation>{state.revision.unavailable();return {};};
    if(!g_pHyprRenderer || !Render::GL::g_pHyprOpenGL)return refused();
    const auto& desktop=Desktop::windowState()->windows();if(desktop.size()>256)return refused();
    const auto family=nativeFamily(window);if(!family || family->empty() || family->size()>256)return refused();
    const auto monitor=window->m_monitor.lock();const auto workspace=window->m_workspace;
    std::set<uint64_t> ids;std::vector<preview::FamilyNode> rows;size_t sampledRows=0;
    for(const auto& candidate:*family) {
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& row){return row.window.lock()==candidate;});
        if(member==members.end() || !member->id || !ids.insert(member->id).second || !previewContext(candidate,member->id) || !candidate->m_isMapped || candidate->m_monitor.lock()!=monitor || candidate->m_workspace!=workspace || !workspace || candidate->onSpecialWorkspace() || workspace->m_renderOffset->value()!=Vector2D{} || !preview::capture::clientLayout(candidate))return refused();
        const auto tree=preview::capture::rootPopupTree(candidate);if(!tree || tree->rows.size()>256-sampledRows)return refused();sampledRows+=tree->rows.size();
        const uint64_t content=state.trees[member->id].observe(*tree);if(!content)return refused();
        const auto parent=candidate->parent();const auto owner=std::find_if(members.begin(),members.end(),[&](const Member& row){return row.window.lock()==parent;});
        if(parent && (owner==members.end() || std::ranges::find(*family,parent)==family->end()))return refused();
        const auto place=std::ranges::find(desktop,candidate);if(place==desktop.end())return refused();
        const auto position=candidate->position(Desktop::View::IGeometric::GEOMETRIC_CURRENT),size=candidate->size(Desktop::View::IGeometric::GEOMETRIC_CURRENT);const auto box=candidate->getFullWindowBoundingBox();
        const bool modal=candidate->isModal() || (candidate->m_xdgSurface && candidate->m_xdgSurface->m_toplevel && candidate->m_xdgSurface->m_toplevel->m_dialog && candidate->m_xdgSurface->m_toplevel->m_dialog->modal);
        const uint64_t flags=(Desktop::WindowPolicy::isMinimized(candidate)?1:0) | (workspace->isVisible()?2:0) | (candidate->m_pinned?4:0) | (candidate->isHidden()?8:0) | (g_pHyprRenderer->shouldRenderWindow(candidate)?16:0) | (g_pHyprRenderer->shouldRenderWindow(candidate,monitor)?32:0) | (modal?64:0) | (candidate->acceptsInput()?128:0);
        rows.push_back({member->id,parent?owner->id:0,content,static_cast<uint64_t>(std::distance(desktop.begin(),place)),flags,{position.x,position.y,size.x,size.y,box.x,box.y,box.w,box.h},{candidate->effectiveAlpha(),candidate->rounding(),candidate->roundingPower()}});
    }
    std::erase_if(state.trees,[&](const auto& pair){return !ids.contains(pair.first);});
    if(!state.revision.observe(subject,rows))return refused();
    base->content={state.revision.value()};return FamilyObservation{*base,std::move(rows)};
}
std::string familyMembersJSON(const FamilyObservation& observed) {
    std::string value="[";bool first=true;
    for(const auto& row:observed.members){if(!first)value+=',';first=false;
        value+="{\"incarnation\":"+quote(std::to_string(row.id))+",\"parent\":"+(row.parent?quote(std::to_string(row.parent)):"null")+",\"content\":"+quote(std::to_string(row.content))+",\"renderOrder\":"+std::to_string(row.order)+",\"flags\":"+std::to_string(row.flags)+",\"geometry\":[";
        for(size_t i=0;i<row.geometry.size();++i){if(i)value+=',';value+=std::to_string(row.geometry[i]);}
        value+="]}";
    }
    return value+"]";
}

#include "style-source.inc"
