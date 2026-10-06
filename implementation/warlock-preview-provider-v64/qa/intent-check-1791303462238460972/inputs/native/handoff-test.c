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
 g_autoptr(JsonParser) binding=json_parser_new();
 if(!json_parser_load_from_data(binding,argv[2],-1,NULL) || !admission_bind(json_parser_get_root(binding)))return 2;
 g_print("{\"ready\":true}\n");fflush(stdout);
 char *line=NULL;size_t capacity=0;
 while(getline(&line,&capacity,stdin)>0){
  g_autoptr(JsonParser) parser=json_parser_new();gboolean ok=json_parser_load_from_data(parser,line,-1,NULL);
  JsonNode *root=ok?json_parser_get_root(parser):NULL;
  if(root && JSON_NODE_HOLDS_ARRAY(root))ok=admission_batch(json_node_get_array(root),json_parser_get_root(binding));
  else if(root && JSON_NODE_HOLDS_OBJECT(root))ok=admission_retire(root);
  else ok=FALSE;
  g_print("{\"ok\":%s}\n",ok?"true":"false");fflush(stdout);
 }
 free(line);admission_close();return 0;
}
