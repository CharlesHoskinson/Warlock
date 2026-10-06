#pragma once
#include "preview-control.h"
#include <string.h>

/* The caller derives receiver from the actual native WebKit target. Binding
 * and epoch are decoded canonically from the packet. This is delivery metadata;
 * every effect still requires its original native handler validation. */
typedef struct {
    guint64 lifetime,session,frontend,receiver,epoch;
} PreviewControlGrant;
typedef enum {
    PREVIEW_CONTROL_REFUSED,
    PREVIEW_CONTROL_INVOKE,
    PREVIEW_CONTROL_REPEAT_RECEIPT
} PreviewControlDecision;
typedef struct {
    PreviewControl prefix;
    PreviewControlGrant grant;
    gboolean initialized;
    guint64 confirmed;
    char pending[4097],latest[4097];
} PreviewControlDelivery;
static inline gboolean preview_control_grant_equal(PreviewControlGrant a,PreviewControlGrant b) {
    return a.lifetime==b.lifetime && a.session==b.session && a.frontend==b.frontend &&
        a.receiver==b.receiver && a.epoch==b.epoch;
}
static inline gboolean preview_control_delivery_init(PreviewControlDelivery *state,PreviewControlGrant grant) {
    if(!state || state->initialized || state->confirmed || state->prefix.delivered || state->prefix.inFlight || state->prefix.ordered ||
       !grant.lifetime || !grant.session || !grant.frontend || !grant.receiver || !grant.epoch)return FALSE;
    state->grant=grant;state->initialized=TRUE;return TRUE;
}
static inline PreviewControlDecision preview_control_delivery_receive(PreviewControlDelivery *state,
        PreviewControlGrant actual,guint64 ordinal,const char *wire,gsize length) {
    if(!state || !state->initialized || !preview_control_grant_equal(state->grant,actual) ||
       !ordinal || !wire || !length || length>4096 || strlen(wire)!=length || state->prefix.inFlight)
        return PREVIEW_CONTROL_REFUSED;
    if(ordinal==state->prefix.delivered && !strcmp(wire,state->latest))
        return PREVIEW_CONTROL_REPEAT_RECEIPT;
    if(!preview_control_next(&state->prefix,ordinal))return PREVIEW_CONTROL_REFUSED;
    // Fixed storage is reserved before invoking a handler. No receipt can make
    // this packet enter the handler again, even if its effect outcome is Unknown.
    memcpy(state->pending,wire,length+1);
    preview_control_begin(&state->prefix,ordinal);return PREVIEW_CONTROL_INVOKE;
}
static inline gboolean preview_control_delivery_complete(PreviewControlDelivery *state,guint64 ordinal) {
    if(!state || !state->initialized || !state->prefix.inFlight ||
       state->prefix.delivered==G_MAXUINT64 || ordinal!=state->prefix.delivered+1)return FALSE;
    memcpy(state->latest,state->pending,sizeof(state->latest));
    preview_control_delivered(&state->prefix,ordinal);state->pending[0]='\0';return TRUE;
}
static inline guint64 preview_control_delivery_receipt(const PreviewControlDelivery *state) {
    return state && state->initialized && !state->prefix.inFlight?state->prefix.delivered:0;
}
// This compact prefix confirms receipt delivery to the original frontend. It
// cannot confirm an in-flight/future invocation or assert effect settlement.
static inline gboolean preview_control_delivery_confirm(PreviewControlDelivery *state,
        PreviewControlGrant actual,guint64 ordinal) {
    if(!state || !state->initialized || !preview_control_grant_equal(state->grant,actual) ||
       !ordinal || ordinal>state->prefix.delivered)return FALSE;
    if(ordinal>state->confirmed)state->confirmed=ordinal;
    return TRUE;
}
static inline gboolean preview_control_delivery_confirmed(const PreviewControlDelivery *state) {
    return state && state->initialized && !state->prefix.inFlight &&
        state->confirmed==state->prefix.delivered;
}
