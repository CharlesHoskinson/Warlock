#define _GNU_SOURCE
#include <gtk/gtk.h>
#include <gtk-layer-shell.h>
#include <gdk/gdkwayland.h>
#include <webkit2/webkit2.h>
#include <json-glib/json-glib.h>
#include <glib-unix.h>
#include <gio/gunixinputstream.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>
#include "surface.h"
#include "host-journal.h"
#include "preview-uri-api.h"
#include "preview-integration.h"
static void *native_preview_endpoint;
#include "preview-control.h"
static PreviewControl preview_controls;
static GThread *preview_owner;
static PreviewCommandHandler native_preview_handler;
void preview_host_set_endpoint(void *endpoint) { if (preview_owner==g_thread_self()) native_preview_endpoint=endpoint; }
void preview_host_set_command_handler(PreviewCommandHandler handler) { if (preview_owner==g_thread_self()) native_preview_handler=handler; }


/* Authenticated experimental effect helper is selected by trusted launcher arguments, never by web content. */
static GtkWidget *window, *popover, *retired_popup;
typedef struct {GObject *target;gulong handler;} PopupSignal;
static PopupSignal popup_signals[6];
static guint popup_signal_count;
static gboolean popup_events_drained=TRUE;
static gboolean surface_experiment, popup_active;
static gboolean qa_exit, reported, failed, shutting_down, renderer_failed, quit_requested;
static gboolean qa_controlled_preview;
static void (*controlled_surface_notice)(JsonNode*);
static GdkMonitor *owned_monitor;
static GdkDisplay *owned_display;
static gulong monitor_removed_handler,monitor_geometry_handler;
static gboolean output_retired;
static int monitor_index=-1;
static WebKitWebView *view, *popup_view;
WebKitWebView *preview_host_popup_view(void) { return preview_owner==g_thread_self() ? popup_view : NULL; }
static WebKitUserContentManager *primary_manager, *popup_manager;
static SurfaceGate surface_gate;
static JsonNode *surface_snapshot;
static gboolean popup_ready, grab_ready, keyboard_ready;
typedef struct {guint64 lease;GtkWidget *owner;} PopupScope;
static guint64 configured_lease, applied_publication, applied_lease;
static JsonNode *pending_focus, *issued_focus;
static guint64 issued_publication, issued_lease;
static void surface_focus_maybe(void);
static GdkEvent *bar_event;
static void (*shared_input_cancel)(void);
static GdkRectangle context_anchor;
static gboolean has_context_anchor,shared_preserve_context_anchor;
typedef enum { SURFACE_IGNORED, SURFACE_PREFLIGHT_UNSENT, SURFACE_ADMITTED, SURFACE_UNCERTAIN } SurfaceDisposition;
static SurfaceDisposition surface_receive(WebKitUserContentManager *,const char *,JsonNode *);
static void popup_hide(void);
static void popup_disconnect(void) {
    while (popup_signal_count) {
        PopupSignal signal=popup_signals[--popup_signal_count];
        if (g_signal_handler_is_connected(signal.target,signal.handler))
            g_signal_handler_disconnect(signal.target,signal.handler);
        g_object_unref(signal.target);
    }
}
typedef struct {
    gpointer context;
    gpointer (*take)(gpointer);
    gboolean (*retired)(gpointer,gpointer);
    void (*restore)(gpointer,gpointer);
    GDestroyNotify release;
} PopupEventQueue;
static gboolean popup_retire_events(const PopupEventQueue *queue,guint limit,guint *dropped) {
    GPtrArray *others=g_ptr_array_new_with_free_func(queue->release);
    gboolean drained=FALSE;*dropped=0;
    /* No GTK/main-loop dispatch: discard only queued events for the closed
     * popup tree, retaining every other event in its original order. A flood
     * refuses remapping rather than admitting old input into a fresh lease. */
    for (guint count=0;count<limit;count++) {
        gpointer event=queue->take(queue->context);
        if (!event) {drained=TRUE;break;}
        if (queue->retired(queue->context,event)) {queue->release(event);(*dropped)++;}
        else g_ptr_array_add(others,event);
    }
    for (guint i=others->len;i>0;i--) queue->restore(queue->context,g_ptr_array_index(others,i-1));
    g_ptr_array_unref(others);
    return drained;
}
typedef struct {GdkDisplay *display;GdkWindow *retired;} PopupNativeQueue;
static gpointer popup_native_take(gpointer context) {
    return gdk_display_get_event(((PopupNativeQueue *)context)->display);
}
static gboolean popup_native_retired(gpointer context,gpointer event) {
    GdkWindow *retired=((PopupNativeQueue *)context)->retired,*source=gdk_event_get_window(event);
    return source && (source==retired || gdk_window_get_toplevel(source)==retired);
}
static void popup_native_restore(gpointer context,gpointer event) {
    gdk_display_put_event(((PopupNativeQueue *)context)->display,event);
}
static gboolean popup_drain_retired(GdkDisplay *display,GdkWindow *retired) {
    PopupNativeQueue native={display,retired};guint dropped;
    PopupEventQueue queue={&native,popup_native_take,popup_native_retired,popup_native_restore,(GDestroyNotify)gdk_event_free};
    gboolean drained=popup_retire_events(&queue,4096,&dropped);
    if (qa_exit) {g_print("surface-retired-input: lease=%" G_GUINT64_FORMAT " dropped=%u drained=%d\n",surface_gate.lease,dropped,drained);fflush(stdout);}
    return drained;
}
static void popup_release_retired(void) {
    if (!retired_popup) return;
    GtkWidget *retired=retired_popup;retired_popup=NULL;
    if (gtk_widget_get_parent(GTK_WIDGET(popup_view))==retired)
        gtk_container_remove(GTK_CONTAINER(retired),GTK_WIDGET(popup_view));
    gtk_widget_destroy(retired);
}
/* Private qualification can retain the same renderer after normal wrapper
 * destruction. No product callback is installed by the inherited host. */
static void (*qa_popup_retired)(void);
static void (*shared_popup_notice)(const char *,guint64);
static void (*shared_frame_notice)(void);
static WebKitWebView *(*shared_bar_focus_view)(void);
static const char *asset_dir;
/* Optional owning shared-host hook; standalone legacy behavior stays exact. */
static gboolean (*renderer_failure_drain_hook)(void);
static guint quit_source;
static const char *authority_config, *backend_path;
static GSubprocess *backend;
static JsonNode *authority_binding;
static GString *backend_buffer;
static guint backend_source;
static GCancellable *io_cancel;
static char *active_request;
static GQueue requests = G_QUEUE_INIT;
static gboolean backend_ready, backend_done, gpu_info, qa_stay;
#include "host-fault.h"
static void deliver(const char *text);
static void write_next(void);

static void backend_finished(GObject *object,GAsyncResult *result,gpointer unused) {
    (void)unused;GError *error=NULL;
    gboolean ok=g_subprocess_wait_finish(G_SUBPROCESS(object),result,&error);
    if(authority_binding){json_node_unref(authority_binding);authority_binding=NULL;}
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
        JsonNode *root=json_parser_get_root(parser);
        if (JSON_NODE_HOLDS_OBJECT(root)) {
            JsonObject *object=json_node_get_object(root);JsonNode *kind=json_object_get_member(object,"kind");
            if(surface_text(kind,32,FALSE) && g_str_equal(json_node_get_string(kind),"host-admission-settled")) {
                const char *const fields[]={"protocolVersion","kind","binding","record"};
                JsonNode *pv=json_object_get_member(object,"protocolVersion"),*bound=json_object_get_member(object,"binding");
                gboolean ok=surface_fields(object,fields,4) && json_node_get_value_type(pv)==G_TYPE_INT64 && json_node_get_int(pv)==3 && authority_binding && json_node_equal(bound,authority_binding) && admission_retire(json_object_get_member(object,"record"));
                if(!ok){
                    backend_ready=FALSE;deliver("{\"protocolVersion\":3,\"kind\":\"host-recovery-failed\",\"reason\":\"unavailable\"}");
                    g_cancellable_cancel(io_cancel);g_subprocess_send_signal(backend,SIGTERM);g_string_truncate(backend_buffer,0);backend_source=0;return G_SOURCE_REMOVE;
                }
                g_string_erase(backend_buffer,0,length+1);continue;
            }
            if(surface_text(kind,32,FALSE) && g_str_equal(json_node_get_string(kind),"attached")) {
                JsonNode *bound=json_object_get_member(object,"binding");
                const char *const fields[]={"lifetime","session","frontend"};
                if(!bound || !JSON_NODE_HOLDS_OBJECT(bound) || !surface_fields(json_node_get_object(bound),fields,3)){failed=TRUE;gtk_main_quit();return G_SOURCE_CONTINUE;}
                for(guint i=0;i<3;i++)if(!admission_positive(json_node_get_object(bound),fields[i])){failed=TRUE;gtk_main_quit();return G_SOURCE_CONTINUE;}
                if(!admission_bind(bound)){
                    backend_ready=FALSE;
                    deliver("{\"protocolVersion\":3,\"kind\":\"host-recovery-failed\",\"reason\":\"unavailable\"}");
                    g_cancellable_cancel(io_cancel);g_subprocess_send_signal(backend,SIGTERM);
                    g_string_erase(backend_buffer,0,length+1);continue;
                }
                if(authority_binding)json_node_unref(authority_binding);
                authority_binding=json_node_copy(bound);
            }
        }
        if (qa_exit) { g_print("backend-frame: %s\n",frame);fflush(stdout); }
        deliver(frame);g_string_erase(backend_buffer,0,length+1);
    }
    (void)condition;return G_SOURCE_CONTINUE;
}
static void backend_start(void) {
    if (shutting_down || output_retired) return;
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
    if(host_fault_hold(backend,g_queue_peek_head(&requests)))return;
    active_request=g_queue_pop_head(&requests);
    g_output_stream_write_all_async(g_subprocess_get_stdin_pipe(backend),active_request,strlen(active_request),G_PRIORITY_DEFAULT,io_cancel,wrote,NULL);
}


static const char *asset_name(const char *uri) {
    static const char *names[] = {"index.html", "elm.js", "adapter.js", "shell.css", "popup.html", "popup.js", "popup-adapter.js", "bar.html", "bar.js", "bar-adapter.js", "context.js", "activation.js", "appearance.js", "controlled-popup.html", "controlled-popup-adapter.js", "native-preview-admission.js", "native-visual-renderer.js"};
    for (guint i=0; i<G_N_ELEMENTS(names); i++) {
        g_autofree char *expected=g_strconcat("elm-shell://app/",names[i],NULL);
        if (g_str_equal(uri,expected)) return names[i];
    }
    return NULL;
}

/* Observation carrier only. Semantic identity/counter validation remains in
 * the authenticated broker; raw duplicate fields must survive no JSON loss. */
