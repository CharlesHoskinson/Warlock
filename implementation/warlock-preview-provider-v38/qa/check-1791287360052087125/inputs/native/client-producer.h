#pragma once
#include <gio/gio.h>
G_BEGIN_DECLS
typedef struct WarlockClientProducer WarlockClientProducer;
/* Trusted GTK owner only. This initial single-source integration is explicit
 * private qualification; it does not promote native previewEligible:false. */
WarlockClientProducer *warlock_client_producer_open(void *native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
WarlockClientProducer *warlock_family_producer_open(void *native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
WarlockClientProducer *warlock_backdrop_producer_open(void *native,gpointer popup,guint64 subject,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
gboolean warlock_client_producer_command(WarlockClientProducer*,const char *identity,const char *command,char **events,GError**);
gboolean warlock_client_producer_poll(WarlockClientProducer*,guint64 publication,guint64 lease,char **events,GError**);
gboolean warlock_client_producer_resume(WarlockClientProducer*,guint64 publication,guint64 lease,char **events,GError**);
guint64 warlock_client_producer_lease(WarlockClientProducer*);
guint64 warlock_client_producer_request(WarlockClientProducer*);
gboolean warlock_client_producer_uri(WarlockClientProducer*,char **uri,GError**);
gboolean warlock_client_producer_empty(WarlockClientProducer*);
gboolean warlock_client_producer_status(WarlockClientProducer*,char **status,GError**);
/* Same native endpoint and receiver checks used by the WebKit URI callback. */
GInputStream *warlock_client_producer_stream(WarlockClientProducer*,gpointer popup,const char *uri,gsize *length,GError**);
gboolean warlock_client_producer_close(WarlockClientProducer*,GError**);
G_END_DECLS
