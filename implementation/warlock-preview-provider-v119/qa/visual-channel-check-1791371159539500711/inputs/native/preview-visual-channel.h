#pragma once
#include "elm-preview-policy.h"+#include <glib-object.h>
G_BEGIN_DECLS
typedef struct _WarlockVisualChannel WarlockVisualChannel;
typedef enum { WARLOCK_VISUAL_INVALID=1, WARLOCK_VISUAL_WRONG_THREAD, WARLOCK_VISUAL_WRONG_CONTEXT,
               WARLOCK_VISUAL_NOT_CURRENT, WARLOCK_VISUAL_EXHAUSTED } WarlockVisualError;
/* Separate visual counters never issue native effect/control ordinals. Context
 * objects are supplied by native, strongly retained until explicit detach.
 * The host must bind the real WebKit callback identity and conceal physically
 * before policy changes/invalidation. This component proves neither DOM nor
 * frame application. No renderer-supplied object establishes context identity. */
WarlockVisualChannel* warlock_visual_channel_new(void);
gboolean warlock_visual_channel_attach(WarlockVisualChannel*, WarlockPreviewPolicy*, GObject*, char** grant, GError**);
gboolean warlock_visual_channel_offer(WarlockVisualChannel*, WarlockPreviewPolicy*, GObject*, char** packet, GError**);
gboolean warlock_visual_channel_retry(WarlockVisualChannel*, WarlockPreviewPolicy*, GObject*, char** packet, GError**);
gboolean warlock_visual_channel_ack(WarlockVisualChannel*, WarlockPreviewPolicy*, GObject*, const char* exact_receipt, GError**);
gboolean warlock_visual_channel_current(WarlockVisualChannel*, WarlockPreviewPolicy*, GObject*, GError**);
gboolean warlock_visual_channel_invalidate(WarlockVisualChannel*, GObject*, GError**);
gboolean warlock_visual_channel_detach(WarlockVisualChannel*, GObject*, GError**);
/* Destroys only detached channel custody, never its policy/native resources. */
gboolean warlock_visual_channel_close(WarlockVisualChannel*, GError**);
G_END_DECLS
