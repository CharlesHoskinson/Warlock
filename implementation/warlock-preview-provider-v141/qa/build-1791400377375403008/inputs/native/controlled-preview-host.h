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
static guint64 controlled_current_epoch(void) {return controlled_epoch;}
static guint64 controlled_navigation;
static guint controlled_source;
static guint controlled_poll_stage;
static gboolean controlled_uncertain,controlled_initialized;
static gboolean controlled_retiring,controlled_retired;
static gboolean controlled_failure_draining;
static gboolean controlled_reload_retiring;
static gboolean controlled_qa_reload_requested;
static char *controlled_last_visual;
static char *controlled_last_private_status;

/* Explicit QA-only actual original URI reader. It supplies no Native fact,
 * ticket, grant or settlement. The original GIO reader itself keeps physical
 * custody until the private monotonic release stimulus closes that reader. */
static GInputStream *controlled_held_reader;
static char *controlled_held_uri;
static gboolean controlled_reader_probed,controlled_reader_released;
static gboolean controlled_reader_hold(GError **error) {
    if(!qa_controlled_reader_path || controlled_held_reader || controlled_reader_released)return TRUE;
    if(qa_reader_control(qa_controlled_reader_path)!=QA_READER_HOLD) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled reader hold stimulus required");return FALSE;
    }
    g_autofree char *identity=g_strdup_printf("family:%" G_GUINT64_FORMAT,qa_import_subjects[0]);
    g_autofree char *uri=NULL;gsize length=0;guint8 first=0;
    if(!warlock_imported_clients_uri(imported_clients,identity,&uri,error) || !uri || !*uri)return FALSE;
    controlled_held_reader=preview_uri_router_open(controlled_router,popup_view,uri,&length,error);
    if(!controlled_held_reader)return FALSE;
    controlled_held_uri=g_strdup(uri);
    if(g_input_stream_read(controlled_held_reader,&first,1,NULL,error)!=1 || first!=137) {
        if(!error || !*error){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled PNG reader byte required");}
        return FALSE;
    }
    g_print("controlled-native-reader-held: epoch=%" G_GUINT64_FORMAT " actualGIO=1 firstByte=%u bytes=%zu physicalSettlement=0\n",controlled_epoch,first,length);fflush(stdout);return TRUE;
}
static gboolean controlled_reader_tick(GError **error) {
    if(!controlled_held_reader)return TRUE;
    QAReaderControl control=qa_reader_control(qa_controlled_reader_path);
    if(control==QA_READER_INVALID || (control==QA_READER_HOLD && controlled_reader_probed) || (control==QA_READER_RELEASE && !controlled_reader_probed)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_INVALID_DATA,"Original controlled reader monotonic stimulus required");return FALSE;
    }
    if(control==QA_READER_PROBE && !controlled_reader_probed) {
        GError *held_error=NULL,*fresh_error=NULL;guint8 byte=0;gsize length=0;
        gssize read=g_input_stream_read(controlled_held_reader,&byte,1,NULL,&held_error);
        GInputStream *fresh=preview_uri_router_open(controlled_router,popup_view,controlled_held_uri,&length,&fresh_error);
        const gboolean held_denied=read==-1 && g_error_matches(held_error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED);
        const gboolean fresh_denied=!fresh && g_error_matches(fresh_error,G_IO_ERROR,G_IO_ERROR_PERMISSION_DENIED);
        g_clear_error(&held_error);g_clear_error(&fresh_error);
        if(fresh){g_input_stream_close(fresh,NULL,NULL);g_object_unref(fresh);}
        controlled_reader_probed=TRUE;
        g_print("controlled-native-reader-probed: epoch=%" G_GUINT64_FORMAT " heldRead=%zd heldDenied=%d freshDenied=%d actualGIO=1 physicalSettlement=0\n",controlled_epoch,read,held_denied,fresh_denied);fflush(stdout);
    }
    if(control==QA_READER_RELEASE) {
        if(!g_input_stream_close(controlled_held_reader,NULL,error))return FALSE;
        g_clear_object(&controlled_held_reader);controlled_reader_released=TRUE;g_clear_pointer(&controlled_held_uri,g_free);
        g_print("controlled-native-reader-released: epoch=%" G_GUINT64_FORMAT " originalCloseCalls=1 nativeGrantReset=0\n",controlled_epoch);fflush(stdout);
    }
    return TRUE;
}

