#define ELM_SHARED_HOST_MAIN retained_shared_host_main
#include "/home/charles/Warlock/implementation/warlock/native/shared-host.c"

static GString *observed;
static void capture(const gchar *text) { g_string_append(observed,text); }
static gboolean observe_from(WebKitUserContentManager *manager,const char *name,const char *wire,const char *expected_reason) {
    SurfaceGate before=surface_gate;
    guint q=g_queue_get_length(&requests), batches=g_queue_get_length(&shared_batches);
    gboolean ready=backend_ready; GSubprocess *old_backend=backend;
    g_string_truncate(observed,0);
    shared_receive_text(manager,wire);
    gboolean untouched=memcmp(&before,&surface_gate,sizeof(before))==0 && q==g_queue_get_length(&requests)
        && batches==g_queue_get_length(&shared_batches) && ready==backend_ready && old_backend==backend && active_request==NULL;
    gboolean reason=strstr(observed->str,expected_reason)!=NULL;
    g_printerr("case=%s state_unchanged=%d refusal_recorded=%d log=%s\n",name,untouched,reason,observed->str);
    return untouched && reason;
}
static gboolean observe(const char *name,const char *wire,const char *expected_reason) {return observe_from(primary_manager,name,wire,expected_reason);}
int main(void) {
    int primary=0,popup=0;
    primary_manager=(WebKitUserContentManager *)&primary; popup_manager=(WebKitUserContentManager *)&popup;
    output_views=g_ptr_array_new(); surface_gate=(SurfaceGate){11,3,2}; backend_ready=FALSE;
    observed=g_string_new(""); g_set_print_handler(capture);
    gboolean malformed=observe("malformed-json","{bad","view-refused:");
    gboolean notobject=observe("non-object","[]","view-refused:");
    gboolean version=observe("unsupported-version","{\"viewProtocol\":2,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[],\"focus\":[]}","view-refused:");
    gboolean missing=observe("null-text",NULL,"view-refused: missing-text");
    gboolean scalar=observe("scalar-root","true","view-refused: non-object");
    gboolean duplicate=observe("duplicate-field","{\"viewProtocol\":1,\"viewProtocol\":1}","view-refused: duplicate-or-malformed-json");
    g_autofree char *large=g_strnfill(1048577,'x');
    gboolean bound=observe("transport-bound",large,"view-refused: transport-bound");
    g_autofree char *control=g_strnfill(4097,' ');
    g_autofree char *oversized=g_strconcat("{\"kind\":\"ignored\"}",control,NULL);
    gboolean smallbound=observe_from(popup_manager,"control-bound",oversized,"view-refused: control-bound");
    int foreign=0;gboolean origin=observe_from((WebKitUserContentManager *)&foreign,"foreign-origin","{\"kind\":\"ignored\"}","view-refused: origin");
    JSCContext *context=jsc_context_new();
    JSCValue *number=jsc_value_new_number(context,7),*null_value=jsc_value_new_null(context);
    gboolean typed=TRUE;
    for(guint i=0;i<2;i++) {
        SurfaceGate before=surface_gate;guint queued=g_queue_get_length(&requests),batches=g_queue_get_length(&shared_batches);
        g_string_truncate(observed,0);shared_receive_value(primary_manager,i?null_value:number);
        gboolean same=memcmp(&before,&surface_gate,sizeof(before))==0 && queued==g_queue_get_length(&requests) && batches==g_queue_get_length(&shared_batches) && backend==NULL && !backend_ready && active_request==NULL;
        gboolean reason=strstr(observed->str,"view-refused: type")!=NULL;typed=typed&&same&&reason;
        g_printerr("case=typed-%s state_unchanged=%d refusal_recorded=%d log=%s\n",i?"null":"number",same,reason,observed->str);
    }
    g_object_unref(number);g_object_unref(null_value);g_object_unref(context);
    int target=0;popup_view=(WebKitWebView *)&target;preview_test_view=popup_view;preview_owner=g_thread_self();
    preview_controls=(PreviewControl){0};preview_test_calls=0;preview_host_set_command_handler(preview_test_handler);
    const char *unsupported="{\"kind\":\"preview-commands\",\"previewProtocol\":9,\"entries\":[{\"identity\":\"family:1\",\"commands\":[]}]}";
    gboolean preview=observe_from(popup_manager,"unsupported-preview-version",unsupported,"preview-refused:");
    preview=preview&&preview_test_calls==0&&preview_controls.delivered==0;
    const char *malformed_preview="{\"kind\":\"preview-commands\",\"previewProtocol\":true,\"entries\":[{}]}";
    gboolean preview_shape=observe_from(popup_manager,"malformed-preview-version",malformed_preview,"preview-refused:")&&preview_test_calls==0;
    const char *legacy_extra="{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"entries\":[{}],\"extra\":true}";
    gboolean legacy=observe_from(popup_manager,"malformed-legacy-preview",legacy_extra,"preview-refused:")&&preview_test_calls==0;
    const char *ordinal_bad="{\"kind\":\"preview-commands\",\"previewProtocol\":2,\"controlOrdinal\":0,\"entries\":[{}]}";
    gboolean ordinal=observe_from(popup_manager,"malformed-preview-ordinal",ordinal_bad,"preview-refused:")&&preview_test_calls==0&&preview_controls.delivered==0;
    const char *valid_preview="{\"kind\":\"preview-commands\",\"previewProtocol\":1,\"entries\":[{\"identity\":\"family:1\",\"commands\":[]}]}";
    shared_receive_text(popup_manager,valid_preview);gboolean preview_positive=preview_test_calls==1;
    g_printerr("positive=current-preview-router handler_calls=%u returned=%d\n",preview_test_calls,preview_positive);
    shutting_down=TRUE;
    gboolean shutdown=observe("shutdown-non-preview","{\"kind\":\"ignored\"}","view-refused: shutdown");
    const char *acquire="{\"kind\":\"preview-commands\",\"previewProtocol\":2,\"controlOrdinal\":\"1\",\"entries\":[{\"identity\":\"family:1\",\"commands\":[{\"kind\":\"acquire\"}]}]}";
    gboolean retirement=observe_from(popup_manager,"retirement-acquire",acquire,"preview-refused: retirement")&&preview_test_calls==1&&preview_controls.delivered==1;
    g_printerr("positive=retirement-delivery delivered=%" G_GUINT64_FORMAT " handler_calls=%u returned=%d\n",preview_controls.delivered,preview_test_calls,retirement);
    shutting_down=FALSE;
    gboolean popup_closed=observe_from(popup_manager,"popup-not-ready","{\"kind\":\"ignored\"}","view-refused: popup-not-ready");
    preview_controls=(PreviewControl){0};
    preview_host_set_command_handler(NULL);popup_view=NULL;preview_test_view=NULL;preview_owner=NULL;
    g_set_print_handler(NULL);g_string_free(observed,TRUE);
    g_ptr_array_unref(output_views);output_views=NULL;primary_manager=NULL;popup_manager=NULL;
    test_surface_preflight();test_projection_capabilities();test_shared_preview_router();
    g_printerr("positive=existing-shared-preview-router returned=1\n");
    return malformed && notobject && version && missing && scalar && duplicate && bound && smallbound && origin && typed && preview && preview_shape && legacy && ordinal && preview_positive && shutdown && retirement && popup_closed ? 0 : 1;
}
