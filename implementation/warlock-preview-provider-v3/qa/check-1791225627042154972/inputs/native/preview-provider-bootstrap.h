#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct WarlockPreviewBootstrap WarlockPreviewBootstrap;
/* Own native-host grant; never a backend/frontend supplied grant. */
WarlockPreviewBootstrap *warlock_preview_bootstrap_open(const char *config,GError **error);
gboolean warlock_preview_bootstrap_binding(WarlockPreviewBootstrap *owner,char **binding,GError **error);
void warlock_preview_bootstrap_free(WarlockPreviewBootstrap *owner);
G_END_DECLS
