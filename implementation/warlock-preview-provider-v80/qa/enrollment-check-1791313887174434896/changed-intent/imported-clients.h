#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct WarlockImportedClients WarlockImportedClients;
/* Trusted GTK owner only. Transport is borrowed from the owning native
 * bootstrap, which must outlive this handle and every reader. Subjects and
 * publication/lease come from admitted native facts and the GTK gate.
 * This client-plane qualification route remains previewEligible:false. */
WarlockImportedClients *warlock_imported_clients_open(void *transport,gpointer popup,guint64 first,guint64 second,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
typedef enum {
    WARLOCK_IMPORTED_INVALID,
    WARLOCK_IMPORTED_STARTED,
    WARLOCK_IMPORTED_WAITING,
    WARLOCK_IMPORTED_CAPACITY,
    WARLOCK_IMPORTED_EXPIRED,
    WARLOCK_IMPORTED_CONFLICT,
    WARLOCK_IMPORTED_EXHAUSTED,
    WARLOCK_IMPORTED_NATIVE_REJECTED,
    WARLOCK_IMPORTED_RETAINED
} WarlockImportedAdmission;
/* Trusted GTK qualification path with at most 256 retained actor identities,
 * sharing the original two physical items and byte/journal/reader limits.
 * Attach ReceiptDelivery to the returned endpoint through the SAME bootstrap.
 * After enroll, explicitly extend that delivery before publishing events.
 * The original two-subject API and previewEligible:false remain unchanged. */
WarlockImportedClients *warlock_imported_clients_open_dynamic(void *transport,gpointer popup,guint64 first,guint64 publication,guint64 lease,char **initial,void **endpoint,GError **error);
/* Call on the opening GTK thread. Inputs are actual native catalog subjects and
 * current admitted GTK presentation stamps. Capacity creates no job or proof;
 * repeated enrollment reuses the original deadline and identity. Events never
 * report a fabricated Refused. The typed result is local scheduling feedback. */
gboolean warlock_imported_clients_enroll(WarlockImportedClients*,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,GError**);
gboolean warlock_imported_clients_command(WarlockImportedClients*,const char *identity,const char *command,char **events,GError**);
gboolean warlock_imported_clients_poll(WarlockImportedClients*,const char *identity,char **events,GError**);
gboolean warlock_imported_clients_poll_at(WarlockImportedClients*,const char *identity,guint64 publication,guint64 lease,char **events,GError**);
gboolean warlock_imported_clients_resume(WarlockImportedClients*,const char *identity,guint64 publication,guint64 lease,char **events,GError**);
gboolean warlock_imported_clients_resume_at(WarlockImportedClients*,const char *identity,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,GError**);
/* Local feedback is separate from issued source/job events and terminal receipts. */
gboolean warlock_imported_clients_resume_feedback(WarlockImportedClients*,const char *identity,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,char **feedback,GError**);
gboolean warlock_imported_clients_enroll_feedback(WarlockImportedClients*,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,char **feedback,GError**);
/* Explicit later picker enrollment: only an expired unissued intent and strictly
 * newer publication AND lease may receive a new native two-second cutoff.
 * Same-stamp calls retain the original cutoff; issued ownership is retained. */
gboolean warlock_imported_clients_enroll_next_feedback(WarlockImportedClients*,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,char **feedback,GError**);
guint64 warlock_imported_clients_lease(WarlockImportedClients*,const char *identity);
gboolean warlock_imported_clients_uri(WarlockImportedClients*,const char *identity,char **uri,GError**);
gboolean warlock_imported_clients_status(WarlockImportedClients*,char **status,GError**);
gboolean warlock_imported_clients_empty(WarlockImportedClients*);
/* Refusal retains the owner and receiver for physical drain and exact ACK. */
gboolean warlock_imported_clients_close(WarlockImportedClients*,GError**);
G_END_DECLS
