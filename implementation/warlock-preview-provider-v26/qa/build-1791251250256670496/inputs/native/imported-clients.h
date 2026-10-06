#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct WarlockImportedClients WarlockImportedClients;
/* Trusted GTK owner only. Transport is borrowed from the owning native
 * bootstrap, which must outlive this handle and every reader. Subjects and
 * publication/lease come from admitted native facts and the GTK gate.
 * This client-plane qualification route remains previewEligible:false. */
WarlockImportedClients *warlock_imported_clients_open(void *transport,gpointer popup,guint64 first,guint64 second,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
gboolean warlock_imported_clients_command(WarlockImportedClients*,const char *identity,const char *command,char **events,GError**);
gboolean warlock_imported_clients_poll(WarlockImportedClients*,const char *identity,char **events,GError**);
gboolean warlock_imported_clients_uri(WarlockImportedClients*,const char *identity,char **uri,GError**);
gboolean warlock_imported_clients_status(WarlockImportedClients*,char **status,GError**);
gboolean warlock_imported_clients_empty(WarlockImportedClients*);
/* Refusal retains the owner and receiver for physical drain and exact ACK. */
gboolean warlock_imported_clients_close(WarlockImportedClients*,GError**);
G_END_DECLS