static gboolean geometry_kind(const char *kind) {
    return kind && (g_str_equal(kind,"geometry-attach") || g_str_equal(kind,"geometry-facts-request"));
}
static gboolean observation_kind(const char *kind) {
    return geometry_kind(kind) || (kind && g_str_equal(kind,"reconciliation-ready"));
}
static gboolean geometry_contains(JsonNode *node) {
    if (!node || !JSON_NODE_HOLDS_OBJECT(node)) return FALSE;
    JsonObject *o=json_node_get_object(node);JsonNode *kind=json_object_get_member(o,"kind");
    if (kind && json_node_get_value_type(kind)==G_TYPE_STRING && observation_kind(json_node_get_string(kind))) return TRUE;
    JsonNode *requests_node=json_object_get_member(o,"requests");
    if (!requests_node || !JSON_NODE_HOLDS_ARRAY(requests_node)) return FALSE;
    JsonArray *items=json_node_get_array(requests_node);
    for (guint i=0;i<json_array_get_length(items);i++) {
        JsonNode *item=json_array_get_element(items,i);
        if (!JSON_NODE_HOLDS_OBJECT(item)) continue;
        JsonNode *k=json_object_get_member(json_node_get_object(item),"kind");
        if (k && json_node_get_value_type(k)==G_TYPE_STRING && observation_kind(json_node_get_string(k))) return TRUE;
    }
    return FALSE;
}
typedef struct {GHashTable *members;gboolean duplicate;} GeometryParse;
static void geometry_member(JsonParser *parser,JsonObject *object,const gchar *name,gpointer data) {
    (void)parser;GeometryParse *state=data;
    char *key=g_strdup_printf("%p:%s",(void *)object,name);
    if (g_hash_table_contains(state->members,key)) {state->duplicate=TRUE;g_free(key);}
    else g_hash_table_add(state->members,key);
}
static gboolean geometry_parse(JsonParser *parser,const char *text) {
    GeometryParse state={g_hash_table_new_full(g_str_hash,g_str_equal,g_free,NULL),FALSE};
    gulong handler=g_signal_connect(parser,"object-member",G_CALLBACK(geometry_member),&state);
    gboolean parsed=json_parser_load_from_data(parser,text,-1,NULL);
    g_signal_handler_disconnect(parser,handler);
    gboolean accepted=parsed && !(state.duplicate && geometry_contains(json_parser_get_root(parser)));
    g_hash_table_unref(state.members);return accepted;
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
    gboolean snapshot=g_str_equal(value,"projection-request") || g_str_equal(value,"catalog-request") || g_str_equal(value,"activation-history-request");
    gboolean launch=g_str_equal(value,"application-launch");
    gboolean effect=g_str_equal(value,"window-effect");
    if(g_str_equal(value,"motion-preferences-request") || g_str_equal(value,"motion-preferences-write")) {
        const gboolean write=g_str_equal(value,"motion-preferences-write");const char *const fields[]={"protocolVersion","kind","binding","requestId","proposal"};guint64 request;
        JsonNode *bound=json_object_get_member(obj,"binding");
        if(!surface_fields(obj,fields,write?5:4) || !bound || !JSON_NODE_HOLDS_OBJECT(bound) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(write) {
            JsonNode *node=json_object_get_member(obj,"proposal");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
            JsonObject *proposal=json_node_get_object(node);const char *const names[]={"schema","revision","override"};guint64 revision;
            JsonNode *schema=json_object_get_member(proposal,"schema"),*override=json_object_get_member(proposal,"override");
            if(!surface_fields(proposal,names,3) || !schema || json_node_get_value_type(schema)!=G_TYPE_INT64 || json_node_get_int(schema)!=1 || !surface_uint(json_object_get_member(proposal,"revision"),&revision) || !revision || !override)return NULL;
            if(!JSON_NODE_HOLDS_NULL(override) && (!surface_text(override,16,FALSE) || (!g_str_equal(json_node_get_string(override),"reduced") && !g_str_equal(json_node_get_string(override),"full"))))return NULL;
        }
        return value;
    }
    if(g_str_equal(value,"motion-profile-set")) {
        const char *const names[]={"protocolVersion","kind","binding","requestId","profile"};guint64 request;
        JsonNode *profile=json_object_get_member(obj,"profile"),*bound=json_object_get_member(obj,"binding");
        if(!surface_fields(obj,names,5) || !bound || !JSON_NODE_HOLDS_OBJECT(bound) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request || !surface_text(profile,16,FALSE) || (!g_str_equal(json_node_get_string(profile),"reduced") && !g_str_equal(json_node_get_string(profile),"full")))return NULL;
        return value;
    }
    if(g_str_equal(value,"switcher-selection-request") || g_str_equal(value,"switcher-cancel-request")) {
        gboolean selection=g_str_equal(value,"switcher-selection-request");
        const char *const names[]={"protocolVersion","kind","binding","requestId","chord","root"};
        guint64 request,chord,root;
        if(!surface_fields(obj,names,selection?6:5) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request || !surface_uint(json_object_get_member(obj,"chord"),&chord) || !chord || (selection && (!surface_uint(json_object_get_member(obj,"root"),&root) || !root)))return NULL;
        return value;
    }
    if(g_str_equal(value,"jump-list-request") || g_str_equal(value,"jump-list-effect")) {
        gboolean dispatch=g_str_equal(value,"jump-list-effect");guint64 request;
        const char *const fields[]={"protocolVersion","kind","binding","requestId",dispatch?"intent":"entry"};
        if(!surface_fields(obj,fields,5) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(dispatch) {
            JsonNode *node=json_object_get_member(obj,"intent");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
            JsonObject *intent=json_node_get_object(node);const char *const names[]={"service","revision","entry","action"};guint64 service,revision;
            if(!surface_fields(intent,names,4) || !surface_uint(json_object_get_member(intent,"service"),&service) || !service || !surface_uint(json_object_get_member(intent,"revision"),&revision) || !revision || !surface_text(json_object_get_member(intent,"entry"),1024,FALSE) || g_utf8_strlen(json_object_get_string_member(intent,"entry"),-1)>256 || !surface_text(json_object_get_member(intent,"action"),1024,FALSE) || g_utf8_strlen(json_object_get_string_member(intent,"action"),-1)>256)return NULL;
        } else if(!surface_text(json_object_get_member(obj,"entry"),1024,FALSE) || g_utf8_strlen(json_object_get_string_member(obj,"entry"),-1)>256)return NULL;
        return value;
    }
    if(g_str_equal(value,"files-request") || g_str_equal(value,"files-open")) {
        gboolean navigation=g_str_equal(value,"files-open");guint64 request;
        const char *const fields[]={"protocolVersion","kind","binding","requestId","intent"};
        if(!surface_fields(obj,fields,navigation?5:4) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(navigation) {
            JsonNode *node=json_object_get_member(obj,"intent");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
            JsonObject *intent=json_node_get_object(node);const char *const names[]={"service","revision","target"};guint64 service,revision;
            if(!surface_fields(intent,names,3) || !surface_uint(json_object_get_member(intent,"service"),&service) || !service || !surface_uint(json_object_get_member(intent,"revision"),&revision) || !revision || !surface_text(json_object_get_member(intent,"target"),2048,FALSE) || g_utf8_strlen(json_object_get_string_member(intent,"target"),-1)>512)return NULL;
        }
        return value;
    }
    if(g_str_equal(value,"system-menu-request") || g_str_equal(value,"system-menu-effect")) {
        gboolean effect=g_str_equal(value,"system-menu-effect");guint64 request;
        const char *const fields[]={"protocolVersion","kind","binding","requestId","intent"};
        if(!surface_fields(obj,fields,effect?5:4) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(effect) {
            JsonNode *node=json_object_get_member(obj,"intent");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
            JsonObject *intent=json_node_get_object(node);const char *const names[]={"service","revision","operation","value"};guint64 service,revision;
            JsonNode *operation=json_object_get_member(intent,"operation"),*number=json_object_get_member(intent,"value");
            if(!surface_fields(intent,names,4) || !surface_uint(json_object_get_member(intent,"service"),&service) || !service || !surface_uint(json_object_get_member(intent,"revision"),&revision) || !revision || !surface_text(operation,32,FALSE) || !number || json_node_get_value_type(number)!=G_TYPE_INT64)return NULL;
            const char *op=json_node_get_string(operation);gint64 n=json_node_get_int(number);
            if(g_str_equal(op,"volume-set")){if(n<0 || n>100)return NULL;}
            else if(g_str_equal(op,"volume-mute") || g_str_equal(op,"network-enable")){if(n!=0 && n!=1)return NULL;}
            else if(g_str_equal(op,"suspend") || g_str_equal(op,"reboot") || g_str_equal(op,"poweroff") || g_str_equal(op,"session-lock") || g_str_equal(op,"session-logout")){if(n!=0)return NULL;}
            else return NULL;
        }
        return value;
    }
    if(g_str_equal(value,"notification-request") || g_str_equal(value,"notification-effect")) {
        gboolean effect=g_str_equal(value,"notification-effect");guint64 request;
        const char *const fields[]={"protocolVersion","kind","binding","requestId","intent"};
        if(!surface_fields(obj,fields,effect?5:4) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(effect) {
            JsonNode *node=json_object_get_member(obj,"intent");if(!node || !JSON_NODE_HOLDS_OBJECT(node))return NULL;
            JsonObject *intent=json_node_get_object(node);const char *const names[]={"service","id","incarnation","producer","action","verb"};guint64 service,id,incarnation;
            JsonNode *producer=json_object_get_member(intent,"producer"),*action=json_object_get_member(intent,"action"),*verb=json_object_get_member(intent,"verb");
            if(!surface_fields(intent,names,6) || !surface_uint(json_object_get_member(intent,"service"),&service) || !service || !surface_uint(json_object_get_member(intent,"id"),&id) || !id || id>G_MAXUINT32 || !surface_uint(json_object_get_member(intent,"incarnation"),&incarnation) || !incarnation || !surface_text(producer,128,FALSE) || json_node_get_string(producer)[0]!=':' || !surface_text(action,64,TRUE) || !surface_text(verb,16,FALSE))return NULL;
            const char *v=json_node_get_string(verb),*a=json_node_get_string(action);
            if((!g_str_equal(v,"invoke") && !g_str_equal(v,"dismiss")) || (g_str_equal(v,"invoke") && !*a) || (g_str_equal(v,"dismiss") && *a))return NULL;
        }
        return value;
    }
    if(g_str_equal(value,"shell-settings-request") || g_str_equal(value,"shell-settings-write")) {
        gboolean write=g_str_equal(value,"shell-settings-write");
        const char *const fields[]={"protocolVersion","kind","binding","requestId","proposal"};guint64 request,revision;
        if(!surface_fields(obj,fields,write?5:4) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request)return NULL;
        if(write){
            JsonNode *proposal=json_object_get_member(obj,"proposal");if(!proposal || !JSON_NODE_HOLDS_OBJECT(proposal))return NULL;
            JsonObject *p=json_node_get_object(proposal);const char *const pfields[]={"schema","revision","values"};JsonNode *version=json_object_get_member(p,"schema"),*values=json_object_get_member(p,"values");
            if(!surface_fields(p,pfields,3) || !version || json_node_get_value_type(version)!=G_TYPE_INT64 || json_node_get_int(version)!=1 || !surface_uint(json_object_get_member(p,"revision"),&revision) || !revision || !values || !JSON_NODE_HOLDS_OBJECT(values))return NULL;
            JsonObject *v=json_node_get_object(values);const char *const vfields[]={"theme","textScale"};JsonNode *theme=json_object_get_member(v,"theme"),*scale=json_object_get_member(v,"textScale");
            if(!surface_fields(v,vfields,2) || !surface_theme(theme) || !scale || json_node_get_value_type(scale)!=G_TYPE_INT64 || (json_node_get_int(scale)!=100 && json_node_get_int(scale)!=125 && json_node_get_int(scale)!=150 && json_node_get_int(scale)!=200))return NULL;
        }
        return value;
    }
    if (g_str_equal(value,"taskbar-pins-write")) {
        const char *const fields[]={"protocolVersion","kind","binding","requestId","proposal"},*const proposal_fields[]={"revision","identities"};
        guint64 request,revision;JsonNode *proposal=json_object_get_member(obj,"proposal");
        if (!surface_fields(obj,fields,5) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) || !surface_uint(json_object_get_member(obj,"requestId"),&request) || !request || !proposal || !JSON_NODE_HOLDS_OBJECT(proposal)) return NULL;
        JsonObject *p=json_node_get_object(proposal);JsonNode *ids=json_object_get_member(p,"identities");
        if (!surface_fields(p,proposal_fields,2) || !surface_uint(json_object_get_member(p,"revision"),&revision) || !revision || !ids || !JSON_NODE_HOLDS_ARRAY(ids)) return NULL;
        JsonArray *rows=json_node_get_array(ids);if(json_array_get_length(rows)>32)return NULL;
        for(guint i=0;i<json_array_get_length(rows);i++) {
            JsonNode *id=json_array_get_element(rows,i);if(!surface_text(id,256,FALSE))return NULL;
            for(guint j=0;j<i;j++)if(json_node_equal(id,json_array_get_element(rows,j)))return NULL;
        }
        return value;
    }
    if (g_str_equal(value,"reconciliation-ready")) {
        const char *const fields[]={"protocolVersion","kind","binding","proofRequestId","queriedBinding"};
        if (!surface_fields(obj,fields,5) || !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) ||
            !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"queriedBinding")) ||
            json_node_get_value_type(json_object_get_member(obj,"proofRequestId"))!=G_TYPE_STRING) return NULL;
        return value; /* Strict full binding/canonical IDs are checked by the broker. */
    }
    if (geometry_kind(value)) {
        gboolean facts=g_str_equal(value,"geometry-facts-request");
        const char *const fields[]={"protocolVersion","kind","geometryProtocol","binding","requestId","minimumWatermark"};
        if (!surface_fields(obj,fields,facts?6:5)) return NULL;
        JsonNode *protocol=json_object_get_member(obj,"geometryProtocol");
        if (json_node_get_value_type(protocol)!=G_TYPE_INT64 || (json_node_get_int(protocol)!=1 && (json_node_get_int(protocol)!=2 && json_node_get_int(protocol)!=3)) ||
            !JSON_NODE_HOLDS_OBJECT(json_object_get_member(obj,"binding")) ||
            json_node_get_value_type(json_object_get_member(obj,"requestId"))!=G_TYPE_STRING ||
            (facts && json_node_get_value_type(json_object_get_member(obj,"minimumWatermark"))!=G_TYPE_STRING)) return NULL;
        return value;
    }
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
    quit_requested=TRUE;gtk_main_quit();
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
    if (error) { g_printerr("Native delivery failed: %s\n",error->message); g_error_free(error); failed=TRUE; if(!renderer_failure_drain_hook || !renderer_failure_drain_hook())gtk_main_quit(); }
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
/* Both native entry points share the same popup-only preview router. The
 * installed native provider still validates exact jobs and retained ownership.
 * Recognized malformed/foreign commands never fall through to desktop actions. */
static gboolean preview_route_commands(WebKitUserContentManager *manager,const char *text,JsonNode *root) {
    if (!text || !root || !JSON_NODE_HOLDS_OBJECT(root)) return FALSE;
    JsonObject *obj=json_node_get_object(root);JsonNode *kind=json_object_get_member(obj,"kind");
    if (!surface_text(kind,32,FALSE) || !g_str_equal(json_node_get_string(kind),"preview-commands")) return FALSE;
    JsonNode *version=json_object_get_member(obj,"previewProtocol"),*entries=json_object_get_member(obj,"entries");
    if(strlen(text)>4096 || preview_owner!=g_thread_self() || !manager || manager!=popup_manager || !popup_view ||
       !version || json_node_get_value_type(version)!=G_TYPE_INT64 || !entries || !JSON_NODE_HOLDS_ARRAY(entries) ||
       json_array_get_length(json_node_get_array(entries))!=1 || !native_preview_handler)return TRUE;
    if(json_node_get_int(version)==1) {
        const char *const fields[]={"previewProtocol","kind","entries"};
        if(!preview_controls.ordered && surface_fields(obj,fields,3))native_preview_handler(popup_view,root);
    }else if(json_node_get_int(version)==2) {
        const char *const fields[]={"previewProtocol","kind","controlOrdinal","entries"};guint64 ordinal;
        if(!surface_fields(obj,fields,4) || !surface_uint(json_object_get_member(obj,"controlOrdinal"),&ordinal) ||
           !preview_control_next(&preview_controls,ordinal))return TRUE;
        /* Hold this packet until its handler returns. Nested transport
         * delivery cannot replay or overtake it. Effect/ACK success is separate;
         * the aggregate transaction still verifies every original obligation. */
        preview_control_begin(&preview_controls,ordinal);native_preview_handler(popup_view,root);
        preview_control_delivered(&preview_controls,ordinal);
    }
    return TRUE;
}
static void receive(WebKitUserContentManager *manager,WebKitJavascriptResult *result,gpointer unused) {
    (void)unused;
    if (shutting_down) return;
    JSCValue *value=webkit_javascript_result_get_js_value(result);
    if (!jsc_value_is_string(value)) { g_print("bridge-refused: type\n"); return; }
    g_autofree char *text=jsc_value_to_string(value);
    if (strlen(text)>1048576) { g_print("bridge-refused: bound\n"); return; }
    g_autoptr(JsonParser) parser=json_parser_new();
    if (!geometry_parse(parser,text)) { g_print("bridge-refused: malformed\n"); return; }
    JsonNode *root=json_parser_get_root(parser);
    if (preview_route_commands(manager,text,root)) return;
    if (surface_experiment) {surface_receive(manager,text,root);return;}
    const char *kind=request_kind(root);
    if (!kind) { g_print("bridge-refused: schema\n"); return; }
    if (!bridge_bound(strlen(text),kind,qa_exit)) { g_print("bridge-refused: control-bound\n"); return; }
    if (qa_exit && (g_str_equal(kind,"window-effect") || g_str_equal(kind,"application-launch") || g_str_equal(kind,"host-reconnect"))) { g_print("frontend-request: %s\n",text);fflush(stdout); }
    if (g_str_equal(kind,"host-ready")) backend_start();
    else if (g_str_equal(kind,"host-reconnect")) backend_restart();
    else if ((observation_kind(kind) || g_str_equal(kind,"projection-request") || g_str_equal(kind,"activation-history-request") || g_str_equal(kind,"switcher-selection-request") || g_str_equal(kind,"switcher-cancel-request") || g_str_equal(kind,"window-effect") || g_str_equal(kind,"catalog-request") || g_str_equal(kind,"taskbar-pins-write") || g_str_equal(kind,"jump-list-request") || g_str_equal(kind,"jump-list-effect") || g_str_equal(kind,"files-request") || g_str_equal(kind,"files-open") || g_str_equal(kind,"system-menu-request") || g_str_equal(kind,"system-menu-effect") || g_str_equal(kind,"notification-request") || g_str_equal(kind,"notification-effect") || g_str_equal(kind,"shell-settings-request") || g_str_equal(kind,"shell-settings-write") || g_str_equal(kind,"motion-profile-set") || g_str_equal(kind,"motion-preferences-request") || g_str_equal(kind,"motion-preferences-write") || g_str_equal(kind,"application-launch"))) {
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
static gboolean (*native_icon_dispatch)(WebKitURISchemeRequest*);
static gboolean (*native_picker_dispatch)(WebKitURISchemeRequest*);
static void scheme(WebKitURISchemeRequest *request,gpointer unused) {
    if (native_picker_dispatch && native_picker_dispatch(request)) return;
    if (unused && preview_uri_router_dispatch((PreviewURIRouter*)unused,request)) return;
    if (!unused && preview_uri_dispatch(native_preview_endpoint,request)) return;
    if (native_icon_dispatch && native_icon_dispatch(request)) return;
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
        if (!g_str_equal(uri,webview==popup_view?(qa_controlled_preview?"elm-shell://app/controlled-popup.html":"elm-shell://app/popup.html"):webview!=view?"elm-shell://app/bar.html":gpu_info?"webkit://gpu":"elm-shell://app/index.html")) { webkit_policy_decision_ignore(decision);return TRUE; }
    }
    return FALSE;
}
static void terminated(WebKitWebView *webview,WebKitWebProcessTerminationReason reason,gpointer unused) {
    (void)webview;(void)unused;
    if (shutting_down) return;
    renderer_failed=TRUE;failed=TRUE;g_printerr("Web process terminated: %d\n",reason);gtk_main_quit();
}
static void surface_eval(WebKitWebView *target,const char *function,JsonNode *value) {
    g_autofree char *wire=json_to_string(value,FALSE);
    g_autofree char *script=g_strdup_printf("window.%s(%s);",function,wire);
    webkit_web_view_evaluate_javascript(target,script,-1,NULL,NULL,NULL,evaluate_done,NULL);
}
static void surface_present(void) {
    if(controlled_surface_notice && surface_snapshot)controlled_surface_notice(surface_snapshot);
    if (popup_ready && surface_snapshot) surface_eval(popup_view,"receivePresentation",surface_snapshot);
}
static void popup_hide(void) {
    gboolean keep_anchor=shared_preserve_context_anchor && has_context_anchor;
    GdkRectangle requested_anchor=context_anchor;
    if (shared_input_cancel) shared_input_cancel();
    if(keep_anchor) {context_anchor=requested_anchor;has_context_anchor=TRUE;}
    if (!popup_active) return;
    popup_active=FALSE;grab_ready=FALSE;keyboard_ready=FALSE;configured_lease=0;applied_publication=0;applied_lease=0;
    if (pending_focus) {json_node_unref(pending_focus);pending_focus=NULL;}
    if (issued_focus) {json_node_unref(issued_focus);issued_focus=NULL;}
    surface_gate.closed=MAX(surface_gate.closed,surface_gate.lease);
    if (gtk_grab_get_current()==popover) gtk_grab_remove(popover);
    gdk_seat_ungrab(gdk_display_get_default_seat(gtk_widget_get_display(window)));
    GtkWidget *retired=popover;popover=NULL;
    popup_disconnect();
    /* Retire the xdg_popup role and input lease, retaining the realized GTK
     * presentation tree. Reparenting destroys its accelerated paint context. */
    g_object_ref(popup_view);gtk_widget_hide(retired);retired_popup=retired;
    /* Fence withdrawal before purging retired input and the authoritative read. */
    gdk_display_sync(gtk_widget_get_display(window));
    popup_events_drained=popup_drain_retired(gtk_widget_get_display(window),gtk_widget_get_window(retired));
    g_print("surface-popup-closed: lease=%" G_GUINT64_FORMAT "\n",surface_gate.lease);fflush(stdout);
    if(qa_popup_retired)qa_popup_retired();
}
static void surface_dismiss(void) {
    if (!popup_active) return;
    guint64 lease=surface_gate.lease;popup_hide();
    if (shared_popup_notice) {shared_popup_notice("receiveDismiss",lease);return;}
    g_autofree char *script=g_strdup_printf("window.receiveDismiss(\"%" G_GUINT64_FORMAT "\");",lease);
    webkit_web_view_evaluate_javascript(view,script,-1,NULL,NULL,NULL,evaluate_done,NULL);
}
static JsonNode *surface_focus_packet(JsonNode *targets) {
    JsonObject *obj=json_object_new();json_object_set_int_member(obj,"surfaceProtocol",2);
    json_object_set_string_member(obj,"kind","surface-focus");
    g_autofree char *pub=g_strdup_printf("%" G_GUINT64_FORMAT,surface_gate.publication),*lease=g_strdup_printf("%" G_GUINT64_FORMAT,surface_gate.lease);
    json_object_set_string_member(obj,"publication",pub);json_object_set_string_member(obj,"lease",lease);
    json_object_set_member(obj,"targets",json_node_copy(targets));JsonNode *node=json_node_new(JSON_NODE_OBJECT);json_node_take_object(node,obj);return node;
}
static gboolean surface_popup_ready(void) {
    return popup_active && grab_ready && keyboard_ready && configured_lease==surface_gate.lease && applied_publication==surface_gate.publication && applied_lease==surface_gate.lease;
}
static void surface_focus_maybe(void) {
    if (!pending_focus || !surface_popup_ready()) return;
    if (issued_focus) json_node_unref(issued_focus);
    issued_focus=pending_focus;pending_focus=NULL;issued_publication=surface_gate.publication;issued_lease=surface_gate.lease;
    JsonNode *packet=surface_focus_packet(issued_focus);surface_eval(popup_view,"receiveFocus",packet);json_node_unref(packet);
    g_print("surface-focus-issued: publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",issued_publication,issued_lease);fflush(stdout);
}
static gboolean popup_scope_current(const PopupScope *scope) {
    return scope && popup_active && scope->lease==surface_gate.lease && scope->owner==popover;
}
static void popup_scope_free(gpointer data,GClosure *closure) {(void)closure;g_free(data);}
static void popup_connect(GObject *target,const char *name,GCallback handler) {
    PopupScope *scope=g_new(PopupScope,1);*scope=(PopupScope){surface_gate.lease,popover};
    g_assert(popup_signal_count<G_N_ELEMENTS(popup_signals));
    gulong id=g_signal_connect_data(target,name,handler,scope,popup_scope_free,0);
    popup_signals[popup_signal_count++]=(PopupSignal){g_object_ref(target),id};
}
static void popup_positioned(GdkWindow *native,GdkRectangle *flipped,GdkRectangle *final,gboolean flip_x,gboolean flip_y,gpointer data) {
    (void)flipped;(void)flip_x;(void)flip_y;PopupScope *scope=data;
    if (!popup_scope_current(scope) || !popover || native!=gtk_widget_get_window(popover) || (final && (final->width<=0 || final->height<=0))) return;
    /* gtk-layer-shell emits this from xdg_popup.configure with NULL rectangles. */
    configured_lease=surface_gate.lease;
    g_print("surface-configured: lease=%" G_GUINT64_FORMAT " rectKnown=%d gdkWidth=%d gdkHeight=%d\n",configured_lease,final!=NULL,gdk_window_get_width(native),gdk_window_get_height(native));fflush(stdout);
    surface_focus_maybe();
}
static gboolean surface_ack(JsonObject *o,const char *kind,gboolean focus) {
    const char *const names[]={"surfaceProtocol","kind","publication","lease","targets"};
    guint64 publication,lease;
    if (!surface_fields(o,names,focus?5:4) || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2 || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),kind) || !surface_uint(json_object_get_member(o,"publication"),&publication) || !surface_uint(json_object_get_member(o,"lease"),&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease || !popup_active || lease<=surface_gate.closed) return FALSE;
    if (!focus) {
        applied_publication=publication;applied_lease=lease;
        g_print("surface-presentation-applied: publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",publication,lease);fflush(stdout);surface_focus_maybe();return TRUE;
    }
    JsonNode *targets=json_object_get_member(o,"targets");
    if (!surface_popup_ready() || !issued_focus || issued_publication!=publication || issued_lease!=lease || !JSON_NODE_HOLDS_ARRAY(targets)) return FALSE;
    JsonArray *values=json_node_get_array(targets),*requested=json_node_get_array(issued_focus);
    if (!json_array_get_length(values) || json_array_get_length(values)>json_array_get_length(requested)) return FALSE;
    for (guint i=0;i<json_array_get_length(values);i++) {
        JsonNode *value=json_array_get_element(values,i);if (!surface_text(value,1024,FALSE)) return FALSE;
        gboolean found=FALSE;for(guint j=0;j<json_array_get_length(requested);j++) if (g_str_equal(json_node_get_string(value),json_array_get_string_element(requested,j))) found=TRUE;
        if (!found) return FALSE;
    }
    g_print("surface-focus-applied: publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT "\n",publication,lease);fflush(stdout);
    json_node_unref(issued_focus);issued_focus=NULL;return TRUE;
}
static gboolean popup_unmapped(GtkWidget *widget,GdkEvent *event,gpointer unused) {
    (void)event;if (popup_scope_current(unused) && widget==popover) surface_dismiss();return FALSE;
}
static gboolean popup_button(GtkWidget *widget,GdkEventButton *event,gpointer unused) {
    if (!popup_scope_current(unused) || widget!=popover) return FALSE;
    GtkAllocation a;gtk_widget_get_allocation(widget,&a);
    if (widget==popover && (event->x<0 || event->y<0 || event->x>=a.width || event->y>=a.height)) {surface_dismiss();return TRUE;}return FALSE;
}
static gboolean popup_focus(GtkWidget *widget,GdkEventFocus *event,gpointer scope) {
    if (popup_scope_current(scope) && widget==popover) {
        keyboard_ready=event->in;
        g_print("surface-native-keyboard-focus: lease=%" G_GUINT64_FORMAT " in=%d\n",surface_gate.lease,event->in);fflush(stdout);
        surface_focus_maybe();
    }
    return FALSE;
}
static gboolean popup_broken(GtkWidget *widget,GdkEventGrabBroken *event,gpointer unused) {
    (void)event;if (popup_scope_current(unused) && widget==popover) surface_dismiss();return FALSE;
}
static void popup_prepare(GdkSeat *seat,GdkWindow *native,gpointer widget) {
    (void)seat;(void)native;if (widget==popover) gtk_widget_show_all(GTK_WIDGET(widget));
}
static gboolean retain_event(GtkWidget *widget,GdkEvent *event,gpointer unused) {
    (void)widget;(void)unused;
    if (event->type==GDK_BUTTON_PRESS || event->type==GDK_KEY_PRESS) {if (bar_event) gdk_event_free(bar_event);bar_event=gdk_event_copy(event);}return FALSE;
}
static gboolean popup_dimensions(int logical_width,int logical_height,int *width,int *height) {
    if (logical_width<=8 || logical_height<=52) return FALSE;
    /* Owning compositor positioner insets its constraint box by four logical pixels. */
    *width=MIN(700,logical_width-8);*height=MIN(420,logical_height-(window?MAX(48,gtk_widget_get_allocated_height(window)):48)-4);return *height>0;
}
static gboolean popup_open(void) {
    if (popup_active) return TRUE;
    GdkRectangle geometry;int width,height;
    if (output_retired || !owned_monitor) return FALSE;
    gdk_monitor_get_geometry(owned_monitor,&geometry);
    if (!popup_dimensions(geometry.width,geometry.height,&width,&height)) {g_print("surface-popup-refused: unavailable-logical-area\n");return FALSE;}
    gboolean reused=retired_popup!=NULL;
    if (reused && !popup_events_drained) {
        gdk_display_sync(gtk_widget_get_display(window));
        popup_events_drained=popup_drain_retired(gtk_widget_get_display(window),gtk_widget_get_window(retired_popup));
        if (!popup_events_drained) {g_print("surface-popup-refused: retired-input-pending\n");return FALSE;}
    }
    popover=reused?retired_popup:gtk_window_new(GTK_WINDOW_POPUP);retired_popup=NULL;
    gtk_window_set_transient_for(GTK_WINDOW(popover),GTK_WINDOW(window));
    gtk_window_set_attached_to(GTK_WINDOW(popover),window);
    gtk_window_set_type_hint(GTK_WINDOW(popover),GDK_WINDOW_TYPE_HINT_POPUP_MENU);
    gtk_window_set_default_size(GTK_WINDOW(popover),width,height);
    gtk_widget_set_size_request(GTK_WIDGET(popup_view),width,height);
    /* Default size only governs the first map. A retained presentation tree
     * must also shrink its previous allocation before its fresh popup role. */
    gtk_window_resize(GTK_WINDOW(popover),width,height);
    if (!reused) gtk_container_add(GTK_CONTAINER(popover),GTK_WIDGET(popup_view));
    g_object_unref(popup_view);
    popup_connect(G_OBJECT(popover),"unmap-event",G_CALLBACK(popup_unmapped));
    popup_connect(G_OBJECT(popover),"focus-in-event",G_CALLBACK(popup_focus));
    popup_connect(G_OBJECT(popover),"focus-out-event",G_CALLBACK(popup_focus));
    popup_connect(G_OBJECT(popover),"button-press-event",G_CALLBACK(popup_button));
    popup_connect(G_OBJECT(popover),"grab-broken-event",G_CALLBACK(popup_broken));
    gtk_widget_realize(popover);
    GdkRectangle anchor=has_context_anchor?context_anchor:(GdkRectangle){50,0,1,MAX(48,gtk_widget_get_allocated_height(window))};GdkWindow *native=gtk_widget_get_window(popover);
    popup_connect(G_OBJECT(native),"moved-to-rect",G_CALLBACK(popup_positioned));
    gdk_window_move_to_rect(native,&anchor,GDK_GRAVITY_SOUTH_WEST,GDK_GRAVITY_NORTH_WEST,GDK_ANCHOR_SLIDE_X|GDK_ANCHOR_FLIP_Y|GDK_ANCHOR_SLIDE_Y,0,0);
    popup_active=TRUE;
    GdkGrabStatus status=gdk_seat_grab(gdk_display_get_default_seat(gtk_widget_get_display(window)),native,GDK_SEAT_CAPABILITY_ALL,TRUE,NULL,bar_event,popup_prepare,popover);
    if (status!=GDK_GRAB_SUCCESS) {surface_dismiss();g_print("surface-popup-refused: grab=%d\n",status);return FALSE;}
    gtk_grab_add(popover);gtk_widget_grab_focus(GTK_WIDGET(popup_view));grab_ready=TRUE;
    g_print("surface-popup-open: lease=%" G_GUINT64_FORMAT "\n",surface_gate.lease);fflush(stdout);return TRUE;
}
typedef struct { JsonNode *frame,*focus;JsonArray *requests;guint64 publication,lease;gboolean open; } SurfaceCommit;
static gboolean surface_preflight(SurfaceGate *gate,JsonNode *root,guint queued,guint active,gboolean ready,SurfaceCommit *result) {
    if (!root || !JSON_NODE_HOLDS_OBJECT(root)) return FALSE;
    JsonObject *o=json_node_get_object(root);
    const char *const fields[]={"surfaceProtocol","kind","frame","requests","focus"};
    if (!surface_fields(o,fields,5) || json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))!=G_TYPE_INT64 || json_object_get_int_member(o,"surfaceProtocol")!=2 || !surface_text(json_object_get_member(o,"kind"),32,FALSE) || !g_str_equal(json_object_get_string_member(o,"kind"),"surface-commit")) return FALSE;
    guint64 publication,lease;gboolean open;
    JsonNode *frame=json_object_get_member(o,"frame"),*rn=json_object_get_member(o,"requests"),*fn=json_object_get_member(o,"focus");
    if (!surface_admit(gate,frame,&publication,&lease,&open) || !JSON_NODE_HOLDS_ARRAY(rn) || !JSON_NODE_HOLDS_ARRAY(fn)) return FALSE;
    JsonArray *req=json_node_get_array(rn),*focus=json_node_get_array(fn);
    guint count=json_array_get_length(req);
    if (count>16 || count+queued+active>16 || json_array_get_length(focus)>16) return FALSE;
    /* Validate the entire commit before mutating surfaces, backend or queues. */
    for (guint i=0;i<count;i++) {
        JsonNode *item=json_array_get_element(req,i);const char *rk=request_kind(item);
        g_autofree char *wire=json_to_string(item,FALSE);
        if (!rk || strlen(wire)>4096 || (!observation_kind(rk) && !g_str_equal(rk,"projection-request") && !g_str_equal(rk,"activation-history-request") && !g_str_equal(rk,"switcher-selection-request") && !g_str_equal(rk,"switcher-cancel-request") && !g_str_equal(rk,"catalog-request") && !g_str_equal(rk,"taskbar-pins-write") && !g_str_equal(rk,"jump-list-request") && !g_str_equal(rk,"jump-list-effect") && !g_str_equal(rk,"files-request") && !g_str_equal(rk,"files-open") && !g_str_equal(rk,"system-menu-request") && !g_str_equal(rk,"system-menu-effect") && !g_str_equal(rk,"notification-request") && !g_str_equal(rk,"notification-effect") && !g_str_equal(rk,"shell-settings-request") && !g_str_equal(rk,"shell-settings-write") && !g_str_equal(rk,"motion-profile-set") && !g_str_equal(rk,"motion-preferences-request") && !g_str_equal(rk,"motion-preferences-write") && !g_str_equal(rk,"application-launch") && !g_str_equal(rk,"window-effect") && !g_str_equal(rk,"host-reconnect")) || (open && (g_str_equal(rk,"application-launch") || g_str_equal(rk,"window-effect") || g_str_equal(rk,"files-open") || g_str_equal(rk,"jump-list-effect")))) return FALSE;
        if (g_str_equal(rk,"host-reconnect") && count!=1) return FALSE;
        if (!ready && !g_str_equal(rk,"host-reconnect")) return FALSE;
    }
    for (guint i=0;i<json_array_get_length(focus);i++) if (!surface_text(json_array_get_element(focus,i),1024,FALSE)) return FALSE;
    *result=(SurfaceCommit){frame,fn,req,publication,lease,open};return TRUE;
}
static SurfaceDisposition surface_receive(WebKitUserContentManager *manager,const char *text,JsonNode *root) {
    if (output_retired || !root || !JSON_NODE_HOLDS_OBJECT(root)) return SURFACE_IGNORED;
    JsonObject *o=json_node_get_object(root);
    if (qa_exit && manager==primary_manager && surface_text(json_object_get_member(o,"kind"),32,FALSE) && g_str_equal(json_object_get_string_member(o,"kind"),"surface-inspection")) {
        g_print("surface-inspection: %s\n",text);fflush(stdout);return SURFACE_IGNORED;
    }
    if (qa_exit && (manager==primary_manager || manager==popup_manager) && surface_text(json_object_get_member(o,"kind"),32,FALSE) && g_str_equal(json_object_get_string_member(o,"kind"),"surface-report")) {
        g_print("surface-report: origin=%s %s\n",manager==primary_manager?"bar":"popup",text);fflush(stdout);
        reported=TRUE;if (quit_source) {g_source_remove(quit_source);quit_source=0;}return SURFACE_IGNORED;
    }
    if (manager==popup_manager) {
        const char *const ready[]={"surfaceProtocol","kind"};
        if (surface_fields(o,ready,2) && json_node_get_value_type(json_object_get_member(o,"surfaceProtocol"))==G_TYPE_INT64 && json_object_get_int_member(o,"surfaceProtocol")==2 && surface_text(json_object_get_member(o,"kind"),32,FALSE) && g_str_equal(json_object_get_string_member(o,"kind"),"presentation-ready")) {popup_ready=TRUE;surface_present();return SURFACE_IGNORED;}
        if (strlen(text)<=4096 && (surface_ack(o,"presentation-applied",FALSE) || surface_ack(o,"focus-applied",TRUE))) return SURFACE_IGNORED;
        if (strlen(text)<=4096 && surface_popup_ready() && surface_action(&surface_gate,root,surface_snapshot,TRUE)) surface_eval(view,"receiveAction",root);
        else g_print("surface-refused: popup-origin-or-stale\n");
        return SURFACE_IGNORED;
    }
    if (manager!=primary_manager) return SURFACE_IGNORED;
    const char *kind=request_kind(root);
    if (kind && g_str_equal(kind,"host-ready") && strlen(text)<=4096) {backend_start();return SURFACE_IGNORED;}
    SurfaceCommit commit;
    if (!surface_preflight(&surface_gate,root,g_queue_get_length(&requests),active_request?1:0,backend_ready,&commit)) {g_print("surface-refused: preflight-unsent\n");fflush(stdout);return SURFACE_PREFLIGHT_UNSENT;}
    JsonNode *frame=commit.frame,*fn=commit.focus;JsonArray *req=commit.requests;
    guint64 publication=commit.publication,lease=commit.lease;gboolean open=commit.open;
    if (!admission_batch(req,authority_binding)) {
        backend_ready=FALSE;
        if(admission_storage_failed){
            deliver("{\"protocolVersion\":3,\"kind\":\"host-recovery-failed\",\"reason\":\"unavailable\"}");
            g_cancellable_cancel(io_cancel);g_subprocess_send_signal(backend,SIGTERM);
        } else deliver("{\"protocolVersion\":3,\"kind\":\"host-disconnected\"}");
        return SURFACE_UNCERTAIN;
    }
    guint count=json_array_get_length(req);
    /* Preserve an undelivered focus request through observation-only frames on
     * the same popup lease, only while every exact DOM target survives enabled.
     * Already-issued focus is never replayed; owner changes retire the popup. */
    JsonNode *retained_focus=NULL;
    if (popup_active && open && lease==surface_gate.lease && pending_focus && !json_array_get_length(json_node_get_array(fn)) && surface_snapshot && g_str_equal(json_object_get_string_member(json_node_get_object(frame),"mode"),json_object_get_string_member(json_node_get_object(surface_snapshot),"mode")) && surface_focus_targets_present(pending_focus,frame)) {retained_focus=pending_focus;pending_focus=NULL;}
    if (popup_active && (!open || lease!=surface_gate.lease)) popup_hide();
    surface_gate.publication=publication;surface_gate.lease=lease;
    if (surface_snapshot) json_node_unref(surface_snapshot);
    surface_snapshot=json_node_copy(frame);
    /* Project committed text size into the native layer reservation. This does
     * not observe or apply the user's draft and cannot submit a window effect. */
    static gint appearance_height=48;
    JsonNode *appearance=json_object_get_member(json_node_get_object(frame),"appearance");
    gint scale=appearance?json_object_get_int_member(json_node_get_object(appearance),"textScale"):100;
    gint height=48*scale/100;
    if(!shared_frame_notice && height!=appearance_height){
        appearance_height=height;
        gtk_widget_set_size_request(window,-1,height);
        gtk_widget_set_size_request(GTK_WIDGET(view),-1,height);
        gtk_layer_set_exclusive_zone(GTK_WINDOW(window),height);
    }

    if (shared_frame_notice) shared_frame_notice();
    applied_publication=0;applied_lease=0;
    if (pending_focus) {json_node_unref(pending_focus);pending_focus=NULL;}
    if (issued_focus) {json_node_unref(issued_focus);issued_focus=NULL;}
    if (open && json_array_get_length(json_node_get_array(fn))) pending_focus=json_node_copy(fn);
    else pending_focus=retained_focus;
    surface_present();
    /* Preflight excludes all effects/launches while open. No request from this
     * original invocation has entered the backend queue at this boundary. */
    if (open && !popup_open()) return SURFACE_PREFLIGHT_UNSENT;
    surface_focus_maybe();
    /* All native grab retirement above is synchronous and precedes all requests. */
    for (guint i=0;i<count;i++) {
        JsonNode *item=json_array_get_element(req,i);const char *rk=request_kind(item);
        if (g_str_equal(rk,"host-reconnect")) {backend_restart();continue;}
        g_autofree char *wire=json_to_string(item,FALSE);g_print("frontend-request: %s\n",wire);
        g_queue_push_tail(&requests,g_strconcat(wire,"\n",NULL));
    }
    write_next();
    if (!open && json_array_get_length(json_node_get_array(fn))) {JsonNode *packet=surface_focus_packet(fn);surface_eval(shared_bar_focus_view?shared_bar_focus_view():view,"receiveFocus",packet);json_node_unref(packet);}
    g_print("surface-commit: publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " open=%d\n",publication,lease,open);fflush(stdout);return SURFACE_ADMITTED;
}
static void test_assets(void) {
    g_assert_cmpstr(asset_name("elm-shell://app/index.html"),==,"index.html");
    g_assert_cmpstr(asset_name("elm-shell://app/activation.js"),==,"activation.js");
    g_assert_null(asset_name("elm-shell://app/event-fields.js"));
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
    g_autoptr(JsonParser) jump_parser=json_parser_new();
    g_assert_true(json_parser_load_from_data(jump_parser,"{\"protocolVersion\":3,\"kind\":\"jump-list-effect\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"revision\":\"1\",\"entry\":\"editor\",\"action\":\"desktop:Alpha\"}}",-1,NULL));
    g_assert_nonnull(request_kind(json_parser_get_root(jump_parser)));
    JsonObject *jump_intent=json_object_get_object_member(json_node_get_object(json_parser_get_root(jump_parser)),"intent");
    json_object_set_string_member(jump_intent,"uri","file:///tmp/foreign");g_assert_null(request_kind(json_parser_get_root(jump_parser)));json_object_remove_member(jump_intent,"uri");
    json_object_set_string_member(jump_intent,"Exec","/usr/bin/false");g_assert_null(request_kind(json_parser_get_root(jump_parser)));json_object_remove_member(jump_intent,"Exec");
    json_object_set_string_member(jump_intent,"revision","0");g_assert_null(request_kind(json_parser_get_root(jump_parser)));
    const char *good[]={"{\"protocolVersion\":3,\"kind\":\"host-ready\"}","{\"protocolVersion\":3,\"kind\":\"projection-request\",\"binding\":{},\"requestId\":\"1\"}"};
    const char *bad[]={"[]","{}","{\"protocolVersion\":1,\"kind\":\"host-ready\"}","{\"protocolVersion\":3,\"kind\":\"execute\"}","{\"protocolVersion\":3,\"kind\":\"host-ready\",\"path\":\"/etc/passwd\"}","{\"protocolVersion\":3,\"kind\":\"snapshot-request\"}"};
    g_autoptr(JsonParser) motion_parser=json_parser_new();
    g_assert_true(json_parser_load_from_data(motion_parser,"{\"protocolVersion\":3,\"kind\":\"motion-profile-set\",\"binding\":{},\"requestId\":\"1\",\"profile\":\"reduced\"}",-1,NULL));
    JsonObject *motion=json_node_get_object(json_parser_get_root(motion_parser));g_assert_nonnull(request_kind(json_parser_get_root(motion_parser)));
    json_object_set_string_member(motion,"profile","full");g_assert_nonnull(request_kind(json_parser_get_root(motion_parser)));
    json_object_set_string_member(motion,"profile","fast");g_assert_null(request_kind(json_parser_get_root(motion_parser)));json_object_set_string_member(motion,"profile","reduced");
    json_object_set_string_member(motion,"requestId","0");g_assert_null(request_kind(json_parser_get_root(motion_parser)));json_object_set_string_member(motion,"requestId","1");
    json_object_set_boolean_member(motion,"execute",TRUE);g_assert_null(request_kind(json_parser_get_root(motion_parser)));
    g_autoptr(JsonParser) preference_parser=json_parser_new();
    g_assert_true(json_parser_load_from_data(preference_parser,"{\"protocolVersion\":3,\"kind\":\"motion-preferences-write\",\"binding\":{},\"requestId\":\"1\",\"proposal\":{\"schema\":1,\"revision\":\"1\",\"override\":null}}",-1,NULL));
    JsonObject *preference=json_node_get_object(json_parser_get_root(preference_parser)),*proposal=json_object_get_object_member(preference,"proposal");
    g_assert_nonnull(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_string_member(proposal,"override","reduced");g_assert_nonnull(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_string_member(proposal,"override","full");g_assert_nonnull(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_string_member(proposal,"override","fast");g_assert_null(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_null_member(proposal,"override");json_object_set_int_member(proposal,"schema",2);g_assert_null(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_int_member(proposal,"schema",1);json_object_set_string_member(proposal,"path","/tmp/foreign");g_assert_null(request_kind(json_parser_get_root(preference_parser)));
    json_object_remove_member(proposal,"path");json_object_set_string_member(preference,"requestId","0");g_assert_null(request_kind(json_parser_get_root(preference_parser)));
    json_object_set_string_member(preference,"requestId","1");json_object_set_string_member(preference,"kind","motion-preferences-request");g_assert_null(request_kind(json_parser_get_root(preference_parser)));
    json_object_remove_member(preference,"proposal");g_assert_nonnull(request_kind(json_parser_get_root(preference_parser)));
    const char *settings_good="{\"protocolVersion\":3,\"kind\":\"shell-settings-write\",\"binding\":{},\"requestId\":\"1\",\"proposal\":{\"schema\":1,\"revision\":\"1\",\"values\":{\"theme\":\"dawn\",\"textScale\":150}}}";
    g_autoptr(JsonParser) settings_parser=json_parser_new();g_assert_true(json_parser_load_from_data(settings_parser,settings_good,-1,NULL));g_assert_nonnull(request_kind(json_parser_get_root(settings_parser)));
    JsonObject *settings_proposal=json_object_get_object_member(json_node_get_object(json_parser_get_root(settings_parser)),"proposal"),*settings_values=json_object_get_object_member(settings_proposal,"values");
    json_object_set_string_member(settings_values,"theme","high-contrast");g_assert_nonnull(request_kind(json_parser_get_root(settings_parser)));
    json_object_set_string_member(settings_values,"theme","high-contrast/path");g_assert_null(request_kind(json_parser_get_root(settings_parser)));
    json_object_set_string_member(settings_values,"theme","high-contrast");
    json_object_set_int_member(settings_values,"textScale",77);g_assert_null(request_kind(json_parser_get_root(settings_parser)));
    json_object_set_int_member(settings_values,"textScale",150);json_object_set_int_member(settings_proposal,"schema",2);g_assert_null(request_kind(json_parser_get_root(settings_parser)));
    json_object_set_int_member(settings_proposal,"schema",1);json_object_set_string_member(settings_proposal,"path","/tmp/foreign");g_assert_null(request_kind(json_parser_get_root(settings_parser)));
    const char *pins_good="{\"protocolVersion\":3,\"kind\":\"taskbar-pins-write\",\"binding\":{},\"requestId\":\"1\",\"proposal\":{\"revision\":\"1\",\"identities\":[\"files\",\"editor\"]}}";
    g_autoptr(JsonParser) pins_parser=json_parser_new();g_assert_true(json_parser_load_from_data(pins_parser,pins_good,-1,NULL));g_assert_nonnull(request_kind(json_parser_get_root(pins_parser)));
    JsonObject *pins_proposal=json_object_get_object_member(json_node_get_object(json_parser_get_root(pins_parser)),"proposal");json_object_set_string_member(pins_proposal,"path","/tmp/foreign");g_assert_null(request_kind(json_parser_get_root(pins_parser)));json_object_remove_member(pins_proposal,"path");json_array_add_string_element(json_object_get_array_member(pins_proposal,"identities"),"files");g_assert_null(request_kind(json_parser_get_root(pins_parser)));
    for (guint i=0;i<G_N_ELEMENTS(good);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,good[i],-1,NULL));g_assert_nonnull(request_kind(json_parser_get_root(p))); }
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) { g_autoptr(JsonParser) p=json_parser_new();g_assert_true(json_parser_load_from_data(p,bad[i],-1,NULL));g_assert_null(request_kind(json_parser_get_root(p))); }
}

static JsonNode *test_json(const char *text) {
    JsonParser *parser=json_parser_new();g_assert_true(json_parser_load_from_data(parser,text,-1,NULL));JsonNode *node=json_node_copy(json_parser_get_root(parser));g_object_unref(parser);return node;
}
static JsonNode *test_commit(void) {
    return test_json("{\"surfaceProtocol\":2,\"kind\":\"surface-commit\",\"frame\":{\"surfaceProtocol\":2,\"publication\":\"11\",\"lease\":\"3\",\"mode\":\"closed\",\"status\":\"Ready\",\"bar\":[],\"popup\":[]},\"requests\":[{\"protocolVersion\":3,\"kind\":\"projection-request\",\"binding\":{},\"requestId\":\"1\"}],\"focus\":[]}");
}
static void test_surface_preflight(void) {
    SurfaceGate gate={10,3,2};SurfaceCommit out;JsonNode *root=test_commit();JsonObject *o=json_node_get_object(root);JsonArray *array=json_object_get_array_member(o,"requests");
    g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));g_assert_false(surface_preflight(&gate,root,16,0,TRUE,&out));g_assert_false(surface_preflight(&gate,root,15,1,TRUE,&out));g_assert_false(surface_preflight(&gate,root,0,0,FALSE,&out));
    JsonNode *bad=test_json("{\"protocolVersion\":3,\"kind\":\"execute\"}");json_array_add_element(array,bad);
    g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));g_assert_cmpuint(gate.publication,==,10);json_array_remove_element(array,1);
    for(guint i=0;i<16;i++) json_array_add_element(array,json_node_copy(json_array_get_element(array,0)));
    g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));while(json_array_get_length(array)>1) json_array_remove_element(array,1);
    JsonObject *request=json_array_get_object_element(array,0);JsonObject *binding=json_object_get_object_member(request,"binding");g_autofree char *large=g_strnfill(4096,'x');json_object_set_string_member(binding,"payload",large);g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_remove_member(binding,"payload");
    JsonObject *frame=json_object_get_object_member(o,"frame");json_object_set_string_member(frame,"publication","10");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(frame,"publication","11");
    json_object_set_string_member(frame,"mode","applications");json_object_set_string_member(request,"kind","application-launch");json_object_remove_member(request,"requestId");json_object_set_object_member(request,"intent",json_object_new());g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(frame,"mode","notifications");json_array_remove_element(array,0);
    JsonNode *notification=test_json("{\"protocolVersion\":3,\"kind\":\"notification-effect\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"id\":\"1\",\"incarnation\":\"7\",\"producer\":\":1.5\",\"action\":\"open\",\"verb\":\"invoke\"}}");
    json_array_add_element(array,notification);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    JsonObject *intent=json_object_get_object_member(json_node_get_object(notification),"intent");
    json_object_set_string_member(intent,"id","0");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(intent,"id","4294967296");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(intent,"id","1");
    json_object_set_string_member(intent,"verb","execute");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(intent,"verb","invoke");
    json_object_set_string_member(intent,"path","/tmp/foreign");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_remove_member(intent,"path");
    g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(frame,"mode","system");json_array_remove_element(array,0);
    JsonNode *system=test_json("{\"protocolVersion\":3,\"kind\":\"system-menu-effect\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"revision\":\"1\",\"operation\":\"volume-set\",\"value\":25}}");
    json_array_add_element(array,system);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    JsonObject *system_intent=json_object_get_object_member(json_node_get_object(system),"intent");
    json_object_set_int_member(system_intent,"value",101);g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_int_member(system_intent,"value",25);
    json_object_set_string_member(system_intent,"service","0");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(system_intent,"service","9");
    json_object_set_string_member(system_intent,"operation","network-enable");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_int_member(system_intent,"value",1);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(system_intent,"operation","execute");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(system_intent,"operation","session-lock");json_object_set_int_member(system_intent,"value",0);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(system_intent,"path","/tmp/foreign");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_remove_member(system_intent,"path");
    json_object_set_string_member(frame,"mode","closed");json_array_remove_element(array,0);
    JsonNode *files=test_json("{\"protocolVersion\":3,\"kind\":\"files-open\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"revision\":\"1\",\"target\":\"coll:images\"}}");
    json_array_add_element(array,files);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    JsonObject *files_intent=json_object_get_object_member(json_node_get_object(files),"intent");
    json_object_set_string_member(frame,"mode","files");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(frame,"mode","closed");json_object_set_string_member(files_intent,"instance","foreign");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_remove_member(files_intent,"instance");
    json_object_set_string_member(files_intent,"revision","0");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));json_object_set_string_member(files_intent,"revision","1");
    json_object_set_string_member(files_intent,"target","/tmp/Documents");g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_array_remove_element(array,0);
    JsonNode *jump=test_json("{\"protocolVersion\":3,\"kind\":\"jump-list-effect\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"revision\":\"1\",\"entry\":\"editor\",\"action\":\"desktop:Alpha\"}}");
    json_array_add_element(array,jump);g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(frame,"mode","jump");g_assert_false(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_object_set_string_member(frame,"mode","closed");g_assert_true(surface_preflight(&gate,root,0,0,TRUE,&out));
    json_node_unref(root);
}
static void test_surface_managers(void) {
    int primary=0,popup=0,other=0;primary_manager=(WebKitUserContentManager *)&primary;popup_manager=(WebKitUserContentManager *)&popup;
    surface_gate=(SurfaceGate){11,3,3};popup_active=FALSE;backend_ready=TRUE;
    JsonNode *root=test_commit();g_autofree char *wire=json_to_string(root,FALSE);
    SurfaceGate before=surface_gate;
    surface_receive(popup_manager,wire,root);surface_receive((WebKitUserContentManager *)&other,wire,root);surface_receive(primary_manager,wire,root);
    g_assert_cmpuint(g_queue_get_length(&requests),==,0);g_assert_cmpmem(&surface_gate,sizeof(surface_gate),&before,sizeof(before));g_assert_null(surface_snapshot);
    JsonNode *action=test_json("{\"protocolVersion\":3,\"kind\":\"application-launch\",\"binding\":{},\"intent\":{}}");g_autofree char *launch=json_to_string(action,FALSE);surface_receive(popup_manager,launch,action);g_assert_cmpuint(g_queue_get_length(&requests),==,0);json_node_unref(action);json_node_unref(root);
    primary_manager=NULL;popup_manager=NULL;backend_ready=FALSE;
}
static void test_surface_acknowledgements(void) {
    surface_gate=(SurfaceGate){11,3,2};popup_active=TRUE;grab_ready=FALSE;configured_lease=0;applied_publication=0;applied_lease=0;
    JsonNode *ack=test_json("{\"surfaceProtocol\":2,\"kind\":\"presentation-applied\",\"publication\":\"11\",\"lease\":\"3\"}");JsonObject *o=json_node_get_object(ack);
    g_assert_true(surface_ack(o,"presentation-applied",FALSE));g_assert_false(surface_popup_ready());configured_lease=3;g_assert_false(surface_popup_ready());grab_ready=TRUE;g_assert_false(surface_popup_ready());keyboard_ready=TRUE;g_assert_true(surface_popup_ready());
    json_object_set_string_member(o,"lease","2");g_assert_false(surface_ack(o,"presentation-applied",FALSE));g_assert_cmpuint(applied_lease,==,3);json_object_set_string_member(o,"lease","3");
    json_object_set_string_member(o,"publication","10");g_assert_false(surface_ack(o,"presentation-applied",FALSE));g_assert_cmpuint(applied_publication,==,11);json_object_set_string_member(o,"publication","11");
    json_object_set_string_member(o,"kind","focus-applied");json_object_set_array_member(o,"targets",json_array_new());g_assert_false(surface_ack(o,"focus-applied",TRUE));
    issued_focus=test_json("[\"current\"]");issued_publication=11;issued_lease=3;json_array_add_string_element(json_object_get_array_member(o,"targets"),"unknown");g_assert_false(surface_ack(o,"focus-applied",TRUE));
    json_array_remove_element(json_object_get_array_member(o,"targets"),0);json_array_add_string_element(json_object_get_array_member(o,"targets"),"current");g_assert_true(surface_ack(o,"focus-applied",TRUE));g_assert_null(issued_focus);g_assert_false(surface_ack(o,"focus-applied",TRUE));
    int retired=0,current=0;popover=(GtkWidget *)&current;GdkRectangle configured={.width=700,.height=420};PopupScope oldscope={2,popover};popup_positioned(NULL,NULL,&configured,FALSE,FALSE,&oldscope);g_assert_cmpuint(configured_lease,==,3);g_assert_false(popup_unmapped((GtkWidget *)&retired,NULL,NULL));g_assert_false(popup_unmapped(popover,NULL,&oldscope));g_assert_false(popup_broken(popover,NULL,&oldscope));g_assert_false(popup_button(popover,NULL,&oldscope));g_assert_true(popup_active);
    popover=NULL;popup_active=FALSE;grab_ready=FALSE;keyboard_ready=FALSE;configured_lease=0;applied_publication=0;applied_lease=0;json_node_unref(ack);
}

