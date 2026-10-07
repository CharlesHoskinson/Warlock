#ifndef ELM_CONTEXT_KEYS_H
#define ELM_CONTEXT_KEYS_H

#include <stdint.h>
#include <stddef.h>

/* Each source retains its timestamp watermark across presentation/lease changes.
 * Equal timestamps may contain distinct physical events (e.g. Shift then F10).
 * At the signature bound the whole remainder of that timestamp fails closed.
 * Newer means unsigned forward distance strictly less than half the clock range.
 * This is replay suppression, not transport authentication or a held-key guard.
 */
#define CONTEXT_KEY_SIGNATURE_LIMIT 32u

typedef struct {
    uint32_t type, time, hardware, keyval, state, group;
    uintptr_t window, device;
} ContextKeySignature;

typedef struct {
    int initialized;
    uint32_t watermark;
    size_t count;
    ContextKeySignature signatures[CONTEXT_KEY_SIGNATURE_LIMIT];
} ContextKeySource;

static int context_keys_same(const ContextKeySignature *a, const ContextKeySignature *b) {
    return a->type==b->type && a->time==b->time && a->hardware==b->hardware
        && a->keyval==b->keyval && a->state==b->state && a->group==b->group
        && a->window==b->window && a->device==b->device;
}

static int context_keys_admit(ContextKeySource *source, const ContextKeySignature *signature) {
    if (source->initialized) {
        uint32_t advance=signature->time-source->watermark;
        if (advance==UINT32_C(0x80000000)) return -1;
        if (advance>UINT32_C(0x80000000)) return 0;
        if (advance!=0) {
            source->watermark=signature->time;
            source->count=0;
        }
    } else {
        source->initialized=1;
        source->watermark=signature->time;
    }
    for (size_t i=0;i<source->count;i++)
        if (context_keys_same(&source->signatures[i],signature)) return 0;
    if (source->count>=CONTEXT_KEY_SIGNATURE_LIMIT) return -1;
    source->signatures[source->count++]=*signature;
    return 1;
}

#ifndef CONTEXT_KEYS_PRIMITIVES_ONLY
/* Include after GTK/WebKit declarations and the host's popup_view declaration. */
static ContextKeySource context_key_sources[2];
static int context_key_admit(GtkWidget *widget, GdkEventKey *key) {
    if (!key || (key->type!=GDK_KEY_PRESS && key->type!=GDK_KEY_RELEASE)) return FALSE;
    ContextKeySignature signature={
        .type=(uint32_t)key->type,.time=key->time,.hardware=key->hardware_keycode,
        .keyval=key->keyval,.state=key->state,.group=key->group,
        .window=(uintptr_t)key->window,
        .device=(uintptr_t)gdk_event_get_device((GdkEvent *)key)
    };
    return context_keys_admit(&context_key_sources[widget==GTK_WIDGET(popup_view)?1:0],&signature);
}
#endif
#endif
