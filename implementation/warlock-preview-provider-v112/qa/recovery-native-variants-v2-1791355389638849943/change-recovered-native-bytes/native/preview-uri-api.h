#pragma once
#include <webkit2/webkit2.h>
#include "preview-uri-router.h"
#ifdef __cplusplus
extern "C" {
#endif
/* Native Endpoint pointer supplied only by the trusted capture bridge. A null
 * endpoint denies preview access. Web content cannot install an endpoint or
 * enroll views. Returns true when the preview URI namespace was handled. */
/* GTK owner-thread installation by native producer/supervisor only. Clear this
 * pointer and unregister its views before destroying the endpoint. A stream
 * closing never grants a producer or consumer fence. */
void preview_host_set_endpoint(void* endpoint);
gboolean preview_uri_dispatch(void* endpoint,WebKitURISchemeRequest* request);
/* Controlled callback path. Context owns an independent router reference. */
gboolean preview_uri_router_dispatch(PreviewURIRouter* router,WebKitURISchemeRequest* request);
#ifdef __cplusplus
}
#endif
