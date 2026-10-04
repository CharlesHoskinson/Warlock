#define _GNU_SOURCE
#include <gtk/gtk.h>
#include <gtk-layer-shell.h>
#include <webkit2/webkit2.h>
#include <json-glib/json-glib.h>
#include <glib-unix.h>
#include <gio/gunixinputstream.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>

/* Authenticated experimental effect helper is selected by trusted launcher arguments, never by web content. */
static GtkWidget *window, *popover;
static gboolean surface_experiment;
static WebKitWebView *view;
static const char *asset_dir;
static gboolean qa_exit, reported, failed, shutting_down;
static guint quit_source;
static const char *authority_config, *backend_path;
static GSubprocess *backend;
static GString *backend_buffer;
static guint backend_source;
static GCancellable *io_cancel;
static char *active_request;
static GQueue requests = G_QUEUE_INIT;
static gboolean backend_ready, backend_done, gpu_info, qa_stay;
static void deliver(const char *text);
static void write_next(void);

static void backend_finished(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;GError *error=NULL;
    gboolean ok=g_subprocess_wait_finish(G_SUBPROCESS(object),result,&error);
    backend_done=TRUE;backend_ready=FALSE;g_queue_clear_full(&requests,g_free);
    if (error) { g_printerr("backend-wait-error\n");g_error_free(error); }
    g_print("backend-exit: waited=%d normal=%d code=%d\n",ok,g_subprocess_get_if_exited(backend),g_subprocess_get_if_exited(backend)?g_subprocess_get_exit_status(backend):-1);fflush(stdout);
    if (!shutting_down) deliver("{\"protocolVersion\":3,\"kind\":\"host-disconnected\"}");
}
static gboolean backend_read(gint fd,GIOCondition condition,gpointer unused) {
    (void)unused;
    char bytes[4096];ssize_t count=read(fd,bytes,sizeof(bytes));
    if (count<0 && (errno==EAGAIN || errno==EINTR)) return G_SOURCE_CONTINUE;
    if (count<=0) { backend_source=0;return G_SOURCE_REMOVE; }
    if (backend_buffer->len+(gsize)count>1048576) { failed=TRUE;gtk_main_quit();backend_source=0;return G_SOURCE_REMOVE; }
    g_string_append_len(backend_buffer,bytes,count);
    char *newline;
    while ((newline=memchr(backend_buffer->str,'\n',backend_buffer->len))) {
        gsize length=(gsize)(newline-backend_buffer->str);
        g_autofree char *frame=g_strndup(backend_buffer->str,length);
        g_autoptr(JsonParser) parser=json_parser_new();
        if (!json_parser_load_from_data(parser,frame,-1,NULL)) { failed=TRUE;gtk_main_quit();return G_SOURCE_CONTINUE; }
        if (qa_exit) { g_print("backend-frame: %s\n",frame);fflush(stdout); }
        deliver(frame);g_string_erase(backend_buffer,0,length+1);
    }
    (void)condition;return G_SOURCE_CONTINUE;
}
static void backend_start(void) {
    if (backend || gpu_info) return;
    GError *error=NULL;
    backend=g_subprocess_new(G_SUBPROCESS_FLAGS_STDIN_PIPE|G_SUBPROCESS_FLAGS_STDOUT_PIPE,&error,"/usr/bin/python3","-B",backend_path,authority_config,NULL);
    if (!backend) { failed=TRUE;g_printerr("backend-start-refused\n");g_clear_error(&error);gtk_main_quit();return; }
    backend_buffer=g_string_new(NULL);io_cancel=g_cancellable_new();backend_ready=TRUE;backend_done=FALSE;
    int fd=g_unix_input_stream_get_fd(G_UNIX_INPUT_STREAM(g_subprocess_get_stdout_pipe(backend)));
    fcntl(fd,F_SETFL,fcntl(fd,F_GETFL)|O_NONBLOCK);
    backend_source=g_unix_fd_add(fd,G_IO_IN|G_IO_HUP|G_IO_ERR,backend_read,NULL);
    g_subprocess_wait_async(backend,NULL,backend_finished,NULL);
}
static void backend_restart(void) {
    if (gpu_info || shutting_down) return;
    if (backend && (!backend_done || active_request)) {
        deliver("{\"protocolVersion\":3,\"kind\":\"host-disconnected\"}");return;
    }
    if (backend_source) { g_source_remove(backend_source);backend_source=0; }
    g_queue_clear_full(&requests,g_free);
    if (backend_buffer) { g_string_free(backend_buffer,TRUE);backend_buffer=NULL; }
    g_clear_object(&io_cancel);g_clear_object(&backend);
    backend_start();
}
static void wrote(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;GError *error=NULL;gsize count;
    gboolean ok=g_output_stream_write_all_finish(G_OUTPUT_STREAM(object),result,&count,&error);
    g_clear_pointer(&active_request,g_free);
    if (!ok) { backend_ready=FALSE;g_clear_error(&error);if (!shutting_down) deliver("{\"protocolVersion\":3,\"kind\":\"host-disconnected\"}"); }
    if (!shutting_down && ok) write_next();
}
static void write_next(void) {
    if (active_request || g_queue_is_empty(&requests) || !backend_ready || shutting_down) return;
    active_request=g_queue_pop_head(&requests);
    g_output_stream_write_all_async(g_subprocess_get_stdin_pipe(backend),active_request,strlen(active_request),G_PRIORITY_DEFAULT,io_cancel,wrote,NULL);
}


