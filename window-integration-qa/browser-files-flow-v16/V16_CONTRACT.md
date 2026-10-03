# Immutable actual Files press receipt

V15's genuine Files click focused the exact Files window, changed grid to list,
and generated one button1/modifier0 receipt. The original identity oracle refused:
the selected peer was control:Show list, while the receipt read control:Show grid.
The real Explorer callback changes viewMode synchronously, changing Btn's bound
accessibleName/actionIdentity before the QA Btn.clicked listener reads them.

V16 changes only copied shell QA instrumentation. Btn.qml, Explorer.qml and all
original fifteen checks remain byte exact. A QA Connections object observes the
same exact Btn child MouseArea's real pressed/canceled/clicked signals without
replacing or delegating original handlers. At actual press it captures immutable
primitive name/identity, exact component/observer token, press generation, actual
button/modifiers, visibility/enabled/enabled2 and current viewMode. Missing or
ineligible identity, unsupported button/modifiers, or malformed mouse metadata
cannot arm a receipt. A new press first revokes the old capture. Cancellation,
object destruction and lifetime replacement invalidate it. Pressed=false alone
does not revoke it: Qt may transition pressed before emitting the same release
clicked signal. No receipt is accepted from merely an exposed peer/query label.

Only that same MouseArea's actual clicked signal can consume the capture exactly
once, with the same object token/generation and actual button/modifiers. The
observer records the immutable press name/identity in the existing receipt fields,
plus the current post-handler label/identity, original press metadata and observer
generation as diagnostics. The actual mouse route, original callback and native
window focus decide acceptance through the unchanged original oracle. Keyboard
or accessibility activation of Btn.clicked cannot produce this pointer receipt.
Absent, canceled, mismatched or consumed capture yields an explicit refused
diagnostic with empty identity; it never substitutes the current/reactive label.

This receipt is an observation of an actual component gesture, not permission to
click another identity. If the selected peer changes before press, the original
identity equality still fails. If the real callback does not change viewMode or
focus as expected, the original callback/native-focus oracle still fails. Runtime
window PID/start/stableId/session, strict native hit/cursor, release, app/data/code,
draft/caret, reload, eighteen main guards and normal lifecycle are unchanged.

Pure formal/Qt JavaScript signal tests establish recorder behavior before runtime
instrumentation changes. CPU-only QObject/Connections tests cannot establish
physical MouseArea delivery or installed event ordering. Exact real copied QML
sources remain pinned; root's exclusive actual run provides that final authority.
No main GUI/configuration, product source, browser input, or Files operation changes.
