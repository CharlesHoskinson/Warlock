/* Native admission for one primary controller and an unprivileged renderer. */
typedef struct { guint64 publication, lease, closed; } SurfaceGate;
static gboolean surface_uint(JsonNode *node,guint64 *out) {
    if (!node || json_node_get_value_type(node)!=G_TYPE_STRING) return FALSE;
    const char *s=json_node_get_string(node);
    if (!*s || (s[0]=='0' && s[1])) return FALSE;
    guint64 n=0;
    for (;*s;s++) {if (*s<'0'||*s>'9'||n>(G_MAXUINT64-(guint64)(*s-'0'))/10) return FALSE;n=n*10+(guint64)(*s-'0');}
    *out=n;return TRUE;
}
static gboolean surface_fields(JsonObject *obj,const char *const *names,guint count) {
    if (json_object_get_size(obj)!=count) return FALSE;
    for (guint i=0;i<count;i++) if (!json_object_has_member(obj,names[i])) return FALSE;
    return TRUE;
}
static gboolean surface_text(JsonNode *node,gsize limit,gboolean empty) {
    if (!node || json_node_get_value_type(node)!=G_TYPE_STRING) return FALSE;
    const char *s=json_node_get_string(node);
    if (!g_utf8_validate(s,-1,NULL) || (!empty && !*s) || g_utf8_strlen(s,-1)>(glong)limit) return FALSE;
    for (;*s;s++) if ((guchar)*s<32 || (guchar)*s==127) return FALSE;
    return TRUE;
}
static gboolean surface_controls(JsonNode *node,guint limit,GHashTable *ids,GHashTable *doms) {
    if (!node || !JSON_NODE_HOLDS_ARRAY(node)) return FALSE;
    JsonArray *array=json_node_get_array(node);
    if (json_array_get_length(array)>limit) return FALSE;
    const char *const fields[]={"id","domId","label","ariaLabel","detail","enabled"};
    for (guint i=0;i<json_array_get_length(array);i++) {
        JsonNode *item=json_array_get_element(array,i);
        if (!JSON_NODE_HOLDS_OBJECT(item)) return FALSE;
        JsonObject *o=json_node_get_object(item);
        if (!surface_fields(o,fields,6) || !surface_text(json_object_get_member(o,"id"),512,FALSE) || !surface_text(json_object_get_member(o,"domId"),1024,FALSE) || !surface_text(json_object_get_member(o,"label"),1024,TRUE) || !surface_text(json_object_get_member(o,"ariaLabel"),1024,FALSE) || !surface_text(json_object_get_member(o,"detail"),128,TRUE) || json_node_get_value_type(json_object_get_member(o,"enabled"))!=G_TYPE_BOOLEAN) return FALSE;
        const char *id=json_object_get_string_member(o,"id"),*dom=json_object_get_string_member(o,"domId");
        if (g_hash_table_contains(ids,id)||g_hash_table_contains(doms,dom)) return FALSE;
        g_hash_table_add(ids,(gpointer)id);g_hash_table_add(doms,(gpointer)dom);
    }
    return TRUE;
}
static gboolean surface_frame(JsonNode *node,guint64 *pub,guint64 *lease,gboolean *open) {
    if (!node || !JSON_NODE_HOLDS_OBJECT(node)) return FALSE;
    JsonObject *o=json_node_get_object(node);
    const char *const names[]={"surfaceProtocol","publication","lease","mode","status","bar","popup"};
    if (!surface_fields(o,names,7) || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2 || !surface_uint(json_object_get_member(o,"publication"),pub) || !*pub || !surface_uint(json_object_get_member(o,"lease"),lease) || !surface_text(json_object_get_member(o,"mode"),32,FALSE) || !surface_text(json_object_get_member(o,"status"),1024,TRUE)) return FALSE;
    const char *mode=json_object_get_string_member(o,"mode");
    *open=!g_str_equal(mode,"closed");
    if (*open && (!*lease || (!g_str_equal(mode,"picker") && !g_str_equal(mode,"applications") && !g_str_equal(mode,"menu") && !g_str_equal(mode,"overview") && !g_str_equal(mode,"switcher")))) return FALSE;
    g_autoptr(GHashTable) ids=g_hash_table_new(g_str_hash,g_str_equal),doms=g_hash_table_new(g_str_hash,g_str_equal);
    if (!surface_controls(json_object_get_member(o,"bar"),292,ids,doms) || !surface_controls(json_object_get_member(o,"popup"),2150,ids,doms)) return FALSE;
    return *open || json_array_get_length(json_object_get_array_member(o,"popup"))==0;
}
static gboolean surface_admit(SurfaceGate *gate,JsonNode *frame,guint64 *pub,guint64 *lease,gboolean *open) {
    return surface_frame(frame,pub,lease,open) && *pub>gate->publication && *lease>=gate->lease && (!*open || *lease>gate->closed);
}
static gboolean surface_action(SurfaceGate *gate,JsonNode *node,JsonNode *frame,gboolean popup) {
    if (!node || !frame || !JSON_NODE_HOLDS_OBJECT(node)) return FALSE;
    JsonObject *o=json_node_get_object(node);
    const char *const names[]={"surfaceProtocol","kind","surface","publication","lease","id"};
    guint64 pub,lease;
    if (!surface_fields(o,names,6) || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2 || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"surface-action") || !surface_text(json_object_get_member(o,"surface"),16,FALSE) || !g_str_equal(json_object_get_string_member(o,"surface"),popup?"popup":"bar") || !surface_uint(json_object_get_member(o,"publication"),&pub) || pub!=gate->publication || !surface_uint(json_object_get_member(o,"lease"),&lease) || lease!=gate->lease || (popup && lease<=gate->closed) || !surface_text(json_object_get_member(o,"id"),512,FALSE)) return FALSE;
    JsonArray *items=json_object_get_array_member(json_node_get_object(frame),popup?"popup":"bar");
    for (guint i=0;i<json_array_get_length(items);i++) {JsonObject *item=json_array_get_object_element(items,i);if (g_str_equal(json_object_get_string_member(o,"id"),json_object_get_string_member(item,"id")) && json_object_get_boolean_member(item,"enabled")) return TRUE;}
    return FALSE;
}
/* A bounded field edit carries no window or launch authority. It still belongs
 * to the current enabled field, owning popup publication and live lease. */