static const char *asset_name(const char *uri) {
    static const char *names[] = {"index.html", "elm.js", "adapter.js", "shell.css"};
    for (guint i=0; i<G_N_ELEMENTS(names); i++) {
        g_autofree char *expected=g_strconcat("elm-shell://app/",names[i],NULL);
        if (g_str_equal(uri,expected)) return names[i];
    }
    return NULL;
}

static const char *request_kind(JsonNode *root) {
    if (!root || !JSON_NODE_HOLDS_OBJECT(root)) return NULL;
    JsonObject *obj=json_node_get_object(root);
    JsonNode *version=json_object_get_member(obj,"protocolVersion");
    JsonNode *kind=json_object_get_member(obj,"kind");
    if (!version || json_node_get_value_type(version)!=G_TYPE_INT64 || json_node_get_int(version)!=3 ||
        !kind || json_node_get_value_type(kind)!=G_TYPE_STRING) return NULL;
    const char *value=json_node_get_string(kind);
    gboolean report=g_str_equal(value,"render-report") || g_str_equal(value,"projection-report");
    gboolean snapshot=g_str_equal(value,"projection-request") || g_str_equal(value,"catalog-request");
    gboolean launch=g_str_equal(value,"application-launch");
    gboolean effect=g_str_equal(value,"window-effect");
    if (!report && !snapshot && !effect && !launch && !g_str_equal(value,"host-ready") && !g_str_equal(value,"host-reconnect")) return NULL;
    g_autoptr(GList) members=json_object_get_members(obj);
    for (GList *p=members;p;p=p->next)
        if (!g_str_equal(p->data,"protocolVersion") && !g_str_equal(p->data,"kind") && !(report && g_str_equal(p->data,"body")) && !(snapshot && (g_str_equal(p->data,"binding") || g_str_equal(p->data,"requestId"))) && !(launch && (g_str_equal(p->data,"binding") || g_str_equal(p->data,"intent"))) && !(effect && (g_str_equal(p->data,"binding") || g_str_equal(p->data,"effectProtocol") || g_str_equal(p->data,"intent")))) return NULL;
    if (snapshot && json_object_get_size(obj)!=4) return NULL;
    if (launch && json_object_get_size(obj)!=4) return NULL;
    if (effect && json_object_get_size(obj)!=5) return NULL;
    if (!snapshot && !effect && !launch && !report && json_object_get_size(obj)!=2) return NULL;
    if (report && json_object_get_size(obj)!=3) return NULL;
    if (report) {
        JsonNode *body=json_object_get_member(obj,"body");
        if (!body || !JSON_NODE_HOLDS_OBJECT(body)) return NULL;
    }
    return value;
}

