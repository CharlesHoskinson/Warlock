#pragma once
#include <glib.h>

/* Delivery order belongs to the original popup's control stream. It does not
 * certify native effect success, physical cleanup or a final journal ACK. */
typedef struct { guint64 delivered; gboolean ordered,inFlight; } PreviewControl;
static inline gboolean preview_control_next(const PreviewControl *state,guint64 ordinal) {
    return !state->inFlight && ordinal && state->delivered<G_MAXUINT64 && ordinal==state->delivered+1;
}
static inline void preview_control_begin(PreviewControl *state,guint64 ordinal) {
    g_assert(preview_control_next(state,ordinal));state->ordered=TRUE;state->inFlight=TRUE;
}
static inline void preview_control_delivered(PreviewControl *state,guint64 ordinal) {
    g_assert(state->inFlight);state->inFlight=FALSE;
    g_assert(preview_control_next(state,ordinal));state->delivered=ordinal;
}
