#pragma once
#include <gio/gio.h>
G_BEGIN_DECLS
typedef struct WarlockPickerPreviews WarlockPickerPreviews;
/* Trusted owner-thread gate only. Native independently validates each family.
 * Elm alone issues Acquire/Cancel/Release; this pool retains their custody. */
WarlockPickerPreviews *warlock_picker_previews_open(void *native,gpointer popup,GError **error);
gboolean warlock_picker_previews_poll(WarlockPickerPreviews*,const guint64 *subjects,guint count,guint64 publication,guint64 lease,char **events,GError **error);
gboolean warlock_picker_previews_command(WarlockPickerPreviews*,gpointer popup,const char *identity,const char *command,gboolean acquisition_allowed,guint64 lease,char **events,GError **error);
GInputStream *warlock_picker_previews_stream(WarlockPickerPreviews*,gpointer popup,const char *uri,guint64 lease,gsize *length,GError **error);
GInputStream *warlock_picker_previews_icon_stream(WarlockPickerPreviews*,gpointer popup,const char *uri,guint64 lease,gsize *length,GError **error);
/* Refuses destruction with any reader, export, reservation or retained proof. */
gboolean warlock_picker_previews_empty(WarlockPickerPreviews*);
gboolean warlock_picker_previews_close(WarlockPickerPreviews*,GError **error);
G_END_DECLS
