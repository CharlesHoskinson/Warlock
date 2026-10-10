#define main original_surface_main
#include "../native/surface-test.c"
#undef main
static void test_notification_focus(void) {
 SurfaceGate gate={7,3,2};guint64 pub,lease;gboolean open;JsonNode *f=frame("7","3","notifications");
 JsonObject *row=json_array_get_object_element(json_object_get_array_member(json_node_get_object(f),"popup"),0);
 json_object_set_boolean_member(row,"enabled",FALSE);json_object_set_boolean_member(row,"focusOnly",TRUE);
 g_assert_true(surface_frame(f,&pub,&lease,&open));
 JsonNode *a=parse("{\"surfaceProtocol\":2,\"kind\":\"surface-notification-focus\",\"surface\":\"popup\",\"publication\":\"7\",\"lease\":\"3\",\"id\":\"control:close\"}");
 g_assert_true(surface_notification_focus(&gate,a,f,TRUE));g_assert_false(surface_notification_focus(&gate,a,f,FALSE));g_assert_false(surface_action(&gate,a,f,TRUE));
 JsonObject *event=json_node_get_object(a);json_object_set_string_member(event,"kind","surface-action");g_assert_false(surface_action(&gate,a,f,TRUE));
 json_object_set_string_member(event,"kind","surface-notification-focus");json_object_set_string_member(event,"id","missing");g_assert_false(surface_notification_focus(&gate,a,f,TRUE));
 json_object_set_string_member(event,"id","");g_assert_true(surface_notification_focus(&gate,a,f,TRUE));
 gate.closed=3;g_assert_false(surface_notification_focus(&gate,a,f,TRUE));gate.closed=2;gate.publication=8;g_assert_false(surface_notification_focus(&gate,a,f,TRUE));gate.publication=7;
 json_object_set_int_member(event,"extra",1);g_assert_false(surface_notification_focus(&gate,a,f,TRUE));json_object_remove_member(event,"extra");
 json_object_set_boolean_member(row,"enabled",TRUE);g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_boolean_member(row,"enabled",FALSE);
 json_object_set_int_member(row,"focusOnly",1);g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_boolean_member(row,"focusOnly",TRUE);
 json_object_set_string_member(json_node_get_object(f),"mode","settings");g_assert_false(surface_frame(f,&pub,&lease,&open));g_assert_false(surface_notification_focus(&gate,a,f,TRUE));
 json_node_unref(a);json_node_unref(f);
}
static void test_checked_menu(void) {
 guint64 pub,lease;gboolean open;JsonNode *f=frame("7","3","menu");JsonObject *o=json_node_get_object(f);
 JsonObject *row=json_array_get_object_element(json_object_get_array_member(o,"popup"),0);
 json_object_set_string_member(row,"id","menu:1:2");json_object_set_boolean_member(row,"focusOnly",FALSE);json_object_set_boolean_member(row,"checked",FALSE);g_assert_true(surface_frame(f,&pub,&lease,&open));
 json_object_set_boolean_member(row,"checked",TRUE);g_assert_true(surface_frame(f,&pub,&lease,&open));
 json_object_set_string_member(row,"checked","true");g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_boolean_member(row,"checked",TRUE);
 json_object_set_string_member(o,"mode","settings");g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_string_member(o,"mode","menu");
 json_object_set_string_member(row,"id","control:close");g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_string_member(row,"id","menu:1:2");
 json_object_remove_member(row,"focusOnly");g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_set_boolean_member(row,"focusOnly",FALSE);
 json_object_set_boolean_member(row,"extra",TRUE);g_assert_false(surface_frame(f,&pub,&lease,&open));json_object_remove_member(row,"extra");
 SurfaceGate gate={7,3,2};JsonNode *a=parse("{\"surfaceProtocol\":2,\"kind\":\"surface-action\",\"surface\":\"popup\",\"publication\":\"7\",\"lease\":\"3\",\"id\":\"menu:1:2\"}");
 g_assert_true(surface_action(&gate,a,f,TRUE));json_object_set_boolean_member(row,"enabled",FALSE);g_assert_false(surface_action(&gate,a,f,TRUE));json_object_set_boolean_member(row,"checked",FALSE);g_assert_false(surface_action(&gate,a,f,TRUE));
 json_object_set_boolean_member(json_node_get_object(a),"checked",TRUE);g_assert_false(surface_action(&gate,a,f,TRUE));json_node_unref(a);json_node_unref(f);
}
int main(int argc,char **argv) {
 g_test_init(&argc,&argv,NULL);
 g_test_add_func("/surface/canonical-uint64",test_counter);g_test_add_func("/surface/publication-close-barrier",test_barrier);g_test_add_func("/surface/actual-manager-origin",test_origin);g_test_add_func("/surface/strict-frame",test_schema);g_test_add_func("/surface/query-is-not-action-authority",test_query);g_test_add_func("/surface/typed-committed-appearance",test_appearance);
 g_test_add_func("/surface/passive-notification-focus-never-action",test_notification_focus);g_test_add_func("/surface/observed-checkbox-never-action-authority",test_checked_menu);return g_test_run();
}
