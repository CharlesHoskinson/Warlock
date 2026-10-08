/* Read-only native preference input. No portal activation or desktop writes. */
#pragma once
#include <gtk/gtk.h>
#include <gio/gio.h>

typedef struct {
    GtkSettings *settings;
    GDBusConnection *bus;
    char *owner;
    guint owner_watch, settings_watch;
    guint64 serial, owner_epoch;
    gboolean reduced, portal_valid, started;
    const char *source;
    void (*publish)(const char *);
} WarlockMotionPreference;

static WarlockMotionPreference warlock_motion;
static void motion_publish(void) {
    if (!warlock_motion.publish || !warlock_motion.serial) return;
    g_autofree char *frame=g_strdup_printf("{\"protocolVersion\":3,\"kind\":\"host-motion-preference\",\"serial\":\"%" G_GUINT64_FORMAT "\",\"profile\":\"%s\",\"source\":\"%s\"}",warlock_motion.serial,warlock_motion.reduced?"reduced":"full",warlock_motion.source);
    warlock_motion.publish(frame);
}
static void motion_observed(gboolean reduced,const char *source) {
    if (warlock_motion.serial && warlock_motion.reduced==reduced && g_str_equal(warlock_motion.source,source)) return;
    if (warlock_motion.serial==G_MAXUINT64) return;
    warlock_motion.reduced=reduced;warlock_motion.source=source;++warlock_motion.serial;motion_publish();
}
static void motion_gtk(void) {
    gboolean animations=TRUE;
    if (warlock_motion.settings) g_object_get(warlock_motion.settings,"gtk-enable-animations",&animations,NULL);
    if (!warlock_motion.portal_valid) motion_observed(!animations,"gtk");
}
static void motion_gtk_changed(GObject *object,GParamSpec *spec,gpointer data) {
    (void)object;(void)spec;(void)data;motion_gtk();
}
static gboolean motion_portal_value(GVariant *value) {
    if (!g_variant_is_of_type(value,G_VARIANT_TYPE_UINT32)) return FALSE;
    warlock_motion.portal_valid=TRUE;
    /* Portal values other than 1 mean no reduced-motion preference. */
    motion_observed(g_variant_get_uint32(value)==1,"portal");return TRUE;
}
static void motion_read_done(GObject *object,GAsyncResult *result,gpointer data) {
    guint64 epoch=*(guint64 *)data;g_free(data);
    g_autoptr(GError) error=NULL;g_autoptr(GVariant) reply=g_dbus_connection_call_finish(G_DBUS_CONNECTION(object),result,&error);
    if (epoch!=warlock_motion.owner_epoch) return;
    if (reply) {
        g_autoptr(GVariant) boxed=g_variant_get_child_value(reply,0);
        g_autoptr(GVariant) value=g_variant_get_variant(boxed);
        if (motion_portal_value(value)) return;
    }
    warlock_motion.portal_valid=FALSE;motion_gtk();
}
static void motion_setting_changed(GDBusConnection *bus,const char *sender,const char *path,const char *interface,const char *signal,GVariant *parameters,gpointer data) {
    (void)bus;(void)path;(void)interface;(void)signal;(void)data;
    if (!warlock_motion.owner || !g_str_equal(sender,warlock_motion.owner) || !g_variant_is_of_type(parameters,G_VARIANT_TYPE("(ssv)"))) return;
    const char *namespace_,*key;GVariant *value;
    g_variant_get(parameters,"(&s&sv)",&namespace_,&key,&value);
    if (g_str_equal(namespace_,"org.freedesktop.appearance") && g_str_equal(key,"reduced-motion")) {++warlock_motion.owner_epoch;if (!motion_portal_value(value)) {warlock_motion.portal_valid=FALSE;motion_gtk();}}
    g_variant_unref(value);
}
static void motion_owner(const char *owner) {
    if (warlock_motion.owner && g_str_equal(warlock_motion.owner,owner)) return;
    if (warlock_motion.settings_watch) g_dbus_connection_signal_unsubscribe(warlock_motion.bus,warlock_motion.settings_watch);
    warlock_motion.settings_watch=0;g_clear_pointer(&warlock_motion.owner,g_free);++warlock_motion.owner_epoch;warlock_motion.portal_valid=FALSE;motion_gtk();
    if (!owner || !*owner) return;
    warlock_motion.owner=g_strdup(owner);
    warlock_motion.settings_watch=g_dbus_connection_signal_subscribe(warlock_motion.bus,owner,"org.freedesktop.portal.Settings","SettingChanged","/org/freedesktop/portal/desktop",NULL,G_DBUS_SIGNAL_FLAGS_NONE,motion_setting_changed,NULL,NULL);
    guint64 *epoch=g_new(guint64,1);*epoch=warlock_motion.owner_epoch;
    g_dbus_connection_call(warlock_motion.bus,owner,"/org/freedesktop/portal/desktop","org.freedesktop.portal.Settings","ReadOne",g_variant_new("(ss)","org.freedesktop.appearance","reduced-motion"),G_VARIANT_TYPE("(v)"),G_DBUS_CALL_FLAGS_NO_AUTO_START,1000,NULL,motion_read_done,epoch);
}
static void motion_owner_changed(GDBusConnection *bus,const char *sender,const char *path,const char *interface,const char *signal,GVariant *parameters,gpointer data) {
    (void)bus;(void)sender;(void)path;(void)interface;(void)signal;(void)data;
    const char *name_,*old,*new_;g_variant_get(parameters,"(&s&s&s)",&name_,&old,&new_);(void)old;
    if (g_str_equal(name_,"org.freedesktop.portal.Desktop")) motion_owner(new_);
}
static void motion_owner_done(GObject *object,GAsyncResult *result,gpointer data) {
    guint64 epoch=*(guint64 *)data;g_free(data);
    g_autoptr(GError) error=NULL;g_autoptr(GVariant) reply=g_dbus_connection_call_finish(G_DBUS_CONNECTION(object),result,&error);
    if (epoch!=warlock_motion.owner_epoch || !reply) return;
    const char *owner;g_variant_get(reply,"(&s)",&owner);motion_owner(owner);
}
static void motion_bus_done(GObject *object,GAsyncResult *result,gpointer data) {
    (void)object;(void)data;g_autoptr(GError) error=NULL;
    warlock_motion.bus=g_bus_get_finish(result,&error);if (!warlock_motion.bus) return;
    warlock_motion.owner_watch=g_dbus_connection_signal_subscribe(warlock_motion.bus,"org.freedesktop.DBus","org.freedesktop.DBus","NameOwnerChanged","/org/freedesktop/DBus","org.freedesktop.portal.Desktop",G_DBUS_SIGNAL_FLAGS_NONE,motion_owner_changed,NULL,NULL);
    guint64 *epoch=g_new(guint64,1);*epoch=warlock_motion.owner_epoch;
    g_dbus_connection_call(warlock_motion.bus,"org.freedesktop.DBus","/org/freedesktop/DBus","org.freedesktop.DBus","GetNameOwner",g_variant_new("(s)","org.freedesktop.portal.Desktop"),G_VARIANT_TYPE("(s)"),G_DBUS_CALL_FLAGS_NO_AUTO_START,1000,NULL,motion_owner_done,epoch);
}
static void motion_preference_start(void (*publish)(const char *)) {
    warlock_motion.publish=publish;
    if (warlock_motion.started) {motion_publish();return;}
    warlock_motion.started=TRUE;warlock_motion.settings=gtk_settings_get_default();
    if (warlock_motion.settings) g_signal_connect(warlock_motion.settings,"notify::gtk-enable-animations",G_CALLBACK(motion_gtk_changed),NULL);
    motion_gtk();g_bus_get(G_BUS_TYPE_SESSION,NULL,motion_bus_done,NULL);
}
