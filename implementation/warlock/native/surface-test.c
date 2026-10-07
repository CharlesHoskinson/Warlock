#include <json-glib/json-glib.h>
#include <string.h>
#include "surface.h"
static JsonNode *parse(const char *s) {JsonParser *p=json_parser_new();g_assert_true(json_parser_load_from_data(p,s,-1,NULL));JsonNode *n=json_node_copy(json_parser_get_root(p));g_object_unref(p);return n;}
static JsonNode *frame(const char *publication,const char *lease,const char *mode) {
    char *s=g_strdup_printf("{\"surfaceProtocol\":2,\"publication\":\"%s\",\"lease\":\"%s\",\"mode\":\"%s\",\"status\":\"Ready\",\"bar\":[{\"id\":\"bar:applications\",\"domId\":\"opener\",\"label\":\"Applications\",\"ariaLabel\":\"Accessible action\",\"detail\":\"\",\"enabled\":true}],\"popup\":%s}",publication,lease,mode,g_str_equal(mode,"closed")?"[]":"[{\"id\":\"control:close\",\"domId\":\"close\",\"label\":\"Close\",\"ariaLabel\":\"Accessible action\",\"detail\":\"\",\"enabled\":true}]");JsonNode *n=parse(s);g_free(s);return n;
}
static void test_counter(void) {
    guint64 n;JsonNode *v=parse("\"18446744073709551615\"");g_assert_true(surface_uint(v,&n));g_assert_cmpuint(n,==,G_MAXUINT64);json_node_unref(v);
    const char *bad[]={"\"18446744073709551616\"","\"01\"","\"-1\"","1","true","\"\""};for(guint i=0;i<G_N_ELEMENTS(bad);i++){v=parse(bad[i]);g_assert_false(surface_uint(v,&n));json_node_unref(v);}
}
static void test_barrier(void) {
    SurfaceGate gate={3,1,1};guint64 p,l;gboolean open;JsonNode *n=frame("4","1","applications");g_assert_false(surface_admit(&gate,n,&p,&l,&open));json_node_unref(n);
    n=frame("4","2","applications");g_assert_true(surface_admit(&gate,n,&p,&l,&open));json_node_unref(n);
    n=frame("3","2","applications");g_assert_false(surface_admit(&gate,n,&p,&l,&open));json_node_unref(n);
    n=frame("4","0","closed");g_assert_false(surface_admit(&gate,n,&p,&l,&open));json_node_unref(n);
    n=frame("4","1","closed");g_assert_true(surface_admit(&gate,n,&p,&l,&open));json_node_unref(n);
}
static void test_origin(void) {
    SurfaceGate gate={9007199254740993ULL,2,1};JsonNode *f=frame("9007199254740993","2","applications");
    JsonNode *a=parse("{\"surfaceProtocol\":2,\"kind\":\"surface-action\",\"surface\":\"popup\",\"publication\":\"9007199254740993\",\"lease\":\"2\",\"id\":\"control:close\"}");
    g_assert_true(surface_action(&gate,a,f,TRUE));g_assert_false(surface_action(&gate,a,f,FALSE));
    gate.closed=2;g_assert_false(surface_action(&gate,a,f,TRUE));gate.closed=1;gate.publication++;g_assert_false(surface_action(&gate,a,f,TRUE));gate.publication--;
    JsonObject *o=json_node_get_object(a);json_object_set_string_member(o,"id","bar:applications");g_assert_false(surface_action(&gate,a,f,TRUE));json_object_set_string_member(o,"surface","bar");g_assert_true(surface_action(&gate,a,f,FALSE));
    json_object_set_string_member(o,"Exec","forbidden");g_assert_false(surface_action(&gate,a,f,FALSE));json_node_unref(a);json_node_unref(f);
}
static void test_schema(void) {
    guint64 p,l;gboolean open;JsonNode *f=frame("1","1","applications");g_assert_true(surface_frame(f,&p,&l,&open));JsonObject *o=json_node_get_object(f);json_object_set_string_member(o,"Exec","forbidden");g_assert_false(surface_frame(f,&p,&l,&open));json_object_remove_member(o,"Exec");
    JsonObject *button=json_array_get_object_element(json_object_get_array_member(o,"popup"),0);json_object_set_string_member(button,"id","bar:applications");g_assert_false(surface_frame(f,&p,&l,&open));json_object_set_string_member(button,"id","control:close");json_object_set_string_member(button,"domId","opener");g_assert_false(surface_frame(f,&p,&l,&open));json_node_unref(f);
    f=frame("1","0","applications");g_assert_false(surface_frame(f,&p,&l,&open));json_node_unref(f);f=frame("0","1","closed");g_assert_false(surface_frame(f,&p,&l,&open));json_node_unref(f);
}
static void test_query(void) {
    SurfaceGate gate={5,2,1};JsonNode *f=frame("5","2","applications");
    JsonObject *field=json_array_get_object_element(json_object_get_array_member(json_node_get_object(f),"popup"),0);json_object_set_string_member(field,"id","control:search");
    JsonNode *q=parse("{\"surfaceProtocol\":2,\"kind\":\"surface-query\",\"surface\":\"popup\",\"publication\":\"5\",\"lease\":\"2\",\"id\":\"control:search\",\"query\":\"Files\"}");
    g_assert_true(surface_query(&gate,q,f,TRUE));g_assert_false(surface_query(&gate,q,f,FALSE));g_assert_false(surface_action(&gate,q,f,TRUE));
    JsonNode *targets=parse("[\"close\"]");g_assert_true(surface_focus_targets_present(targets,f));json_object_set_string_member(field,"domId","replacement");g_assert_false(surface_focus_targets_present(targets,f));json_object_set_string_member(field,"domId","close");json_object_set_boolean_member(field,"enabled",FALSE);g_assert_false(surface_focus_targets_present(targets,f));json_object_set_boolean_member(field,"enabled",TRUE);json_node_unref(targets);
    gate.publication++;g_assert_false(surface_query(&gate,q,f,TRUE));gate.publication--;gate.closed=2;g_assert_false(surface_query(&gate,q,f,TRUE));gate.closed=1;
    json_object_set_boolean_member(field,"enabled",FALSE);g_assert_false(surface_query(&gate,q,f,TRUE));json_object_set_boolean_member(field,"enabled",TRUE);
    JsonObject *o=json_node_get_object(q);json_object_set_string_member(o,"Exec","forbidden");g_assert_false(surface_query(&gate,q,f,TRUE));json_node_unref(q);json_node_unref(f);
}
int main(int argc,char **argv) {g_test_init(&argc,&argv,NULL);g_test_add_func("/surface/canonical-uint64",test_counter);g_test_add_func("/surface/publication-close-barrier",test_barrier);g_test_add_func("/surface/actual-manager-origin",test_origin);g_test_add_func("/surface/strict-frame",test_schema);g_test_add_func("/surface/query-is-not-action-authority",test_query);return g_test_run();}