typedef struct {GObject *view;GAsyncResult *result;ClientSnapshot *snapshot;} ControlledDelayedSnapshot;
static ControlledDelayedSnapshot *controlled_delayed_snapshot;
static gboolean controlled_snapshot_held_once;
static gboolean controlled_delay_snapshot(GObject *object,GAsyncResult *result,ClientSnapshot *snapshot) {
    if(!qa_controlled_delayed_snapshot || !qa_controlled_preview || controlled_snapshot_held_once || shutting_down || !snapshot->controlled_visual)return FALSE;
    controlled_snapshot_held_once=TRUE;controlled_delayed_snapshot=g_new(ControlledDelayedSnapshot,1);
    *controlled_delayed_snapshot=(ControlledDelayedSnapshot){g_object_ref(object),g_object_ref(result),snapshot};
    /* Preserve the actual result and original completion scope. No finish,
     * replacement snapshot, artifact or policy/native settlement occurs here. */
    g_print("controlled-native-snapshot-held: actualResult=1 retainedResults=1 finishCalls=0\n");fflush(stdout);return TRUE;
}
static void controlled_release_snapshot(void) {
    ControlledDelayedSnapshot *row=controlled_delayed_snapshot;if(!row)return;
    controlled_delayed_snapshot=NULL;
    if(qa_controlled_reopened_snapshot) {
        g_print("controlled-native-snapshot-crossed-realm: retainedEpoch=%" G_GUINT64_FORMAT " currentEpoch=%" G_GUINT64_FORMAT " retainedNavigation=%" G_GUINT64_FORMAT " currentNavigation=%" G_GUINT64_FORMAT " replacedView=%d originalResult=1 originalFinishCalls=0 nativeSettlement=0\n",row->snapshot->controlled_epoch,controlled_epoch,row->snapshot->controlled_navigation,controlled_navigation,row->view!=G_OBJECT(popup_view));fflush(stdout);
    }
    client_snapshot_complete(row->view,row->result,row->snapshot);
    g_object_unref(row->view);g_object_unref(row->result);g_free(row);
    g_print("controlled-native-snapshot-released: retainedResults=0 originalFinishCalls=1\n");fflush(stdout);
}
typedef struct {
    WebKitWebView *view;GtkWidget *popup;GdkFrameClock *clock;gulong handler;
    guint64 epoch,navigation,publication,lease;char *visual;
} ControlledPaintObservation;
static ControlledPaintObservation *controlled_paint;
static void controlled_paint_free(gpointer data,GClosure *closure) {
    (void)closure;ControlledPaintObservation *row=data;
    g_object_unref(row->view);g_object_unref(row->popup);g_object_unref(row->clock);g_free(row->visual);g_free(row);
}
static void controlled_paint_cancel(void) {
    ControlledPaintObservation *row=controlled_paint;if(!row)return;
    controlled_paint=NULL;g_signal_handler_disconnect(row->clock,row->handler);
}
static void controlled_after_paint(GdkFrameClock *clock,gpointer data) {
    ControlledPaintObservation *row=data;
    if(controlled_paint!=row)return;
    if(clock==row->clock && row->view==popup_view && row->popup==popover && row->epoch==controlled_epoch && row->navigation==controlled_navigation &&
       !shutting_down && !controlled_uncertain && controlled_initialized && surface_popup_ready() && gtk_widget_get_mapped(row->popup) &&
       row->publication==surface_gate.publication && row->lease==surface_gate.lease && !g_strcmp0(row->visual,controlled_last_visual)) {
        GError *error=NULL;WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,&error);
        GdkWindow *native=gtk_widget_get_window(row->popup);
        if(native && policy && warlock_visual_channel_current(controlled_visual,policy,G_OBJECT(row->view),&error)) {
            gint x=0,y=0;gdk_window_get_origin(native,&x,&y); // API return value is not meaningful.
            const gint64 frame=gdk_frame_clock_get_frame_counter(clock);
            const double opacity=gtk_widget_get_opacity(GTK_WIDGET(row->view));
            char opacity_text[G_ASCII_DTOSTR_BUF_SIZE];g_ascii_dtostr(opacity_text,sizeof opacity_text,opacity);
            g_print("controlled-native-paint-observation: {\"nativeEpoch\":\"%" G_GUINT64_FORMAT "\",\"navigation\":\"%" G_GUINT64_FORMAT "\",\"publication\":\"%" G_GUINT64_FORMAT "\",\"lease\":\"%" G_GUINT64_FORMAT "\",\"gtkFrame\":\"%" G_GINT64_FORMAT "\",\"x\":%d,\"y\":%d,\"width\":%d,\"height\":%d,\"opacity\":%s,\"gtkAfterPaint\":true,\"physicalFrameQualified\":false}\n",
                row->epoch,row->navigation,row->publication,row->lease,frame,x,y,gdk_window_get_width(native),gdk_window_get_height(native),opacity_text);fflush(stdout);
        }
        g_clear_error(&error);
    }
    controlled_paint_cancel();
}
static void controlled_paint_request(void) {
    controlled_paint_cancel();
    if(!popover || !controlled_driver || !controlled_visual || !controlled_initialized || controlled_uncertain || !surface_popup_ready() || !controlled_last_visual)return;
    GdkFrameClock *clock=gtk_widget_get_frame_clock(popover);if(!clock)return;
    ControlledPaintObservation *row=g_new0(ControlledPaintObservation,1);
    row->view=g_object_ref(popup_view);row->popup=g_object_ref(popover);row->clock=g_object_ref(clock);
    row->epoch=controlled_epoch;row->navigation=controlled_navigation;row->publication=surface_gate.publication;row->lease=surface_gate.lease;row->visual=g_strdup(controlled_last_visual);
    controlled_paint=row;row->handler=g_signal_connect_data(clock,"after-paint",G_CALLBACK(controlled_after_paint),row,controlled_paint_free,0);
    /* A private observation requests a GTK repaint. It does not issue a preview
     * effect or prove Wayland/hardware presentation, and cannot open the curtain. */
    gtk_widget_queue_draw(popover);
}
static void controlled_input_free(ControlledInput *row) {g_free(row->wire);g_free(row);}
static void controlled_curtain(void) {
    if(popup_view)gtk_widget_set_opacity(GTK_WIDGET(popup_view),0.0);
    /* This is an actual native setter, not a qualified Wayland/frame barrier.
     * Nothing in this route raises opacity based on decoder/RAF acceptance. */
}
static void controlled_fault(GError *error) {
    controlled_curtain();controlled_paint_cancel();controlled_uncertain=TRUE;controlled_release_snapshot();
    client_failure(error?error:g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Controlled host custody uncertain"));
}
static void controlled_snapshot_failure(GError *error) {
    /* The matching renderer failed; original Native duties are still known.
     * Keep their existing poll/receipt path alive instead of exiting early.
     * An uncertain native result still uses the original strict refusal path. */
    g_printerr("Native client producer failed: %s\n",error?error->message:"Owner unavailable");g_clear_error(&error);
    failed=TRUE;controlled_failure_draining=TRUE;controlled_retiring=TRUE;
    controlled_curtain();controlled_paint_cancel();controlled_initialized=FALSE;
    GError *native_error=NULL;
    if(!controlled_driver || !controlled_visual ||
       !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(popup_view),&native_error) ||
       !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&native_error)) {
        controlled_fault(native_error);return;
    }
    g_clear_pointer(&controlled_last_visual,g_free);
    g_print("controlled-native-current-failure-drain: epoch=%" G_GUINT64_FORMAT " quarantine=1 originalNative=1 failureRetained=1 inferredSettlement=0\n",controlled_epoch);fflush(stdout);
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
    if(!controlled_driver || controlled_uncertain || controlled_retired)return;
    controlled_curtain();controlled_paint_cancel();
    GError *error=NULL;
    if(controlled_visual && !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(popup_view),&error)) {controlled_fault(error);return;}
    g_clear_pointer(&controlled_last_visual,g_free);
    /* Release the one actual QA-held result only after native projection
     * invalidation. Its original completion must reject stale pixels. */
    if(!surface_popup_ready() && !qa_controlled_reopened_snapshot)controlled_release_snapshot();
    if(!surface_popup_ready()) {
        controlled_retiring=TRUE;
        if(!warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&error)) {controlled_fault(error);return;}
    }
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
    if(qa_controlled_reload && controlled_driver && !controlled_retired) {
        g_print("controlled-native-qa-reload-start: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " initialized=%d sameView=1 actualLoadStarted=1 uri=%s inferredSettlement=0\n",controlled_epoch,controlled_navigation,controlled_initialized,webkit_web_view_get_uri(target));fflush(stdout);
    }
    if(controlled_driver && !controlled_retired) {
        /* Reload discards renderer authority, never Native custody. Only this
         * trusted document with known duties may keep its original drain loop.
         * Unexpected navigation or uncertain/failing ownership stays fatal. */
        if(controlled_uncertain || controlled_failure_draining ||
           g_strcmp0(webkit_web_view_get_uri(target),"elm-shell://app/controlled-popup.html") ||
           (!controlled_initialized && !controlled_reload_retiring)) {
            controlled_fault(g_error_new_literal(G_IO_ERROR,G_IO_ERROR_FAILED,"Renderer navigation lacks known original reload custody"));return;
        }
        if(controlled_reload_retiring)return; // Later reload cannot cancel retirement.
        controlled_reload_retiring=TRUE;controlled_retiring=TRUE;controlled_initialized=FALSE;
        controlled_paint_cancel();GError *error=NULL;
        if(!controlled_visual ||
           !warlock_visual_channel_invalidate(controlled_visual,G_OBJECT(target),&error) ||
           !warlock_policy_driver_quarantine(controlled_driver,controlled_epoch,&error)) {
            controlled_fault(error);return;
        }
        g_clear_pointer(&controlled_last_visual,g_free);
        g_print("controlled-native-reload-quarantine: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " originalNative=1 samePopup=1 inferredSettlement=0\n",controlled_epoch,controlled_navigation);fflush(stdout);
        /* Original tick/receipts/strict close decide when to replace the view.
         * No grant, epoch, policy, snapshot ordinal or native fact is reset. */
    }
}
static gboolean controlled_open(GError **error) {
    guint64 publication,lease;
    if(!popup_ready || !surface_popup_ready() || !popup_owner || !popup_owner->active ||
       !client_frame_target(surface_snapshot,qa_import_subjects[0],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)return TRUE;
    controlled_curtain();
    const gboolean reopening=controlled_retired;
    const guint64 previous_epoch=controlled_epoch;
    WarlockPreviewPolicy *original_policy=reopening?warlock_policy_driver_policy(controlled_driver,error):NULL;
    if(reopening && !original_policy)return FALSE;
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
    if(reopening) {
        if(!warlock_policy_driver_reopen(&controlled_driver,outbox_source,outbox_length,imported_clients,preview_bootstrap,popup_view,grant,error))return FALSE;
        if(warlock_policy_driver_policy(controlled_driver,error)!=original_policy) {
            if(!error || !*error){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Original persistent policy owner changed on native realm reopen");}
            return FALSE;
        }
    } else controlled_driver=warlock_policy_driver_new(policy_source,policy_length,outbox_source,outbox_length,imported_clients,preview_bootstrap,popup_view,grant,error);
    /* A non-null uncertain driver retains live custody. Never close owner directly. */
    if(!controlled_driver || (error && *error))return FALSE;
    controlled_retired=FALSE;controlled_retiring=FALSE;controlled_initialized=FALSE;controlled_reload_retiring=FALSE;
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
    if(reopening) {g_print("controlled-native-reopened: previousEpoch=%" G_GUINT64_FORMAT " nativeEpoch=%" G_GUINT64_FORMAT " samePolicy=1 sameBinding=1 originalNative=1 grantResets=0 rendererPolicies=0\n",previous_epoch,controlled_epoch);fflush(stdout);}
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
    if(!warlock_policy_driver_inspect(controlled_driver,&state,error) || (!controlled_retired && !imported_report_status(error)))return FALSE;
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
    if(kind && g_str_equal(kind,"preview-image-report")) {
        if(manager!=popup_manager || !qa_client_snapshot || !controlled_driver || !controlled_visual || !controlled_initialized || controlled_uncertain || !surface_popup_ready())return TRUE;
        GError *error=NULL;WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,&error);
        if(policy && warlock_visual_channel_current(controlled_visual,policy,G_OBJECT(popup_view),&error) && imported_image_report(object) && !controlled_reader_hold(&error)) {controlled_fault(error);return TRUE;}
        g_clear_error(&error);return TRUE;
    }
    if(!kind || !g_str_equal(kind,"native-preview-projection-accepted"))return FALSE;
    if(manager!=popup_manager || !controlled_driver || !controlled_visual || !controlled_initialized || controlled_uncertain || strlen(text)>4096)return TRUE;
    GError *error=NULL;WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,&error);
    if(policy && warlock_visual_channel_ack(controlled_visual,policy,G_OBJECT(popup_view),text,&error)) {
        g_print("controlled-renderer-applied: originalContext=1 currentProjection=1 physicalReveal=0\n");fflush(stdout);
        controlled_paint_request();
        /* Explicit QA only: consume the original retained result once after a
         * later original realm/view receives its own current native projection.
         * Original finish/scope rejection owns the old result; no native fact,
         * grant, effect or physical settlement is supplied by this stimulus. */
        if(qa_controlled_reopened_snapshot && controlled_delayed_snapshot &&
           controlled_delayed_snapshot->snapshot->controlled_epoch<controlled_epoch &&
           controlled_delayed_snapshot->view!=G_OBJECT(popup_view))controlled_release_snapshot();
    }
    g_clear_error(&error);return TRUE;
}
static gboolean controlled_snapshot_prepare(ClientSnapshot *snapshot,GError **error) {
    WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,error);
    if(!policy || !controlled_initialized || controlled_uncertain || !controlled_last_visual || !surface_popup_ready() ||
       !warlock_visual_channel_current(controlled_visual,policy,G_OBJECT(popup_view),error))return FALSE;
    snapshot->controlled_visual=g_strdup(controlled_last_visual);
    snapshot->controlled_epoch=controlled_epoch;snapshot->controlled_navigation=controlled_navigation;return TRUE;
}
static gboolean controlled_snapshot_needed(void) {
    /* Private evidence bookkeeping only. Never reset an original snapshot
     * ordinal or infer native job/physical settlement from artifact completion. */
    return controlled_initialized && !controlled_retired && controlled_epoch && controlled_snapshot_written_epoch!=controlled_epoch;
}
static gboolean controlled_snapshot_matches(ClientSnapshot *snapshot,GObject *object) {
    if(object!=G_OBJECT(popup_view) || shutting_down || controlled_uncertain || !controlled_initialized || !surface_popup_ready() ||
       snapshot->controlled_epoch!=controlled_epoch || snapshot->controlled_navigation!=controlled_navigation ||
       g_strcmp0(snapshot->controlled_visual,controlled_last_visual))return FALSE;
    GError *error=NULL;WarlockPreviewPolicy *policy=warlock_policy_driver_policy(controlled_driver,&error);
    gboolean matches=policy && warlock_visual_channel_current(controlled_visual,policy,object,&error);
    g_clear_error(&error);return matches;
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
        if(controlled_retiring || !surface_popup_ready() || !popup_owner || !popup_owner->active || !client_frame_target(surface_snapshot,qa_import_subjects[0],&publication,&lease) || publication!=surface_gate.publication || lease!=surface_gate.lease)publication=lease=0;
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
        /* Sticky old-realm retirement survives every later popup intent.
         * Its original detachment facts/receipts must keep progressing; only
         * strict Native closure can admit that later popup as a fresh realm. */
        if(subject_present && (controlled_retiring || !surface_popup_ready())) {
            g_autofree char *facts=NULL;
            if(!warlock_imported_clients_detachment_inventory(imported_clients,popup_view,identity,&facts,error))return FALSE;
            events=g_strdup_printf("[%s]",facts);
        } else if(!warlock_imported_clients_detachment_pending(imported_clients,delivery,popup_view,&events,error))return FALSE;
        break;
    }
    controlled_queue(g_steal_pointer(&events),FALSE);return !controlled_uncertain;
}
static gboolean controlled_replace_retired_renderer(GError **error) {
    GtkWidget *parent=gtk_widget_get_parent(GTK_WIDGET(popup_view));
    if(!controlled_retired || (parent && parent!=popover)) {
        g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Only original strictly retired popup renderer may be replaced");return FALSE;
    }
    WebKitWebView *retired=popup_view;WebKitUserContentManager *retired_manager=popup_manager;
    const gint width=gtk_widget_get_allocated_width(GTK_WIDGET(retired)),height=gtk_widget_get_allocated_height(GTK_WIDGET(retired));
    controlled_curtain();controlled_paint_cancel();
    WebKitUserContentManager *manager=webkit_user_content_manager_new();manager_configure(manager);
    if(failed) {g_object_unref(manager);g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Later original renderer manager unavailable");return FALSE;}
    if(qa_client_snapshot || qa_import_subjects[0]) {
        WebKitUserScript *script=webkit_user_script_new("window.elmPreviewQA=true;",WEBKIT_USER_CONTENT_INJECT_TOP_FRAME,WEBKIT_USER_SCRIPT_INJECT_AT_DOCUMENT_START,NULL,NULL);
        webkit_user_content_manager_add_script(manager,script);webkit_user_script_unref(script);
    }
    WebKitWebView *replacement=shared_child(manager);g_object_ref_sink(replacement);
    g_signal_handlers_disconnect_by_func(retired,G_CALLBACK(policy),NULL);
    g_signal_handlers_disconnect_by_func(retired,G_CALLBACK(terminated),NULL);
    g_signal_handlers_disconnect_by_func(retired,G_CALLBACK(shared_context_event),NULL);
    g_signal_handlers_disconnect_by_func(retired,G_CALLBACK(controlled_load_changed),NULL);
    g_signal_handlers_disconnect_by_func(retired_manager,G_CALLBACK(shared_receive),NULL);
    webkit_user_content_manager_unregister_script_message_handler(retired_manager,"native");
    webkit_web_view_stop_loading(retired);
    popup_view=replacement;popup_manager=manager;popup_ready=FALSE;applied_publication=0;applied_lease=0;
    g_signal_connect(replacement,"decide-policy",G_CALLBACK(policy),NULL);
    g_signal_connect(replacement,"web-process-terminated",G_CALLBACK(terminated),NULL);
    g_signal_connect(replacement,"event",G_CALLBACK(shared_context_event),NULL);
    g_signal_connect(replacement,"load-changed",G_CALLBACK(controlled_load_changed),NULL);
    controlled_curtain();
    if(parent) {
        /* The current popup may already carry a later user intent. Keep its
         * original lease/window/grab, but require fresh DOM admission on the
         * new fixed-grant context before its native preview factory can open. */
        g_object_ref(retired);gtk_container_remove(GTK_CONTAINER(parent),GTK_WIDGET(retired));
        gtk_widget_set_size_request(GTK_WIDGET(replacement),width,height);
        gtk_container_add(GTK_CONTAINER(parent),GTK_WIDGET(replacement));g_object_unref(replacement);
        gtk_widget_show_all(parent);gtk_widget_grab_focus(GTK_WIDGET(replacement));
    }
    gtk_widget_destroy(GTK_WIDGET(retired));g_object_unref(retired);g_object_unref(retired_manager);
    webkit_web_view_load_uri(replacement,"elm-shell://app/controlled-popup.html");
    g_print("controlled-native-replacement-admission: retiredEpoch=%" G_GUINT64_FORMAT " pendingPopup=%d publication=%" G_GUINT64_FORMAT " lease=%" G_GUINT64_FORMAT " freshDOMRequired=1\n",controlled_epoch,parent!=NULL,surface_gate.publication,surface_gate.lease);fflush(stdout);
    g_print("controlled-renderer-context-replaced: retiredEpoch=%" G_GUINT64_FORMAT " nativeGrantReset=0 navigationReset=0 snapshotOrdinalReset=0\n",controlled_epoch);fflush(stdout);return TRUE;
}
static gboolean controlled_retire_current(GError **error) {
    gboolean ready=FALSE;
    if(!warlock_policy_driver_retirement_ready(controlled_driver,&ready,error))return FALSE;
    if(!ready)return TRUE;
    controlled_curtain();controlled_paint_cancel();
    if(!qa_controlled_reopened_snapshot)controlled_release_snapshot();
    if(controlled_visual) {
        if(!warlock_visual_channel_detach(controlled_visual,G_OBJECT(popup_view),error) || !warlock_visual_channel_close(controlled_visual,error))return FALSE;
        controlled_visual=NULL;
    }
    if(!preview_uri_router_clear(controlled_router,error))return FALSE;
    preview_host_set_endpoint(NULL);preview_host_set_command_handler(NULL);
    if(!warlock_policy_driver_retire(controlled_driver,error))return FALSE;
    imported_clients=NULL;controlled_retired=TRUE;controlled_retiring=FALSE;controlled_initialized=FALSE;
    g_clear_pointer(&controlled_last_visual,g_free);g_clear_pointer(&controlled_last_private_status,g_free);g_clear_pointer(&imported_last_status,g_free);
    if(!controlled_report_status(error))return FALSE;
    g_print("controlled-native-realm-retired: epoch=%" G_GUINT64_FORMAT " samePolicyRetained=1 strictNativeClose=1 rendererGrantReused=0\n",controlled_epoch);fflush(stdout);
    if(controlled_failure_draining) {
        /* Original policy/physical/journal/confirmation close already passed.
         * Failure remains failure; do not reopen or construct a replacement. */
        g_print("controlled-native-current-failure-retired: epoch=%" G_GUINT64_FORMAT " failureRetained=1 originalStrictClose=1\n",controlled_epoch);fflush(stdout);
        gtk_main_quit();return TRUE;
    }
    return controlled_replace_retired_renderer(error);
}
static gboolean controlled_tick(gpointer unused) {
    (void)unused;
    if(shutting_down || controlled_uncertain) {controlled_source=0;return G_SOURCE_REMOVE;}
    GError *error=NULL;
    if(!controlled_driver || controlled_retired) {if(!controlled_open(&error))goto uncertain;return G_SOURCE_CONTINUE;}
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
    if(!controlled_reader_tick(&error) || !controlled_produce(&error))goto uncertain;
    if(!controlled_flush(&error))goto refused;
    if(!controlled_report_status(&error))goto uncertain;
    if(qa_controlled_reload && !controlled_qa_reload_requested && controlled_epoch==1 && controlled_initialized && !controlled_retiring && controlled_snapshot_written_epoch==controlled_epoch) {
        /* Explicit private QA only. First real snapshot is already consumed and
         * written; invoke the actual WebKit API, never manufacture a load event,
         * grant, native receipt, epoch or completion. Original handler decides. */
        controlled_qa_reload_requested=TRUE;
        g_print("controlled-native-qa-reload-requested: epoch=%" G_GUINT64_FORMAT " navigation=%" G_GUINT64_FORMAT " actualWebKitReload=1 snapshotWritten=1 inferredSettlement=0\n",controlled_epoch,controlled_navigation);fflush(stdout);
        webkit_web_view_reload(popup_view);
    }
    if(controlled_retiring && !controlled_retire_current(&error))goto uncertain;
    return G_SOURCE_CONTINUE;
refused:
    if(error && g_error_matches(error,G_IO_ERROR,G_IO_ERROR_WOULD_BLOCK)) {g_clear_error(&error);return G_SOURCE_CONTINUE;}
uncertain:
    controlled_fault(error);controlled_source=0;return G_SOURCE_REMOVE;
}
static gboolean controlled_close(GError **error) {
    controlled_curtain();controlled_paint_cancel();controlled_release_snapshot();
    if(controlled_source){g_source_remove(controlled_source);controlled_source=0;}
    if(controlled_held_reader || controlled_uncertain || !g_queue_is_empty(&controlled_pending)) {
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