static gboolean parse_monitor_index(const char *text,int *index) {
    if (!text || !*text || (text[0]=='0' && text[1])) return FALSE;
    guint64 value=0;
    for (const char *cursor=text;*cursor;cursor++) {
        if (*cursor<'0' || *cursor>'9' || value>((guint64)G_MAXINT-(*cursor-'0'))/10) return FALSE;
        value=value*10+(*cursor-'0');
    }
    *index=(int)value;return TRUE;
}
static void output_geometry_changed(GObject *object,GParamSpec *property,gpointer unused) {
    (void)property;(void)unused;
    if (object!=G_OBJECT(owned_monitor) || output_retired || shutting_down || !popup_active) return;
    GdkRectangle geometry;int width,height;gdk_monitor_get_geometry(owned_monitor,&geometry);
    if (!popup_dimensions(geometry.width,geometry.height,&width,&height)) {surface_dismiss();return;}
    /* GTK3 layer popup interception does not reposition an already mapped popup.
       Retain the Elm presentation engine and logical lease, replacing only its
       scoped native wrapper. popup_hide clears all native readiness first. */
    guint64 retired=surface_gate.lease;popup_hide();
    g_autofree char *script=g_strdup_printf("window.receiveReflow(\"%" G_GUINT64_FORMAT "\");",retired);
    webkit_web_view_evaluate_javascript(view,script,-1,NULL,NULL,NULL,evaluate_done,NULL);
    g_print("output-popup-reflow: logical=%d,%d popup=%d,%d lease=%" G_GUINT64_FORMAT "\n",geometry.width,geometry.height,width,height,surface_gate.lease);fflush(stdout);
}
static void output_removed(GdkDisplay *display,GdkMonitor *monitor,gpointer unused) {
    (void)display;(void)unused;
    if (output_retired || monitor!=owned_monitor) return;
    output_retired=TRUE;shutting_down=TRUE;backend_ready=FALSE;
    guint queued=g_queue_get_length(&requests);g_queue_clear_full(&requests,g_free);
    if (io_cancel) g_cancellable_cancel(io_cancel);
    if (popup_active) popup_hide();
    if (window) gtk_widget_hide(window);
    g_print("output-retired: startup-index=%d discarded-queued=%u active-write=%d\n",monitor_index,queued,active_request!=NULL);fflush(stdout);
    gtk_main_quit();
}
static void test_popup_dimensions(void) {
    int width,height;
    g_assert_true(popup_dimensions(800,600,&width,&height));g_assert_cmpint(width,==,700);g_assert_cmpint(height,==,420);
    g_assert_true(popup_dimensions(640,480,&width,&height));g_assert_cmpint(width,==,632);g_assert_cmpint(height,==,420);
    g_assert_true(popup_dimensions(800,300,&width,&height));g_assert_cmpint(height,==,248);
    g_assert_false(popup_dimensions(0,600,&width,&height));g_assert_false(popup_dimensions(800,48,&width,&height));
}
static void test_monitor_index(void) {
    int index=-1;g_assert_true(parse_monitor_index("0",&index));g_assert_cmpint(index,==,0);
    g_assert_true(parse_monitor_index("2147483647",&index));g_assert_cmpint(index,==,G_MAXINT);
    const char *bad[]={"", "01", "-1", "+1", "1x", " 1", "2147483648", "99999999999999999999"};
    for (guint i=0;i<G_N_ELEMENTS(bad);i++) g_assert_false(parse_monitor_index(bad[i],&index));
}

