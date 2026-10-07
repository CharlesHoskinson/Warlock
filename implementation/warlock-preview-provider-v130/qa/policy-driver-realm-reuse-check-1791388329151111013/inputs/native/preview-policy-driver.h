#pragma once
#include "elm-preview-policy.h"
#include "imported-clients.h"
#include "preview-provider-bootstrap.h"
G_BEGIN_DECLS
typedef struct _WarlockPolicyDriver WarlockPolicyDriver;
/* Native-only creator API. Held policy/outbox sources are trusted bundle bytes.
 * Success takes closure custody of the original controlled imported owner.
 * Bootstrap, original popup and endpoint must outlive the driver; callers must
 * not independently close/reset them. A nonempty issued realm cannot initialize
 * a fresh driver. No mutable JSC value or renderer-chosen grant escapes. */
/* A non-null handle with GError on grant processing uncertainty retains live
 * custody; it is not successful admission or permission to discard/recreate it. */
WarlockPolicyDriver* warlock_policy_driver_new(const char* policy_source,gsize policy_length,const char* outbox_source,gsize outbox_length,
    WarlockImportedClients*,WarlockPreviewBootstrap*,gpointer popup,const char* original_grant,GError**);
/* Retains the entire original input batch atomically before reporting success.
 * Refusal before custody leaves caller responsible for the exact bytes; stop
 * polling a producer until admission. Source epoch is stamped before JavaScript.
 * Custody survives renderer recreation, not owning process loss. */
gboolean warlock_policy_driver_native(WarlockPolicyDriver*,guint64 source_epoch,const char* event_array,GError**);
gboolean warlock_policy_driver_presentation(WarlockPolicyDriver*,const char* snapshot,GError**);
/* Urgent native quarantine bypasses ordinary queued/backpressured input. */
gboolean warlock_policy_driver_quarantine(WarlockPolicyDriver*,guint64 source_epoch,GError**);
/* Exactly one bounded driver action. The host schedules repeated calls; JS
 * callbacks store bytes only and never dispatch an effect reentrantly. Returned
 * output custody reserves one original <=8192-byte/two-event dispatch batch
 * before effects; 3195 batches/26173440 bytes bound this queue. WOULD_BLOCK leaves
 * the exact ticket retained. Pause ordinary producers and drain original work;
 * never interpret pressure as settlement. An unexpected original producer
 * contract violation retains live Unknown outcome custody rather than discard. */
gboolean warlock_policy_driver_step(WarlockPolicyDriver*,gboolean* progressed,GError**);
/* Borrowed native-only policy for its readonly visual getter/channel. */
WarlockPreviewPolicy* warlock_policy_driver_policy(WarlockPolicyDriver*,GError**);
/* Private native/QA observation only; never send this diagnostic packet to JS. */
gboolean warlock_policy_driver_inspect(WarlockPolicyDriver*,char** private_state,GError**);
/* Readonly readiness: policy queues and the original strict C physical/journal/
 * independent-confirmation gates must all be empty. No settlement is inferred. */
gboolean warlock_policy_driver_retirement_ready(WarlockPolicyDriver*,gboolean* ready,GError**);
/* Retires only the drained original native realm. The same Elm owner and its
 * permanent chronology remain alive; this does not close or reconstruct policy. */
gboolean warlock_policy_driver_retire(WarlockPolicyDriver*,GError**);
/* Original creator only, after strict retirement. Same binding, later original
 * Native epoch and empty issued namespace are required. Before grant processing,
 * refusal leaves *owned unchanged. Once policy custody transfers, *owned points
 * to the sole replacement driver even on uncertain processing failure: retain it.
 * Caller retains the newly-created imported owner on pre-transfer refusal. */
gboolean warlock_policy_driver_reopen(WarlockPolicyDriver** owned,const char* outbox_source,gsize outbox_length,
    WarlockImportedClients*,WarlockPreviewBootstrap*,gpointer popup,const char* original_grant,GError**);
/* Refuses with original custody retained until exact Elm and native physical /
 * independent confirmation gates permit original strict realm closure. */
gboolean warlock_policy_driver_close(WarlockPolicyDriver*,GError**);
G_END_DECLS
