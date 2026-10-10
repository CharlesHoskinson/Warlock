#include <glib.h>
#include <json-glib/json-glib.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include "surface.h"
#include "host-journal.h"
int main(int argc,char **argv) {
 if(argc!=4)return 2;
 JsonParser *bound=json_parser_new(),*requests=json_parser_new();
 if(!json_parser_load_from_data(bound,argv[2],-1,NULL) || !json_parser_load_from_data(requests,argv[3],-1,NULL))return 2;
 if(!admission_open(argv[1]) || !admission_bind(json_parser_get_root(bound)))return 2;
 gboolean ok=admission_batch(json_node_get_array(json_parser_get_root(requests)),json_parser_get_root(bound));
 admission_close();g_object_unref(bound);g_object_unref(requests);return ok?0:1;
}
