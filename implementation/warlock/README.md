# Warlock integration candidate

This is the active editable product source. It was materialized once from held GUI143; `ANCESTRY.json` records exact inherited bytes and the held build. Historical prototypes and reports are unchanged. Future source revisions are Git commits here.

Follow `docs/warlock-build-loop/v2/INSTRUCTIONS.md`. Generated builds/browser profiles live in ignored `.build/` / `qa/runs/`; commit only minimal reports needed by a bounded claim. Use the held pinned compiler/toolchain by verified reference, not another toolchain copy. Changed Main/Bar/Popup must be rebuilt as one asset package before native qualification.

This candidate is not installed on the user's desktop. Its component results, native scenario acceptance and full release acceptance are separate. Preserve the exact GUI143/core16/plugin19/AQ155 ABI manifests for inherited native code; numbering alone is not ABI proof. The controlled preview curtain remains closed until native reveal conditions are implemented and accepted.

The shared surface host accepts `--text-scale 1.5` for enlarged text. Values from
1 to 2 scale the base text and taskbar height together; the default remains 1.
This startup option does not configure the desktop or implement a Settings page.

In the taskbar, vertical wheel input scrolls an overflowing row. While a bar
control has keyboard focus, Home/End reach the endpoints and Left/Right visit
enabled controls in order. Current logical selection survives presentation
updates, menu grabs and output resizing; focus restoration requires real document
focus and a currently rendered enabled control. Context operations retain the
existing native physical-key/pointer proof and Elm policy route. Current observed
coverage and remaining AT/independent review are recorded in
`qa/evidence/dense-taskbar/manifest.json`.

In a window-group picker, Up/Down traverse enabled controls and Home/End reach
the close action and final member. The view retains the focused logical identity
through the same popup lease, including reordered publications, resizing and
late preview-content growth. A remembered old-lease identity alone cannot restore
focus; native reflow can retain the currently focused eligible DOM control.
Navigation changes no window state; activation and context operations still use
the existing Elm/native authority. The ten-member, 150% text native journey,
member menus, selected-window pixels and real keyboard recipient are recorded in
`qa/evidence/dense-picker/manifest.json`. That snapshot leaves native popup
reflow and action-menu overflow unverified; see the later evidence below.
Applicable AT and independent acceptance remain open.

Window-action menus reveal their current Elm-selected operation after row growth
or viewport changes. Ordinary publications preserve deliberate wheel scrolling
and Tab focus on Close; keyboard navigation reveals the current focus again.
An inactive document cannot acquire operation focus from the view adapter.
`qa/evidence/dense-menu/manifest.json` records the 480x360 native journey at
200% text, current operation endpoints/disabled rows/Tab/Escape and text pixels,
plus the default-size minimize/restore regression. AT, independent original
acceptance remain open; later native reflow evidence is described below.

Native output resizing now retires the popup input lease and publishes the same
Elm choices under a fresh lease without a destructive window refresh. The
retained GTK presentation tree explicitly resizes its previous allocation,
including shrinking after growth. `qa/evidence/popup-reflow/manifest.json`
records 18 overflowing configured pins and ten native roots at 200% text:
480x360 to 640x480 and back preserves the focused picker member and menu
operation, configured/control order, complete physical control bounds and label
pixels. In that retained failed journey, Escape and exact activation passed,
but the final GTK keystroke failed its original six-second observation
deadline. Default-size minimize/restore, real
application typing and Task View dismissal pass against the same host. Applicable
AT and independent original-scenario acceptance remain open.

The current shared host relinquishes taskbar keyboard eligibility before
dispatching an admitted, current-binding Activate or Restore request. The
existing Elm policy chooses the action and native authority validates it; the
host makes no window-focus call. Escape and background Minimize retain the
keyboard-eligible parent. `qa/evidence/keyboard-handoff/manifest.json` records the
successful original reflow journey: the exact last picker member activates once,
its pixels are presented, and its GTK entry receives the physical keypress.
The same host also passes Escape, inactive-Minimize keyboard preservation,
Restore typing and subsequent Task View dismissal. Original deadlines, owning
core/plugin pair and compiled Elm assets are unchanged. Applicable AT and
independent acceptance still remain open.

Window actions now include a snap chooser for eligible ordinary windows. It
shows six half/quarter regions derived from the observed native work area,
including negative output origins and odd dimensions. Tab reaches the chooser
utility; Enter opens it without applying the selected menu operation. Inside
the chooser, Up/Down and Home/End traverse enabled controls, and selection uses
the current view identity. Changed output/work-area scope retires the preview.
The selected region uses the shared color, glow, shadow and shading language.
Native placement uses the negotiated snap capability. Apply closes the chooser,
reads fresh unblocked facts and submits the exact region through the shared
geometry request allocator, custody journal and native authority. Changed scope
refuses placement; only a correlated native receipt settles the request. Unknown
retains the existing read-only recovery path and is never replayed. Original
scenario observations and independent acceptance remain separate.


The taskbar Settings control opens validated appearance preferences. Choose Night
or Dawn and 100%, 125%, 150% or 200% text size, then Save settings. Draft changes
remain unapplied until an exact save receipt; committed appearance also changes
the native taskbar reservation. Tab/arrows/Home/End reach the controls and Escape
closes the popup. Refresh discards the draft and reads storage without repeating
an unconfirmed write. The supervisor selects private settings storage; a stale
revision, invalid value or unsupported schema cannot overwrite the existing copy.
The bounded native save/whole-host-restart and invalid-scale journey is tracked
under ELM-UX-030; independent and applicable release acceptance remain separate.

The Notifications button opens the current native notification center. It shows
plain notification text, live actions, and bounded retired history. Incoming
notifications never open a popup or steal focus; the center announces status
politely while open. Producer actions use exact service, unique bus producer,
numeric ID and native incarnation, consume their target before signal emission,
and cannot repeat after a lost receipt. Refresh reads current targets without
replaying actions. Expiry, dismissal, replacement and producer disconnect retire
actions; text from expired entries remains readable in history.

The freedesktop notification adapter lives in the existing broker process, uses
the session bus, and claims its name without replacement or queuing. If another
notification service owns the name, the center explains its unavailability. It
implements plain body/actions, never executes notification text, and does not
advertise activation-token, sound, image, markup or persistence capabilities.
See the [native notification protocol](https://specifications.freedesktop.org/notification/latest/protocol.html).

The System button opens native volume, networking, power and session controls.
Unavailable services are named explicitly; supported controls show current
observed state. Volume presets and mute use the current local audio sink. Network
changes use NetworkManager, and power/session requests use login1 capabilities
and the broker's own session. Restart, shutdown, logout and disabling networking
require confirmation; Cancel has no native effect. Refreshed state never repeats
a prior request. A confirmed change, an accepted request, a refusal and an unknown
result have distinct messages. Submitted means the service accepted the request;
it does not claim that a suspension or shutdown completed.

ELM-UX-032 has a private native-protocol and compositor recording of unavailable
networking with observed remaining state, physical volume/mute changes and
confirmation cancellation. Actual hardware, authorization dialogs, accessibility
and independent original-scenario acceptance remain separate.
