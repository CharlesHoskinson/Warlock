#pragma once
#include <glib.h>
#include <string.h>

/* Kernel start time parser, not a renderer-supplied process identity. */
static gboolean popup_start_parse(const char *text,guint64 *result) {
    if (!text || !result || strlen(text)>65536) return FALSE;
    const char *end=strrchr(text,')');
    if (!end || end[1]!=' ' || !end[2]) return FALSE;
    g_auto(GStrv) fields=g_strsplit(end+2," ",-1);
    if (g_strv_length(fields)<20 || strlen(fields[0])!=1) return FALSE;
    const char *number=fields[19];guint64 value=0;
    if (!*number || (number[0]=='0' && number[1])) return FALSE;
    for (;*number;number++) {
        if (*number<'0' || *number>'9' || value>(G_MAXUINT64-(guint64)(*number-'0'))/10) return FALSE;
        value=value*10+(guint64)(*number-'0');
    }
    if (!value) return FALSE;
    *result=value;return TRUE;
}
typedef struct {
    guint64 pid,start,view,generation,topology,publication,lease;
    guint32 popup,root;
    gboolean active,mapped,root_mapped,same_display,ready,current_owner;
} PopupNativeIdentity;
static gboolean popup_identity_valid(const PopupNativeIdentity *s) {
    return s && s->pid && s->start && s->view && s->generation && s->topology &&
        s->publication && s->lease && s->popup && s->root && s->popup!=s->root &&
        s->active && s->mapped && s->root_mapped && s->same_display && s->ready && s->current_owner;
}
static gboolean popup_identity_same(const PopupNativeIdentity *a,const PopupNativeIdentity *b) {
    return popup_identity_valid(a) && popup_identity_valid(b) && a->pid==b->pid &&
        a->start==b->start && a->view==b->view && a->generation==b->generation &&
        a->topology==b->topology && a->publication==b->publication && a->lease==b->lease &&
        a->popup==b->popup && a->root==b->root;
}