typedef struct {guint sequence;gboolean retired;} TestPopupEvent;
static gpointer test_popup_take(gpointer context) {return g_queue_pop_head(context);}
static gboolean test_popup_retired(gpointer context,gpointer event) {
    (void)context;return ((TestPopupEvent *)event)->retired;
}
static void test_popup_restore(gpointer context,gpointer event) {
    TestPopupEvent *copy=g_new(TestPopupEvent,1);*copy=*(TestPopupEvent *)event;
    g_queue_push_head(context,copy);
}
static void test_popup_queue(void) {
    GQueue events=G_QUEUE_INIT;
    PopupEventQueue queue={&events,test_popup_take,test_popup_retired,test_popup_restore,g_free};guint dropped;
    /* Interleaved retired and unrelated events: only retired input disappears. */
    for(guint i=0;i<6;i++) {TestPopupEvent *event=g_new(TestPopupEvent,1);*event=(TestPopupEvent){i,i%2==0};g_queue_push_tail(&events,event);}
    g_assert_true(popup_retire_events(&queue,4096,&dropped));g_assert_cmpuint(dropped,==,3);
    for(guint i=1;i<6;i+=2) {TestPopupEvent *event=g_queue_pop_head(&events);g_assert_cmpuint(event->sequence,==,i);g_free(event);}
    g_assert_true(g_queue_is_empty(&events));
    /* At the finite bound, admission stays closed even if the last item was
     * consumed: only an observed empty queue proves the retirement barrier. */
    for(guint i=0;i<4097;i++) {TestPopupEvent *event=g_new(TestPopupEvent,1);*event=(TestPopupEvent){i,i%2==0};g_queue_push_tail(&events,event);}
    g_assert_false(popup_retire_events(&queue,4096,&dropped));g_assert_cmpuint(dropped,==,2048);
    for(guint i=1;i<4096;i+=2) {TestPopupEvent *event=g_queue_pop_head(&events);g_assert_cmpuint(event->sequence,==,i);g_free(event);}
    g_assert_cmpuint(((TestPopupEvent *)g_queue_peek_head(&events))->sequence,==,4096);
    g_assert_true(popup_retire_events(&queue,4096,&dropped));g_assert_cmpuint(dropped,==,1);
    g_assert_true(g_queue_is_empty(&events));
    TestPopupEvent *last=g_new(TestPopupEvent,1);*last=(TestPopupEvent){1,TRUE};g_queue_push_tail(&events,last);
    g_assert_false(popup_retire_events(&queue,1,&dropped));g_assert_cmpuint(dropped,==,1);
    g_assert_true(popup_retire_events(&queue,1,&dropped));g_assert_cmpuint(dropped,==,0);
}
static guint test_popup_notifications;
static void test_popup_notify(GObject *object,GParamSpec *property,gpointer data) {
    (void)object;(void)property;if(popup_scope_current(data))test_popup_notifications++;
}
static void test_popup_callback_retirement(void) {
    GtkWidget *saved=popover;gboolean active=popup_active;guint64 lease=surface_gate.lease;
    g_assert_cmpuint(popup_signal_count,==,0);
    GObject *target=g_object_new(G_TYPE_OBJECT,NULL);
    popover=(GtkWidget *)target;popup_active=TRUE;surface_gate.lease=100;
    PopupScope old={100,popover};g_assert_true(popup_scope_current(&old));
    popup_connect(target,"notify",G_CALLBACK(test_popup_notify));
    g_signal_emit_by_name(target,"notify",NULL);g_assert_cmpuint(test_popup_notifications,==,1);
    popup_active=FALSE;g_assert_false(popup_scope_current(&old));popup_disconnect();
    g_assert_cmpuint(popup_signal_count,==,0);
    g_signal_emit_by_name(target,"notify",NULL);g_assert_cmpuint(test_popup_notifications,==,1);
    /* Reusing the same wrapper cannot revive the previous lease. */
    popup_active=TRUE;surface_gate.lease=101;g_assert_false(popup_scope_current(&old));
    for(guint i=0;i<6;i++)popup_connect(target,"notify",G_CALLBACK(test_popup_notify));
    g_signal_emit_by_name(target,"notify",NULL);g_assert_cmpuint(test_popup_notifications,==,7);
    popup_disconnect();g_signal_emit_by_name(target,"notify",NULL);g_assert_cmpuint(test_popup_notifications,==,7);
    g_assert_cmpuint(popup_signal_count,==,0);g_object_unref(target);
    popover=saved;popup_active=active;surface_gate.lease=lease;
}

