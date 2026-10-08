#define _GNU_SOURCE
#include <json-glib/json-glib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include "surface.h"
#include "host-journal.h"
int main(int argc,char **argv) {
    if(argc!=2)return 2;
    g_autoptr(JsonParser) parser=json_parser_new();
    if(!json_parser_load_from_data(parser,argv[1],-1,NULL))return 2;
    g_autoptr(JsonNode) record=admission_record(json_parser_get_root(parser));
    if(!record)return 1;
    g_autofree char *key=admission_key(record);puts(key);return 0;
}
