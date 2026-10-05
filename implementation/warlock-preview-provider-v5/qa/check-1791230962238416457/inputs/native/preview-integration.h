#pragma once
#include <webkit2/webkit2.h>
#include <json-glib/json-glib.h>
#ifdef __cplusplus
extern "C" {
#endif
/* GTK owner-thread native provider only. The borrowed actual popup view must be
 * enrolled before exposing an image. The handler must independently validate
 * native binding/job, ownership and budgets; JSON does not authorize effects.
 * Clear handlers/endpoint and revoke/drain registered views before teardown. */
typedef gboolean (*PreviewCommandHandler)(WebKitWebView*,JsonNode*);
void preview_host_set_command_handler(PreviewCommandHandler handler);
WebKitWebView* preview_host_popup_view(void);
#ifdef __cplusplus
}
#endif
#ifdef __cplusplus
extern "C" {
#endif
/* Trusted producer-only transport installation. Endpoint must already contain
 * native-enrolled popup subjects and outlive the borrowed transport. This does
 * not authorize capture or infer any producer/consumer fence. */
gboolean preview_host_attach_delivery(void* endpoint,GError** error);
gboolean preview_host_publish_receipts(GError** error);
#ifdef __cplusplus
}
#endif
