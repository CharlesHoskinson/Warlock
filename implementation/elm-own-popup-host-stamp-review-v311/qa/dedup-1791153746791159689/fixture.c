
#include <glib.h>
#include <json-glib/json-glib.h>
#include "identity.h"
static JsonNode *native_popup_stamp;
static guint64 native_popup_mapped_lease=4;
static int emitted;
static gboolean surface_uint(JsonNode *node,guint64 *value) {
 *value=g_ascii_strtoull(json_node_get_string(node),NULL,10); return TRUE;
}
static void observe(PopupNativeIdentity identity) {
    if (native_popup_stamp && native_popup_mapped_lease==identity.lease &&
        json_object_get_string_member(json_node_get_object(native_popup_stamp),"publication") &&
        json_object_get_int_member(json_node_get_object(native_popup_stamp),"popupSurface")==identity.popup) {
        guint64 prior;
        if (surface_uint(json_object_get_member(json_node_get_object(native_popup_stamp),"publication"),&prior) && prior==identity.publication) return;
    }
 ++emitted;
}
int main(void) {
 JsonObject *object=json_object_new();
 json_object_set_string_member(object,"publication","9");
 json_object_set_int_member(object,"popupSurface",37);
 json_object_set_int_member(object,"rootSurface",34);
 json_object_set_string_member(object,"topology","1");
 native_popup_stamp=json_node_new(JSON_NODE_OBJECT);json_node_take_object(native_popup_stamp,object);
 PopupNativeIdentity identity={.lease=4,.publication=9,.popup=37,.root=34,.topology=1};
 observe(identity);g_assert_cmpint(emitted,==,0);
 identity.topology=2;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.root=38;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.view=5;observe(identity);g_assert_cmpint(emitted,==,0);
 identity.publication=10;observe(identity);g_assert_cmpint(emitted,==,1);
 identity.publication=9;identity.lease=5;observe(identity);g_assert_cmpint(emitted,==,2);
 json_node_unref(native_popup_stamp);
 return 0;
}
