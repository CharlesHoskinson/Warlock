#define _GNU_SOURCE
#include <glib.h>
#include <json-glib/json-glib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <string.h>
#include "surface.h"
#include "host-journal.h"
int main(int argc,char **argv) {
 if(argc!=3 || !admission_open(argv[1]))return 2;
 g_autoptr(JsonParser) parser=json_parser_new();
 if(!json_parser_load_from_data(parser,argv[2],-1,NULL))return 2;
 JsonNode *bound=json_parser_get_root(parser);
 int instance=admission.instance;
 gboolean first=admission_bind(bound);
 g_print("{\"first\":%d,\"instanceRetained\":%d,\"lifetimeRetired\":%d}\n",first,admission.instance==instance && fcntl(instance,F_GETFD)>=0,admission.directory<0 && admission.lock<0 && admission.lifetime==NULL);fflush(stdout);
 char signal;if(read(0,&signal,1)!=1)return 2;
 gboolean retry=admission_bind(bound);
 g_autoptr(JsonNode) foreign=json_node_copy(bound);json_object_set_string_member(json_node_get_object(foreign),"lifetime","72");
 gboolean foreign_refused=!admission_bind(foreign),same=admission_bind(bound);
 g_print("{\"retry\":%d,\"foreignLifetimeRefused\":%d,\"sameLifetimeIdempotent\":%d}\n",retry,foreign_refused,same);
 admission_close();g_print("{\"closed\":%d}\n",admission.instance<0 && admission.directory<0 && admission.lock<0 && admission.lifetime==NULL);fflush(stdout);return retry?0:1;
}
