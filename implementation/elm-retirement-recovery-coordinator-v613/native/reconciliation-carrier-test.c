#define main archived_host_main
#include "host.c"
#undef main
static guint checks;
#define CHECK(x) do {checks++;if(!(x)){g_printerr("failed %u: %s\n",checks,#x);return 1;}} while(0)
int main(void) {
    const char *wire="{\"protocolVersion\":3,\"kind\":\"reconciliation-ready\",\"binding\":{\"lifetime\":\"19\",\"session\":\"10\",\"frontend\":\"1\"},\"proofRequestId\":\"1\",\"queriedBinding\":{\"lifetime\":\"19\",\"session\":\"1\",\"frontend\":\"1\"}}";
    g_autoptr(JsonParser) parser=json_parser_new();CHECK(geometry_parse(parser,wire));
    JsonNode *root=json_parser_get_root(parser);CHECK(request_kind(root)!=NULL);CHECK(observation_kind(request_kind(root)));CHECK(!geometry_kind(request_kind(root)));
    CHECK(bridge_bound(4096,"reconciliation-ready",FALSE));CHECK(!bridge_bound(4097,"reconciliation-ready",FALSE));
    JsonObject *o=json_node_get_object(root);json_object_set_string_member(o,"extra","x");CHECK(!request_kind(root));json_object_remove_member(o,"extra");
    json_object_set_boolean_member(o,"proofRequestId",TRUE);CHECK(!request_kind(root));json_object_set_string_member(o,"proofRequestId","1");
    json_object_set_null_member(o,"queriedBinding");CHECK(!request_kind(root));
    g_autoptr(JsonParser) clean=json_parser_new();CHECK(geometry_parse(clean,wire));JsonNode *ack=json_parser_get_root(clean);
    const char *duplicate[]={
        "{\"protocolVersion\":3,\"kind\":\"reconciliation-ready\",\"binding\":{},\"proofRequestId\":\"1\",\"proofRequestId\":\"2\",\"queriedBinding\":{}}",
        "{\"protocolVersion\":3,\"kind\":\"reconciliation-ready\",\"binding\":{},\"proofRequestId\":\"1\",\"queriedBinding\":{\"session\":\"1\",\"session\":\"2\"}}",
        "{\"requests\":[],\"requests\":[{\"protocolVersion\":3,\"kind\":\"reconciliation-ready\",\"binding\":{},\"proofRequestId\":\"1\",\"queriedBinding\":{}}]}"
    };
    for(guint i=0;i<G_N_ELEMENTS(duplicate);i++){g_autoptr(JsonParser) p=json_parser_new();CHECK(!geometry_parse(p,duplicate[i]));}
    JsonNode *commit=test_commit();JsonObject *co=json_node_get_object(commit);JsonArray *requests=json_object_get_array_member(co,"requests");
    json_array_remove_element(requests,0);json_array_add_element(requests,json_node_copy(ack));
    JsonObject *frame=json_object_get_object_member(co,"frame");json_object_set_string_member(frame,"mode","menu");
    SurfaceGate gate={10,3,2},before=gate;SurfaceCommit result;
    CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));CHECK(!memcmp(&gate,&before,sizeof(gate)));CHECK(!surface_preflight(&gate,commit,0,0,FALSE,&result));
    for(guint i=1;i<16;i++)json_array_add_element(requests,json_node_copy(ack));
    CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));CHECK(!surface_preflight(&gate,commit,0,1,TRUE,&result));
    json_array_add_element(requests,json_node_copy(ack));CHECK(!surface_preflight(&gate,commit,0,0,TRUE,&result));
    json_node_unref(commit);g_print("reconciliation-carrier-checks: %u\n",checks);return 0;
}
