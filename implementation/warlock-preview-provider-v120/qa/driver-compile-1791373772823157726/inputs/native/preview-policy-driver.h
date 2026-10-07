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
 * callbacks store bytes only and never dispatch an effect reentrantly. */
gboolean warlock_policy_driver_step(WarlockPolicyDriver*,gboolean* progressed,GError**);
/* Borrowed native-only policy for its readonly visual getter/channel. */
WarlockPreviewPolicy* warlock_policy_driver_policy(WarlockPolicyDriver*,GError**);
/* Private native/QA observation only; never send this diagnostic packet to JS. */
gboolean warlock_policy_driver_inspect(WarlockPolicyDriver*,char** private_state,GError**);
/* Refuses with original custody retained until exact Elm and native physical /
 * independent confirmation gates permit original strict realm closure. */
gboolean warlock_policy_driver_close(WarlockPolicyDriver*,GError**);
G_END_DECLS
