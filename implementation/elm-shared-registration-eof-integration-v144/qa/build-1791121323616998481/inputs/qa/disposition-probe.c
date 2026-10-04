#define main original_host_main
#include "../native/host.c"
#undef main
#define CONTEXT_KEYS_PRIMITIVES_ONLY
#include "../native/context-keys.h"
#include "actual-shared-helpers.h"
int main(int argc,char **argv) {
    (void)context_keys_admit;
    (void)admission_open;(void)admission_close;
    g_assert_cmpint(argc,==,2);g_autoptr(JsonParser) input=json_parser_new();
    g_assert_true(json_parser_load_from_file(input,argv[1],NULL));JsonObject *args=json_node_get_object(json_parser_get_root(input));
    const char *original=json_object_get_string_member(args,"original");
    g_autoptr(JsonParser) parser=json_parser_new();g_assert_true(json_parser_load_from_data(parser,original,-1,NULL));
    JsonNode *batch=json_parser_get_root(parser);JsonObject *object=json_node_get_object(batch);
    JsonObject *projection=json_object_get_object_member(object,"projection");JsonNode *frame=json_object_get_member(projection,"frame");
    guint64 publication,lease;gboolean open;g_assert_true(surface_frame(frame,&publication,&lease,&open));
    g_assert_true(surface_uint(json_object_get_member(projection,"revision"),&topology_revision));
    authority_binding=json_node_copy(json_object_get_member(args,"binding"));
    JsonObject *gate=json_object_get_object_member(args,"gate");
    g_assert_true(surface_uint(json_object_get_member(gate,"publication"),&surface_gate.publication));
    g_assert_true(surface_uint(json_object_get_member(gate,"lease"),&surface_gate.lease));
    g_assert_true(surface_uint(json_object_get_member(gate,"closed"),&surface_gate.closed));
    backend_ready=TRUE;
    /* Distinct manager identity only; no GTK/WebKit object is constructed. */
    int controller_marker=0;primary_manager=(WebKitUserContentManager *)&controller_marker;
    JsonObject *translated=json_object_new();json_object_set_int_member(translated,"surfaceProtocol",2);json_object_set_string_member(translated,"kind","surface-commit");
    json_object_set_member(translated,"frame",json_node_copy(frame));json_object_set_member(translated,"requests",json_node_copy(json_object_get_member(object,"requests")));json_object_set_member(translated,"focus",json_node_copy(json_object_get_member(object,"focus")));
    JsonNode *legacy=json_node_new(JSON_NODE_OBJECT);json_node_take_object(legacy,translated);SurfaceCommit result;
    SurfaceGate before=surface_gate;
    g_assert_false(surface_preflight(&surface_gate,legacy,0,0,TRUE,&result));
    g_autofree char *wire=json_to_string(legacy,FALSE);
    g_assert_cmpint(surface_receive(primary_manager,wire,legacy),==,SURFACE_PREFLIGHT_UNSENT);
    g_assert_cmpmem(&before,sizeof(before),&surface_gate,sizeof(surface_gate));g_assert_cmpuint(g_queue_get_length(&requests),==,0);
    OutputView one={.id=1,.generation=1,.active=TRUE};
    JsonNode *certificate=shared_batch_certificate(batch,original,&one,publication,lease,SURFACE_PREFLIGHT_UNSENT);g_assert_nonnull(certificate);
    g_assert_cmpstr(json_object_get_string_member(json_node_get_object(certificate),"batch"),==,original);
    g_autofree char *encoded=json_to_string(certificate,FALSE);puts(encoded);
    json_node_unref(certificate);json_node_unref(legacy);json_node_unref(authority_binding);authority_binding=NULL;return 0;
}
