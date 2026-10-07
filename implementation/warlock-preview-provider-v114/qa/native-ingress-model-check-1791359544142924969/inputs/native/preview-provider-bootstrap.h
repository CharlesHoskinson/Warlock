#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct WarlockPreviewBootstrap WarlockPreviewBootstrap;
/* Own native-host grant; never a backend/frontend supplied grant. */
WarlockPreviewBootstrap *warlock_preview_bootstrap_open(const char *config,GError **error);
gboolean warlock_preview_bootstrap_binding(WarlockPreviewBootstrap *owner,char **binding,GError **error);
/* Borrowed trusted Native transport; same own grant. Bootstrap must outlive it. */
void *warlock_preview_bootstrap_native_transport(WarlockPreviewBootstrap*,GError**);
/* Strict own-native catalog, stamped only by the current admitted picker. No capture grant. */
gboolean warlock_preview_bootstrap_catalog(WarlockPreviewBootstrap*,guint64 publication,guint64 lease,char **json,GError**);
/* Typed metadata/scope; a native492 probe always remains previewEligible:false. */
gboolean warlock_preview_bootstrap_enrollment(WarlockPreviewBootstrap*,char **json,GError**);
gboolean warlock_preview_bootstrap_scope(WarlockPreviewBootstrap*,guint64 subject,char **json,GError**);
/* Exact isolated client source; bounded qualification remains ineligible. */
gboolean warlock_preview_bootstrap_client_scope(WarlockPreviewBootstrap*,guint64 subject,char **json,GError**);
/* Native producer-only borrowed Endpoint must outlive the delivery handle. */
gboolean warlock_preview_bootstrap_attach_delivery(WarlockPreviewBootstrap*,void *endpoint,gpointer popup,GError**);
/* Trusted producer only: admit current own native view membership, same epoch. */
gboolean warlock_preview_bootstrap_extend_delivery(WarlockPreviewBootstrap*,gpointer popup,GError**);
/* Borrowed native-only journal capability for a validated aggregate transaction.
 * Requires the original enrolled popup and epoch. Bootstrap outlives its use. */
void *warlock_preview_bootstrap_delivery(WarlockPreviewBootstrap*,gpointer popup,GError**);
gboolean warlock_preview_bootstrap_pending(WarlockPreviewBootstrap*,gpointer popup,char **json,GError**);
gboolean warlock_preview_bootstrap_acknowledge(WarlockPreviewBootstrap*,gpointer popup,const char *identity,const char *command,GError**);
void warlock_preview_bootstrap_free(WarlockPreviewBootstrap *owner);
G_END_DECLS