int main(int argc,char **argv) {
    if (argc==2 && g_str_equal(argv[1],"--self-test")) {
        g_test_init(&argc,&argv,NULL);g_test_add_func("/host/assets",test_assets);g_test_add_func("/host/request-schema",test_requests);g_test_add_func("/host/qa-report-control-bounds",test_bridge_bounds);g_test_add_func("/host/surface-atomic-preflight",test_surface_preflight);g_test_add_func("/host/surface-manager-isolation",test_surface_managers);g_test_add_func("/host/surface-acknowledgements",test_surface_acknowledgements);g_test_add_func("/host/monitor-index-boundaries",test_monitor_index);g_test_add_func("/host/popup-logical-dimensions",test_popup_dimensions);g_test_add_func("/host/popup-retired-event-order-and-bound",test_popup_queue);g_test_add_func("/host/popup-callback-retirement",test_popup_callback_retirement);return g_test_run();
    }
    gboolean layer=FALSE;
    for (int i=1;i<argc;i++) {
        if (g_str_equal(argv[i],"--assets") && i+1<argc) asset_dir=argv[++i];
        else if (g_str_equal(argv[i],"--authority-config") && i+1<argc) authority_config=argv[++i];
        else if (g_str_equal(argv[i],"--backend") && i+1<argc) backend_path=argv[++i];
        else if (g_str_equal(argv[i],"--gpu-info")) gpu_info=TRUE;
        else if (g_str_equal(argv[i],"--qa-stay-open")) qa_stay=TRUE;
        else if (g_str_equal(argv[i],"--monitor-index") && i+1<argc) {if (!parse_monitor_index(argv[++i],&monitor_index)) {g_printerr("Invalid startup monitor index\n");return 2;}}
        else if (g_str_equal(argv[i],"--layer")) layer=TRUE;
        else if (g_str_equal(argv[i],"--surface-experiment")) {surface_experiment=TRUE;layer=TRUE;}
        else if (g_str_equal(argv[i],"--qa-exit-after-render")) qa_exit=TRUE;
        else { g_printerr("Unknown argument\n");return 2; }
    }
    if (!gpu_info && (!authority_config || !backend_path)) { g_printerr("Authority config and reviewed backend required\n");return 2; }
    if (!asset_dir) { g_printerr("--assets requires a bundled asset directory\n");return 2; }
    if (!gtk_init_check(NULL,NULL)) { g_printerr("GTK display unavailable\n");return 2; }
    if (layer && !gtk_layer_is_supported()) { g_printerr("Layer shell unavailable\n");return 2; }
    if (monitor_index>=0 && !layer) {g_printerr("Explicit monitor requires a layer surface\n");return 2;}
    if (layer) {
        owned_display=gdk_display_get_default();
        if (monitor_index>=0) owned_monitor=gdk_display_get_monitor(owned_display,monitor_index);
        else {owned_monitor=gdk_display_get_primary_monitor(owned_display);if (!owned_monitor) owned_monitor=gdk_display_get_monitor(owned_display,0);}
        if (!owned_monitor || !GDK_IS_WAYLAND_MONITOR(owned_monitor) || !gdk_wayland_monitor_get_wl_output(owned_monitor)) {g_printerr("Requested Wayland monitor unavailable\n");return 2;}
        g_object_ref(owned_monitor);
        GdkRectangle geometry;gdk_monitor_get_geometry(owned_monitor,&geometry);
        g_print("output-owner: startup-index=%d geometry=%d,%d,%d,%d scale=%d model=%s\n",monitor_index,geometry.x,geometry.y,geometry.width,geometry.height,gdk_monitor_get_scale_factor(owned_monitor),gdk_monitor_get_model(owned_monitor)?gdk_monitor_get_model(owned_monitor):"unknown");fflush(stdout);
        monitor_removed_handler=g_signal_connect(owned_display,"monitor-removed",G_CALLBACK(output_removed),NULL);
        monitor_geometry_handler=g_signal_connect(owned_monitor,"notify::geometry",G_CALLBACK(output_geometry_changed),NULL);
    }
    WebKitWebContext *context=webkit_web_context_new_ephemeral();
    webkit_web_context_set_sandbox_enabled(context,TRUE);
    webkit_web_context_register_uri_scheme(context,"elm-shell",scheme,NULL,NULL);
    WebKitSecurityManager *security=webkit_web_context_get_security_manager(context);
    webkit_security_manager_register_uri_scheme_as_local(security,"elm-shell");
    webkit_security_manager_register_uri_scheme_as_secure(security,"elm-shell");
    WebKitUserContentManager *manager=webkit_user_content_manager_new();primary_manager=manager;
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
        gtk_layer_init_for_window(GTK_WINDOW(window));gtk_layer_set_monitor(GTK_WINDOW(window),owned_monitor);gtk_layer_set_namespace(GTK_WINDOW(window),"elm-shell-recovery-v17");
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
        popup_manager=webkit_user_content_manager_new();
        if (qa_exit) {WebKitUserScript *qa=webkit_user_script_new("window.elmHostQA=true;",WEBKIT_USER_CONTENT_INJECT_TOP_FRAME,WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START,NULL,NULL);webkit_user_content_manager_add_script(popup_manager,qa);webkit_user_script_unref(qa);}
        g_signal_connect(popup_manager,"script-message-received::native",G_CALLBACK(receive),NULL);
        if (!webkit_user_content_manager_register_script_message_handler(popup_manager,"native")) return 2;
        popup_view=WEBKIT_WEB_VIEW(g_object_new(WEBKIT_TYPE_WEB_VIEW,"web-context",context,"user-content-manager",popup_manager,"settings",settings,NULL));
        g_object_ref_sink(popup_view);
        g_signal_connect(popup_view,"decide-policy",G_CALLBACK(policy),NULL);
        g_signal_connect(popup_view,"web-process-terminated",G_CALLBACK(terminated),NULL);
        webkit_web_view_set_background_color(popup_view,&backdrop);
        g_signal_connect(view,"button-press-event",G_CALLBACK(retain_event),NULL);
        g_signal_connect(view,"key-press-event",G_CALLBACK(retain_event),NULL);
        gtk_widget_set_size_request(GTK_WIDGET(view),-1,48);
        gtk_container_add(GTK_CONTAINER(window),GTK_WIDGET(view));gtk_widget_show_all(window);
        webkit_web_view_load_uri(popup_view,"elm-shell://app/popup.html");
        g_print("surface-policy: bar-exclusive=48 bar-keyboard=none popup-modal=1 single-controller=1\n");
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
        /* Keep draining stdout while the child handles normal stdin EOF.
         * Removing the reader first can itself block delivery and child exit. */
        gint64 write_until=g_get_monotonic_time()+500000;
        while (active_request && g_get_monotonic_time()<write_until) { while (g_get_monotonic_time()<write_until && g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        g_output_stream_close(g_subprocess_get_stdin_pipe(backend),NULL,NULL);
        /* One process-drain cap, not a fresh deadline for queued operations.
         * Native requests retain their own 3s deadline. A receipt held past
         * this cap remains conservative journal uncertainty, never replay. */
        gint64 backend_until=g_get_monotonic_time()+3500000;
        while (!backend_done && g_get_monotonic_time()<backend_until) { while (!backend_done && g_get_monotonic_time()<backend_until && g_main_context_iteration(NULL,FALSE)) {} g_usleep(1000); }
        if (!backend_done) { failed=TRUE;g_subprocess_force_exit(backend);g_subprocess_wait(backend,NULL,NULL); }
        if (backend_source) { g_source_remove(backend_source);backend_source=0; }
    }
    g_queue_clear_full(&requests,g_free);
    if (popup_active) popup_hide();
    popup_release_retired();
    if (popup_view) g_object_unref(popup_view);
    if (popup_manager) g_object_unref(popup_manager);
    if (surface_snapshot) json_node_unref(surface_snapshot);
    if (pending_focus) json_node_unref(pending_focus);
    if (issued_focus) json_node_unref(issued_focus);
    if (bar_event) gdk_event_free(bar_event);
    if (monitor_geometry_handler) g_signal_handler_disconnect(owned_monitor,monitor_geometry_handler);
    if (monitor_removed_handler) g_signal_handler_disconnect(owned_display,monitor_removed_handler);
    gtk_widget_destroy(window);g_clear_object(&owned_monitor);g_object_unref(manager);g_object_unref(context);
    gint64 cleanup_until=g_get_monotonic_time()+500000;
    while (g_get_monotonic_time()<cleanup_until) { while (g_main_context_iteration(NULL,FALSE)) {} g_usleep(5000); }
    g_print("host-exit: failure=%d rendered=%d\n",failed,reported);fflush(stdout);
    return failed || (qa_exit && !reported);
}
