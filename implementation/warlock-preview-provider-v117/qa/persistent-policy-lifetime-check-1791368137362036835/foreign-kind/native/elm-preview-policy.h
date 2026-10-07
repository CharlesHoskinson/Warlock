#pragma once
#include <glib.h>
G_BEGIN_DECLS
typedef struct _WarlockPreviewPolicy WarlockPreviewPolicy;
typedef enum {
    WARLOCK_POLICY_INVALID_INPUT = 1,
    WARLOCK_POLICY_WRONG_THREAD,
    WARLOCK_POLICY_WOULD_BLOCK,
    WARLOCK_POLICY_PROCESSING_UNKNOWN,
    WARLOCK_POLICY_NOT_CLOSED
} WarlockPolicyError;

/* Native-only API. Source bytes must come from the held compiled asset package.
 * No JSC context or mutable JS value escapes this owner. This module issues no
 * native ticket and performs no effect or physical cleanup. */
WarlockPreviewPolicy* warlock_preview_policy_new(const char* source, gsize length, GError** error);
/* Caller retains original input on WOULD_BLOCK. PROCESSING_UNKNOWN must never
 * be treated as a safe refusal, success or permission to reconstruct the model. */
gboolean warlock_preview_policy_invoke(WarlockPreviewPolicy*, const char* input, char** output, GError** error);
/* Refuses normal destruction while original policy membership/ingress remains,
 * before its trusted native-close notification, or after processing uncertainty. */
gboolean warlock_preview_policy_close(WarlockPreviewPolicy*, GError** error);
G_END_DECLS