static gboolean quit_main(gpointer unused) {
    (void)unused;
    gtk_main_quit();
    return G_SOURCE_REMOVE;
}
static gboolean deadline(gpointer unused) {
    (void)unused;
    quit_source=0;
    failed=TRUE;
    g_printerr("QA render report deadline expired\n");
    gtk_main_quit();
    return G_SOURCE_REMOVE;
}
static void evaluate_done(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;
    GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    if (error) { g_printerr("Native delivery failed: %s\n",error->message); g_error_free(error); failed=TRUE; gtk_main_quit(); }
    if (value) g_object_unref(value);
}
static void deliver(const char *text) {
    if (shutting_down) return;
    g_autofree char *script=g_strdup_printf("window.receiveNative(%s);",text);
    webkit_web_view_evaluate_javascript(view,script,-1,NULL,"elm-shell://app/adapter.js",NULL,evaluate_done,NULL);
}
static void gpu_done(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    if (value) { g_autofree char *text=jsc_value_to_string(value);g_print("gpu-info: %s\n",text);g_object_unref(value);reported=TRUE;g_timeout_add(1000,quit_main,NULL); }
    if (error) { failed=TRUE;g_clear_error(&error);gtk_main_quit(); }
    fflush(stdout);
}
static void loaded(WebKitWebView *webview,WebKitLoadEvent event,gpointer unused) {
    (void)unused;
    if (gpu_info && event==WEBKIT_LOAD_FINISHED) webkit_web_view_evaluate_javascript(webview,"document.body.innerText",-1,NULL,NULL,NULL,gpu_done,NULL);
}
static void diagnostics_done(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    if (value) { g_autofree char *text=jsc_value_to_string(value);g_print("view-diagnostics: %s\n",text);g_object_unref(value); }
    if (error) { g_printerr("view-diagnostics-error: %s\n",error->message);g_error_free(error); }
    fflush(stdout);
}
static gboolean diagnostics(gpointer unused) {
    (void)unused;
    if (shutting_down) return G_SOURCE_REMOVE;
    const char *script="JSON.stringify({visibility:document.visibilityState,entries:document.querySelectorAll('[data-incarnation]').length,root:!!document.getElementById('shell-root'),receiver:typeof window.receiveNative,width:innerWidth,height:innerHeight})";
    webkit_web_view_evaluate_javascript(view,script,-1,NULL,NULL,NULL,diagnostics_done,NULL);return G_SOURCE_REMOVE;
}
static gboolean bridge_bound(gsize length,const char *kind,gboolean qa) {
    if (length<=4096) return TRUE;
    return qa && length<=1048576 && kind && (g_str_equal(kind,"projection-report") || g_str_equal(kind,"render-report"));
}
static void receive(WebKitUserContentManager *manager,WebKitJavascriptResult *result,gpointer unused) {
    (void)manager;(void)unused;
    if (shutting_down) return;
    JSCValue *value=webkit_javascript_result_get_js_value(result);
    if (!jsc_value_is_string(value)) { g_print("bridge-refused: type\n"); return; }
    g_autofree char *text=jsc_value_to_string(value);
    if (strlen(text)>(qa_exit?1048576:4096)) { g_print("bridge-refused: bound\n"); return; }
    g_autoptr(JsonParser) parser=json_parser_new();
    if (!json_parser_load_from_data(parser,text,-1,NULL)) { g_print("bridge-refused: malformed\n"); return; }
    const char *kind=request_kind(json_parser_get_root(parser));
    if (!kind) { g_print("bridge-refused: schema\n"); return; }
    if (!bridge_bound(strlen(text),kind,qa_exit)) { g_print("bridge-refused: control-bound\n"); return; }
    if (qa_exit && (g_str_equal(kind,"window-effect") || g_str_equal(kind,"application-launch") || g_str_equal(kind,"host-reconnect"))) { g_print("frontend-request: %s\n",text);fflush(stdout); }
    if (g_str_equal(kind,"host-ready")) backend_start();
    else if (g_str_equal(kind,"host-reconnect")) backend_restart();
    else if ((g_str_equal(kind,"projection-request") || g_str_equal(kind,"window-effect") || g_str_equal(kind,"catalog-request") || g_str_equal(kind,"application-launch"))) {
        if (!backend_ready || shutting_down) return;
        if (g_queue_get_length(&requests)>=16) { failed=TRUE;backend_ready=FALSE;deliver("{\"kind\":\"host-disconnected\"}");gtk_main_quit();return; }
        g_queue_push_tail(&requests,g_strconcat(text,"\n",NULL));write_next();
    } else {
        if (g_str_equal(kind,"projection-report")) { if (qa_exit) { g_print("projection-report: %s\n",text);fflush(stdout); } return; }
        if (reported) return;
        reported=TRUE;
        JsonObject *body=json_object_get_object_member(json_node_get_object(json_parser_get_root(parser)),"body");
        g_print("render-report: %s\n",text);
        JsonNode *families=json_object_get_member(body,"groups");
        JsonNode *disabled=json_object_get_member(body,"actionsDisabled");
        if (!families || json_node_get_value_type(families)!=G_TYPE_INT64 || json_node_get_int(families)<1 ||
            !disabled || json_node_get_value_type(disabled)!=G_TYPE_BOOLEAN || json_node_get_boolean(disabled)) failed=TRUE;
        if (!failed && quit_source) { g_source_remove(quit_source);quit_source=0; }
        if (qa_exit && !qa_stay) g_timeout_add(3000,quit_main,NULL);
    }
    fflush(stdout);
}
static void scheme(WebKitURISchemeRequest *request,gpointer unused) {
    (void)unused;
    const char *name=asset_name(webkit_uri_scheme_request_get_uri(request));
    if (!name) {
        g_autoptr(GError) error=g_error_new_literal(G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED,"Asset not allowlisted");
        webkit_uri_scheme_request_finish_error(request,error);return;
    }
    int dir=open(asset_dir,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
    int fd=dir<0?-1:openat(dir,name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if (dir>=0) close(dir);
    struct stat info;
    if (fd<0 || fstat(fd,&info)<0 || !S_ISREG(info.st_mode) || info.st_size<=0 || info.st_size>4*1024*1024) {
        if (fd>=0) close(fd);
        g_autoptr(GError) error=g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Invalid bundled asset");
        webkit_uri_scheme_request_finish_error(request,error);return;
    }
    gsize count=(gsize)info.st_size,offset=0;
    void *bytes=g_malloc(count);
    while (offset<count) { ssize_t got=read(fd,(char *)bytes+offset,count-offset); if (got<=0) break;offset+=(gsize)got; }
    close(fd);
    if (offset!=count) { g_free(bytes);g_autoptr(GError) error=g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Incomplete asset read");webkit_uri_scheme_request_finish_error(request,error);return; }
    GInputStream *stream=g_memory_input_stream_new_from_data(bytes,count,g_free);
    const char *mime=g_str_has_suffix(name,".html")?"text/html":g_str_has_suffix(name,".css")?"text/css":"application/javascript";
    webkit_uri_scheme_request_finish(request,stream,count,mime);g_object_unref(stream);
}
static gboolean policy(WebKitWebView *webview,WebKitPolicyDecision *decision,WebKitPolicyDecisionType type,gpointer unused) {
    (void)webview;(void)unused;
    if (type==WEBKIT_POLICY_DECISION_TYPE_NEW_WINDOW_ACTION) { webkit_policy_decision_ignore(decision);return TRUE; }
    if (type==WEBKIT_POLICY_DECISION_TYPE_NAVIGATION_ACTION) {
        WebKitNavigationAction *action=webkit_navigation_policy_decision_get_navigation_action(WEBKIT_NAVIGATION_POLICY_DECISION(decision));
        const char *uri=webkit_uri_request_get_uri(webkit_navigation_action_get_request(action));
        if (!g_str_equal(uri,gpu_info?"webkit://gpu":"elm-shell://app/index.html")) { webkit_policy_decision_ignore(decision);return TRUE; }
    }
    return FALSE;
}
static void terminated(WebKitWebView *webview,WebKitWebProcessTerminationReason reason,gpointer unused) {
    (void)webview;(void)unused;
    if (shutting_down) return;
    failed=TRUE;g_printerr("Web process terminated: %d\n",reason);gtk_main_quit();
}
static void popup_hide(void) {
    if (!gtk_widget_get_visible(popover)) return;
    gtk_grab_remove(popover);
    gdk_seat_ungrab(gdk_display_get_default_seat(gtk_widget_get_display(window)));
    gtk_widget_hide(popover);
    g_print("surface-popup-closed\n");fflush(stdout);
}
static gboolean popup_key(GtkWidget *widget,GdkEventKey *event,gpointer unused) {
    (void)widget;(void)unused;
    if (event->keyval==GDK_KEY_Escape) {popup_hide();return TRUE;}
    return FALSE;
}
static gboolean popup_button(GtkWidget *widget,GdkEventButton *event,gpointer unused) {
    (void)unused;
    GtkAllocation allocation;gtk_widget_get_allocation(widget,&allocation);
    if (event->x<0 || event->y<0 || event->x>=allocation.width || event->y>=allocation.height) {popup_hide();return TRUE;}
    return FALSE;
}
static gboolean popup_broken(GtkWidget *widget,GdkEventGrabBroken *event,gpointer unused) {
    (void)widget;(void)event;(void)unused;popup_hide();return FALSE;
}
static void popup_prepare(GdkSeat *seat,GdkWindow *native,gpointer unused) {
    (void)seat;(void)native;(void)unused;gtk_widget_show_all(popover);
}
static void popup_open(GtkButton *button,gpointer unused) {
    (void)unused;
    if (gtk_widget_get_visible(popover)) return;
    GtkAllocation allocation;gtk_widget_get_allocation(GTK_WIDGET(button),&allocation);
    GdkRectangle anchor={allocation.x,allocation.y,allocation.width,allocation.height};
    GdkWindow *native=gtk_widget_get_window(popover);
    gdk_window_move_to_rect(native,&anchor,GDK_GRAVITY_SOUTH,GDK_GRAVITY_NORTH,GDK_ANCHOR_SLIDE_X|GDK_ANCHOR_FLIP_Y|GDK_ANCHOR_SLIDE_Y,0,0);
    GdkEvent *event=gtk_get_current_event();
    GdkSeat *seat=gdk_display_get_default_seat(gtk_widget_get_display(window));
    GdkGrabStatus status=gdk_seat_grab(seat,native,GDK_SEAT_CAPABILITY_ALL,TRUE,NULL,event,popup_prepare,NULL);
    if (event) gdk_event_free(event);
    if (status!=GDK_GRAB_SUCCESS) {gtk_widget_hide(popover);g_print("surface-popup-refused: grab=%d\n",status);return;}
    gtk_grab_add(popover);gtk_widget_grab_focus(GTK_WIDGET(view));
    g_print("surface-popup-open\n");fflush(stdout);
}
static void test_assets(void) {
    g_assert_cmpstr(asset_name("elm-shell://app/index.html"),==,"index.html");
    const char *bad[]={"file:///etc/passwd","https://example.com/","elm-shell://app/../host.c","elm-shell://app/%2e%2e/host.c","elm-shell://other/index.html","elm-shell://app/index.html?extra=1"};
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) g_assert_null(asset_name(bad[i]));
}
static void test_bridge_bounds(void) {
    g_assert_true(bridge_bound(4096,"window-effect",FALSE));
    g_assert_false(bridge_bound(4097,"window-effect",TRUE));
    g_assert_false(bridge_bound(4097,"projection-request",TRUE));
    g_assert_false(bridge_bound(4097,"projection-report",FALSE));
    g_assert_true(bridge_bound(1048576,"projection-report",TRUE));
    g_assert_false(bridge_bound(1048577,"projection-report",TRUE));
    g_assert_false(bridge_bound(4097,"host-reconnect",TRUE));
    g_assert_false(bridge_bound(4097,NULL,TRUE));
}
static void test_requests(void) {
    const char *good[]={"{\"protocolVersion\":3,\"kind\":\"host-ready\"}","{\"protocolVersion\":3,\"kind\":\"projection-request\",\"binding\":{},\"requestId\":\"1\"}"};
    const char *bad[]={"[]","{}","{\"protocolVersion\":1,\"kind\":\"host-ready\"}","{\"protocolVersion\":3,\"kind\":\"execute\"}","{\"protocolVersion\":3,\"kind\":\"host-ready\",\"path\":\"/etc/passwd\"}","{\"protocolVersion\":3,\"kind\":\"snapshot-request\"}"};
    for (guint i=0;i<G_N_ELEMENTS(good);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,good[i],-1,NULL));g_assert_nonnull(request_kind(json_parser_get_root(p))); }
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,bad[i],-1,NULL));g_assert_null(request_kind(json_parser_get_root(p))); }
}