static gboolean surface_query(SurfaceGate *gate,JsonNode *node,JsonNode *frame,gboolean popup) {
    if (!popup || !node || !frame || !JSON_NODE_HOLDS_OBJECT(node)) return FALSE;
    JsonObject *o=json_node_get_object(node);
    const char *const fields[]={"surfaceProtocol","kind","surface","publication","lease","id","query"};
    if (!surface_fields(o,fields,7) || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"surface-query") || !surface_text(json_object_get_member(o,"id"),512,FALSE) || !g_str_equal(json_object_get_string_member(o,"id"),"control:search") || !surface_text(json_object_get_member(o,"query"),256,TRUE) || !g_str_equal(json_object_get_string_member(json_node_get_object(frame),"mode"),"applications")) return FALSE;
    JsonObject *action=json_object_new();
    for (guint i=0;i<6;i++) json_object_set_member(action,fields[i],json_node_copy(json_object_get_member(o,fields[i])));
    json_object_set_string_member(action,"kind","surface-action");
    JsonNode *copy=json_node_new(JSON_NODE_OBJECT);json_node_take_object(copy,action);
    gboolean accepted=surface_action(gate,copy,frame,TRUE);json_node_unref(copy);return accepted;
}
static gboolean surface_focus_targets_present(JsonNode *targets,JsonNode *frame) {
    JsonArray *wanted=json_node_get_array(targets),*controls=json_object_get_array_member(json_node_get_object(frame),"popup");
    if (!json_array_get_length(wanted)) return FALSE;
    for (guint i=0;i<json_array_get_length(wanted);i++) {
        const char *target=json_array_get_string_element(wanted,i);gboolean found=FALSE;
        for (guint j=0;j<json_array_get_length(controls);j++) {
            JsonObject *control=json_array_get_object_element(controls,j);
            if (json_object_get_boolean_member(control,"enabled") && g_str_equal(target,json_object_get_string_member(control,"domId"))) found=TRUE;
        }
        if (!found) return FALSE;
    }
    return TRUE;
}
