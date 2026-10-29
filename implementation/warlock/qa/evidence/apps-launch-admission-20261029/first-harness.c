#define main unused_host_main
#include HOST_SOURCE
#undef main
static void test(gboolean condition,const char *name) { if(!condition){g_printerr("FAIL %s\n",name);exit(1);}g_print("PASS %s\n",name); }
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 g_autoptr(JsonParser) parser=json_parser_new();GError *error=NULL;
 if(!json_parser_load_from_file(parser,argv[1],&error)){g_printerr("parse failed\n");return 2;}
 JsonObject *generated=json_node_get_object(json_parser_get_root(parser));
 test(json_object_get_boolean_member(generated,"opened") && json_object_get_boolean_member(generated,"catalogPresent"),"actual-elm-setup");
 JsonObject *batch=json_object_get_object_member(generated,"batch"),*projection=json_object_get_object_member(batch,"projection");
 JsonNode *frame=json_object_get_member(projection,"frame"),*requests=json_object_get_member(batch,"requests"),*focus=json_object_get_member(batch,"focus");
 test(frame && requests && focus && JSON_NODE_HOLDS_ARRAY(requests) && json_array_get_length(json_node_get_array(requests))==1,"one-actual-controller-request");
 JsonNode *req=json_array_get_element(json_node_get_array(requests),0);
 test(request_kind(req) && g_str_equal(request_kind(req),"application-launch"),"actual-elm-launch-kind");
 JsonObject *fo=json_node_get_object(frame);guint64 pub,lease;gboolean open;
 test(surface_frame(frame,&pub,&lease,&open) && open && g_str_equal(json_object_get_string_member(fo,"mode"),"applications") && pub>1 && lease>0,"actual-elm-frame");
 JsonObject *o=json_object_new();json_object_set_int_member(o,"surfaceProtocol",2);json_object_set_string_member(o,"kind","surface-commit");json_object_set_member(o,"frame",json_node_copy(frame));json_object_set_member(o,"requests",json_node_copy(requests));json_object_set_member(o,"focus",json_node_copy(focus));
 JsonNode *root=json_node_new(JSON_NODE_OBJECT);json_node_take_object(root,o);
 SurfaceGate gate={pub-1,lease,lease-1};SurfaceCommit out;
 gboolean expected=g_str_equal(argv[2],"new");test(surface_preflight(&gate,root,0,0,TRUE,&out)==expected,"original-vs-reviewed-singleton");
 test(!surface_preflight(&gate,root,16,0,TRUE,&out),"queue-capacity");test(!surface_preflight(&gate,root,0,0,FALSE,&out),"backend-not-ready");
 SurfaceGate stale=gate;stale.publication=pub;test(!surface_preflight(&stale,root,0,0,TRUE,&out),"stale-publication");stale=gate;stale.closed=lease;test(!surface_preflight(&stale,root,0,0,TRUE,&out),"stale-lease");
 JsonArray *array=json_object_get_array_member(o,"requests");json_array_add_element(array,json_node_copy(json_array_get_element(array,0)));test(!surface_preflight(&gate,root,0,0,TRUE,&out),"duplicate-launch");json_array_remove_element(array,1);
 JsonObject *f=json_object_get_object_member(o,"frame");json_object_set_string_member(f,"mode","menu");json_object_set_array_member(f,"popup",json_array_new());test(!surface_preflight(&gate,root,0,0,TRUE,&out),"other-open-mode");
 json_object_set_string_member(f,"mode","closed");test(surface_preflight(&gate,root,0,0,TRUE,&out),"closed-launch");
 json_object_set_string_member(f,"mode","applications");json_array_remove_element(array,0);
 json_array_add_element(array,test_json("{\"protocolVersion\":3,\"kind\":\"files-open\",\"binding\":{},\"requestId\":\"1\",\"intent\":{\"service\":\"9\",\"revision\":\"1\",\"target\":\"coll:images\"}}"));test(!surface_preflight(&gate,root,0,0,TRUE,&out),"other-open-mutation");
 json_node_unref(root);return 0;
}
