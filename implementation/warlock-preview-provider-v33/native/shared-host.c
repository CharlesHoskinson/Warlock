/* Reuse the qualified backend/surface machinery, with one new owning host. */
#define main inherited_main
#include "host.c"
#undef main

#define CONTEXT_KEYS_PRIMITIVES_ONLY
#include "context-keys.h"
#include "preview-provider-bootstrap.h"
#include "client-producer.h"
#include "imported-clients.h"
static WarlockPreviewBootstrap *preview_bootstrap;
static WarlockClientProducer *client_producer;
static WarlockImportedClients *imported_clients;
static guint64 qa_import_subjects[2];
static guint imported_poll_source;
static guint64 imported_snapshot_ordinal;
static char *imported_last_status;
static gboolean imported_image_report(JsonObject *object);
static char *client_last_status;
static guint64 qa_client_subject;
static gboolean qa_family_mode;
static guint client_poll_source;
static const char *qa_client_snapshot;
static gboolean client_snapshot_pending,client_snapshot_written;
static gboolean client_image_report(JsonObject *object);
static void client_wake(void);
static void imported_wake(void);
typedef struct {char *path;guint64 request;} ClientSnapshot;

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
static GPtrArray *output_views;
static guint64 issued_view,topology_revision=1;
static gboolean controller_ready;
static OutputView *popup_owner,*focus_owner;
static GtkWidget *controller_window;
static WebKitWebContext *shared_context;
static WebKitSettings *shared_settings;

static JsonNode *scope_packet(const OutputView *owner) {
    if (!owner) return json_node_new(JSON_NODE_NULL);
    JsonNode *node=json_node_new(JSON_NODE_OBJECT);
    JsonObject *object=json_object_new();
    g_autofree char *id=g_strdup_printf("%" G_GUINT64_FORMAT,owner->id),*generation=g_strdup_printf("%" G_GUINT64_FORMAT,owner->generation);
    json_object_set_string_member(object,"id",id);json_object_set_string_member(object,"generation",generation);
    json_node_take_object(node,object);return node;
}
static OutputView *scope_lookup(JsonNode *node) {
    if (!node || !JSON_NODE_HOLDS_OBJECT(node)) return NULL;
    JsonObject *object=json_node_get_object(node);const char *const fields[]={"id","generation"};guint64 id,generation;
    if (!surface_fields(object,fields,2) || !surface_uint(json_object_get_member(object,"id"),&id) || !surface_uint(json_object_get_member(object,"generation"),&generation) || !id || !generation) return NULL;
    for (guint i=0;i<output_views->len;i++) {OutputView *row=g_ptr_array_index(output_views,i);if (row->active && row->id==id && row->generation==generation) return row;}
    return NULL;
}
static OutputView *manager_lookup(WebKitUserContentManager *manager) {
    if (!manager) return NULL;
    for (guint i=0;i<output_views->len;i++) {OutputView *row=g_ptr_array_index(output_views,i);if (row->active && row->manager==manager) return row;}
    return NULL;
}
static void shared_context_forward(OutputView *,JsonNode *,gboolean);
#include "shared-context.h"