int main(int argc,char **argv) {
    if (argc==2 && g_str_equal(argv[1],"--self-test")) {
        g_test_init(&argc,&argv,NULL);g_test_add_func("/host/assets",test_assets);g_test_add_func("/host/request-schema",test_requests);g_test_add_func("/host/qa-report-control-bounds",test_bridge_bounds);return g_test_run();
    }
    gboolean layer=FALSE;
    for (int i=1;i<argc;i++) {
        if (g_str_equal(argv[i],"--assets") && i+1<argc) asset_dir=argv[++i];
        else if (g_str_equal(argv[i],"--authority-config") && i+1<argc) authority_config=argv[++i];
        else if (g_str_equal(argv[i],"--backend") && i+1<argc) backend_path=argv[++i];
        else if (g_str_equal(argv[i],"--gpu-info")) gpu_info=TRUE;
        else if (g_str_equal(argv[i],"--qa-stay-open")) qa_stay=TRUE;
        else if (g_str_equal(argv[i],"--layer")) layer=TRUE;
        else if (g_str_equal(argv[i],"--surface-experiment")) {surface_experiment=TRUE;layer=TRUE;}
        else if (g_str_equal(argv[i],"--qa-exit-after-render")) qa_exit=TRUE;
        else { g_printerr("Unknown argument\n");return 2; }
    }
    if (!gpu_info && (!authority_config || !backend_path)) { g_printerr("Authority config and reviewed backend required\n");return 2; }
    if (!asset_dir) { g_printerr("--assets requires a bundled asset directory\n");return 2; }
    if (!gtk_init_check(NULL,NULL)) { g_printerr("GTK display unavailable\n");return 2; }
    if (layer && !gtk_layer_is_supported()) { g_printerr("Layer shell unavailable\n");return 2; }
    WebKitWebContext *context=webkit_web_context_new_ephemeral();
    webkit_web_context_set_sandbox_enabled(context,TRUE);
    webkit_web_context_register_uri_scheme(context,"elm-shell",scheme,NULL,NULL);
    WebKitSecurityManager *security=webkit_web_context_get_security_manager(context);
    webkit_security_manager_register_uri_scheme_as_local(security,"elm-shell");
    webkit_security_manager_register_uri_scheme_as_secure(security,"elm-shell");
    WebKitUserContentManager *manager=webkit_user_content_manager_new();
    if (qa_exit) { WebKitUserScript *qa=webkit_user_script_new("window.elmHostQA=true;",WEBKIT_USER_CONTENT_INJECT_TOP_FRAME,WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START,NULL,NULL);webkit_user_content_manager_add_script(manager,qa);webkit_user_script_unref(qa); }
    g_signal_connect(manager,"script-message-received::native",G_CALLBACK(receive),NULL);
    if (!webkit_user_content_manager_register_script_message_handler(manager,"native")) return 2;
    view=WEBKIT_WEB_VIEW(g_object_new(WEBKIT_TYPE_WEB_VIEW,"web-context",context,"user-content-manager",manager,NULL));
    WebKitSettings *settings=webkit_web_view_get_settings(view);
    webkit_settings_set_enable_developer_extras(settings,FALSE);
    webkit_settings_set_enable_write_console_messages_to_stdout(settings,qa_exit);
    webkit_settings_set_javascript_can_open_windows_automatically(settings,FALSE);
    webkit_settings_set_enable_html5_local_storage(settings,FALSE);
    webkit_settings_set_hardware_acceleration_policy(settings,WEBKIT_HARDWARE_ACCELERATION_POLICY_ALWAYS);
    window=gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(window),"Elm windows");gtk_window_set_default_size(GTK_WINDOW(window),800,420);
    if (layer) {
        gtk_layer_init_for_window(GTK_WINDOW(window));gtk_layer_set_namespace(GTK_WINDOW(window),"elm-shell-recovery-v17");
        gtk_widget_set_size_request(window,-1,surface_experiment?48:420);gtk_window_resize(GTK_WINDOW(window),1,1);
        gtk_layer_set_layer(GTK_WINDOW(window),GTK_LAYER_SHELL_LAYER_TOP);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_TOP,TRUE);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_LEFT,TRUE);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_RIGHT,TRUE);
        gtk_layer_set_exclusive_zone(GTK_WINDOW(window),surface_experiment?48:0);
        gtk_layer_set_keyboard_mode(GTK_WINDOW(window),surface_experiment?GTK_LAYER_SHELL_KEYBOARD_MODE_NONE:GTK_LAYER_SHELL_KEYBOARD_MODE_ON_DEMAND);
    }
    g_signal_connect(window,"destroy",G_CALLBACK(gtk_main_quit),NULL);
    g_signal_connect(view,"load-changed",G_CALLBACK(loaded),NULL);
    g_signal_connect(view,"decide-policy",G_CALLBACK(policy),NULL);
    g_signal_connect(view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    GdkRGBA backdrop={0.09,0.125,0.16,1.0};webkit_web_view_set_background_color(view,&backdrop);
    if (surface_experiment) {
        GtkWidget *button=gtk_button_new_with_label("Elm shell surface experiment");
        gtk_container_add(GTK_CONTAINER(window),button);
        popover=gtk_window_new(GTK_WINDOW_POPUP);
        gtk_window_set_transient_for(GTK_WINDOW(popover),GTK_WINDOW(window));
        gtk_window_set_attached_to(GTK_WINDOW(popover),window);
        gtk_window_set_type_hint(GTK_WINDOW(popover),GDK_WINDOW_TYPE_HINT_POPUP_MENU);
        gtk_window_set_default_size(GTK_WINDOW(popover),700,420);
        gtk_widget_set_size_request(GTK_WIDGET(view),700,420);
        gtk_container_add(GTK_CONTAINER(popover),GTK_WIDGET(view));
        g_signal_connect(button,"clicked",G_CALLBACK(popup_open),NULL);
        g_signal_connect(popover,"key-press-event",G_CALLBACK(popup_key),NULL);
        g_signal_connect(popover,"button-press-event",G_CALLBACK(popup_button),NULL);
        g_signal_connect(popover,"grab-broken-event",G_CALLBACK(popup_broken),NULL);
        gtk_widget_realize(popover);
        gtk_widget_show_all(window);
        g_print("surface-policy: bar-exclusive=48 bar-keyboard=none popup-modal=1\n");
    } else {gtk_container_add(GTK_CONTAINER(window),GTK_WIDGET(view));gtk_widget_show_all(window);}
    if (layer) gtk_layer_try_force_commit(GTK_WINDOW(window));
    webkit_web_view_load_uri(view,gpu_info?"webkit://gpu":"elm-shell://app/index.html");
    g_unix_signal_add(SIGTERM,quit_main,NULL);g_unix_signal_add(SIGINT,quit_main,NULL);
    if (qa_exit) { quit_source=g_timeout_add_seconds(15,deadline,NULL);g_timeout_add_seconds(4,diagnostics,NULL); }
    g_print("host-start: layer=%d sandbox=%d acceleration-policy=always experimental-effects=1\n",layer,webkit_web_context_get_sandbox_enabled(context));fflush(stdout);
    gtk_main();
    if (quit_source) g_source_remove(quit_source);
    shutting_down=TRUE;
    g_signal_handlers_disconnect_by_func(window,G_CALLBACK(gtk_main_quit),NULL);
    if (backend) {
        if (io_cancel) g_cancellable_cancel(io_cancel);
        if (backend_source) { g_source_remove(backend_source);backend_source=0; }
        gint64 write_until=g_get_monotonic_time()+500000;
        while (active_request && g_get_monotonic_time()<write_until) { while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        g_output_stream_close(g_subprocess_get_stdin_pipe(backend),NULL,NULL);
        gint64 backend_until=g_get_monotonic_time()+2000000;
        while (!backend_done && g_get_monotonic_time()<backend_until) { while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        if (!backend_done) { failed=TRUE;g_subprocess_force_exit(backend);g_subprocess_wait(backend,NULL,NULL); }
    }
    g_queue_clear_full(&requests,g_free);
    if (popover) gtk_widget_destroy(popover);
    gtk_widget_destroy(window);g_object_unref(manager);g_object_unref(context);
    gint64 cleanup_until=g_get_monotonic_time()+500000;
    while (g_get_monotonic_time()<cleanup_until) { while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(5000); }
    g_print("host-exit: failure=%d rendered=%d\n",failed,reported);fflush(stdout);
    return failed || (qa_exit && !reported);
}
