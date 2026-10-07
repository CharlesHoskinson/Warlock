#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct WarlockImportedClients WarlockImportedClients;
gboolean warlock_imported_clients_retirement_poll(WarlockImportedClients *owner,void *delivery,gpointer popup,char **events,GError **error);
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
/* Opt-in controlled namespace. Empty receiver and native cleanup reservations
 * precede the first job. The owning native transport permits only one such
 * namespace; reload retains this owner and cannot reset its grant or prefix.
 * No legacy raw command/retirement API may invoke this owner's controls.
 * Strict completed-actor close remains separate from live-binding detachment. */
WarlockImportedClients *warlock_imported_clients_open_controlled(void *transport,gpointer popup,guint64 first,guint64 publication,guint64 lease,char **initial,char **grant,void **endpoint,GError **error);
gboolean warlock_imported_clients_propose_control(WarlockImportedClients*,void *delivery,gpointer popup,const char *identity,const char *command,char **proposal,GError**);
/* Only original native-issued immutable tickets are effects. Returned receipt
 * proves that the dispatcher returned, independently of its effect outcome.
 * On an Unknown handler outcome, retain the receipt AND original obligations. */
gboolean warlock_imported_clients_dispatch_control(WarlockImportedClients*,void *delivery,gpointer popup,const char *ticket,char **events,char **receipt,GError**);
gboolean warlock_imported_clients_confirm_control(WarlockImportedClients*,gpointer popup,const char *confirmation,char **receipt,GError**);
gboolean warlock_imported_clients_control_receipt(WarlockImportedClients*,gpointer popup,char **receipt,GError**);
/* Call on the opening GTK thread. Inputs are actual native catalog subjects and
 * current admitted GTK presentation stamps. Capacity creates no job or proof;
 * repeated enrollment reuses the original deadline and identity. Events never
 * report a fabricated Refused. The typed result is local scheduling feedback. */
gboolean warlock_imported_clients_enroll(WarlockImportedClients*,gpointer popup,guint64 subject,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,GError**);
gboolean warlock_imported_clients_command(WarlockImportedClients*,const char *identity,const char *command,char **events,GError**);
gboolean warlock_imported_clients_poll(WarlockImportedClients*,const char *identity,char **events,GError**);
/* Factual native lifetime observation only; does not release resources or jobs. */
gboolean warlock_imported_clients_retirement_state(WarlockImportedClients*,const char *identity,char **facts,GError**);
/* Trusted native owner only. The renderer host must first establish exact Elm
 * settlement and its ordered control barrier. Delivery is borrowed from the
 * same bootstrap, original endpoint and receiver epoch; no UI cleanup claim
 * substitutes for native resource retirement and terminal acknowledgement. */
gboolean warlock_imported_clients_retire_native(WarlockImportedClients*,void *delivery,gpointer popup,const char *identity,gboolean *retired,char **facts,GError**);
/* Native QA inventory on the original receiver, not a cleanup certificate. */
gboolean warlock_imported_clients_actor_counts(WarlockImportedClients*,void *delivery,char **facts,GError**);
/* Trusted native observation; renderer readiness must match retained own proof. */
gboolean warlock_imported_clients_retirement_observe(WarlockImportedClients*,gpointer popup,const char *identity,char **events,GError**);
/* Borrowed original ReceiptDelivery capability, same popup and epoch. Retries
 * the retained oldest completion; transport ACK never grants physical cleanup. */
gboolean warlock_imported_clients_retirement_pending(WarlockImportedClients*,void *delivery,gpointer popup,char **events,GError**);
gboolean warlock_imported_clients_retirement_control(WarlockImportedClients*,void *delivery,gpointer popup,const char *identity,const char *command,char **events,GError**);
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
/* Exact old-job physical/terminal retirement and retained request floor precede
 * explicit succession of an expired unissued resume intent. Both picker stamps
 * increase; same-stamp retries and old APIs keep their original cutoff. */
gboolean warlock_imported_clients_resume_next_feedback(WarlockImportedClients*,const char *identity,guint64 publication,guint64 lease,WarlockImportedAdmission*,char **events,char **feedback,GError**);
guint64 warlock_imported_clients_lease(WarlockImportedClients*,const char *identity);
gboolean warlock_imported_clients_uri(WarlockImportedClients*,const char *identity,char **uri,GError**);
gboolean warlock_imported_clients_status(WarlockImportedClients*,char **status,GError**);
gboolean warlock_imported_clients_empty(WarlockImportedClients*);
/* Refusal retains the owner and receiver for physical drain and exact ACK. */
gboolean warlock_imported_clients_close(WarlockImportedClients*,GError**);
G_END_DECLS
