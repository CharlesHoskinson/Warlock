typedef struct {
    guint64 id,generation;
    GdkMonitor *monitor;
    GtkWidget *bar;
    WebKitWebView *engine;
    WebKitUserContentManager *manager;
    gulong geometry_handler;
    gboolean ready,active;
    ContextKeySource context_keys;
} OutputView;
static guint64 topology_revision;
static JsonNode *scope_packet(const OutputView *owner) {
    if (!owner) return json_node_new(JSON_NODE_NULL);
    JsonNode *node=json_node_new(JSON_NODE_OBJECT);
    JsonObject *object=json_object_new();
    g_autofree char *id=g_strdup_printf("%" G_GUINT64_FORMAT,owner->id),*generation=g_strdup_printf("%" G_GUINT64_FORMAT,owner->generation);
    json_object_set_string_member(object,"id",id);json_object_set_string_member(object,"generation",generation);
    json_node_take_object(node,object);return node;
}
static JsonNode *shared_batch_certificate(JsonNode *batch,const char *original,OutputView *scope,
        guint64 publication,guint64 lease,SurfaceDisposition disposition) {
    if (!scope || !scope->active || !authority_binding || !JSON_NODE_HOLDS_OBJECT(batch)) return NULL;
    JsonObject *source=json_node_get_object(batch);
    JsonNode *rn=json_object_get_member(source,"requests");
    if (!rn || !JSON_NODE_HOLDS_ARRAY(rn)) return NULL;
    JsonArray *rows=json_node_get_array(rn);guint count=json_array_get_length(rows);
    if (!count || count>16) return NULL;
    if (!original || strlen(original)>131072) return NULL;
    for (guint i=0;i<count;i++) {
        JsonNode *request=json_array_get_element(rows,i);if (!request_kind(request)) return NULL;
        g_autofree char *wire=json_to_string(request,FALSE);if (strlen(wire)>4096) return NULL;
        JsonNode *binding=json_object_get_member(json_node_get_object(request),"binding");
        if (!binding || !json_node_equal(binding,authority_binding)) return NULL;
    }
    const char *state=disposition==SURFACE_PREFLIGHT_UNSENT?"preflight-unsent":
        disposition==SURFACE_ADMITTED?"admitted":disposition==SURFACE_UNCERTAIN?"uncertain":NULL;
    if (!state) return NULL;
    JsonObject *object=json_object_new();
    json_object_set_int_member(object,"viewProtocol",1);json_object_set_string_member(object,"kind","batch-disposition");
    json_object_set_string_member(object,"disposition",state);json_object_set_member(object,"scope",scope_packet(scope));
    g_autofree char *pub=g_strdup_printf("%" G_GUINT64_FORMAT,publication),*token=g_strdup_printf("%" G_GUINT64_FORMAT,lease),*revision=g_strdup_printf("%" G_GUINT64_FORMAT,topology_revision);
    json_object_set_string_member(object,"revision",revision);json_object_set_string_member(object,"publication",pub);json_object_set_string_member(object,"lease",token);
    json_object_set_member(object,"binding",json_node_copy(authority_binding));json_object_set_string_member(object,"batch",original);
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,object);return packet;
}
