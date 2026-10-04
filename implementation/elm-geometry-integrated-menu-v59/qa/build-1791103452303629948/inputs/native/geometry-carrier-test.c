#define main archived_host_main
#include "host.c"
#undef main
static const char *attach_wire="{\"protocolVersion\":3,\"kind\":\"geometry-attach\",\"geometryProtocol\":1,\"binding\":{\"lifetime\":\"1\",\"session\":\"2\",\"frontend\":\"3\"},\"requestId\":\"4\"}";
static const char *facts_wire="{\"protocolVersion\":3,\"kind\":\"geometry-facts-request\",\"geometryProtocol\":1,\"binding\":{},\"requestId\":\"4\",\"minimumWatermark\":\"0\"}";
static guint checks;
#define CHECK(x) do { checks++; if (!(x)) {g_printerr("failed %u: %s\n",checks,#x);return 1;} } while(0)
int main(void) {
    const char *good[]={attach_wire,facts_wire};
    for(guint i=0;i<G_N_ELEMENTS(good);i++) {
        g_autoptr(JsonParser) p=json_parser_new();CHECK(geometry_parse(p,good[i]));CHECK(request_kind(json_parser_get_root(p))!=NULL);
    }
    const char *bad[]={"{}","[]","{", "{\"protocolVersion\":3,\"kind\":\"geometry-facts\",\"geometryProtocol\":1,\"binding\":{},\"requestId\":\"4\"}"};
    for(guint i=0;i<G_N_ELEMENTS(bad);i++) {g_autoptr(JsonParser) p=json_parser_new();CHECK(!geometry_parse(p,bad[i]) || !request_kind(json_parser_get_root(p)));}
    JsonNode *root=test_json(attach_wire);JsonObject *o=json_node_get_object(root);
    json_object_set_int_member(o,"geometryProtocol",2);CHECK(!request_kind(root));json_object_set_int_member(o,"geometryProtocol",1);
    json_object_set_boolean_member(o,"geometryProtocol",TRUE);CHECK(!request_kind(root));json_object_set_double_member(o,"geometryProtocol",1.0);CHECK(!request_kind(root));json_object_set_int_member(o,"geometryProtocol",1);
    json_object_set_string_member(o,"extra","x");CHECK(!request_kind(root));json_object_remove_member(o,"extra");
    json_object_remove_member(o,"requestId");CHECK(!request_kind(root));json_object_set_int_member(o,"requestId",4);CHECK(!request_kind(root));json_object_set_string_member(o,"requestId","4");
    json_object_set_null_member(o,"binding");CHECK(!request_kind(root));json_object_set_object_member(o,"binding",json_object_new());CHECK(request_kind(root)!=NULL);
    CHECK(bridge_bound(4096,"geometry-attach",FALSE));CHECK(!bridge_bound(4097,"geometry-attach",TRUE));CHECK(!bridge_bound(4097,"geometry-facts-request",TRUE));
    const char *duplicates[]={
        "{\"protocolVersion\":3,\"kind\":\"geometry-attach\",\"geometryProtocol\":2,\"geometryProtocol\":1,\"binding\":{},\"requestId\":\"4\"}",
        "{\"protocolVersion\":3,\"kind\":\"geometry-attach\",\"geometryProtocol\":1,\"binding\":{\"lifetime\":\"1\",\"lifetime\":\"2\"},\"requestId\":\"4\"}",
        "{\"protocolVersion\":3,\"kind\":\"geometry-attach\",\"geometryProtocol\":1,\"binding\":{},\"requestId\":\"3\",\"request\\u0049d\":\"4\"}"
    };
    for(guint i=0;i<G_N_ELEMENTS(duplicates);i++) {g_autoptr(JsonParser) p=json_parser_new();CHECK(!geometry_parse(p,duplicates[i]));}
    SurfaceGate gate={10,3,2},before=gate;SurfaceCommit result;JsonNode *commit=test_commit();JsonObject *co=json_node_get_object(commit);JsonArray *requests_array=json_object_get_array_member(co,"requests");
    json_array_remove_element(requests_array,0);json_array_add_element(requests_array,json_node_copy(root));
    JsonObject *frame=json_object_get_object_member(co,"frame");json_object_set_string_member(frame,"mode","menu");
    CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));CHECK(!memcmp(&gate,&before,sizeof(gate)));
    json_array_add_element(requests_array,test_json(facts_wire));CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));CHECK(!surface_preflight(&gate,commit,15,0,TRUE,&result));CHECK(!surface_preflight(&gate,commit,0,0,FALSE,&result));
    for(guint i=2;i<16;i++) {json_array_add_element(requests_array,json_node_copy(root));}
    CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));CHECK(!surface_preflight(&gate,commit,0,1,TRUE,&result));
    json_array_add_element(requests_array,json_node_copy(root));CHECK(!surface_preflight(&gate,commit,0,0,TRUE,&result));while(json_array_get_length(requests_array)>1) json_array_remove_element(requests_array,1);
    g_autofree char *large=g_strnfill(4096,'x');json_object_set_string_member(json_node_get_object(json_array_get_element(requests_array,0)),"requestId",large);CHECK(!surface_preflight(&gate,commit,0,0,TRUE,&result));json_array_remove_element(requests_array,0);
    json_array_add_element(requests_array,test_json("{\"protocolVersion\":3,\"kind\":\"window-effect\",\"effectProtocol\":2,\"binding\":{},\"intent\":{}}"));CHECK(!surface_preflight(&gate,commit,0,0,TRUE,&result));json_object_set_string_member(frame,"mode","closed");CHECK(surface_preflight(&gate,commit,0,0,TRUE,&result));
    g_autofree char *duplicate_commit=g_strdup_printf("{\"requests\":[%s],\"requests\":[%s]}",attach_wire,facts_wire);g_autoptr(JsonParser) parser=json_parser_new();CHECK(!geometry_parse(parser,duplicate_commit));
    json_node_unref(commit);json_node_unref(root);g_print("geometry-carrier-checks: %u\n",checks);return 0;
}
