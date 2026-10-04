/* Synthetic identities; actual production C guards; no GTK dispatch or DOM call. */
#define G_DISABLE_CAST_CHECKS
#define ELM_SHARED_HOST_MAIN archived_shared_main
#include "shared-host.c"
static guint checks;
#define CHECK(name,expr) do { checks++; if(!(expr)){g_printerr("failed %u: %s\n",checks,name);return 1;} } while(0)
static JsonNode *load(const char *path) {JsonParser *parser=json_parser_new();GError *error=NULL;if(!json_parser_load_from_file(parser,path,&error))g_error("load failed: %s",error->message);JsonNode *root=json_node_copy(json_parser_get_root(parser));g_object_unref(parser);return root;}
int main(int argc,char **argv) {
 if(argc!=3)return 2;
 JsonNode *witness=load(argv[1]);JsonObject *w=json_node_get_object(witness);JsonNode *before=json_object_get_member(w,"before"),*after=json_object_get_member(w,"after");
 gboolean expected=g_str_equal(argv[2],"521"),opened,popup;guint64 pub,lease;
 OutputView one={.id=1,.generation=1,.engine=(WebKitWebView*)11,.manager=(WebKitUserContentManager*)21,.active=TRUE};
 output_views=g_ptr_array_new();g_ptr_array_add(output_views,&one);popup_view=(WebKitWebView*)13;popup_manager=(WebKitUserContentManager*)23;primary_manager=(WebKitUserContentManager*)24;popup_owner=&one;
 CHECK("compiled Elm before packet validates",surface_frame(before,&pub,&lease,&opened)&&!opened);
 surface_gate=(SurfaceGate){pub,lease,0};surface_snapshot=json_node_copy(before);context_epoch=1;
 context_proof=(ContextProof){.source=(GtkWidget*)one.engine,.view_id=1,.view_generation=1,.epoch=1,.publication=pub,.lease=lease,.captured=g_get_monotonic_time(),.pointer=TRUE,.available=TRUE,.x=229,.y=21};
 JsonArray *bar=json_object_get_array_member(json_node_get_object(before),"bar");const char *id=NULL;
 for(guint i=0;i<json_array_get_length(bar);i++){JsonObject *o=json_array_get_object_element(bar,i);if(g_str_has_prefix(json_object_get_string_member(o,"id"),"bar:group:")&&json_object_get_boolean_member(o,"enabled"))id=json_object_get_string_member(o,"id");}
 CHECK("captured state contains enabled application group",id!=NULL);
 JsonObject *o=json_object_new();json_object_set_int_member(o,"surfaceProtocol",2);json_object_set_string_member(o,"kind","surface-context");json_object_set_string_member(o,"surface","bar");gchar *stamp=g_strdup_printf("%" G_GUINT64_FORMAT,pub);json_object_set_string_member(o,"publication",stamp);g_free(stamp);stamp=g_strdup_printf("%" G_GUINT64_FORMAT,lease);json_object_set_string_member(o,"lease",stamp);g_free(stamp);json_object_set_string_member(o,"id",id);json_object_set_string_member(o,"trigger","pointer");json_object_set_int_member(o,"x",229);json_object_set_int_member(o,"y",21);JsonNode *request=json_node_new(JSON_NODE_OBJECT);json_node_take_object(request,o);
 ContextProof admitted;CHECK("original native proof admits before update",context_admit(one.manager,request,&admitted,&popup)&&!popup);
 CHECK("compiled Elm after packet validates",surface_frame(after,&pub,&lease,&opened)&&!opened);
 surface_gate=(SurfaceGate){pub,lease,0};json_node_unref(surface_snapshot);surface_snapshot=json_node_copy(after);
 CHECK("counterfactual publication decides original callback",context_admit(one.manager,request,&admitted,&popup)==expected);
 if(expected){
  context_epoch++;CHECK("later physical event refused",!context_admit(one.manager,request,&admitted,&popup));context_epoch--;
  one.generation++;CHECK("replaced engine generation refused",!context_admit(one.manager,request,&admitted,&popup));one.generation--;
  gint64 captured=context_proof.captured;context_proof.captured=g_get_monotonic_time()-500001;CHECK("expired original proof refused",!context_admit(one.manager,request,&admitted,&popup));context_proof.captured=captured;
  surface_gate.lease++;CHECK("changed lease refused",!context_admit(one.manager,request,&admitted,&popup));surface_gate.lease--;
  JsonObject *control=json_array_get_object_element(json_object_get_array_member(json_node_get_object(surface_snapshot),"bar"),1);CHECK("selected group is actual second control",g_str_equal(id,json_object_get_string_member(control,"id")));json_object_set_boolean_member(control,"enabled",FALSE);CHECK("disabled group refused",!context_admit(one.manager,request,&admitted,&popup));json_object_set_boolean_member(control,"enabled",TRUE);
  CHECK("matching callback re-admits",context_admit(one.manager,request,&admitted,&popup));CHECK("consume once",context_consume(&admitted,FALSE));CHECK("duplicate admission refused",!context_admit(one.manager,request,&admitted,&popup));
  CHECK("verified same engine finishes",context_finish_allowed(&admitted,FALSE,(GObject*)one.engine,TRUE));CHECK("unverified DOM refuses",!context_finish_allowed(&admitted,FALSE,(GObject*)one.engine,FALSE));surface_gate.publication++;CHECK("publication change during verification refuses",!context_finish_allowed(&admitted,FALSE,(GObject*)one.engine,TRUE));
 }
 g_print("{\"passed\":true,\"checks\":%u,\"nativeAcceptance\":false}\n",checks);json_node_unref(request);json_node_unref(surface_snapshot);json_node_unref(witness);g_ptr_array_unref(output_views);return 0;
}
