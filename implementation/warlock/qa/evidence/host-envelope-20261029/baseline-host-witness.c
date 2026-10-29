#define ELM_SHARED_HOST_MAIN retained_shared_host_main
#include "/home/charles/Warlock/implementation/warlock/native/shared-host.c"

static GString *observed;
static void capture(const gchar *text) { g_string_append(observed,text); }
static gboolean observe(const char *name,const char *wire,const char *expected_reason) {
    SurfaceGate before=surface_gate;
    guint q=g_queue_get_length(&requests), batches=g_queue_get_length(&shared_batches);
    gboolean ready=backend_ready; GSubprocess *old_backend=backend;
    g_string_truncate(observed,0);
    shared_receive_text(primary_manager,wire);
    gboolean untouched=memcmp(&before,&surface_gate,sizeof(before))==0 && q==g_queue_get_length(&requests)
        && batches==g_queue_get_length(&shared_batches) && ready==backend_ready && old_backend==backend && active_request==NULL;
    gboolean reason=strstr(observed->str,expected_reason)!=NULL;
    g_printerr("case=%s state_unchanged=%d refusal_recorded=%d log=%s\n",name,untouched,reason,observed->str);
    return untouched && reason;
}
int main(void) {
    int primary=0,popup=0;
    primary_manager=(WebKitUserContentManager *)&primary; popup_manager=(WebKitUserContentManager *)&popup;
    output_views=g_ptr_array_new(); surface_gate=(SurfaceGate){11,3,2}; backend_ready=FALSE;
    observed=g_string_new(""); g_set_print_handler(capture);
    gboolean malformed=observe("malformed-json","{bad","view-refused:");
    gboolean notobject=observe("non-object","[]","view-refused:");
    gboolean version=observe("unsupported-version","{\"viewProtocol\":2,\"kind\":\"view-commit\",\"projection\":{},\"requests\":[],\"focus\":[]}","view-refused:");
    g_set_print_handler(NULL);g_string_free(observed,TRUE);
    g_ptr_array_unref(output_views);output_views=NULL;primary_manager=NULL;popup_manager=NULL;
    test_shared_preview_router();
    g_printerr("positive=existing-shared-preview-router returned=1\n");
    return malformed && notobject && version ? 0 : 1;
}
