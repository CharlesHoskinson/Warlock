#pragma once
#include <wayland-client-core.h>
#include "popup-native-identity.h"

static JsonNode *native_popup_stamp;
static guint64 native_popup_sequence,native_popup_map_generation;
static guint64 native_popup_start,native_popup_mapped_lease;
static gboolean native_popup_retiring;
static char *native_popup_lifetime;
static PopupNativeIdentity native_popup_last;

static void popup_stamp_uint(JsonObject *object,const char *name,guint64 value) {
    g_autofree char *s=g_strdup_printf("%" G_GUINT64_FORMAT,value);
    json_object_set_string_member(object,name,s);
}
static void shared_native_popup_observation(gboolean closing) {
    /* Called only by owner GTK lifecycle callbacks, never a WebKit message. */
    if (closing) {
        if (popup_active) {
            native_popup_retiring=native_popup_stamp && native_popup_mapped_lease==surface_gate.lease;
            return;
        }
        if (native_popup_retiring && native_popup_stamp && native_popup_sequence<G_MAXUINT64) {
            JsonObject *object=json_node_get_object(native_popup_stamp);
            json_object_set_string_member(object,"kind","host-popup-sync-complete");
            popup_stamp_uint(object,"sequence",++native_popup_sequence);
            json_object_set_boolean_member(object,"displaySyncComplete",TRUE);
            g_autofree char *wire=json_to_string(native_popup_stamp,FALSE);
            g_print("host-popup-native: %s\n",wire);fflush(stdout);
        }
        g_clear_pointer(&native_popup_stamp,json_node_unref);native_popup_retiring=FALSE;
        return;
    }
    if (shutting_down || !popup_owner || !popup_owner->active || !popover ||
        !window || window!=popup_owner->bar || !surface_popup_ready() || !authority_binding ||
        native_popup_sequence==G_MAXUINT64 || native_popup_map_generation==G_MAXUINT64) return;
    GdkWindow *popup=gtk_widget_get_window(popover),*root=gtk_widget_get_window(window);
    if (!popup || !root || !GDK_IS_WAYLAND_WINDOW(popup) || !GDK_IS_WAYLAND_WINDOW(root)) return;
    struct wl_surface *ps=gdk_wayland_window_get_wl_surface(popup),*rs=gdk_wayland_window_get_wl_surface(root);
    if (!ps || !rs) return;
    if (!native_popup_start) {
        g_autofree char *stat=NULL;
        if (!g_file_get_contents("/proc/self/stat",&stat,NULL,NULL) || !popup_start_parse(stat,&native_popup_start)) return;
    }
    JsonNode *scope=scope_packet(popup_owner);
    gboolean current_owner=scope_lookup(scope)==popup_owner;json_node_unref(scope);
    PopupNativeIdentity identity={.pid=getpid(),.start=native_popup_start,
        .view=popup_owner->id,.generation=popup_owner->generation,.topology=topology_revision,
        .publication=surface_gate.publication,.lease=surface_gate.lease,
        .popup=wl_proxy_get_id((struct wl_proxy *)ps),.root=wl_proxy_get_id((struct wl_proxy *)rs),
        .active=popup_active,.mapped=gtk_widget_get_mapped(popover),.root_mapped=gtk_widget_get_mapped(window),
        .same_display=gdk_window_get_display(popup)==gdk_window_get_display(root),
        .ready=surface_popup_ready(),.current_owner=current_owner};
    if (!popup_identity_valid(&identity)) return;
    if (native_popup_stamp && popup_identity_same(&native_popup_last,&identity) &&
        json_node_equal(json_object_get_member(json_node_get_object(native_popup_stamp),"binding"),authority_binding)) return;
    if (native_popup_mapped_lease!=identity.lease || native_popup_last.popup!=identity.popup ||
        native_popup_last.root!=identity.root || native_popup_last.view!=identity.view || native_popup_last.generation!=identity.generation) {
        ++native_popup_map_generation;native_popup_mapped_lease=identity.lease;
    }
    native_popup_last=identity;
    if (!native_popup_lifetime) native_popup_lifetime=g_uuid_string_random();
    JsonObject *object=json_object_new();json_object_set_int_member(object,"hostPopupProtocol",1);
    json_object_set_string_member(object,"kind","host-popup-mapped");
    json_object_set_string_member(object,"hostLifetime",native_popup_lifetime);
    popup_stamp_uint(object,"pid",identity.pid);popup_stamp_uint(object,"start",identity.start);
    popup_stamp_uint(object,"sequence",++native_popup_sequence);popup_stamp_uint(object,"mapGeneration",native_popup_map_generation);
    popup_stamp_uint(object,"view",identity.view);popup_stamp_uint(object,"generation",identity.generation);
    popup_stamp_uint(object,"topology",identity.topology);popup_stamp_uint(object,"publication",identity.publication);popup_stamp_uint(object,"lease",identity.lease);
    json_object_set_int_member(object,"popupSurface",identity.popup);json_object_set_int_member(object,"rootSurface",identity.root);
    json_object_set_member(object,"binding",json_node_copy(authority_binding));
    json_object_set_boolean_member(object,"displaySyncComplete",FALSE);
    g_clear_pointer(&native_popup_stamp,json_node_unref);native_popup_stamp=json_node_new(JSON_NODE_OBJECT);json_node_take_object(native_popup_stamp,object);
    g_autofree char *wire=json_to_string(native_popup_stamp,FALSE);g_print("host-popup-native: %s\n",wire);fflush(stdout);
}
