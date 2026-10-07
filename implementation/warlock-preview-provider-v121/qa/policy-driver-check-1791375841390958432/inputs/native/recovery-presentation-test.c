#include <json-glib/json-glib.h>
#include <string.h>
#include <stdio.h>
#include "surface.h"
static gboolean admits(SurfaceGate *gate,JsonNode *frame,const char *id) {
 JsonObject *o=json_object_new();json_object_set_int_member(o,"surfaceProtocol",2);json_object_set_string_member(o,"kind","surface-action");json_object_set_string_member(o,"surface","bar");JsonObject *f=json_node_get_object(frame);json_object_set_string_member(o,"publication",json_object_get_string_member(f,"publication"));json_object_set_string_member(o,"lease",json_object_get_string_member(f,"lease"));json_object_set_string_member(o,"id",id);JsonNode *n=json_node_new(JSON_NODE_OBJECT);json_node_take_object(n,o);gboolean result=surface_action(gate,n,frame,FALSE);json_node_unref(n);return result;
}
int main(int argc,char **argv) {
 if(argc!=2) {return 2;}
 JsonParser *parser=json_parser_new();
 if(!json_parser_load_from_file(parser,argv[1],NULL)) {return 2;}
 JsonNode *frame=json_parser_get_root(parser);guint64 p=0,l=0;gboolean open=FALSE;
 if(!surface_frame(frame,&p,&l,&open))return 3;
 SurfaceGate empty={0,0,0};
 if(!surface_admit(&empty,frame,&p,&l,&open)) {return 4;}
 SurfaceGate gate={p,l,0};gboolean blocked=!admits(&gate,frame,"bar:group:application:GTK Application"),refresh=admits(&gate,frame,"bar:recovery-refresh"),apps=admits(&gate,frame,"bar:applications");
 JsonArray *bar=json_object_get_array_member(json_node_get_object(frame),"bar");
 for(guint i=json_array_get_length(bar);i<259;i++) {JsonObject *item=json_object_new();char id[64];snprintf(id,sizeof id,"fixture-%u",i);json_object_set_string_member(item,"id",id);json_object_set_string_member(item,"domId",id);json_object_set_string_member(item,"label","Fixture");json_object_set_string_member(item,"ariaLabel","Fixture");json_object_set_string_member(item,"detail","");json_object_set_boolean_member(item,"enabled",TRUE);json_array_add_object_element(bar,item);}
 gboolean at_limit=surface_frame(frame,&p,&l,&open);JsonObject *extra=json_object_new();json_object_set_string_member(extra,"id","over-limit");json_object_set_string_member(extra,"domId","over-limit");json_object_set_string_member(extra,"label","Fixture");json_object_set_string_member(extra,"ariaLabel","Fixture");json_object_set_string_member(extra,"detail","");json_object_set_boolean_member(extra,"enabled",TRUE);json_array_add_object_element(bar,extra);gboolean beyond_limit=!surface_frame(frame,&p,&l,&open);
 printf("{\"blockedMutation\":%s,\"refreshAdmitted\":%s,\"applicationsAdmitted\":%s,\"bar259Admitted\":%s,\"bar260Refused\":%s}\n",blocked?"true":"false",refresh?"true":"false",apps?"true":"false",at_limit?"true":"false",beyond_limit?"true":"false");g_object_unref(parser);return blocked&&refresh&&apps&&at_limit&&beyond_limit?0:1;
}
