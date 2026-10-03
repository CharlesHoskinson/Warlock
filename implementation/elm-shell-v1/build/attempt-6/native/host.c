#define _GNU_SOURCE
#include <gtk/gtk.h>
#include <gtk-layer-shell.h>
#include <webkit2/webkit2.h>
#include <json-glib/json-glib.h>
#include <glib-unix.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>

/* Fixture-only host. No compositor IPC, command executor or window effects. */
static GtkWidget *window;
static WebKitWebView *view;
static const char *asset_dir;
static gboolean qa_exit, reported, failed, shutting_down;
static guint quit_source;
static const char *fixture = "{\"protocolVersion\":1,\"kind\":\"fixture-snapshot\",\"source\":\"fixture\",\"epoch\":\"1\",\"windows\":[{\"incarnation\":\"9007199254740993\",\"label\":\"Brave fixture\",\"minimized\":false},{\"incarnation\":\"9007199254740994\",\"label\":\"Heroic fixture\",\"minimized\":true}]}";

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
    if (!version || json_node_get_value_type(version)!=G_TYPE_INT64 || json_node_get_int(version)!=1 ||
        !kind || json_node_get_value_type(kind)!=G_TYPE_STRING) return NULL;
    const char *value=json_node_get_string(kind);
    gboolean report=g_str_equal(value,"render-report");
    if (!report && !g_str_equal(value,"snapshot-request")) return NULL;
    g_autoptr(GList) members=json_object_get_members(obj);
    for (GList *p=members;p;p=p->next)
        if (!g_str_equal(p->data,"protocolVersion") && !g_str_equal(p->data,"kind") && !(report && g_str_equal(p->data,"body"))) return NULL;
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
static void receive(WebKitUserContentManager *manager,WebKitJavascriptResult *result,gpointer unused) {
    (void)manager;(void)unused;
    if (shutting_down) return;
    JSCValue *value=webkit_javascript_result_get_js_value(result);
    if (!jsc_value_is_string(value)) { g_print("bridge-refused: type\n"); return; }
    g_autofree char *text=jsc_value_to_string(value);
    if (strlen(text)>4096) { g_print("bridge-refused: bound\n"); return; }
    g_autoptr(JsonParser) parser=json_parser_new();
    if (!json_parser_load_from_data(parser,text,-1,NULL)) { g_print("bridge-refused: malformed\n"); return; }
    const char *kind=request_kind(json_parser_get_root(parser));
    if (!kind) { g_print("bridge-refused: schema\n"); return; }
    if (g_str_equal(kind,"snapshot-request")) {
        g_autofree char *script=g_strdup_printf("window.receiveNative(%s);",fixture);
        webkit_web_view_evaluate_javascript(view,script,-1,NULL,"elm-shell://app/adapter.js",NULL,evaluate_done,NULL);
        g_print("fixture-snapshot-delivered\n");
    } else {
        if (reported) return;
        reported=TRUE;
        JsonObject *body=json_object_get_object_member(json_node_get_object(json_parser_get_root(parser)),"body");
        g_print("render-report: %s\n",text);
        JsonNode *families=json_object_get_member(body,"families");
        JsonNode *disabled=json_object_get_member(body,"actionsDisabled");
        if (!families || json_node_get_value_type(families)!=G_TYPE_INT64 || json_node_get_int(families)!=2 ||
            !disabled || json_node_get_value_type(disabled)!=G_TYPE_BOOLEAN || !json_node_get_boolean(disabled)) failed=TRUE;
        if (qa_exit) g_timeout_add(3000,quit_main,NULL);
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
        if (!g_str_equal(uri,"elm-shell://app/index.html")) { webkit_policy_decision_ignore(decision);return TRUE; }
    }
    return FALSE;
}
static void terminated(WebKitWebView *webview,WebKitWebProcessTerminationReason reason,gpointer unused) {
    (void)webview;(void)unused;
    if (shutting_down) return;
    failed=TRUE;g_printerr("Web process terminated: %d\n",reason);gtk_main_quit();
}
static void test_assets(void) {
    g_assert_cmpstr(asset_name("elm-shell://app/index.html"),==,"index.html");
    const char *bad[]={"file:///etc/passwd","https://example.com/","elm-shell://app/../host.c","elm-shell://app/%2e%2e/host.c","elm-shell://other/index.html","elm-shell://app/index.html?extra=1"};
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) g_assert_null(asset_name(bad[i]));
}
static void test_requests(void) {
    const char *good[]={"{\"protocolVersion\":1,\"kind\":\"snapshot-request\"}","{\"protocolVersion\":1,\"kind\":\"render-report\",\"body\":{}}"};
    const char *bad[]={"[]","{}","{\"protocolVersion\":2,\"kind\":\"snapshot-request\"}","{\"protocolVersion\":1.0,\"kind\":\"snapshot-request\"}","{\"protocolVersion\":1,\"kind\":\"execute\"}","{\"protocolVersion\":1,\"kind\":\"snapshot-request\",\"path\":\"/etc/passwd\"}","{\"protocolVersion\":1,\"kind\":\"render-report\",\"body\":[]}"};
    for (guint i=0;i<G_N_ELEMENTS(good);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,good[i],-1,NULL));g_assert_nonnull(request_kind(json_parser_get_root(p))); }
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,bad[i],-1,NULL));g_assert_null(request_kind(json_parser_get_root(p))); }
}
int main(int argc,char **argv) {
    if (argc==2 && g_str_equal(argv[1],"--self-test")) {
        g_test_init(&argc,&argv,NULL);g_test_add_func("/host/assets",test_assets);g_test_add_func("/host/request-schema",test_requests);return g_test_run();
    }
    gboolean layer=FALSE;
    for (int i=1;i<argc;i++) {
        if (g_str_equal(argv[i],"--assets") && i+1<argc) asset_dir=argv[++i];
        else if (g_str_equal(argv[i],"--layer")) layer=TRUE;
        else if (g_str_equal(argv[i],"--qa-exit-after-render")) qa_exit=TRUE;
        else { g_printerr("Unknown argument\n");return 2; }
    }
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
    gtk_window_set_title(GTK_WINDOW(window),"Elm fixture host");gtk_window_set_default_size(GTK_WINDOW(window),800,420);
    if (layer) {
        gtk_layer_init_for_window(GTK_WINDOW(window));gtk_layer_set_namespace(GTK_WINDOW(window),"elm-shell-fixture-v1");
        gtk_layer_set_layer(GTK_WINDOW(window),GTK_LAYER_SHELL_LAYER_TOP);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_TOP,TRUE);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_LEFT,TRUE);
        gtk_layer_set_anchor(GTK_WINDOW(window),GTK_LAYER_SHELL_EDGE_RIGHT,TRUE);
        gtk_layer_set_exclusive_zone(GTK_WINDOW(window),0);
        gtk_layer_set_keyboard_mode(GTK_WINDOW(window),GTK_LAYER_SHELL_KEYBOARD_MODE_ON_DEMAND);
    }
    g_signal_connect(window,"destroy",G_CALLBACK(gtk_main_quit),NULL);
    g_signal_connect(view,"decide-policy",G_CALLBACK(policy),NULL);
    g_signal_connect(view,"web-process-terminated",G_CALLBACK(terminated),NULL);
    gtk_container_add(GTK_CONTAINER(window),GTK_WIDGET(view));gtk_widget_show_all(window);
    webkit_web_view_load_uri(view,"elm-shell://app/index.html");
    g_unix_signal_add(SIGTERM,quit_main,NULL);g_unix_signal_add(SIGINT,quit_main,NULL);
    if (qa_exit) quit_source=g_timeout_add_seconds(15,deadline,NULL);
    g_print("host-start: layer=%d sandbox=%d acceleration-policy=always fixture-only=1\n",layer,webkit_web_context_get_sandbox_enabled(context));fflush(stdout);
    gtk_main();
    if (quit_source) g_source_remove(quit_source);
    shutting_down=TRUE;
    g_signal_handlers_disconnect_by_func(window,G_CALLBACK(gtk_main_quit),NULL);
    gtk_widget_destroy(window);g_object_unref(manager);g_object_unref(context);
    gint64 cleanup_until=g_get_monotonic_time()+500000;
    while (g_get_monotonic_time()<cleanup_until) { while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(5000); }
    g_print("host-exit: failure=%d rendered=%d\n",failed,reported);fflush(stdout);
    return failed || (qa_exit && !reported);
}
