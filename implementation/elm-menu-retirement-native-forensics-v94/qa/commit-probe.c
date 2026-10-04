/* Include the actual held host implementation; invoke only its pure preflight.
 * No GTK initialization, surface creation, backend process, or native socket. */
#define main original_host_main
#include "../native/host.c"
#undef main

int main(int argc,char **argv) {
    g_assert_cmpint(argc,==,2);
    g_autoptr(JsonParser) parser=json_parser_new();
    g_assert_true(json_parser_load_from_file(parser,argv[1],NULL));
    JsonObject *root=json_node_get_object(json_parser_get_root(parser));
    JsonObject *gate=json_object_get_object_member(root,"nativeGate");
    SurfaceGate retired={0};
    g_assert_true(surface_uint(json_object_get_member(gate,"publication"),&retired.publication));
    g_assert_true(surface_uint(json_object_get_member(gate,"lease"),&retired.lease));
    g_assert_true(surface_uint(json_object_get_member(gate,"closed"),&retired.closed));
    JsonNode *rejected=json_object_get_member(root,"rejectedCommit");
    JsonNode *closed=json_object_get_member(root,"closedCommit");
    JsonNode *later=json_object_get_member(root,"laterCommit");
    SurfaceCommit result;
    SurfaceGate live=retired;live.closed=0;
    g_assert_true(surface_preflight(&live,rejected,0,0,TRUE,&result));
    g_assert_cmpuint(json_array_get_length(result.requests),==,2);
    g_assert_false(surface_preflight(&retired,rejected,0,0,TRUE,&result));
    g_assert_true(surface_preflight(&retired,closed,0,0,TRUE,&result));
    g_assert_false(result.open);
    g_assert_cmpuint(json_array_get_length(result.requests),==,0);
    retired.publication=result.publication;retired.lease=result.lease;
    /* Elm coalesces identical notifications without advancing publication.
     * The repeated closed frame is correctly rejected as non-new; it cannot
     * rescue the already allocated observation correlations. */
    g_assert_false(surface_preflight(&retired,later,0,0,TRUE,&result));
    puts("{\"passed\":true,\"actualHostPreflight\":true,\"liveLeaseAcceptsTwoObservations\":true,\"retiredLeaseRejectsEntireBatch\":true,\"nonAdvancingClosedFrameRejected\":true,\"nativeAcceptance\":false}");
    return 0;
}