static void shared_publish(void) {
    if (!surface_snapshot || shutting_down) return;
    for (guint i=0;i<output_views->len;i++) {OutputView *row=g_ptr_array_index(output_views,i);if (row->active && row->ready) surface_eval(row->engine,"receivePresentation",surface_snapshot);}
}
static WebKitWebView *shared_focus_target(void) {
    return focus_owner && focus_owner->active ? focus_owner->engine : view;
}
static void shared_popup_notify(const char *function,guint64 lease) {
    if (!popup_owner || !popup_owner->active || shutting_down) return;
    JsonObject *object=json_object_new();json_object_set_member(object,"scope",scope_packet(popup_owner));
    g_autofree char *token=g_strdup_printf("%" G_GUINT64_FORMAT,lease);json_object_set_string_member(object,"lease",token);
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,object);surface_eval(view,function,packet);json_node_unref(packet);
}
static void shared_topology(void) {
    shared_context_cancel();
    if (!controller_ready || shutting_down) return;
    JsonObject *object=json_object_new();JsonArray *array=json_array_new();
    for (guint i=0;i<output_views->len;i++) {OutputView *row=g_ptr_array_index(output_views,i);if (row->active) json_array_add_element(array,scope_packet(row));}
    json_object_set_int_member(object,"viewProtocol",1);json_object_set_string_member(object,"kind","view-topology");
    g_autofree char *revision=g_strdup_printf("%" G_GUINT64_FORMAT,topology_revision);json_object_set_string_member(object,"revision",revision);json_object_set_array_member(object,"views",array);
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,object);
    g_autofree char *wire=json_to_string(packet,FALSE);g_print("view-topology: %s\n",wire);fflush(stdout);
    surface_eval(view,"receiveTopology",packet);json_node_unref(packet);
}
static void topology_advance(void) {
    if (topology_revision==G_MAXUINT64) {failed=TRUE;gtk_main_quit();return;}
    topology_revision++;shared_topology();
}
static gboolean projection_scopes(JsonObject *projection,OutputView **popup,OutputView **focus) {
    const char *const fields[]={"viewProtocol","kind","revision","views","popupOwner","focusOwner","frame"};guint64 revision;
    if (!surface_fields(projection,fields,7) || json_node_get_value_type(json_object_get_member(projection,"viewProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(projection,"viewProtocol")!=1 || !surface_text(json_object_get_member(projection,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(projection,"kind"),"view-frame") || !surface_uint(json_object_get_member(projection,"revision"),&revision) || revision!=topology_revision) return FALSE;
    JsonNode *vn=json_object_get_member(projection,"views"),*pn=json_object_get_member(projection,"popupOwner"),*fn=json_object_get_member(projection,"focusOwner");
    if (!vn || !JSON_NODE_HOLDS_ARRAY(vn)) return FALSE;
    JsonArray *rows=json_node_get_array(vn);if (json_array_get_length(rows)!=output_views->len || output_views->len>64) return FALSE;
    for (guint i=0;i<json_array_get_length(rows);i++) {
        OutputView *row=scope_lookup(json_array_get_element(rows,i));if (!row) return FALSE;
        for (guint j=0;j<i;j++) if (row==scope_lookup(json_array_get_element(rows,j))) return FALSE;
    }
    *popup=scope_lookup(pn);*focus=scope_lookup(fn);
    return (*popup || (pn && JSON_NODE_HOLDS_NULL(pn))) && (*focus || (fn && JSON_NODE_HOLDS_NULL(fn))) && (!output_views->len || *focus);
}
/* Negative correlation is not historical surface authority. IDs are allocated
 * densely (++issued_view), generation is immutable 1, and never reused. */
static gboolean shared_issued_scope(JsonNode *node,OutputView *scope) {
    if (!node || !JSON_NODE_HOLDS_OBJECT(node)) return FALSE;
    JsonObject *o=json_node_get_object(node);const char *const fields[]={"id","generation"};guint64 id,generation;
    if (!surface_fields(o,fields,2) || !surface_uint(json_object_get_member(o,"id"),&id) || !surface_uint(json_object_get_member(o,"generation"),&generation) || !id || id>issued_view || generation!=1) return FALSE;
    *scope=(OutputView){.id=id,.generation=generation};return TRUE;
}
static gboolean shared_batch_identity(JsonNode *batch,const char *wire,OutputView *scope,guint64 *revision,guint64 *publication,guint64 *lease) {
    if (!batch || !JSON_NODE_HOLDS_OBJECT(batch) || !authority_binding || !wire || strlen(wire)>131072) return FALSE;
    JsonObject *o=json_node_get_object(batch);const char *const fields[]={"viewProtocol","kind","projection","requests","focus"};
    if (!surface_fields(o,fields,5) || json_node_get_value_type(json_object_get_member(o,"viewProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"viewProtocol")!=1 || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"view-commit")) return FALSE;
    JsonNode *pn=json_object_get_member(o,"projection"),*rn=json_object_get_member(o,"requests"),*fn=json_object_get_member(o,"focus");
    if (!pn || !JSON_NODE_HOLDS_OBJECT(pn) || !rn || !JSON_NODE_HOLDS_ARRAY(rn) || !fn || !JSON_NODE_HOLDS_ARRAY(fn)) return FALSE;
    JsonObject *p=json_node_get_object(pn);const char *const pf[]={"viewProtocol","kind","revision","views","popupOwner","focusOwner","frame"};gboolean open;
    if (!surface_fields(p,pf,7) || json_node_get_value_type(json_object_get_member(p,"viewProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(p,"viewProtocol")!=1 || !surface_text(json_object_get_member(p,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(p,"kind"),"view-frame") || !surface_uint(json_object_get_member(p,"revision"),revision) || !*revision || *revision>topology_revision || !surface_frame(json_object_get_member(p,"frame"),publication,lease,&open)) return FALSE;
    JsonNode *vn=json_object_get_member(p,"views"),*popup=json_object_get_member(p,"popupOwner"),*focus=json_object_get_member(p,"focusOwner");
    if (!vn || !JSON_NODE_HOLDS_ARRAY(vn)) return FALSE;
    JsonArray *views=json_node_get_array(vn);guint count=json_array_get_length(views);if (!count || count>64) return FALSE;
    OutputView owner={0},other={0};
    if (!popup || !focus || (!JSON_NODE_HOLDS_NULL(popup) && !shared_issued_scope(popup,&owner)) || (!JSON_NODE_HOLDS_NULL(focus) && !shared_issued_scope(focus,&other))) return FALSE;
    *scope=owner.id?owner:other;if (!scope->id) return FALSE;
    gboolean owns=FALSE;
    for (guint i=0;i<count;i++) {OutputView row={0};if (!shared_issued_scope(json_array_get_element(views,i),&row)) return FALSE;if(row.id==scope->id) owns=TRUE;
        for(guint j=0;j<i;j++){OutputView prior={0};if(!shared_issued_scope(json_array_get_element(views,j),&prior) || prior.id==row.id) return FALSE;}}
    if (!owns) return FALSE;
    for(guint k=0;k<2;k++){guint64 id=k?other.id:owner.id;gboolean found=!id;for(guint i=0;i<json_array_get_length(views);i++){OutputView row={0};shared_issued_scope(json_array_get_element(views,i),&row);if(row.id==id)found=TRUE;}if(!found)return FALSE;}
    JsonArray *requests=json_node_get_array(rn),*focuses=json_node_get_array(fn);count=json_array_get_length(requests);if(!count || count>16 || json_array_get_length(focuses)>16) return FALSE;
    for(guint i=0;i<count;i++){JsonNode *request=json_array_get_element(requests,i);if(!request_kind(request)) return FALSE;g_autofree char *text=json_to_string(request,FALSE);JsonNode *binding=json_object_get_member(json_node_get_object(request),"binding");if(strlen(text)>4096 || !binding || !json_node_equal(binding,authority_binding)) return FALSE;}
    for(guint i=0;i<json_array_get_length(focuses);i++)if(!surface_text(json_array_get_element(focuses,i),1024,FALSE)) return FALSE;
    return TRUE;
}
static JsonNode *shared_batch_certificate(JsonNode *batch,const char *original,OutputView *scope,guint64 publication,guint64 lease,SurfaceDisposition disposition) {
    OutputView identity={0};guint64 revision,pub,token;
    if (!scope || !shared_batch_identity(batch,original,&identity,&revision,&pub,&token) || scope->id!=identity.id || scope->generation!=identity.generation || publication!=pub || lease!=token) return NULL;
    const char *state=disposition==SURFACE_PREFLIGHT_UNSENT?"preflight-unsent":disposition==SURFACE_ADMITTED?"admitted":disposition==SURFACE_UNCERTAIN?"uncertain":NULL;if(!state)return NULL;
    JsonObject *o=json_object_new();json_object_set_int_member(o,"viewProtocol",1);json_object_set_string_member(o,"kind","batch-disposition");json_object_set_string_member(o,"disposition",state);json_object_set_member(o,"scope",scope_packet(&identity));
    g_autofree char *r=g_strdup_printf("%" G_GUINT64_FORMAT,revision),*p=g_strdup_printf("%" G_GUINT64_FORMAT,pub),*l=g_strdup_printf("%" G_GUINT64_FORMAT,token);
    json_object_set_string_member(o,"revision",r);json_object_set_string_member(o,"publication",p);json_object_set_string_member(o,"lease",l);json_object_set_member(o,"binding",json_node_copy(authority_binding));json_object_set_string_member(o,"batch",original);
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,o);return packet;
}
/* Fixed dedup window + non-decreasing floor: never negative-certify replay
 * after eviction. FIFO first delivery remains an explicit qualification gate. */
/* The cache and each active callback independently own one reference.
 * Reentrant callbacks may evict/reset the cache without retiring callers. */
typedef struct {grefcount refs;char *wire;JsonNode *certificate;gboolean finished;} SharedBatchRecord;
static GQueue shared_batches=G_QUEUE_INIT;
static JsonNode *shared_batch_binding;
static guint64 shared_batch_highest;
static SharedBatchRecord *shared_batch_ref(SharedBatchRecord *row){g_ref_count_inc(&row->refs);return row;}
static void shared_batch_free(SharedBatchRecord *row){if(row && g_ref_count_dec(&row->refs)){g_free(row->wire);json_node_unref(row->certificate);g_free(row);}}
G_DEFINE_AUTOPTR_CLEANUP_FUNC(SharedBatchRecord,shared_batch_free)
static void shared_batch_emit(SharedBatchRecord *row){
    if(!row || !row->finished || !authority_binding || !json_node_equal(json_object_get_member(json_node_get_object(row->certificate),"binding"),authority_binding))return;
    surface_eval(view,"receiveBatchDisposition",row->certificate);
}
static SharedBatchRecord *shared_batch_reserve(JsonNode *root,const char *wire,gboolean *duplicate) {
    *duplicate=FALSE;OutputView identity={0};guint64 revision,publication,lease;
    if(!shared_batch_identity(root,wire,&identity,&revision,&publication,&lease))return NULL;
    if(!shared_batch_binding || !json_node_equal(shared_batch_binding,authority_binding)){
        while(!g_queue_is_empty(&shared_batches))shared_batch_free(g_queue_pop_head(&shared_batches));
        if(shared_batch_binding)json_node_unref(shared_batch_binding);
        shared_batch_binding=json_node_copy(authority_binding);shared_batch_highest=0;
    }
    for(GList *it=shared_batches.head;it;it=it->next){SharedBatchRecord *row=it->data;if(g_str_equal(row->wire,wire)){*duplicate=TRUE;return shared_batch_ref(row);}}
    if(publication<=shared_batch_highest)return NULL;
    JsonNode *certificate=shared_batch_certificate(root,wire,&identity,publication,lease,SURFACE_UNCERTAIN);if(!certificate)return NULL;
    SharedBatchRecord *row=g_new0(SharedBatchRecord,1);g_ref_count_init(&row->refs);row->wire=g_strdup(wire);row->certificate=certificate;
    if(g_queue_get_length(&shared_batches)>=16)shared_batch_free(g_queue_pop_head(&shared_batches));
    g_queue_push_tail(&shared_batches,row);shared_batch_highest=publication;return shared_batch_ref(row);
}
static void shared_batch_finish(SharedBatchRecord *row,SurfaceDisposition disposition) {
    if(!row)return;
    /* Only the original callback calls finish. Finalize before delivering;
     * nested duplicates can observe only this immutable first disposition. */
    if(!row->finished){
        const char *state=disposition==SURFACE_PREFLIGHT_UNSENT?"preflight-unsent":disposition==SURFACE_ADMITTED?"admitted":"uncertain";
        JsonObject *original=json_node_get_object(row->certificate),*final=json_object_new();
        GList *members=json_object_get_members(original);
        for(GList *it=members;it;it=it->next)json_object_set_member(final,it->data,json_node_copy(json_object_get_member(original,it->data)));
        g_list_free(members);json_object_set_string_member(final,"disposition",state);
        JsonNode *certificate=json_node_new(JSON_NODE_OBJECT);json_node_take_object(certificate,final);
        json_node_unref(row->certificate);row->certificate=certificate;row->finished=TRUE;
    }
    shared_batch_emit(row);
}
static void shared_commit(JsonNode *root,const char *original) {
    g_autofree char *wire=NULL;gboolean duplicate=FALSE;
    g_autoptr(SharedBatchRecord) record=shared_batch_reserve(root,original,&duplicate);
    if(duplicate){shared_batch_emit(record);return;}
    if (!root || !JSON_NODE_HOLDS_OBJECT(root)) goto refuse;
    JsonObject *object=json_node_get_object(root);const char *const fields[]={"viewProtocol","kind","projection","requests","focus"};
    if (!surface_fields(object,fields,5) || json_node_get_value_type(json_object_get_member(object,"viewProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(object,"viewProtocol")!=1 || !surface_text(json_object_get_member(object,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(object,"kind"),"view-commit")) goto refuse;
    JsonNode *pn=json_object_get_member(object,"projection");if (!pn || !JSON_NODE_HOLDS_OBJECT(pn)) goto refuse;
    JsonObject *projection=json_node_get_object(pn);OutputView *next_popup=NULL,*next_focus=NULL;
    if (!projection_scopes(projection,&next_popup,&next_focus)) goto refuse;
    JsonNode *frame=json_object_get_member(projection,"frame"),*rn=json_object_get_member(object,"requests"),*fn=json_object_get_member(object,"focus");
    guint64 publication,lease;gboolean open;
    if (rn && JSON_NODE_HOLDS_ARRAY(rn) && json_array_get_length(json_node_get_array(rn)) && !record) {
        JsonArray *rows=json_node_get_array(rn);const char *kind=request_kind(json_array_get_element(rows,0));
        /* Existing explicit reconnect has no binding and no registered effect. */
        if(json_array_get_length(rows)!=1 || !kind || !g_str_equal(kind,"host-reconnect"))goto refuse;
    }
    if (!surface_frame(frame,&publication,&lease,&open) || !rn || !JSON_NODE_HOLDS_ARRAY(rn) || !fn || !JSON_NODE_HOLDS_ARRAY(fn) || open!=(next_popup!=NULL)) goto refuse;
    /* A topology-only publication reuses the exact accepted frame, never effects. */
    if (publication==surface_gate.publication && surface_snapshot && !json_array_get_length(json_node_get_array(rn)) && !json_array_get_length(json_node_get_array(fn))) {
        g_autofree char *prior=json_to_string(surface_snapshot,FALSE),*shown=json_to_string(frame,FALSE);
        if (!g_str_equal(prior,shown) || next_popup!=popup_owner) goto refuse;
        focus_owner=next_focus;shared_publish();g_print("view-commit: topology-only=1\n");fflush(stdout);return;
    }
    JsonObject *legacy=json_object_new();json_object_set_int_member(legacy,"surfaceProtocol",2);json_object_set_string_member(legacy,"kind","surface-commit");
    json_object_set_member(legacy,"frame",json_node_copy(frame));json_object_set_member(legacy,"requests",json_node_copy(rn));json_object_set_member(legacy,"focus",json_node_copy(fn));
    JsonNode *translated=json_node_new(JSON_NODE_OBJECT);json_node_take_object(translated,legacy);
    SurfaceGate candidate=surface_gate;SurfaceCommit admitted;
    if (popup_active && popup_owner!=next_popup) candidate.closed=MAX(candidate.closed,candidate.lease);
    if (!surface_preflight(&candidate,translated,g_queue_get_length(&requests),active_request?1:0,backend_ready,&admitted)) {
        json_node_unref(translated);goto refuse;
    }
    shared_preserve_context_anchor=shared_anchor_for(next_popup,frame);
    if (popup_active && popup_owner!=next_popup) popup_hide();
    popup_owner=next_popup;focus_owner=next_focus;
    owned_monitor=popup_owner?popup_owner->monitor:NULL;window=popup_owner?popup_owner->bar:controller_window;
    wire=json_to_string(translated,FALSE);SurfaceDisposition disposition=surface_receive(primary_manager,wire,translated);shared_preserve_context_anchor=FALSE;json_node_unref(translated);
    shared_batch_finish(record,disposition);
    g_print("view-commit: popup=%" G_GUINT64_FORMAT " focus=%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT "\n",popup_owner?popup_owner->id:0,focus_owner?focus_owner->id:0,publication);fflush(stdout);return;
refuse:
    shared_batch_finish(record,SURFACE_PREFLIGHT_UNSENT);
    g_print("view-refused: commit-preflight\n");fflush(stdout);
}
static void shared_forward(OutputView *origin,JsonNode *action,gboolean popup) {
    if (!origin || !origin->active || (popup && origin!=popup_owner) || !surface_action(&surface_gate,action,surface_snapshot,popup)) return;
    JsonObject *object=json_object_new();json_object_set_int_member(object,"viewProtocol",1);json_object_set_string_member(object,"kind","view-action");
    json_object_set_member(object,"scope",scope_packet(origin));json_object_set_member(object,"action",json_node_copy(action));
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,object);surface_eval(view,"receiveAction",packet);json_node_unref(packet);
}
typedef struct {GHashTable *members;gboolean duplicate;} JsonAdmission;
static void json_member_seen(JsonParser *parser,JsonObject *object,const char *member,gpointer data) {
    (void)parser;JsonAdmission *admission=data;
    char *key=g_strdup_printf("%p:%s",(void*)object,member);
    if (g_hash_table_contains(admission->members,key)) {admission->duplicate=TRUE;g_free(key);}
    else g_hash_table_add(admission->members,key);
}
static gboolean strict_json_load(JsonParser *parser,const char *text) {
    JsonAdmission admission={g_hash_table_new_full(g_str_hash,g_str_equal,g_free,NULL),FALSE};
    gulong handler=g_signal_connect(parser,"object-member",G_CALLBACK(json_member_seen),&admission);
    gboolean parsed=json_parser_load_from_data(parser,text,-1,NULL);
    g_signal_handler_disconnect(parser,handler);g_hash_table_unref(admission.members);
    return parsed && !admission.duplicate;
}
static void shared_context_forward(OutputView *origin,JsonNode *action,gboolean popup) {
    if (!origin || !origin->active || (popup && origin!=popup_owner)) return;
    JsonObject *object=json_object_new();json_object_set_int_member(object,"viewProtocol",1);json_object_set_string_member(object,"kind","view-action");
    json_object_set_member(object,"scope",scope_packet(origin));json_object_set_member(object,"action",json_node_copy(action));
    JsonNode *packet=json_node_new(JSON_NODE_OBJECT);json_node_take_object(packet,object);surface_eval(view,"receiveAction",packet);json_node_unref(packet);
}
static void shared_receive_text(WebKitUserContentManager *manager,const char *text) {
    if (shutting_down || !text || strlen(text)>1048576) return;
    g_autoptr(JsonParser) parser=json_parser_new();if (!strict_json_load(parser,text)) {g_print("view-refused: duplicate-or-malformed-json\n");fflush(stdout);return;}
    JsonNode *root=json_parser_get_root(parser);if (!JSON_NODE_HOLDS_OBJECT(root)) return;
    JsonObject *object=json_node_get_object(root);const char *kind=surface_text(json_object_get_member(object,"kind"),32,FALSE)?json_object_get_string_member(object,"kind"):NULL;
    if (preview_route_commands(manager,text,root)) return;
    if(manager==popup_manager && kind && g_str_equal(kind,"preview-image-report")) {
        if(qa_client_subject) {client_image_report(object);return;}
        if(qa_import_subjects[0]) {imported_image_report(object);return;}
    }
    OutputView *origin=manager_lookup(manager);
    if (qa_exit && kind && g_str_equal(kind,"surface-report") && (origin || manager==popup_manager)) {
        g_print("surface-report: origin=%s %s\n",origin?"bar":"popup",text);
        if (origin) {GdkRectangle geometry;gdk_monitor_get_geometry(origin->monitor,&geometry);g_print("view-report: id=%" G_GUINT64_FORMAT " x=%d y=%d %s\n",origin->id,geometry.x,geometry.y,text);}
        reported=TRUE;if (quit_source) {g_source_remove(quit_source);quit_source=0;}fflush(stdout);return;
    }
    if (manager==primary_manager) {
        if (qa_exit && kind && g_str_equal(kind,"surface-inspection")) {g_print("surface-inspection: %s\n",text);fflush(stdout);return;}
        const char *const ready[]={"protocolVersion","kind"};
        if (strlen(text)<=4096 && surface_fields(object,ready,2) && request_kind(root) && g_str_equal(request_kind(root),"host-ready")) {controller_ready=TRUE;shared_topology();backend_start();return;}
        shared_commit(root,text);return;
    }
    if (!origin && manager!=popup_manager) return;
    const char *const ready[]={"surfaceProtocol","kind"};
    if (strlen(text)<=4096 && surface_fields(object,ready,2) && json_node_get_value_type(json_object_get_member(object,"surfaceProtocol"))==G_TYPE_INT64 && json_object_get_int_member(object,"surfaceProtocol")==2 && kind && g_str_equal(kind,"presentation-ready")) {
        if (origin) {origin->ready=TRUE;shared_publish();} else {popup_ready=TRUE;surface_present();}return;
    }
    if (strlen(text)>4096) return;
    if (kind && g_str_equal(kind,"context-input-report") && qa_exit) {g_print("context-input-report: %s\n",text);fflush(stdout);return;}
    if (kind && g_str_equal(kind,"surface-context")) {if(!shared_context_receive(manager,root)){g_print("surface-context-refused: origin-or-proof\n");fflush(stdout);}return;}
    if (kind && g_str_equal(kind,"surface-menu-navigation")) {if(!shared_navigation_receive(manager,root)){g_print("surface-menu-navigation-refused\n");
        if(qa_exit){
            g_autofree char *diagnostic=json_to_string(root,FALSE);
            g_print("surface-navigation-diagnostic: ready=%d available=%d released=%d current=%d key=%u epoch=%" G_GUINT64_FORMAT "/%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT "/%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "/%" G_GUINT64_FORMAT " age=%" G_GINT64_FORMAT " message=%s\n",
                surface_popup_ready(),context_proof.available,context_proof.released,context_current(&context_proof,TRUE),context_proof.key,
                context_proof.epoch,context_epoch,context_proof.publication,surface_gate.publication,context_proof.lease,surface_gate.lease,
                g_get_monotonic_time()-context_proof.captured,diagnostic);}
        fflush(stdout);}return;}
    if (manager==popup_manager) {
        if (surface_ack(object,"presentation-applied",FALSE) || surface_ack(object,"focus-applied",TRUE)) {client_wake();imported_wake();return;}
        if (surface_popup_ready()) shared_forward(popup_owner,root,TRUE);
    } else shared_forward(origin,root,FALSE);
}
static void shared_receive(WebKitUserContentManager *manager,WebKitJavascriptResult *result,gpointer unused) {
    (void)unused;if (shutting_down) return;
    JSCValue *value=webkit_javascript_result_get_js_value(result);if (!jsc_value_is_string(value)) return;
    g_autofree char *text=jsc_value_to_string(value);shared_receive_text(manager,text);
}
static void shared_geometry(GObject *object,GParamSpec *property,gpointer data) {
    (void)property;OutputView *row=data;
    if (!row->active || object!=G_OBJECT(row->monitor) || shutting_down) return;
    shared_context_cancel();
    if(row!=popup_owner || !popup_active) return;
    guint64 lease=surface_gate.lease;popup_hide();shared_popup_notify("receiveReflow",lease);
    g_print("view-reflow: id=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",row->id,lease);fflush(stdout);
}
static void manager_configure(WebKitUserContentManager *manager) {
    if (qa_exit) {WebKitUserScript *script=webkit_user_script_new("window.elmHostQA=true;",WEBKIT_USER_CONTENT_INJECT_TOP_FRAME,WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START,NULL,NULL);webkit_user_content_manager_add_script(manager,script);webkit_user_script_unref(script);}
    g_signal_connect(manager,"script-message-received::native",G_CALLBACK(shared_receive),NULL);
    if (!webkit_user_content_manager_register_script_message_handler(manager,"native")) {failed=TRUE;gtk_main_quit();}
}
/* Share only the renderer process; every bridge manager remains distinct.
 * Supplying web-context with related-view is rejected by WebKit construction.
 */
static WebKitWebView *shared_child(WebKitUserContentManager *manager) {
    g_assert(manager && manager!=primary_manager);
    WebKitWebView *child=WEBKIT_WEB_VIEW(g_object_new(WEBKIT_TYPE_WEB_VIEW,
        "related-view",view,"user-content-manager",manager,"settings",shared_settings,NULL));
    g_assert(webkit_web_view_get_context(child)==shared_context);
    g_assert(webkit_web_view_get_settings(child)==shared_settings);
    g_assert(webkit_web_view_get_user_content_manager(child)==manager);
    g_print("view-process-policy: related=1 distinct-manager=1\n");fflush(stdout);
    return child;
}
static void shared_add(GdkDisplay *display,GdkMonitor *monitor,gpointer unused) {
    (void)display;(void)unused;if (shutting_down) return;
    if (output_views->len>=64 || issued_view==G_MAXUINT64 || !GDK_IS_WAYLAND_MONITOR(monitor) || !gdk_wayland_monitor_get_wl_output(monitor)) {failed=TRUE;gtk_main_quit();return;}
    for (guint i=0;i<output_views->len;i++) if (((OutputView*)g_ptr_array_index(output_views,i))->monitor==monitor) return;
    OutputView *row=g_new0(OutputView,1);row->id=++issued_view;row->generation=1;row->monitor=g_object_ref(monitor);row->active=TRUE;
    row->manager=webkit_user_content_manager_new();manager_configure(row->manager);
    row->engine=shared_child(row->manager);
    row->bar=gtk_window_new(GTK_WINDOW_TOPLEVEL);gtk_window_set_title(GTK_WINDOW(row->bar),"Elm bar");
    gtk_layer_init_for_window(GTK_WINDOW(row->bar));gtk_layer_set_monitor(GTK_WINDOW(row->bar),monitor);gtk_layer_set_namespace(GTK_WINDOW(row->bar),"elm-shell-recovery-v17");
    gtk_layer_set_layer(GTK_WINDOW(row->bar),GTK_LAYER_SHELL_LAYER_TOP);gtk_layer_set_anchor(GTK_WINDOW(row->bar),GTK_LAYER_SHELL_EDGE_TOP,TRUE);gtk_layer_set_anchor(GTK_WINDOW(row->bar),GTK_LAYER_SHELL_EDGE_LEFT,TRUE);gtk_layer_set_anchor(GTK_WINDOW(row->bar),GTK_LAYER_SHELL_EDGE_RIGHT,TRUE);gtk_layer_set_exclusive_zone(GTK_WINDOW(row->bar),48);gtk_layer_set_keyboard_mode(GTK_WINDOW(row->bar),GTK_LAYER_SHELL_KEYBOARD_MODE_NONE);
    gtk_widget_set_size_request(row->bar,-1,48);gtk_window_resize(GTK_WINDOW(row->bar),1,1);gtk_widget_set_size_request(GTK_WIDGET(row->engine),-1,48);
    gtk_container_add(GTK_CONTAINER(row->bar),GTK_WIDGET(row->engine));
    g_signal_connect(row->engine,"decide-policy",G_CALLBACK(policy),NULL);g_signal_connect(row->engine,"web-process-terminated",G_CALLBACK(terminated),NULL);
    g_signal_connect(row->engine,"event",G_CALLBACK(shared_context_event),NULL);
    g_signal_connect(row->engine,"button-press-event",G_CALLBACK(retain_event),NULL);g_signal_connect(row->engine,"key-press-event",G_CALLBACK(retain_event),NULL);
    row->geometry_handler=g_signal_connect(monitor,"notify::geometry",G_CALLBACK(shared_geometry),row);
    g_ptr_array_add(output_views,row);gtk_widget_show_all(row->bar);gtk_layer_try_force_commit(GTK_WINDOW(row->bar));
    webkit_web_view_load_uri(row->engine,"elm-shell://app/bar.html");
    GdkRectangle geometry;gdk_monitor_get_geometry(monitor,&geometry);g_print("view-added: id=%" G_GUINT64_FORMAT " geometry=%d,%d,%d,%d\n",row->id,geometry.x,geometry.y,geometry.width,geometry.height);fflush(stdout);
    if (controller_ready) topology_advance();
}
static void view_retire(OutputView *row) {
    shared_context_cancel();
    row->active=FALSE;
    if (row==popup_owner) {if (popup_active) popup_hide();popup_owner=NULL;owned_monitor=NULL;window=controller_window;}
    if (row==focus_owner) focus_owner=NULL;
    g_signal_handler_disconnect(row->monitor,row->geometry_handler);
    g_signal_handlers_disconnect_by_func(row->manager,G_CALLBACK(shared_receive),NULL);
    gtk_widget_destroy(row->bar);g_object_unref(row->manager);g_object_unref(row->monitor);
    g_print("view-retired: id=%" G_GUINT64_FORMAT "\n",row->id);fflush(stdout);g_free(row);
}
static void shared_remove(GdkDisplay *display,GdkMonitor *monitor,gpointer unused) {
    (void)display;(void)unused;if (shutting_down) return;
    for (guint i=0;i<output_views->len;i++) {OutputView *row=g_ptr_array_index(output_views,i);if (row->monitor!=monitor) continue;g_ptr_array_remove_index(output_views,i);view_retire(row);topology_advance();return;}
}
static void test_view_capabilities(void) {
    OutputView one={.id=1,.generation=1,.active=TRUE,.manager=(WebKitUserContentManager*)1},two={.id=2,.generation=1,.active=TRUE,.manager=(WebKitUserContentManager*)2};
    output_views=g_ptr_array_new();g_ptr_array_add(output_views,&one);g_ptr_array_add(output_views,&two);
    JsonNode *scope=scope_packet(&one);g_assert_true(scope_lookup(scope)==&one);g_assert_true(manager_lookup(one.manager)==&one);g_assert_null(manager_lookup((WebKitUserContentManager*)3));
    one.active=FALSE;g_assert_null(scope_lookup(scope));g_assert_null(manager_lookup(one.manager));one.active=TRUE;
    json_object_set_string_member(json_node_get_object(scope),"generation","2");g_assert_null(scope_lookup(scope));
    json_object_set_string_member(json_node_get_object(scope),"generation","1");json_object_set_string_member(json_node_get_object(scope),"extra","forged");g_assert_null(scope_lookup(scope));
    json_node_unref(scope);g_ptr_array_unref(output_views);output_views=NULL;
}
static void test_projection_capabilities(void) {
    OutputView one={.id=1,.generation=1,.active=TRUE},two={.id=2,.generation=1,.active=TRUE};
    output_views=g_ptr_array_new();g_ptr_array_add(output_views,&one);g_ptr_array_add(output_views,&two);
    g_autoptr(JsonParser) parser=json_parser_new();
    g_assert_true(json_parser_load_from_data(parser,"{\"viewProtocol\":1,\"kind\":\"view-frame\",\"revision\":\"1\",\"views\":[{\"id\":\"1\",\"generation\":\"1\"},{\"id\":\"2\",\"generation\":\"1\"}],\"popupOwner\":null,\"focusOwner\":{\"id\":\"1\",\"generation\":\"1\"},\"frame\":null}",-1,NULL));
    JsonObject *object=json_node_get_object(json_parser_get_root(parser));OutputView *popup=NULL,*focus=NULL;
    g_assert_true(projection_scopes(object,&popup,&focus));g_assert_null(popup);g_assert_true(focus==&one);
    json_object_set_string_member(object,"revision","0");g_assert_false(projection_scopes(object,&popup,&focus));json_object_set_string_member(object,"revision","1");
    json_object_set_member(object,"popupOwner",scope_packet(&two));g_assert_true(projection_scopes(object,&popup,&focus));g_assert_true(popup==&two);
    two.active=FALSE;g_assert_false(projection_scopes(object,&popup,&focus));two.active=TRUE;
    json_object_set_member(object,"focusOwner",json_node_new(JSON_NODE_NULL));g_assert_false(projection_scopes(object,&popup,&focus));
    json_object_set_member(object,"focusOwner",scope_packet(&one));
    JsonArray *rows=json_object_get_array_member(object,"views");json_array_remove_element(rows,1);json_array_add_element(rows,scope_packet(&one));g_assert_false(projection_scopes(object,&popup,&focus));
    json_array_remove_element(rows,1);json_array_add_element(rows,scope_packet(&two));json_object_set_string_member(object,"injected","authority");g_assert_false(projection_scopes(object,&popup,&focus));
    g_ptr_array_unref(output_views);output_views=NULL;
}
static void test_duplicate_fields(void) {
    const char *accepted[]={"{\"scope\":{\"id\":\"1\"},\"other\":{\"id\":\"2\"}}","{\"views\":[{\"id\":\"1\"},{\"id\":\"2\"}]}"};
    const char *refused[]={"{\"kind\":\"action\",\"kind\":\"execute\"}","{\"scope\":{\"id\":\"1\",\"id\":\"2\"}}","{\"id\":\"1\",\"\\u0069d\":\"2\"}","{\"scope\":{\"id\":\"1\"},\"scope\":{\"id\":\"2\"}}","{bad"};
    for (guint i=0;i<G_N_ELEMENTS(accepted);i++) {g_autoptr(JsonParser) parser=json_parser_new();g_assert_true(strict_json_load(parser,accepted[i]));}
    for (guint i=0;i<G_N_ELEMENTS(refused);i++) {g_autoptr(JsonParser) parser=json_parser_new();g_assert_false(strict_json_load(parser,refused[i]));}
}
/* Native journal delivery is independent from URI reads and popup visibility.
 * Sending a terminal proof never consumes it; only the exact Elm Ack can. */
static gboolean native_preview_acknowledgements(WebKitWebView *target,JsonNode *root) {
    if(preview_owner!=g_thread_self() || target!=popup_view || !preview_bootstrap || !JSON_NODE_HOLDS_OBJECT(root))return FALSE;
    JsonObject *object=json_node_get_object(root);JsonNode *entries=json_object_get_member(object,"entries");
    if(!entries || !JSON_NODE_HOLDS_ARRAY(entries) || json_array_get_length(json_node_get_array(entries))!=1)return FALSE;
    JsonNode *row=json_array_get_element(json_node_get_array(entries),0);if(!JSON_NODE_HOLDS_OBJECT(row))return FALSE;
    JsonObject *entry=json_node_get_object(row);const char *const fields[]={"identity","commands"};JsonNode *identity=json_object_get_member(entry,"identity"),*commands=json_object_get_member(entry,"commands");
    if(!surface_fields(entry,fields,2) || !surface_text(identity,512,FALSE) || !commands || !JSON_NODE_HOLDS_ARRAY(commands))return FALSE;
    JsonArray *array=json_node_get_array(commands);if(json_array_get_length(array)>64)return FALSE;
    /* Other preview effects await eligible capture integration. Never partly
     * consume a mixed supported/unsupported effect batch. */
    for(guint i=0;i<json_array_get_length(array);i++) {
        JsonNode *command=json_array_get_element(array,i);if(!JSON_NODE_HOLDS_OBJECT(command))return FALSE;
        JsonObject *record=json_node_get_object(command);const char *const ack[]={"kind","job","sequence"};JsonNode *kind=json_object_get_member(record,"kind");
        if(!surface_fields(record,ack,3) || !surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"acknowledge"))return FALSE;
    }
    gboolean accepted=TRUE;
    for(guint i=0;i<json_array_get_length(array);i++) {
        g_autofree char *wire=json_to_string(json_array_get_element(array,i),FALSE);GError *error=NULL;
        if(!warlock_preview_bootstrap_acknowledge(preview_bootstrap,target,json_node_get_string(identity),wire,&error))accepted=FALSE;
        g_clear_error(&error);
    }
    return accepted;
}
static gboolean client_frame_target(JsonNode *frame,guint64 subject,guint64 *publication,guint64 *lease) {
    gboolean open;
    if(!subject || !surface_frame(frame,publication,lease,&open) || !open)return FALSE;
    JsonObject *object=json_node_get_object(frame);
    if(!g_str_equal(json_object_get_string_member(object,"mode"),"picker"))return FALSE;
    g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,subject);
    JsonArray *controls=json_object_get_array_member(object,"popup");
    for(guint i=0;i<json_array_get_length(controls);i++) {
        JsonObject *control=json_node_get_object(json_array_get_element(controls,i));
        if(g_str_equal(json_object_get_string_member(control,"id"),identity))return json_object_get_boolean_member(control,"enabled");
    }
    return FALSE;
}
static gboolean imported_frame_target(JsonNode *frame,guint64 first,guint64 second,guint64 *publication,guint64 *lease) {
    guint64 other_publication,other_lease;
    return first && second && first!=second && client_frame_target(frame,first,publication,lease) &&
        client_frame_target(frame,second,&other_publication,&other_lease) && *publication==other_publication && *lease==other_lease;
}
static gboolean client_publish(const char *wire,GError **error) {
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!wire || !strict_json_load(parser,wire) || !JSON_NODE_HOLDS_ARRAY(json_parser_get_root(parser))) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Native client event batch");return FALSE;
    }
    JsonArray *events=json_node_get_array(json_parser_get_root(parser));
    if(json_array_get_length(events)>4) {g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Native client event bound");return FALSE;}
    if(json_array_get_length(events)) {g_print("native-client-events: %s\n",wire);fflush(stdout);surface_eval(popup_view,"receiveNativePreviewBatch",json_parser_get_root(parser));}
    return TRUE;
}
static void client_failure(GError *error) {
    g_printerr("Native client producer failed: %s\n",error?error->message:"Owner unavailable");g_clear_error(&error);failed=TRUE;gtk_main_quit();
}
static cairo_status_t snapshot_write(void *opaque,const unsigned char *bytes,unsigned length) {
    int fd=*(int*)opaque;unsigned offset=0;
    while(offset<length) {ssize_t n=write(fd,bytes+offset,length-offset);if(n<0 && errno==EINTR)continue;if(n<=0)return CAIRO_STATUS_WRITE_ERROR;offset+=(unsigned)n;}
    return CAIRO_STATUS_SUCCESS;
}
static void client_snapshot_complete(GObject *object,GAsyncResult *result,gpointer unused) {
    ClientSnapshot *snapshot=unused;GError *error=NULL;
    cairo_surface_t *image=webkit_web_view_get_snapshot_finish(WEBKIT_WEB_VIEW(object),result,&error);client_snapshot_pending=FALSE;
    if(!image) {g_free(snapshot->path);g_free(snapshot);client_failure(error);return;}
    g_autofree char *directory=g_path_get_dirname(snapshot->path),*name=g_path_get_basename(snapshot->path);
    int parent=open(directory,O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);struct stat info;
    int fd=-1;
    if(parent>=0 && fstat(parent,&info)==0 && info.st_uid==getuid() && (info.st_mode&0777)==0700)fd=openat(parent,name,O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
    cairo_status_t status=fd>=0?cairo_surface_write_to_png_stream(image,snapshot_write,&fd):CAIRO_STATUS_WRITE_ERROR;
    if(fd>=0)close(fd);
    if(parent>=0)close(parent);
    cairo_surface_destroy(image);
    if(status!=CAIRO_STATUS_SUCCESS) {g_free(snapshot->path);g_free(snapshot);client_failure(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Private WebKit snapshot write"));return;}
    if((client_producer && snapshot->request==warlock_client_producer_request(client_producer)) || imported_clients)client_snapshot_written=TRUE;
    g_print("native-client-webkit-snapshot: saved=1 hardwarePresentation=0\n");
    g_print("native-client-webkit-snapshot-job: request=%" G_GUINT64_FORMAT " path=%s\n",snapshot->request,snapshot->path);fflush(stdout);g_free(snapshot->path);g_free(snapshot);
}
static gboolean client_image_report(JsonObject *object) {
    const char *const fields[]={"kind","images"};JsonNode *node=json_object_get_member(object,"images");
    if(!qa_client_snapshot || !surface_fields(object,fields,2) || !node || !JSON_NODE_HOLDS_ARRAY(node))return FALSE;
    JsonArray *images=json_node_get_array(node);if(json_array_get_length(images)!=1)return FALSE;
    JsonNode *row=json_array_get_element(images,0);if(!JSON_NODE_HOLDS_OBJECT(row))return FALSE;
    JsonObject *image=json_node_get_object(row);const char *const names[]={"uri","complete","naturalWidth","naturalHeight","width","height"};
    if(!surface_fields(image,names,6) || !surface_text(json_object_get_member(image,"uri"),128,FALSE))return FALSE;
    GError *error=NULL;g_autofree char *current_uri=NULL;
    if(!client_producer || !warlock_client_producer_uri(client_producer,&current_uri,&error)) {g_clear_error(&error);return FALSE;}
    if(!*current_uri || !g_str_equal(current_uri,json_object_get_string_member(image,"uri")))return FALSE;
    JsonNode *complete=json_object_get_member(image,"complete");if(!complete || json_node_get_value_type(complete)!=G_TYPE_BOOLEAN || !json_node_get_boolean(complete))return FALSE;
    for(guint i=2;i<6;i++) {JsonNode *value=json_object_get_member(image,names[i]);if(!value || json_node_get_value_type(value)!=G_TYPE_INT64 || json_node_get_int(value)<=0 || json_node_get_int(value)>4096)return FALSE;}
    g_autofree char *wire=json_to_string(node,FALSE);g_print("native-client-image: %s\n",wire);fflush(stdout);
    if(!client_snapshot_pending && !client_snapshot_written && client_producer) {
        ClientSnapshot *snapshot=g_new0(ClientSnapshot,1);snapshot->request=warlock_client_producer_request(client_producer);
        snapshot->path=snapshot->request==1?g_strdup(qa_client_snapshot):g_strdup_printf("%s.request-%" G_GUINT64_FORMAT ".png",qa_client_snapshot,snapshot->request);
        client_snapshot_pending=TRUE;webkit_web_view_get_snapshot(popup_view,WEBKIT_SNAPSHOT_REGION_VISIBLE,WEBKIT_SNAPSHOT_OPTIONS_NONE,NULL,client_snapshot_complete,snapshot);
    }
    return TRUE;
}
static gboolean client_report_status(GError **error) {
    g_autofree char *status=NULL;
    if(!warlock_client_producer_status(client_producer,&status,error))return FALSE;
    if(g_strcmp0(status,client_last_status)) {g_free(client_last_status);client_last_status=g_strdup(status);g_print("native-client-ownership: %s\n",status);fflush(stdout);}
    return TRUE;
}
static gboolean client_commands(WebKitWebView *target,JsonNode *root) {
    if(preview_owner!=g_thread_self() || target!=popup_view || !client_producer || !JSON_NODE_HOLDS_OBJECT(root))return FALSE;
    JsonObject *object=json_node_get_object(root);JsonArray *entries=json_object_get_array_member(object,"entries");
    if(json_array_get_length(entries)!=1)return FALSE;
    JsonNode *row=json_array_get_element(entries,0);if(!JSON_NODE_HOLDS_OBJECT(row))return FALSE;
    JsonObject *entry=json_node_get_object(row);const char *const fields[]={"identity","commands"};
    JsonNode *identity=json_object_get_member(entry,"identity"),*commands=json_object_get_member(entry,"commands");
    if(!surface_fields(entry,fields,2) || !surface_text(identity,512,FALSE) || !commands || !JSON_NODE_HOLDS_ARRAY(commands))return FALSE;
    JsonArray *array=json_node_get_array(commands);if(json_array_get_length(array)!=1)return FALSE;
    JsonNode *command=json_array_get_element(array,0);if(!JSON_NODE_HOLDS_OBJECT(command))return FALSE;
    JsonObject *record=json_node_get_object(command);JsonNode *kind=json_object_get_member(record,"kind");if(!surface_text(kind,32,FALSE))return FALSE;
    g_autofree char *wire=json_to_string(command,FALSE);
    if(g_str_equal(json_node_get_string(kind),"acknowledge")) {
        gboolean accepted=native_preview_acknowledgements(target,root);
        if(accepted) {g_print("native-client-ack: %s\n",wire);fflush(stdout);}return accepted;
    }
    GError *error=NULL;g_autofree char *events=NULL;
    if(!warlock_client_producer_command(client_producer,json_node_get_string(identity),wire,&events,&error)) {client_failure(error);return FALSE;}
    g_print("native-client-command: %s\n",wire);fflush(stdout);
    if(!client_report_status(&error) || !client_publish(events,&error) || !preview_host_publish_receipts(&error)) {client_failure(error);return FALSE;}
    return TRUE;
}
static gboolean client_poll(gpointer unused) {
    (void)unused;
    if(shutting_down || preview_owner!=g_thread_self()) {client_poll_source=0;return G_SOURCE_REMOVE;}
    GError *error=NULL;g_autofree char *events=NULL;
    if(!client_producer) {
        guint64 publication,lease;
        if(!popup_ready || !surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_client_subject,&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)return G_SOURCE_CONTINUE;
        void *native=preview_host_native_transport(&error),*endpoint=NULL;
        if(!native) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        client_producer=qa_family_mode?warlock_family_producer_open(native,popup_view,qa_client_subject,publication,lease,&events,&endpoint,&error):warlock_client_producer_open(native,popup_view,qa_client_subject,publication,lease,&events,&endpoint,&error);
        if(!client_producer || !preview_host_attach_delivery(endpoint,&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        preview_host_set_endpoint(endpoint);preview_host_set_command_handler(client_commands);
        g_print("native-client-start: subject=%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " previewEligible=0\n",qa_client_subject,publication,lease);fflush(stdout);
        if(!client_publish(events,&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        return G_SOURCE_CONTINUE;
    }
    guint64 publication=0,lease=0;
    if(!surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_client_subject,&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)publication=lease=0;
    if(warlock_client_producer_empty(client_producer)) {
        g_print("native-client-complete: physical=0 journal=0 previewEligible=0\n");fflush(stdout);
        if(!warlock_client_producer_resume(client_producer,publication,lease,&events,&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        if(g_str_equal(events,"[]")) {client_poll_source=0;return G_SOURCE_REMOVE;}
        client_snapshot_written=FALSE;g_print("native-client-resume: publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " request=%" G_GUINT64_FORMAT "\n",publication,lease,warlock_client_producer_request(client_producer));fflush(stdout);
        if(!client_publish(events,&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        return G_SOURCE_CONTINUE;
    }
    if(!warlock_client_producer_poll(client_producer,publication,lease,&events,&error) || !client_publish(events,&error) || !preview_host_publish_receipts(&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
    if(!client_report_status(&error)) {client_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
    return G_SOURCE_CONTINUE;
}
static void client_wake(void) {
    guint64 publication,lease;
    if(shutting_down || client_poll_source || !qa_client_subject || !client_producer || !surface_popup_ready() || !popup_owner || !popup_owner->active ||
       !client_frame_target(surface_snapshot,qa_client_subject,&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease || lease<=warlock_client_producer_lease(client_producer))return;
    client_poll_source=g_timeout_add(50,client_poll,NULL);
}
static gboolean imported_report_status(GError **error) {
    g_autofree char *status=NULL;
    if(!warlock_imported_clients_status(imported_clients,&status,error))return FALSE;
    if(g_strcmp0(status,imported_last_status)) {g_free(imported_last_status);imported_last_status=g_strdup(status);g_print("native-imported-ownership: %s\n",status);fflush(stdout);}
    return TRUE;
}
static gboolean imported_image_report(JsonObject *object) {
    const char *const fields[]={"kind","images"};JsonNode *node=json_object_get_member(object,"images");
    if(!imported_clients || !surface_fields(object,fields,2) || !node || !JSON_NODE_HOLDS_ARRAY(node))return FALSE;
    JsonArray *images=json_node_get_array(node);if(json_array_get_length(images)!=2)return FALSE;
    GError *error=NULL;g_autofree char *first=NULL,*second=NULL;
    g_autofree char *a=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[0]);
    g_autofree char *b=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[1]);
    if(!warlock_imported_clients_uri(imported_clients,a,&first,&error) || !warlock_imported_clients_uri(imported_clients,b,&second,&error)) {g_clear_error(&error);return FALSE;}
    if(!*first || !*second)return FALSE;
    guint seen=0;
    for(guint i=0;i<2;i++) {
        JsonNode *row=json_array_get_element(images,i);if(!JSON_NODE_HOLDS_OBJECT(row))return FALSE;
        JsonObject *image=json_node_get_object(row);const char *const members[]={"uri","complete","naturalWidth","naturalHeight","width","height"};
        JsonNode *uri=json_object_get_member(image,"uri"),*complete=json_object_get_member(image,"complete");
        if(!surface_fields(image,members,6) || !surface_text(uri,256,FALSE) || !complete || !JSON_NODE_HOLDS_VALUE(complete) || json_node_get_value_type(complete)!=G_TYPE_BOOLEAN || !json_node_get_boolean(complete))return FALSE;
        const char *value=json_node_get_string(uri);guint bit=g_str_equal(value,first)?1:g_str_equal(value,second)?2:0;if(!bit || (seen&bit))return FALSE;seen|=bit;
        const char *sizes[]={"naturalWidth","naturalHeight","width","height"};
        for(guint k=0;k<4;k++) {JsonNode *size=json_object_get_member(image,sizes[k]);if(!size || !JSON_NODE_HOLDS_VALUE(size) || json_node_get_value_type(size)!=G_TYPE_INT64 || json_node_get_int(size)<=0 || json_node_get_int(size)>4096)return FALSE;}
    }
    if(seen!=3)return FALSE;
    g_autofree char *wire=json_to_string(node,FALSE);g_print("native-imported-image: %s\n",wire);fflush(stdout);
    if(qa_client_snapshot && !client_snapshot_pending && !client_snapshot_written) {
        if(imported_snapshot_ordinal==G_MAXUINT64)return FALSE;
        ClientSnapshot *snapshot=g_new0(ClientSnapshot,1);snapshot->request=++imported_snapshot_ordinal;
        snapshot->path=snapshot->request==1?g_strdup(qa_client_snapshot):g_strdup_printf("%s.request-%" G_GUINT64_FORMAT ".png",qa_client_snapshot,snapshot->request);
        client_snapshot_pending=TRUE;
        webkit_web_view_get_snapshot(popup_view,WEBKIT_SNAPSHOT_REGION_VISIBLE,WEBKIT_SNAPSHOT_OPTIONS_NONE,NULL,client_snapshot_complete,snapshot);
    }
    return TRUE;
}
/* json_node_copy references complex objects. Build a separate envelope so
 * narrowing one acknowledgement cannot mutate the array being iterated. */
static JsonNode *imported_command_row(JsonNode *root,JsonNode *row) {
    JsonObject *copy=json_object_new();JsonObject *original=json_node_get_object(root);
    JsonObjectIter iter;const gchar *name;JsonNode *value;
    json_object_iter_init(&iter,original);
    while(json_object_iter_next(&iter,&name,&value)) {
        if(!g_str_equal(name,"entries"))json_object_set_member(copy,name,json_node_copy(value));
    }
    JsonArray *entries=json_array_new();json_array_add_element(entries,json_node_copy(row));
    json_object_set_array_member(copy,"entries",entries);
    JsonNode *single=json_node_new(JSON_NODE_OBJECT);json_node_take_object(single,copy);return single;
}
static gboolean imported_commands(WebKitWebView *target,JsonNode *root) {
    if(preview_owner!=g_thread_self() || target!=popup_view || !imported_clients || !JSON_NODE_HOLDS_OBJECT(root))return FALSE;
    JsonArray *entries=json_object_get_array_member(json_node_get_object(root),"entries");if(!entries || json_array_get_length(entries)==0 || json_array_get_length(entries)>2)return FALSE;
    for(guint i=0;i<json_array_get_length(entries);i++) {
        JsonNode *row=json_array_get_element(entries,i);if(!JSON_NODE_HOLDS_OBJECT(row))return FALSE;
        JsonObject *entry=json_node_get_object(row);const char *const fields[]={"identity","commands"};JsonNode *identity=json_object_get_member(entry,"identity"),*commands=json_object_get_member(entry,"commands");
        if(!surface_fields(entry,fields,2) || !surface_text(identity,512,FALSE) || !commands || !JSON_NODE_HOLDS_ARRAY(commands))return FALSE;
        JsonArray *array=json_node_get_array(commands);if(json_array_get_length(array)!=1)return FALSE;JsonNode *command=json_array_get_element(array,0);if(!JSON_NODE_HOLDS_OBJECT(command))return FALSE;
        JsonNode *kind=json_object_get_member(json_node_get_object(command),"kind");if(!surface_text(kind,32,FALSE))return FALSE;
        g_autofree char *wire=json_to_string(command,FALSE);GError *error=NULL;
        if(g_str_equal(json_node_get_string(kind),"acknowledge")) {
            JsonNode *single=imported_command_row(root,row);
            gboolean accepted=native_preview_acknowledgements(target,single);json_node_unref(single);if(!accepted)return FALSE;
            g_print("native-imported-ack: %s\n",wire);fflush(stdout);
        }else {
            g_autofree char *events=NULL;
            if(!warlock_imported_clients_command(imported_clients,json_node_get_string(identity),wire,&events,&error)) {client_failure(error);return FALSE;}
            g_print("native-imported-command: %s\n",wire);fflush(stdout);
            if(!imported_report_status(&error) || !client_publish(events,&error) || !preview_host_publish_receipts(&error)) {client_failure(error);return FALSE;}
        }
    }
    return TRUE;
}
static gboolean imported_poll(gpointer unused) {
    (void)unused;
    if(shutting_down || preview_owner!=g_thread_self()) {imported_poll_source=0;return G_SOURCE_REMOVE;}
    GError *error=NULL;
    if(!imported_clients) {
        guint64 publication,lease;
        if(!popup_ready || !surface_popup_ready() || !popup_owner || !popup_owner->active ||
           !imported_frame_target(surface_snapshot,qa_import_subjects[0],qa_import_subjects[1],&publication,&lease) ||
           publication!=surface_gate.publication || lease!=surface_gate.lease)return G_SOURCE_CONTINUE;
        void *native=preview_host_native_transport(&error),*endpoint=NULL;g_autofree char *events=NULL;
        if(!native) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        imported_clients=warlock_imported_clients_open(native,popup_view,qa_import_subjects[0],qa_import_subjects[1],publication,lease,&events,&endpoint,&error);
        if(!imported_clients || !preview_host_attach_delivery(endpoint,&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        preview_host_set_endpoint(endpoint);preview_host_set_command_handler(imported_commands);
        g_print("native-imported-start: first=%" G_GUINT64_FORMAT " second=%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " previewEligible=0\n",qa_import_subjects[0],qa_import_subjects[1],publication,lease);fflush(stdout);
        if(!client_publish(events,&error) || !imported_report_status(&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        return G_SOURCE_CONTINUE;
    }
    if(warlock_imported_clients_empty(imported_clients)) {g_print("native-imported-complete: physical=0 journal=0 previewEligible=0\n");fflush(stdout);}
    for(guint i=0;i<2;i++) {
        guint64 publication=0,lease=0;
        if(!surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_import_subjects[i],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)publication=lease=0;
        g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[i]);g_autofree char *events=NULL,*resumed=NULL;
        if(!warlock_imported_clients_resume(imported_clients,identity,publication,lease,&resumed,&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        if(!g_str_equal(resumed,"[]")) {client_snapshot_written=FALSE;g_print("native-imported-resume: identity=%s publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",identity,publication,lease);fflush(stdout);}
        const guint64 retained_lease=warlock_imported_clients_lease(imported_clients,identity);
        if(!client_publish(resumed,&error) || !warlock_imported_clients_poll_at(imported_clients,identity,publication,lease,&events,&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
        if(warlock_imported_clients_lease(imported_clients,identity)>retained_lease) {
            /* A new presentation reuses original pixels and original expiry.
             * Reset only the QA specimen flag, never native job authority. */
            client_snapshot_written=FALSE;
            g_print("native-imported-presentation: identity=%s publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",identity,publication,lease);fflush(stdout);
        }
        if(!client_publish(events,&error) || !preview_host_publish_receipts(&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
    }
    if(!imported_report_status(&error)) {imported_poll_source=0;client_failure(error);return G_SOURCE_REMOVE;}
    if(warlock_imported_clients_empty(imported_clients)) {imported_poll_source=0;return G_SOURCE_REMOVE;}
    return G_SOURCE_CONTINUE;
}
static void imported_wake(void) {
    if(shutting_down || imported_poll_source || !imported_clients || !surface_popup_ready() || !popup_owner || !popup_owner->active)return;
    for(guint i=0;i<2;i++) {
        guint64 publication,lease;g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[i]);
        if(client_frame_target(surface_snapshot,qa_import_subjects[i],&publication,&lease) && publication==surface_gate.publication && lease==surface_gate.lease && lease>warlock_imported_clients_lease(imported_clients,identity)) {imported_poll_source=g_timeout_add(50,imported_poll,NULL);return;}
    }
}
static void test_client_target(void) {
    const char *wire="{\"surfaceProtocol\":2,\"publication\":\"1\",\"lease\":\"1\",\"mode\":\"picker\",\"status\":\"\",\"bar\":[],\"popup\":[{\"id\":\"family:2\",\"domId\":\"fixture\",\"label\":\"Client\",\"ariaLabel\":\"Client\",\"detail\":\"\",\"enabled\":true}]}";
    g_autoptr(JsonParser) parser=json_parser_new();g_assert_true(strict_json_load(parser,wire));JsonNode *node=json_parser_get_root(parser);guint64 pub,lease;
    g_assert_true(client_frame_target(node,2,&pub,&lease));g_assert_cmpuint(pub,==,1);g_assert_cmpuint(lease,==,1);
    g_assert_false(client_frame_target(node,3,&pub,&lease));g_assert_false(client_frame_target(node,0,&pub,&lease));
    JsonObject *frame=json_node_get_object(node),*control=json_node_get_object(json_array_get_element(json_object_get_array_member(frame,"popup"),0));
    json_object_set_boolean_member(control,"enabled",FALSE);g_assert_false(client_frame_target(node,2,&pub,&lease));json_object_set_boolean_member(control,"enabled",TRUE);
    json_object_set_string_member(frame,"mode","menu");g_assert_false(client_frame_target(node,2,&pub,&lease));json_object_set_string_member(frame,"mode","picker");
    json_object_set_string_member(frame,"lease","0");g_assert_false(client_frame_target(node,2,&pub,&lease));json_object_set_string_member(frame,"lease","1");
    json_object_set_string_member(frame,"publication","01");g_assert_false(client_frame_target(node,2,&pub,&lease));json_object_set_string_member(frame,"publication","1");
    json_object_set_string_member(frame,"extra","injected");g_assert_false(client_frame_target(node,2,&pub,&lease));
}
static void test_imported_target(void) {
    const char *wire="{\"surfaceProtocol\":2,\"publication\":\"1\",\"lease\":\"1\",\"mode\":\"picker\",\"status\":\"\",\"bar\":[],\"popup\":[{\"id\":\"family:2\",\"domId\":\"first\",\"label\":\"First\",\"ariaLabel\":\"First\",\"detail\":\"\",\"enabled\":true},{\"id\":\"family:3\",\"domId\":\"second\",\"label\":\"Second\",\"ariaLabel\":\"Second\",\"detail\":\"\",\"enabled\":true}]}";
    g_autoptr(JsonParser) parser=json_parser_new();g_assert_true(strict_json_load(parser,wire));JsonNode *node=json_parser_get_root(parser);guint64 publication,lease;
    g_assert_true(imported_frame_target(node,2,3,&publication,&lease));g_assert_cmpuint(publication,==,1);g_assert_cmpuint(lease,==,1);
    g_assert_false(imported_frame_target(node,2,2,&publication,&lease));g_assert_false(imported_frame_target(node,2,0,&publication,&lease));g_assert_false(imported_frame_target(node,2,4,&publication,&lease));
    JsonObject *frame=json_node_get_object(node);JsonObject *second=json_node_get_object(json_array_get_element(json_object_get_array_member(frame,"popup"),1));
    json_object_set_boolean_member(second,"enabled",FALSE);g_assert_false(imported_frame_target(node,2,3,&publication,&lease));json_object_set_boolean_member(second,"enabled",TRUE);
    json_object_set_string_member(frame,"mode","closed");g_assert_false(imported_frame_target(node,2,3,&publication,&lease));json_object_set_string_member(frame,"mode","picker");
    json_object_set_string_member(frame,"publication","01");g_assert_false(imported_frame_target(node,2,3,&publication,&lease));
}
static void test_imported_acknowledgement_isolation(void) {
    const char *wire="{\"kind\":\"preview-commands\",\"publication\":\"9\",\"lease\":\"1\",\"binding\":{\"session\":\"15\"},\"entries\":[{\"identity\":\"family:2\",\"commands\":[{\"kind\":\"acknowledge\",\"sequence\":\"5\"}]},{\"identity\":\"family:3\",\"commands\":[{\"kind\":\"acknowledge\",\"sequence\":\"6\"}]}]}";
    g_autoptr(JsonParser) parser=json_parser_new();g_assert_true(strict_json_load(parser,wire));
    JsonNode *root=json_parser_get_root(parser);JsonObject *object=json_node_get_object(root);
    JsonArray *entries=json_object_get_array_member(object,"entries");
    g_autofree char *before=json_to_string(root,FALSE);
    for(guint i=0;i<json_array_get_length(entries);i++) {
        JsonNode *row=json_array_get_element(entries,i);JsonNode *single=imported_command_row(root,row);
        JsonObject *copy=json_node_get_object(single);g_assert_true(copy!=object);
        g_assert_cmpuint(json_array_get_length(json_object_get_array_member(copy,"entries")),==,1);
        g_assert_cmpstr(json_object_get_string_member(copy,"publication"),==,"9");
        g_assert_cmpstr(json_object_get_string_member(copy,"lease"),==,"1");
        g_assert_true(json_node_equal(json_object_get_member(copy,"binding"),json_object_get_member(object,"binding")));
        g_assert_true(json_node_equal(json_array_get_element(json_object_get_array_member(copy,"entries"),0),row));
        json_node_unref(single);
        g_autofree char *after=json_to_string(root,FALSE);g_assert_cmpstr(before,==,after);
        g_assert_cmpuint(json_array_get_length(entries),==,2);
    }
    /* The single-row case also keeps its original envelope alive and intact. */
    JsonNode *one=imported_command_row(root,json_array_get_element(entries,0));
    JsonArray *rows=json_object_get_array_member(json_node_get_object(one),"entries");
    JsonNode *again=imported_command_row(one,json_array_get_element(rows,0));
    g_assert_true(json_node_get_object(one)!=json_node_get_object(again));json_node_unref(again);
    g_assert_cmpuint(json_array_get_length(rows),==,1);json_node_unref(one);
}
gboolean preview_host_enrollment(char **json,GError **error) {
    if(json)*json=NULL;
    if(preview_owner!=g_thread_self() || !preview_bootstrap || !json) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview enrollment owner unavailable");return FALSE;
    }
    return warlock_preview_bootstrap_enrollment(preview_bootstrap,json,error);
}
gboolean preview_host_source_scope(guint64 subject,char **json,GError **error) {
    if(json)*json=NULL;
    if(preview_owner!=g_thread_self() || !preview_bootstrap || !json) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview scope owner unavailable");return FALSE;
    }
    return warlock_preview_bootstrap_scope(preview_bootstrap,subject,json,error);
}
gboolean preview_host_client_source_scope(guint64 subject,char **json,GError **error) {
    if(json)*json=NULL;
    if(preview_owner!=g_thread_self() || !preview_bootstrap || !json) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview scope owner unavailable");return FALSE;
    }
    return warlock_preview_bootstrap_client_scope(preview_bootstrap,subject,json,error);
}
gboolean preview_host_attach_delivery(void *endpoint,GError **error) {
    if(preview_owner!=g_thread_self() || !preview_bootstrap || !popup_view || !WEBKIT_IS_WEB_VIEW(popup_view)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview receiver unavailable");return FALSE;
    }
    if(!warlock_preview_bootstrap_attach_delivery(preview_bootstrap,endpoint,popup_view,error))return FALSE;
    preview_host_set_command_handler(native_preview_acknowledgements);return TRUE;
}
void* preview_host_native_transport(GError **error) {
    if(preview_owner!=g_thread_self() || !preview_bootstrap) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native producer owner unavailable");return NULL;
    }
    return warlock_preview_bootstrap_native_transport(preview_bootstrap,error);
}
gboolean preview_host_publish_receipts(GError **error) {
    if(preview_owner!=g_thread_self() || !preview_bootstrap || !popup_view || !WEBKIT_IS_WEB_VIEW(popup_view)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Native preview receiver unavailable");return FALSE;
    }
    g_autofree char *wire=NULL;if(!warlock_preview_bootstrap_pending(preview_bootstrap,popup_view,&wire,error))return FALSE;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,wire,-1,error))return FALSE;
    JsonNode *root=json_parser_get_root(parser);if(!JSON_NODE_HOLDS_ARRAY(root))return FALSE;
    JsonArray *events=json_node_get_array(root);
    for(guint i=0;i<json_array_get_length(events);i++)surface_eval(popup_view,"receiveNativePreview",json_array_get_element(events,i));
    return TRUE;
}
static guint preview_test_calls;
static WebKitWebView *preview_test_view;
static gboolean preview_test_handler(WebKitWebView *target,JsonNode *root) {g_assert_true(target==preview_test_view);g_assert_true(JSON_NODE_HOLDS_OBJECT(root));preview_test_calls++;return TRUE;}
static void test_shared_preview_router(void) {
    int primary=0,popup=0,foreign=0,target=0;primary_manager=(WebKitUserContentManager*)&primary;popup_manager=(WebKitUserContentManager*)&popup;popup_view=(WebKitWebView*)&target;preview_test_view=popup_view;output_views=g_ptr_array_new();preview_owner=g_thread_self();
    const char *wire="{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"entries\":[{\"identity\":\"family:1\",\"commands\":[]}]}";
    preview_test_calls=0;preview_host_set_command_handler(preview_test_handler);
    shared_receive_text(primary_manager,wire);shared_receive_text((WebKitUserContentManager*)&foreign,wire);g_assert_cmpuint(preview_test_calls,==,0);
    shared_receive_text(popup_manager,wire);g_assert_cmpuint(preview_test_calls,==,1);
    const char *bad[]={"{\"kind\":\"preview-commands\",\"previewProtocol\":true,\"entries\":[]}","{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"entries\":[{},{}]}","{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"entries\":[{}],\"extra\":0}","{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"previewProtocol\":1,\"entries\":[{}]}"};
    for(guint i=0;i<G_N_ELEMENTS(bad);i++){shared_receive_text(popup_manager,bad[i]);}
    g_assert_cmpuint(preview_test_calls,==,1);
    g_autofree char *padding=g_strnfill(4097,' '),*oversized=g_strconcat(wire,padding,NULL);shared_receive_text(popup_manager,oversized);g_assert_cmpuint(preview_test_calls,==,1);
    preview_host_set_command_handler(NULL);shared_receive_text(popup_manager,wire);g_assert_cmpuint(preview_test_calls,==,1);
    g_ptr_array_unref(output_views);output_views=NULL;primary_manager=NULL;popup_manager=NULL;popup_view=NULL;preview_test_view=NULL;preview_owner=NULL;
}
static gboolean restart_requested;
static void recovery_restart(GtkButton *button,gpointer unused) {
    (void)button;(void)unused;
    if (!shutting_down || !renderer_failed || restart_requested || quit_requested) return;
    restart_requested=TRUE;g_print("recovery-restart-requested\n");fflush(stdout);gtk_main_quit();
}
static void recovery_allocate(GtkWidget *button,GtkAllocation *allocation,gpointer data) {
    OutputView *row=data;int x=0,y=0;GdkRectangle monitor;
    if (!qa_exit || !row->active || !gtk_widget_translate_coordinates(button,row->bar,0,0,&x,&y)) return;
    gdk_monitor_get_geometry(row->monitor,&monitor);
    g_print("recovery-control: id=%" G_GUINT64_FORMAT " x=%d y=%d w=%d h=%d\n",row->id,monitor.x+x,monitor.y+y,allocation->width,allocation->height);fflush(stdout);
}
static void recovery_show(void) {
    g_signal_handlers_disconnect_by_func(primary_manager,G_CALLBACK(shared_receive),NULL);
    g_signal_handlers_disconnect_by_func(popup_manager,G_CALLBACK(shared_receive),NULL);
    for (guint i=0;i<output_views->len;i++) {
        OutputView *row=g_ptr_array_index(output_views,i);row->ready=FALSE;
        g_signal_handlers_disconnect_by_func(row->manager,G_CALLBACK(shared_receive),NULL);
        gtk_container_remove(GTK_CONTAINER(row->bar),GTK_WIDGET(row->engine));row->engine=NULL;
        GtkWidget *box=gtk_box_new(GTK_ORIENTATION_HORIZONTAL,8);
        gtk_widget_set_margin_start(box,8);gtk_widget_set_margin_end(box,8);
        gtk_widget_set_margin_top(box,4);gtk_widget_set_margin_bottom(box,4);
        GtkWidget *label=gtk_label_new("Desktop display stopped.");gtk_label_set_ellipsize(GTK_LABEL(label),PANGO_ELLIPSIZE_END);
        GtkWidget *button=gtk_button_new_with_label("Restart");
        gtk_box_pack_start(GTK_BOX(box),label,FALSE,TRUE,0);gtk_box_pack_start(GTK_BOX(box),button,FALSE,FALSE,0);
        gtk_container_add(GTK_CONTAINER(row->bar),box);
        g_signal_connect(button,"clicked",G_CALLBACK(recovery_restart),NULL);
        g_signal_connect(button,"size-allocate",G_CALLBACK(recovery_allocate),row);
        gtk_widget_show_all(row->bar);
    }
    g_print("native-recovery-ready: views=%u backend-normal=%d\n",output_views->len,backend_done);fflush(stdout);
}
#ifndef ELM_SHARED_HOST_MAIN
#define ELM_SHARED_HOST_MAIN main
#endif
int ELM_SHARED_HOST_MAIN(int argc,char **argv) {
    if (argc==2 && g_str_equal(argv[1],"--self-test")) {
        g_test_init(&argc,&argv,NULL);g_test_add_func("/host/assets",test_assets);g_test_add_func("/host/request-schema",test_requests);g_test_add_func("/host/qa-report-control-bounds",test_bridge_bounds);g_test_add_func("/host/surface-atomic-preflight",test_surface_preflight);g_test_add_func("/host/surface-manager-isolation",test_surface_managers);g_test_add_func("/host/surface-acknowledgements",test_surface_acknowledgements);g_test_add_func("/host/monitor-index-boundaries",test_monitor_index);g_test_add_func("/host/popup-logical-dimensions",test_popup_dimensions);g_test_add_func("/host/shared-view-capabilities",test_view_capabilities);g_test_add_func("/host/shared-projection-capabilities",test_projection_capabilities);g_test_add_func("/host/shared-duplicate-fields",test_duplicate_fields);g_test_add_func("/host/shared-preview-router",test_shared_preview_router);g_test_add_func("/host/client-source-target",test_client_target);g_test_add_func("/host/imported-source-targets",test_imported_target);g_test_add_func("/host/imported-acknowledgement-isolation",test_imported_acknowledgement_isolation);return g_test_run();
    }
    for (int i=1;i<argc;i++) {
        if (g_str_equal(argv[i],"--assets") && i+1<argc) asset_dir=argv[++i];
        else if (g_str_equal(argv[i],"--authority-config") && i+1<argc) authority_config=argv[++i];
        else if (g_str_equal(argv[i],"--backend") && i+1<argc) backend_path=argv[++i];
        else if (g_str_equal(argv[i],"--qa-stay-open")) qa_stay=TRUE;
        else if (g_str_equal(argv[i],"--qa-exit-after-render")) qa_exit=TRUE;
        else if ((g_str_equal(argv[i],"--qa-preview-client") || g_str_equal(argv[i],"--qa-preview-family")) && i+1<argc) {
            if(qa_client_subject){g_printerr("One native source qualification owner required\n");return 2;}
            qa_family_mode=g_str_equal(argv[i],"--qa-preview-family");
            JsonNode *number=json_node_new(JSON_NODE_VALUE);json_node_set_string(number,argv[++i]);gboolean valid=surface_uint(number,&qa_client_subject) && qa_client_subject;json_node_unref(number);
            if(!valid) {g_printerr("Invalid native qualification subject\n");return 2;}
        }
        else if (g_str_equal(argv[i],"--qa-preview-imported") && i+2<argc) {
            for(guint n=0;n<2;n++) {JsonNode *number=json_node_new(JSON_NODE_VALUE);json_node_set_string(number,argv[++i]);gboolean valid=surface_uint(number,&qa_import_subjects[n]) && qa_import_subjects[n];json_node_unref(number);if(!valid) {g_printerr("Invalid shared native qualification subject\n");return 2;}}
            if(qa_import_subjects[0]==qa_import_subjects[1]) {g_printerr("Distinct shared native qualification subjects required\n");return 2;}
        }
        else if (g_str_equal(argv[i],"--qa-preview-snapshot") && i+1<argc) qa_client_snapshot=argv[++i];
        else if (!g_str_equal(argv[i],"--surface-experiment")) {g_printerr("Unknown shared-host argument\n");return 2;}
    }
    if (qa_client_subject && qa_import_subjects[0]) {g_printerr("One native qualification owner required\n");return 2;}
    if ((qa_client_subject || qa_import_subjects[0]) && (!qa_exit || !qa_stay)) {g_printerr("Client import requires explicit native qualification mode\n");return 2;}
    if(qa_client_snapshot && ((!qa_client_subject && !qa_import_subjects[0]) || !g_path_is_absolute(qa_client_snapshot))) {g_printerr("Private client snapshot requires native qualification mode and absolute output\n");return 2;}
    if (!asset_dir || !authority_config || !backend_path || !gtk_init_check(NULL,NULL) || !gtk_layer_is_supported()) return 2;
    if (!admission_open(authority_config)) {g_printerr("Host durable admission unavailable\n");return 2;}
    GError *preview_error=NULL;
    preview_bootstrap=warlock_preview_bootstrap_open(authority_config,&preview_error);
    if (!preview_bootstrap) {
        g_printerr("Host own native preview grant unavailable: %s\n",preview_error?preview_error->message:"startup admission failed");
        g_clear_error(&preview_error);admission_close();return 2;
    }
    preview_owner=g_thread_self();surface_experiment=TRUE;output_views=g_ptr_array_new();owned_display=gdk_display_get_default();
    shared_context=webkit_web_context_new_ephemeral();webkit_web_context_set_sandbox_enabled(shared_context,TRUE);webkit_web_context_register_uri_scheme(shared_context,"elm-shell",scheme,NULL,NULL);
    WebKitSecurityManager *security=webkit_web_context_get_security_manager(shared_context);webkit_security_manager_register_uri_scheme_as_local(security,"elm-shell");webkit_security_manager_register_uri_scheme_as_secure(security,"elm-shell");
    primary_manager=webkit_user_content_manager_new();manager_configure(primary_manager);
    view=WEBKIT_WEB_VIEW(g_object_new(WEBKIT_TYPE_WEB_VIEW,"web-context",shared_context,"user-content-manager",primary_manager,NULL));shared_settings=webkit_web_view_get_settings(view);
    webkit_settings_set_enable_developer_extras(shared_settings,FALSE);webkit_settings_set_enable_write_console_messages_to_stdout(shared_settings,qa_exit);webkit_settings_set_javascript_can_open_windows_automatically(shared_settings,FALSE);webkit_settings_set_enable_html5_local_storage(shared_settings,FALSE);webkit_settings_set_hardware_acceleration_policy(shared_settings,WEBKIT_HARDWARE_ACCELERATION_POLICY_ALWAYS);
    controller_window=gtk_window_new(GTK_WINDOW_TOPLEVEL);window=controller_window;gtk_container_add(GTK_CONTAINER(controller_window),GTK_WIDGET(view));
    g_signal_connect(view,"decide-policy",G_CALLBACK(policy),NULL);g_signal_connect(view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    popup_manager=webkit_user_content_manager_new();manager_configure(popup_manager);
    if(qa_client_snapshot || qa_import_subjects[0]) {WebKitUserScript *script=webkit_user_script_new("window.elmPreviewQA=true;",WEBKIT_USER_CONTENT_INJECT_TOP_FRAME,WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START,NULL,NULL);webkit_user_content_manager_add_script(popup_manager,script);webkit_user_script_unref(script);}
    popup_view=shared_child(popup_manager);g_object_ref_sink(popup_view);
    g_signal_connect(popup_view,"decide-policy",G_CALLBACK(policy),NULL);g_signal_connect(popup_view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    g_signal_connect(popup_view,"event",G_CALLBACK(shared_context_event),NULL);
    shared_input_cancel=shared_context_cancel;
    shared_popup_notice=shared_popup_notify;shared_frame_notice=shared_publish;shared_bar_focus_view=shared_focus_target;
    gulong add_handler=g_signal_connect(owned_display,"monitor-added",G_CALLBACK(shared_add),NULL),remove_handler=g_signal_connect(owned_display,"monitor-removed",G_CALLBACK(shared_remove),NULL);
    for (int i=0;i<gdk_display_get_n_monitors(owned_display);i++) shared_add(owned_display,gdk_display_get_monitor(owned_display,i),NULL);
    webkit_web_view_load_uri(popup_view,"elm-shell://app/popup.html");webkit_web_view_load_uri(view,"elm-shell://app/index.html");
    g_unix_signal_add(SIGTERM,quit_main,NULL);g_unix_signal_add(SIGINT,quit_main,NULL);
    if (qa_exit) quit_source=g_timeout_add_seconds(15,deadline,NULL);
    if (qa_client_subject) client_poll_source=g_timeout_add(50,client_poll,NULL);
    if (qa_import_subjects[0]) imported_poll_source=g_timeout_add(50,imported_poll,NULL);
    g_print("shared-host-start: views=%u controllers=1 backend-clients=1 sandbox=%d\n",output_views->len,webkit_web_context_get_sandbox_enabled(shared_context));fflush(stdout);
    gtk_main();shutting_down=TRUE;if (quit_source) g_source_remove(quit_source);if(client_poll_source) {g_source_remove(client_poll_source);client_poll_source=0;}if(imported_poll_source) {g_source_remove(imported_poll_source);imported_poll_source=0;}
    g_signal_handler_disconnect(owned_display,add_handler);g_signal_handler_disconnect(owned_display,remove_handler);
    if (popup_active) popup_hide();
    if (backend) {
        if (io_cancel) g_cancellable_cancel(io_cancel);
        if (backend_source) {g_source_remove(backend_source);backend_source=0;}
        gint64 write_until=g_get_monotonic_time()+500000;
        while (active_request && g_get_monotonic_time()<write_until) {while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000);}
        g_output_stream_close(g_subprocess_get_stdin_pipe(backend),NULL,NULL);
        gint64 until=g_get_monotonic_time()+2000000;
        while (!backend_done && g_get_monotonic_time()<until) {while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000);}
        if (!backend_done) {failed=TRUE;g_subprocess_force_exit(backend);g_subprocess_wait(backend,NULL,NULL);}
    }
    if (renderer_failed && !quit_requested) {recovery_show();gtk_main();}
    preview_host_set_command_handler(NULL);preview_host_set_endpoint(NULL);
    if(client_producer) {
        GError *error=NULL;if(!warlock_client_producer_close(client_producer,&error)) {g_printerr("Native client teardown incomplete: %s\n",error?error->message:"Outstanding owner");g_clear_error(&error);failed=TRUE;}else client_producer=NULL;
    }
    if(imported_clients) {
        GError *error=NULL;if(!warlock_imported_clients_close(imported_clients,&error)) {g_printerr("Native imported teardown incomplete: %s\n",error?error->message:"Outstanding owner");g_clear_error(&error);failed=TRUE;}else imported_clients=NULL;
    }
    g_clear_pointer(&client_last_status,g_free);
    g_clear_pointer(&imported_last_status,g_free);
    while (output_views->len) {OutputView *row=g_ptr_array_index(output_views,output_views->len-1);g_ptr_array_remove_index(output_views,output_views->len-1);view_retire(row);}
    g_queue_clear_full(&requests,g_free);gtk_widget_destroy(controller_window);g_object_unref(popup_view);g_object_unref(popup_manager);g_object_unref(primary_manager);g_object_unref(shared_context);g_ptr_array_unref(output_views);
    if (surface_snapshot) json_node_unref(surface_snapshot);
    if (pending_focus) json_node_unref(pending_focus);
    if (issued_focus) json_node_unref(issued_focus);
    if (bar_event) gdk_event_free(bar_event);
    gint64 until=g_get_monotonic_time()+500000;while (g_get_monotonic_time()<until) {while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(5000);}
    if(authority_binding){json_node_unref(authority_binding);authority_binding=NULL;}
    admission_close();
    /* Failed drain keeps the borrowed Native alive until process exit. */
    if(!client_producer && !imported_clients) {warlock_preview_bootstrap_free(preview_bootstrap);preview_bootstrap=NULL;}
    g_print("shared-host-exit: failure=%d rendered=%d\n",failed,reported);fflush(stdout);return restart_requested?3:failed || (qa_exit && !reported);
}
