// Production family capture remains separate from unqualified probe contracts.
// The existing native family compositor supplies the same complete style/crop
// and descriptor proofs; window identity, native privacy and owning grant win.
std::string pickerFamilyProbe(pid_t peer,const std::string& start,const std::string& operation,JsonObject* object) {
    const bool scope=operation=="preview-picker-family-scope-request";
    const bool capture=operation=="preview-picker-family-capture-request";
    const bool retire=operation=="preview-picker-family-retire-request";
    if((!scope && !capture && !retire) || !(capture ? fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation","deadlineNs","context"}) : fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation"}))) return error("picker-preview-schema");
    const auto subject=counter(object,"subjectIncarnation");
    if(!subject) return error("picker-preview-subject");
    CaptureSelection selected(*subject);
    const auto member=std::ranges::find_if(members,[&](const Member& item){return item.id==*subject;});
    const auto window=member==members.end() ? PHLWINDOW{} : member->window.lock();
    if(!retire) {
        if(!window || !window->m_isMapped || window->m_isX11 || window->parent() || !window->m_xdgSurface || !window->m_xdgSurface->m_toplevel || !window->wlSurface() || !window->wlSurface()->resource()) return error("picker-preview-source-unavailable");
        pid_t owner=0;uid_t uid=0;gid_t gid=0;
        wl_client_get_credentials(window->wlSurface()->resource()->client(),&owner,&uid,&gid);
        if(uid!=getuid() || owner<=0 || owner==peer) return error("picker-preview-source-unavailable");
    }
    if(capture && !captureProbes.contains(peer) && std::ranges::count_if(captureProbes,[&](const auto& item){return item.first.peer==peer && item.first.subject!=0;})>=2) return error("picker-preview-capacity");
    JsonObject* cloned=json_object_new();
    GList* names=json_object_get_members(object);
    for(GList* node=names;node;node=node->next) {const char* name=static_cast<const char*>(node->data);json_object_set_member(cloned,name,json_node_copy(json_object_get_member(object,name)));}
    g_list_free(names);
    const std::string legacy=scope ? "preview-family-style-crop-scope-request" : capture ? "preview-family-style-crop-scoped-request" : "preview-family-style-crop-retire-request";
    json_object_set_string_member(cloned,"kind",legacy.c_str());
    if(retire) json_object_remove_member(cloned,"subjectIncarnation");
    const auto reply=scope ? clientProbe(peer,start,legacy,cloned) : previewProbe(peer,start,legacy,cloned);
    json_object_unref(cloned);
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,reply.c_str(),-1,nullptr) || !JSON_NODE_HOLDS_OBJECT(json_parser_get_root(parser))) return error("picker-preview-native-shape");
    auto result=json_node_get_object(json_parser_get_root(parser));
    if(!json_object_has_member(result,"kind") || std::string_view(json_object_get_string_member(result,"kind"))=="refused") return reply;
    json_object_set_string_member(result,"kind",scope ? "preview-picker-family-scope" : capture ? "preview-picker-family-owned" : "preview-picker-family-retired");
    if(!retire) json_object_set_boolean_member(result,"previewEligible",true);
    if(scope) json_object_set_string_member(result,"scopeKind","picker-native-family-style-crop");
    if(capture) json_object_set_string_member(result,"planeSpace","picker-native-family-style-cropped-pixels");
    g_autofree char* encoded=json_to_string(json_parser_get_root(parser),FALSE);
    return encoded;
}
