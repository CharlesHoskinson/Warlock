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
    if(argc!=4 || !admission_open(argv[1]))return 2;
    g_autoptr(JsonParser) requests=json_parser_new(),binding=json_parser_new();
    gboolean ok=json_parser_load_from_data(requests,argv[2],-1,NULL) && JSON_NODE_HOLDS_ARRAY(json_parser_get_root(requests)) && json_parser_load_from_data(binding,argv[3],-1,NULL) &&
        (!JSON_NODE_HOLDS_OBJECT(json_parser_get_root(binding)) || admission_bind(json_parser_get_root(binding))) && admission_batch(json_node_get_array(json_parser_get_root(requests)),json_parser_get_root(binding));
    admission_close();return ok?0:1;
}
