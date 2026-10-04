/* Reuse the qualified backend/surface machinery, with one new owning host. */
#define main inherited_main
#include "host.c"
#undef main

typedef struct {
    guint64 id,generation;
    GdkMonitor *monitor;
    GtkWidget *bar;
    WebKitWebView *engine;
    WebKitUserContentManager *manager;
    gulong geometry_handler;
    gboolean ready,active;
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
static void shared_commit(JsonNode *root) {
    g_autofree char *wire=NULL;
    if (!root || !JSON_NODE_HOLDS_OBJECT(root)) goto refuse;
    JsonObject *object=json_node_get_object(root);const char *const fields[]={"viewProtocol","kind","projection","requests","focus"};
    if (!surface_fields(object,fields,5) || json_node_get_value_type(json_object_get_member(object,"viewProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(object,"viewProtocol")!=1 || !surface_text(json_object_get_member(object,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(object,"kind"),"view-commit")) goto refuse;
    JsonNode *pn=json_object_get_member(object,"projection");if (!pn || !JSON_NODE_HOLDS_OBJECT(pn)) goto refuse;
    JsonObject *projection=json_node_get_object(pn);OutputView *next_popup=NULL,*next_focus=NULL;
    if (!projection_scopes(projection,&next_popup,&next_focus)) goto refuse;
    JsonNode *frame=json_object_get_member(projection,"frame"),*rn=json_object_get_member(object,"requests"),*fn=json_object_get_member(object,"focus");
    guint64 publication,lease;gboolean open;
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
    if (!surface_preflight(&candidate,translated,g_queue_get_length(&requests),active_request?1:0,backend_ready,&admitted)) {json_node_unref(translated);goto refuse;}
    if (popup_active && popup_owner!=next_popup) popup_hide();
    popup_owner=next_popup;focus_owner=next_focus;
    owned_monitor=popup_owner?popup_owner->monitor:NULL;window=popup_owner?popup_owner->bar:controller_window;
    wire=json_to_string(translated,FALSE);surface_receive(primary_manager,wire,translated);json_node_unref(translated);
    g_print("view-commit: popup=%" G_GUINT64_FORMAT " focus=%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT "\n",popup_owner?popup_owner->id:0,focus_owner?focus_owner->id:0,publication);fflush(stdout);return;
refuse:
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
static void shared_receive(WebKitUserContentManager *manager,WebKitJavascriptResult *result,gpointer unused) {
    (void)unused;if (shutting_down) return;
    JSCValue *value=webkit_javascript_result_get_js_value(result);if (!jsc_value_is_string(value)) return;
    g_autofree char *text=jsc_value_to_string(value);if (strlen(text)>1048576) return;
    g_autoptr(JsonParser) parser=json_parser_new();if (!strict_json_load(parser,text)) {g_print("view-refused: duplicate-or-malformed-json\n");fflush(stdout);return;}
    JsonNode *root=json_parser_get_root(parser);if (!JSON_NODE_HOLDS_OBJECT(root)) return;
    JsonObject *object=json_node_get_object(root);const char *kind=surface_text(json_object_get_member(object,"kind"),32,FALSE)?json_object_get_string_member(object,"kind"):NULL;
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
        shared_commit(root);return;
    }
    if (!origin && manager!=popup_manager) return;
    const char *const ready[]={"surfaceProtocol","kind"};
    if (strlen(text)<=4096 && surface_fields(object,ready,2) && json_node_get_value_type(json_object_get_member(object,"surfaceProtocol"))==G_TYPE_INT64 && json_object_get_int_member(object,"surfaceProtocol")==2 && kind && g_str_equal(kind,"presentation-ready")) {
        if (origin) {origin->ready=TRUE;shared_publish();} else {popup_ready=TRUE;surface_present();}return;
    }
    if (strlen(text)>4096) return;
    if (manager==popup_manager) {
        if (surface_ack(object,"presentation-applied",FALSE) || surface_ack(object,"focus-applied",TRUE)) return;
        if (surface_popup_ready()) shared_forward(popup_owner,root,TRUE);
    } else shared_forward(origin,root,FALSE);
}
static void shared_geometry(GObject *object,GParamSpec *property,gpointer data) {
    (void)property;OutputView *row=data;
    if (!row->active || object!=G_OBJECT(row->monitor) || shutting_down || row!=popup_owner || !popup_active) return;
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
    g_signal_connect(row->engine,"button-press-event",G_CALLBACK(retain_event),NULL);g_signal_connect(row->engine,"key-press-event",G_CALLBACK(retain_event),NULL);
    row->geometry_handler=g_signal_connect(monitor,"notify::geometry",G_CALLBACK(shared_geometry),row);
    g_ptr_array_add(output_views,row);gtk_widget_show_all(row->bar);gtk_layer_try_force_commit(GTK_WINDOW(row->bar));
    webkit_web_view_load_uri(row->engine,"elm-shell://app/bar.html");
    GdkRectangle geometry;gdk_monitor_get_geometry(monitor,&geometry);g_print("view-added: id=%" G_GUINT64_FORMAT " geometry=%d,%d,%d,%d\n",row->id,geometry.x,geometry.y,geometry.width,geometry.height);fflush(stdout);
    if (controller_ready) topology_advance();
}
static void view_retire(OutputView *row) {
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
int main(int argc,char **argv) {
    if (argc==2 && g_str_equal(argv[1],"--self-test")) {
        g_test_init(&argc,&argv,NULL);g_test_add_func("/host/assets",test_assets);g_test_add_func("/host/request-schema",test_requests);g_test_add_func("/host/qa-report-control-bounds",test_bridge_bounds);g_test_add_func("/host/surface-atomic-preflight",test_surface_preflight);g_test_add_func("/host/surface-manager-isolation",test_surface_managers);g_test_add_func("/host/surface-acknowledgements",test_surface_acknowledgements);g_test_add_func("/host/monitor-index-boundaries",test_monitor_index);g_test_add_func("/host/popup-logical-dimensions",test_popup_dimensions);g_test_add_func("/host/shared-view-capabilities",test_view_capabilities);g_test_add_func("/host/shared-projection-capabilities",test_projection_capabilities);g_test_add_func("/host/shared-duplicate-fields",test_duplicate_fields);return g_test_run();
    }
    for (int i=1;i<argc;i++) {
        if (g_str_equal(argv[i],"--assets") && i+1<argc) asset_dir=argv[++i];
        else if (g_str_equal(argv[i],"--authority-config") && i+1<argc) authority_config=argv[++i];
        else if (g_str_equal(argv[i],"--backend") && i+1<argc) backend_path=argv[++i];
        else if (g_str_equal(argv[i],"--qa-stay-open")) qa_stay=TRUE;
        else if (g_str_equal(argv[i],"--qa-exit-after-render")) qa_exit=TRUE;
        else if (!g_str_equal(argv[i],"--surface-experiment")) {g_printerr("Unknown shared-host argument\n");return 2;}
    }
    if (!asset_dir || !authority_config || !backend_path || !gtk_init_check(NULL,NULL) || !gtk_layer_is_supported()) return 2;
    surface_experiment=TRUE;output_views=g_ptr_array_new();owned_display=gdk_display_get_default();
    shared_context=webkit_web_context_new_ephemeral();webkit_web_context_set_sandbox_enabled(shared_context,TRUE);webkit_web_context_register_uri_scheme(shared_context,"elm-shell",scheme,NULL,NULL);
    WebKitSecurityManager *security=webkit_web_context_get_security_manager(shared_context);webkit_security_manager_register_uri_scheme_as_local(security,"elm-shell");webkit_security_manager_register_uri_scheme_as_secure(security,"elm-shell");
    primary_manager=webkit_user_content_manager_new();manager_configure(primary_manager);
    view=WEBKIT_WEB_VIEW(g_object_new(WEBKIT_TYPE_WEB_VIEW,"web-context",shared_context,"user-content-manager",primary_manager,NULL));shared_settings=webkit_web_view_get_settings(view);
    webkit_settings_set_enable_developer_extras(shared_settings,FALSE);webkit_settings_set_enable_write_console_messages_to_stdout(shared_settings,qa_exit);webkit_settings_set_javascript_can_open_windows_automatically(shared_settings,FALSE);webkit_settings_set_enable_html5_local_storage(shared_settings,FALSE);webkit_settings_set_hardware_acceleration_policy(shared_settings,WEBKIT_HARDWARE_ACCELERATION_POLICY_ALWAYS);
    controller_window=gtk_window_new(GTK_WINDOW_TOPLEVEL);window=controller_window;gtk_container_add(GTK_CONTAINER(controller_window),GTK_WIDGET(view));
    g_signal_connect(view,"decide-policy",G_CALLBACK(policy),NULL);g_signal_connect(view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    popup_manager=webkit_user_content_manager_new();manager_configure(popup_manager);
    popup_view=shared_child(popup_manager);g_object_ref_sink(popup_view);
    g_signal_connect(popup_view,"decide-policy",G_CALLBACK(policy),NULL);g_signal_connect(popup_view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    shared_popup_notice=shared_popup_notify;shared_frame_notice=shared_publish;shared_bar_focus_view=shared_focus_target;
    gulong add_handler=g_signal_connect(owned_display,"monitor-added",G_CALLBACK(shared_add),NULL),remove_handler=g_signal_connect(owned_display,"monitor-removed",G_CALLBACK(shared_remove),NULL);
    for (int i=0;i<gdk_display_get_n_monitors(owned_display);i++) shared_add(owned_display,gdk_display_get_monitor(owned_display,i),NULL);
    webkit_web_view_load_uri(popup_view,"elm-shell://app/popup.html");webkit_web_view_load_uri(view,"elm-shell://app/index.html");
    g_unix_signal_add(SIGTERM,quit_main,NULL);g_unix_signal_add(SIGINT,quit_main,NULL);
    if (qa_exit) quit_source=g_timeout_add_seconds(15,deadline,NULL);
    g_print("shared-host-start: views=%u controllers=1 backend-clients=1 sandbox=%d\n",output_views->len,webkit_web_context_get_sandbox_enabled(shared_context));fflush(stdout);
    gtk_main();shutting_down=TRUE;if (quit_source) g_source_remove(quit_source);
    g_signal_handler_disconnect(owned_display,add_handler);g_signal_handler_disconnect(owned_display,remove_handler);
    if (popup_active) popup_hide();
    while (output_views->len) {OutputView *row=g_ptr_array_index(output_views,output_views->len-1);g_ptr_array_remove_index(output_views,output_views->len-1);view_retire(row);}
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
    g_queue_clear_full(&requests,g_free);gtk_widget_destroy(controller_window);g_object_unref(popup_view);g_object_unref(popup_manager);g_object_unref(primary_manager);g_object_unref(shared_context);g_ptr_array_unref(output_views);
    if (surface_snapshot) json_node_unref(surface_snapshot);
    if (pending_focus) json_node_unref(pending_focus);
    if (issued_focus) json_node_unref(issued_focus);
    if (bar_event) gdk_event_free(bar_event);
    gint64 until=g_get_monotonic_time()+500000;while (g_get_monotonic_time()<until) {while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(5000);}
    g_print("shared-host-exit: failure=%d rendered=%d\n",failed,reported);fflush(stdout);return failed || (qa_exit && !reported);
}
