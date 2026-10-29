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
    g_set_print_handler(NULL);g_string_free(observed,TRUE);
    g_ptr_array_unref(output_views);output_views=NULL;primary_manager=NULL;popup_manager=NULL;
    test_surface_preflight();test_projection_capabilities();test_shared_preview_router();
    g_printerr("positive=existing-shared-preview-router returned=1\n");
    return malformed && notobject && version && missing && scalar && duplicate && bound && smallbound && origin && typed ? 0 : 1;
}
