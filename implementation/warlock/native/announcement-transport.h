/* Elm selects the source event and owner. This is scoped presentation transport,
 * not native attention/window/notification policy. Forward a serial once across
 * all mirrors. Actual speech/braille delivery is a separate observed contract. */
static JsonNode *announcement_projection;
static guint64 announcement_frontier;
static gboolean announcement_fields(JsonObject *projection) {
    const char *const old[]={"viewProtocol","kind","revision","views","popupOwner","focusOwner","frame"};
    const char *const current[]={"viewProtocol","kind","revision","views","popupOwner","focusOwner","frame","announcer","announcement"};
    return surface_fields(projection,old,7) || surface_fields(projection,current,9);
}
static gboolean announcement_scope(JsonNode *node) {
    if(!node || !JSON_NODE_HOLDS_OBJECT(node))return FALSE;
    const char *const fields[]={"id","generation"};guint64 id,generation;
    JsonObject *scope=json_node_get_object(node);
    return surface_fields(scope,fields,2) && surface_uint(json_object_get_member(scope,"id"),&id) && id && surface_uint(json_object_get_member(scope,"generation"),&generation) && generation;
}
static gboolean announcement_shape(JsonObject *projection) {
    if(!announcement_fields(projection))return FALSE;
    if(!json_object_has_member(projection,"announcer"))return TRUE;
    JsonNode *owner=json_object_get_member(projection,"announcer"),*message=json_object_get_member(projection,"announcement");
    if(!owner || !message)return FALSE;
    if(!JSON_NODE_HOLDS_NULL(owner)) {
        if(!JSON_NODE_HOLDS_OBJECT(owner))return FALSE;
        const char *const fields[]={"scope","surface"};JsonObject *route=json_node_get_object(owner);
        guint64 publication,lease;gboolean open;
        if(!surface_fields(route,fields,2) || !announcement_scope(json_object_get_member(route,"scope")) || !surface_text(json_object_get_member(route,"surface"),5,FALSE) || !surface_frame(json_object_get_member(projection,"frame"),&publication,&lease,&open))return FALSE;
        const char *surface=json_object_get_string_member(route,"surface");
        if(!g_str_equal(surface,open?"popup":"bar") || !json_node_equal(json_object_get_member(route,"scope"),json_object_get_member(projection,open?"popupOwner":"focusOwner")))return FALSE;
    } else if(!JSON_NODE_HOLDS_NULL(json_object_get_member(projection,"focusOwner")))return FALSE;
    if(JSON_NODE_HOLDS_NULL(message))return TRUE;
    if(!JSON_NODE_HOLDS_OBJECT(message))return FALSE;
    const char *const fields[]={"sequence","correlation","text"};JsonObject *body=json_node_get_object(message);guint64 sequence;
    const char *const current[]={"sequence","correlation","text","interrupt"};
    gboolean extended=json_object_has_member(body,"interrupt");
    return surface_fields(body,extended?current:fields,extended?4:3) && (!extended || json_node_get_value_type(json_object_get_member(body,"interrupt"))==G_TYPE_BOOLEAN) && surface_uint(json_object_get_member(body,"sequence"),&sequence) && sequence && surface_text(json_object_get_member(body,"correlation"),8192,FALSE) && surface_text(json_object_get_member(body,"text"),4096,FALSE);
}
static void announcement_save(JsonObject *projection) {
    if(announcement_projection)json_node_unref(announcement_projection);
    announcement_projection=json_node_new(JSON_NODE_OBJECT);json_node_set_object(announcement_projection,projection);
}
static void announcement_counter(JsonObject *object,const char *field,guint64 value) {
    g_autofree char *text=g_strdup_printf("%" G_GUINT64_FORMAT,value);json_object_set_string_member(object,field,text);
}
static gboolean announcement_forward(WebKitWebView *engine,OutputView *recipient,const char *surface,JsonObject *projection,guint64 publication,guint64 lease) {
    JsonNode *owner=json_object_get_member(projection,"announcer"),*message=json_object_get_member(projection,"announcement");
    guint64 sequence=0;if(message && JSON_NODE_HOLDS_OBJECT(message))surface_uint(json_object_get_member(json_node_get_object(message),"sequence"),&sequence);
    gboolean owns=FALSE;
    if(owner && JSON_NODE_HOLDS_OBJECT(owner)) {
        JsonObject *route=json_node_get_object(owner);
        owns=scope_lookup(json_object_get_member(route,"scope"))==recipient && g_str_equal(json_object_get_string_member(route,"surface"),surface);
    }
    gboolean deliver=owns && sequence>announcement_frontier;
    JsonObject *route=json_object_new();json_object_set_member(route,"scope",scope_packet(recipient));json_object_set_string_member(route,"surface",surface);
    JsonObject *packet=json_object_new();json_object_set_int_member(packet,"announcementProtocol",1);json_object_set_string_member(packet,"kind","announcement-projection");
    json_object_set_object_member(packet,"recipient",route);
    json_object_set_member(packet,"announcer",owner?json_node_copy(owner):json_node_new(JSON_NODE_NULL));
    announcement_counter(packet,"publication",publication);announcement_counter(packet,"lease",lease);
    json_object_set_member(packet,"message",message?json_node_copy(message):json_node_new(JSON_NODE_NULL));json_object_set_boolean_member(packet,"deliver",deliver);
    JsonNode *node=json_node_new(JSON_NODE_OBJECT);json_node_take_object(node,packet);surface_eval(engine,"receiveAnnouncement",node);
    if(deliver) {
        announcement_frontier=sequence;
        if(qa_exit){g_autofree char *wire=json_to_string(node,FALSE);g_print("announcement-delivery: %s\n",wire);fflush(stdout);}
    }
    json_node_unref(node);return deliver;
}
static void shared_announcement_publish(void) {
    if(!announcement_projection || !surface_snapshot || shutting_down)return;
    JsonObject *projection=json_node_get_object(announcement_projection);guint64 publication,lease;gboolean open;
    if(!surface_frame(json_object_get_member(projection,"frame"),&publication,&lease,&open) || publication!=surface_gate.publication || lease!=surface_gate.lease)return;
    for(guint i=0;i<output_views->len;i++) {
        OutputView *row=g_ptr_array_index(output_views,i);
        if(row->active && row->ready)announcement_forward(row->engine,row,"bar",projection,publication,lease);
    }
    if(open && popup_ready && popup_owner && popup_owner->active)announcement_forward(popup_view,popup_owner,"popup",projection,publication,lease);
}
