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
