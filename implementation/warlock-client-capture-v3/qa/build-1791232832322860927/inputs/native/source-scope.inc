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
