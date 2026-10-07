#pragma once
#include <gio/gio.h>
G_BEGIN_DECLS
typedef struct PreviewURIRouter PreviewURIRouter;
/* Native-owned callback object. Context registration retains its own reference
 * and releases it using preview_uri_router_unref as destroy notify. Web content
 * cannot construct, bind, clear or choose the native receiver/realm. */
PreviewURIRouter* preview_uri_router_new(void);
PreviewURIRouter* preview_uri_router_ref(PreviewURIRouter* router);
void preview_uri_router_unref(gpointer router);
gboolean preview_uri_router_bind(PreviewURIRouter* router,void* endpoint,gpointer receiver,guint64 epoch,GError** error);
gboolean preview_uri_router_clear(PreviewURIRouter* router,GError** error);
GInputStream* preview_uri_router_open(PreviewURIRouter* router,gpointer receiver,const char* uri,gsize* length,GError** error);
G_END_DECLS
