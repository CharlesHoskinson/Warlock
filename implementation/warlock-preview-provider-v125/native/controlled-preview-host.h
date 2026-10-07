/* Actual QA-only GTK/WebKit route. No second window policy; no physical reveal
 * until its separate native frame acceptance exists. Included by shared-host.c. */
#include "preview-policy-driver.h"
#include "preview-visual-channel.h"
typedef struct {char *wire;gboolean presentation;} ControlledInput;
static WarlockPolicyDriver *controlled_driver;
static WarlockVisualChannel *controlled_visual;
static PreviewURIRouter *controlled_router;
static GQueue controlled_pending=G_QUEUE_INIT;
static gsize controlled_pending_bytes;
static guint64 controlled_epoch;
static guint64 controlled_navigation;
static guint controlled_source;
static guint controlled_poll_stage;
static gboolean controlled_uncertain,controlled_initialized;
static char *controlled_last_visual;
static char *controlled_last_private_status;
static void controlled_input_free(ControlledInput *row) {g_free(row->wire);g_free(row);}
static void controlled_curtain(void) {
    if(popup_view)gtk_widget_set_opacity(GTK_WIDGET(popup_view),0.0);
    /* This is an actual native setter, not a qualified Wayland/frame barrier.
     * Nothing in this route raises opacity based on decoder/RAF acceptance. */
}
static void controlled_fault(GError *error) {
    controlled_curtain();controlled_uncertain=TRUE;
    client_failure(error?error:g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Controlled host custody uncertain"));
}
static gboolean controlled_wire_room(gsize bytes) {
    return !controlled_uncertain && controlled_pending_bytes<=16*1024*1024 && g_queue_get_length(&controlled_pending)<1065 &&
        bytes<=16*1024*1024-controlled_pending_bytes;
}
static gboolean controlled_frame_room(JsonNode *frame) {
    if(!qa_controlled_preview || !controlled_driver)return TRUE;
    g_autofree char *wire=json_to_string(frame,FALSE);
    return controlled_wire_room(strlen(wire));
}
static void controlled_queue(char *wire,gboolean presentation) {
    if(!wire || g_str_equal(wire,"[]")){g_free(wire);return;}
    /* Original producer output is kept exactly, even for an unexpected violated
     * bound. That exceptional custody is Unknown, never normal bounded success. */
    const gboolean room=controlled_wire_room(strlen(wire));
    ControlledInput *row=g_new(ControlledInput,1);*row=(ControlledInput){wire,presentation};
    g_queue_push_tail(&controlled_pending,row);controlled_pending_bytes+=strlen(wire);
    if(!room)controlled_fault(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_NO_SPACE,"Exact original controlled producer output retained beyond expected custody contract"));
}
static gboolean controlled_flush(GError **error) {
    while(!g_queue_is_empty(&controlled_pending)) {
        ControlledInput *row=g_queue_peek_head(&controlled_pending);
        gboolean accepted=row->presentation?warlock_policy_driver_presentation(controlled_driver,row->wire,error):warlock_policy_driver_native(controlled_driver,controlled_epoch,row->wire,error);
        if(!accepted)return FALSE; // Exact original row remains with host; no next poll.
        controlled_pending_bytes-=strlen(row->wire);g_queue_pop_head(&controlled_pending);controlled_input_free(row);
    }
    return TRUE;
}
static void controlled_frame_notice(JsonNode *frame) {
    if(!controlled_driver || controlled_uncertain)return;
    controlled_curtain();
    GError *error=NULL;
    if(controlled_visual && !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(popup_view),&error)) {controlled_fault(error);return;}
    g_clear_pointer(&controlled_last_visual,g_free);
    if(!surface_popup_ready() && !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&error)) {controlled_fault(error);return;}
    controlled_queue(json_to_string(frame,FALSE),TRUE);
}
static gboolean controlled_source_bytes(const char *name,char **bytes,gsize *length,GError **error) {
    int directory=open(asset_dir,O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
    int fd=directory<0?-1:openat(directory,name,O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if(directory>=0)close(directory);
    struct stat info;
    if(fd<0 || fstat(fd,&info)<0 || !S_ISREG(info.st_mode) || info.st_size<=0 || info.st_size>4*1024*1024) {
        if(fd>=0)close(fd);
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Original controlled native bundle bytes unavailable");return FALSE;
    }
    *length=(gsize)info.st_size;*bytes=g_malloc(*length+1);gsize position=0;
    while(position<*length) {ssize_t count=read(fd,*bytes+position,*length-position);if(count<=0)break;position+=(gsize)count;}
    close(fd);(*bytes)[*length]=0;
    if(position!=*length || memchr(*bytes,0,*length)) {g_clear_pointer(bytes,g_free);g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Incomplete or NUL native bundle source");return FALSE;}
    return TRUE;
}
typedef struct {WebKitWebView *view;guint64 epoch,navigation;} ControlledInitialization;
static void controlled_initialized_done(GObject *object,GAsyncResult *result,gpointer raw) {
    ControlledInitialization *attempt=raw;GError *error=NULL;
    JSCValue *value=webkit_web_view_evaluate_javascript_finish(WEBKIT_WEB_VIEW(object),result,&error);
    gboolean current=object==G_OBJECT(attempt->view) && attempt->view==popup_view && attempt->epoch==controlled_epoch && attempt->navigation==controlled_navigation && !shutting_down && !controlled_uncertain;
    if(current && value && jsc_value_is_boolean(value) && jsc_value_to_boolean(value) && !error) {
        controlled_initialized=TRUE;g_print("controlled-renderer-initialized: nativeEpoch=%" G_GUINT64_FORMAT " windowPolicies=0 physicalReveal=0\n",controlled_epoch);fflush(stdout);
    } else if(current) {controlled_fault(error);error=NULL;}
    g_clear_error(&error);g_clear_object(&value);g_object_unref(attempt->view);g_free(attempt);
}
static void controlled_load_changed(WebKitWebView *target,WebKitLoadEvent event,gpointer unused) {
    (void)unused;
    if(target!=popup_view || event!=WEBKIT_LOAD_STARTED)return;
    controlled_curtain();
    if(controlled_navigation==G_MAXUINT64) {controlled_fault(NULL);return;}
    controlled_navigation++;
    if(controlled_driver)controlled_fault(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Renderer navigation retains original live policy; reload recovery not qualified"));
}
static gboolean controlled_open(GError **error) {
    guint64 publication,lease;
    if(!popup_ready || !surface_popup_ready() || !popup_owner || !popup_owner->active ||
       !client_frame_target(surface_snapshot,qa_import_subjects[0],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)return TRUE;
    controlled_curtain();
    void *native=preview_host_native_transport(error),*endpoint=NULL;
    g_autofree char *events=NULL,*grant=NULL,*policy_source=NULL,*outbox_source=NULL,*renderer_grant=NULL;
    gsize policy_length=0,outbox_length=0;
    if(!native || !controlled_source_bytes("native-preview-policy.js",&policy_source,&policy_length,error) ||
       !controlled_source_bytes("native-preview-control-outbox.js",&outbox_source,&outbox_length,error))return FALSE;
    imported_clients=warlock_imported_clients_open_controlled(native,popup_view,qa_import_subjects[0],publication,lease,&events,&grant,&endpoint,error);
    if(!imported_clients || !preview_host_attach_delivery(endpoint,error))return FALSE;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!strict_json_load(parser,grant) || !surface_uint(json_object_get_member(json_node_get_object(json_parser_get_root(parser)),"receiverEpoch"),&controlled_epoch)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original native controlled grant epoch");return FALSE;
    }
    controlled_driver=warlock_policy_driver_new(policy_source,policy_length,outbox_source,outbox_length,imported_clients,preview_bootstrap,popup_view,grant,error);
    /* A non-null uncertain driver retains live custody. Never close owner directly. */
    if(!controlled_driver || (error && *error))return FALSE;
    preview_host_set_endpoint(endpoint);preview_host_set_command_handler(NULL);
    if(!preview_uri_router_bind(controlled_router,endpoint,popup_view,controlled_epoch,error))return FALSE;
    controlled_visual=warlock_visual_channel_new();
    WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,error);
    if(!policy || !warlock_visual_channel_attach(controlled_visual,policy,G_OBJECT(popup_view),&renderer_grant,error))return FALSE;
    controlled_queue(json_to_string(surface_snapshot,FALSE),TRUE);controlled_queue(g_steal_pointer(&events),FALSE);
    ControlledInitialization *attempt=g_new(ControlledInitialization,1);*attempt=(ControlledInitialization){g_object_ref(popup_view),controlled_epoch,controlled_navigation};
    g_autofree char *script=g_strdup_printf("window.initializeNativePreviewRenderer(%s);",renderer_grant);
    webkit_web_view_evaluate_javascript(popup_view,script,-1,NULL,NULL,NULL,controlled_initialized_done,attempt);
    g_print("controlled-native-start: subject=%" G_GUINT64_FORMAT " publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " epoch=%" G_GUINT64_FORMAT " physicalReveal=0\n",qa_import_subjects[0],publication,lease,controlled_epoch);fflush(stdout);
    return TRUE;
}
static gboolean controlled_visual_offer(GError **error) {
    if(!controlled_initialized)return TRUE;
    WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,error);g_autofree char *visual=NULL,*packet=NULL;
    if(!policy || !warlock_preview_policy_visual_projection(policy,&visual,error))return FALSE;
    if(controlled_last_visual && g_str_equal(visual,controlled_last_visual))return TRUE;
    if(!warlock_visual_channel_offer(controlled_visual,policy,G_OBJECT(popup_view),&packet,error))return FALSE;
    g_free(controlled_last_visual);controlled_last_visual=g_steal_pointer(&visual);
    g_autoptr(JsonParser) parser=json_parser_new();if(!strict_json_load(parser,packet))return FALSE;
    surface_eval(popup_view,"receiveNativeVisualProjection",json_parser_get_root(parser));return TRUE;
}
static gboolean controlled_report_status(GError **error) {
    g_autofree char *state=NULL;
    if(!warlock_policy_driver_inspect(controlled_driver,&state,error) || !imported_report_status(error))return FALSE;
    if(g_strcmp0(state,controlled_last_private_status)) {
        g_free(controlled_last_private_status);controlled_last_private_status=g_strdup(state);
        /* Private Native/QA evidence only. No diagnostic packet enters a JS port. */
        g_print("controlled-native-private-status: %s\n",state);fflush(stdout);
    }
    return TRUE;
}
static gboolean controlled_receive(WebKitUserContentManager *manager,const char *text,JsonObject *object) {
    if(!qa_controlled_preview)return FALSE;
    const char *kind=surface_text(json_object_get_member(object,"kind"),64,FALSE)?json_object_get_string_member(object,"kind"):NULL;
    if(!kind || !g_str_equal(kind,"native-preview-projection-accepted"))return FALSE;
    if(manager!=popup_manager || !controlled_driver || !controlled_visual || !controlled_initialized || controlled_uncertain || strlen(text)>4096)return TRUE;
    GError *error=NULL;WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,&error);
    if(policy && warlock_visual_channel_ack(controlled_visual,policy,G_OBJECT(popup_view),text,&error)) {
        g_print("controlled-renderer-applied: originalContext=1 currentProjection=1 physicalReveal=0\n");fflush(stdout);
    }
    g_clear_error(&error);return TRUE;
}
static gboolean controlled_produce(GError **error) {
    g_autofree char *events=NULL,*facts=NULL,*identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[0]);
    void *delivery=warlock_preview_bootstrap_delivery(preview_bootstrap,popup_view,error);if(!delivery)return FALSE;
    /* The original C detachment removes its subject mapping before Elm has
     * processed the retained completion. Only stop identity-dependent producers;
     * keep every original journal, input and confirmation obligation alive. */
    if(!warlock_imported_clients_actor_counts(imported_clients,delivery,&facts,error))return FALSE;
    g_autoptr(JsonParser) inventory=json_parser_new();
    JsonNode *root=NULL,*subjects=NULL;
    if(strict_json_load(inventory,facts))root=json_parser_get_root(inventory);
    if(root && JSON_NODE_HOLDS_OBJECT(root))subjects=json_object_get_member(json_node_get_object(root),"subjects");
    if(!subjects || json_node_get_value_type(subjects)!=G_TYPE_INT64 || json_node_get_int(subjects)<0 || json_node_get_int(subjects)>1) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original single controlled subject inventory unavailable");return FALSE;
    }
    const gboolean subject_present=json_node_get_int(subjects)==1;
    switch(controlled_poll_stage++%4) {
    case 0: {
        if(!subject_present)break;
        guint64 publication=0,lease=0;
        if(!surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_import_subjects[0],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)publication=lease=0;
        if(!warlock_imported_clients_poll_at(imported_clients,identity,publication,lease,&events,error))return FALSE;
        break;
    }
    case 1:
        if(!warlock_preview_bootstrap_pending(preview_bootstrap,popup_view,&events,error))return FALSE;
        break;
    case 2:
        if(!warlock_imported_clients_retirement_poll(imported_clients,delivery,popup_view,&events,error))return FALSE;
        break;
    default:
        if(subject_present && !surface_popup_ready()) {
            g_autofree char *facts=NULL;
            if(!warlock_imported_clients_detachment_inventory(imported_clients,popup_view,identity,&facts,error))return FALSE;
            events=g_strdup_printf("[%s]",facts);
        } else if(!warlock_imported_clients_detachment_pending(imported_clients,delivery,popup_view,&events,error))return FALSE;
        break;
    }
    controlled_queue(g_steal_pointer(&events),FALSE);return !controlled_uncertain;
}
static gboolean controlled_tick(gpointer unused) {
    (void)unused;
    if(shutting_down || controlled_uncertain) {controlled_source=0;return G_SOURCE_REMOVE;}
    GError *error=NULL;
    if(!controlled_driver) {if(!controlled_open(&error))goto uncertain;return G_SOURCE_CONTINUE;}
    controlled_curtain();
    if(!controlled_flush(&error)) {
        if(!error || !g_error_matches(error,G_IO_ERROR,G_IO_ERROR_WOULD_BLOCK))goto uncertain;
        g_clear_error(&error);
    }
    for(guint step=0;step<16;step++) {
        gboolean progressed=FALSE;if(!warlock_policy_driver_step(controlled_driver,&progressed,&error))goto refused;
        if(!progressed)break;
    }
    if(!controlled_flush(&error))goto refused;
    if(!controlled_visual_offer(&error))goto refused;
    /* All producer outputs have one explicit custody point. Drain that queue
     * before obtaining another original native poll result. Never poll in a JS
     * callback or erase a refused batch. Native issuer remains the sole issuer. */
    if(!controlled_produce(&error))goto uncertain;
    if(!controlled_flush(&error))goto refused;
    if(!controlled_report_status(&error))goto uncertain;
    return G_SOURCE_CONTINUE;
refused:
    if(error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_WOULD_BLOCK)) {g_clear_error(&error);return G_SOURCE_CONTINUE;}
uncertain:
    controlled_fault(error);controlled_source=0;return G_SOURCE_REMOVE;
}
static gboolean controlled_close(GError **error) {
    controlled_curtain();
    if(controlled_source){g_source_remove(controlled_source);controlled_source=0;}
    if(controlled_uncertain || !g_queue_is_empty(&controlled_pending)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Controlled exact host input/uncertain custody prevents normal closure");return FALSE;
    }
    if(controlled_visual) {
        if(!warlock_visual_channel_detach(controlled_visual,G_OBJECT(popup_view),error) || !warlock_visual_channel_close(controlled_visual,error))return FALSE;
        controlled_visual=NULL;
    }
    /* Revoke future reader admission before deleting its borrowed endpoint.
     * Existing reader references still obey original physical closure gates. */
    if(!preview_uri_router_clear(controlled_router,error))return FALSE;
    if(controlled_driver) {
        if(!warlock_policy_driver_close(controlled_driver,error))return FALSE;
        controlled_driver=NULL;imported_clients=NULL;
    }
    g_clear_pointer(&controlled_last_visual,g_free);g_clear_pointer(&controlled_last_private_status,g_free);preview_uri_router_unref(controlled_router);controlled_router=NULL;return TRUE;
}
