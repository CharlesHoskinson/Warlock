# Warlock integration candidate

This is the active editable product source. It was materialized once from held GUI143; `ANCESTRY.json` records exact inherited bytes and the held build. Historical prototypes and reports are unchanged. Future source revisions are Git commits here.

Follow `docs/warlock-build-loop/v2/INSTRUCTIONS.md`. Generated builds/browser profiles live in ignored `.build/` / `qa/runs/`; commit only minimal reports needed by a bounded claim. Use the held pinned compiler/toolchain by verified reference, not another toolchain copy. Changed Main/Bar/Popup must be rebuilt as one asset package before native qualification.

This candidate is not installed on the user's desktop. Its component results, native scenario acceptance and full release acceptance are separate. Preserve inherited ABI manifests and verify the current recorded core/plugin/Aquamarine pair before loading native code; numbering alone is not ABI proof. Authorized native picker previews have bounded recordings, while full transition, resource and release acceptance remain open.

Current implementation status and remaining behavior are in the [feature-completion checklist](../../docs/warlock-roadmap/FEATURE-COMPLETION.md). Current design guidance and the [contributor plugin section](../../DesignLanguage/catalog/index.html#contributors) distinguish the editable product from frozen browser examples.

[Offline component recovery](RECOVERY.md) now retains reviewed predecessor and
candidate commands plus compatible preference copies outside Elm. The local
command restores the predecessor selection after a managed host exits, preserves
candidate state, and refuses competing managed hosts. This is preparation for
reversible deployment; accepted Omarchy fallback and full release packaging remain
open. See [recovery evidence](qa/evidence/offline-recovery/README.md).

[Manifest-driven release builds](RELEASE.md) now verify a pinned local input set,
rebuild the three Elm roots and complete native host, and assemble an archive with
payload hashes and the retained exact core/plugin/Aquamarine tuple. The current
protected build reproduces existing asset and host bytes and rejects an altered
consumed source. The archive remains unqualified for installation pending complete
provenance, redistribution, clean offline rebuild and full release gates.

Always on top and MAX use typed native intents, observed geometry protocol 3 and confirmed labels through the existing custody/no-replay route. Stable picker geometry and checkable state now pass the original pointer/keyboard pin/MAX journey. Two floating MAX roots coexist, share committed paint/input order and recover their return placements; actual input-hole passthrough and no-activation exceptions are recorded. Clicking an eligible modal-blocked MAX parent now focuses its accepted modal without forwarding a GTK button event, and retiring the modal restores parent clicking. See [current modal evidence](qa/evidence/max-modal-focus/README.md), [no-activation evidence](qa/evidence/max-no-activation/README.md) and [pin/MAX evidence](qa/evidence/pin-check/README.md). Wider family/fullscreen/race/AT and independent acceptance remain open. Earlier failed [picker](qa/evidence/picker-target-stability/README.md) and [draft](qa/evidence/pin-max/README.md) evidence remains historical. Taskbar application pins are a separate preference feature.

Settings now offers optional keyboard and recovery help. Use **Dismiss help** to hide it and **Show help** to reopen it; the same control retains keyboard focus. Dismissal lasts for the host session, including closing and reopening Settings. Help works while preference writes are pending or unconfirmed and does not send effects, save preferences or discard an unsaved draft. Shortcut-conflict persistence, native AT and offline rollback remain unfinished. See [Settings help evidence](qa/evidence/settings-help/README.md).

Keyboard focus now uses an outer contour distinct from the active-window underline and pressed state. The taskbar reserves eight pixels around its scaled row, reveals the whole contour when horizontal navigation scrolls, and retains the two-line group caption. Settings reserves the same contour space; high contrast and forced colors retain a solid focus ring. Browser checks cover first/last controls at narrow and wide widths, 100%/200% text, all themes and effects preferences. Native keyboard actions and high-contrast save/restart evidence are scoped in [outer-focus evidence](qa/evidence/outer-focus-indicators/README.md); all-surface AT, output profiles and independent acceptance remain open.

The shared surface host accepts `--text-scale 1.5` for enlarged text. Values from
1 to 2 scale the base text and taskbar height together; the default remains 1.
This startup option sets initial scale; the persistent Settings page described below is a separate integrated route.

The taskbar paints a focused control while its WebKit document actually owns keyboard focus, including after pointer-menu use when the browser does not match `:focus-visible`. Native focus loss clears the contour; the Active underline and pressed state retain their separate meaning. This is a projection of actual document/control focus and does not acquire keyboard ownership or issue a window effect. The enlarged 18-pin native menu/scroll/resize journey is recorded in [dense outer-focus evidence](qa/evidence/dense-outer-focus/README.md).

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

These focus guarantees do not mean pointer target geometry is stable across preview arrival; that layout defect remains visible in the pin/MAX native failure above.
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
The selected region uses a provisional shell palette and glow/shadow treatment;
complete adoption of the approved layered-window tokens remains open.
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
notifications never open a popup or steal focus. Permitted new arrivals use
one root-selected announcement owner; the notification center provides session
DND and critical-interruption controls. Producer actions use exact service, unique bus producer,
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


The Files button opens Home, the installed explorer's seven collections, or a
folder entered as an absolute path or `~/…`. Typing does not open a location;
choose Open folder explicitly. Navigation reuses the exact installed Quickshell
instance and reports success only after native location readback. The menu closes
before navigation and does not force keyboard focus afterward. Unknown requests
are never automatically repeated; Refresh reads current explorer state.

The adapter uses the installed explorer's launch/reuse IPC and never invokes or
rewrites `ops.sh` or its Quint specification. Frontend text cannot select an
executable, QML root, instance or IPC method. The ELM-UX-033 recording uses the
actual installed explorer with private HOME/runtime: physical collection choice,
folder typing and observed reuse pass. Cold startup, minimized/other-workspace
summoning, accessibility and independent acceptance remain separate obligations.

Application jump lists show the current desktop entry's declared actions and up
to twelve supported local recent files. Open the first search result's Actions
control, use an application entry's context menu, or open Application actions
from a window menu with an unambiguous catalog identity. A pinned application
with no running window also exposes its jump list through the context menu.
Recent files must name the exact desktop identity in the native XBEL provider;
foreign entries, remote URIs and stored bookmark commands supply no actions.

Elm retains immutable action identities and dispatches an explicit selection
once. Native GIO owns desktop-file commands, document URIs and launch context;
none are frontend capabilities. The popup closes before submission. Submitted
reports native handoff, not application readiness; an unknown result persists
without automatic replay, and Refresh only observes current actions.

ELM-UX-010 has compiled replay/browser/Quint checks, actual GIO/XBEL admission
checks and a private compositor recording of the two declared actions, an owned
recent document and their exact native argv. The launcher route was physically
exercised; additional taskbar routes, assistive technology and independent
original-scenario acceptance remain separate. Run focused component checks with
`qa/check-search.py --jump-lists` through the protected CPU launcher and native
checks with `qa/native-window-feedback.py --jump-lists` through the v2 loop.

Native attention requests produce an amber top-edge marker and an Attention
label on an inactive application's taskbar entry. The active application uses a
blue bottom-edge marker and `aria-current`. Family attention includes eligible
modal members; native active state takes precedence. The indicators are static,
with distinct edge shapes in forced colors and darker amber in the Dawn theme.
Pinned and running applications precede utility controls at the left edge;
Reconnect remains first when the shell is detached.

Attention is read through the existing native authority's opt-in observation
version, keyed to the same binding, incarnation and scene revision. Legacy native
read shapes remain available. Elm joins only coherent bracketing facts and
rejects contradictory same-revision observations. A click cannot invent attention
or active state. Actual native GTK attention, visible pixels, activation and key
recipient checks pass in an isolated desktop; native accessibility consumers and
independent ELM-UX-009 acceptance remain open. Use `--attention` with the protected
component and native runners for this slice.

The candidate authority registers three approved Omarchy shell routes only when their live chords are free: Super+Alt+Space opens Applications, Super+Escape opens System, and Super+Shift+Alt+Comma opens notification history. `native/shell-bindings.lua` retains the move/resize source bindings; it no longer unconditionally installs these three shell chords. No candidate bindings are installed on the user's desktop.

Settings displays native default/alternative availability and observed active mappings. Choose **Keep existing shortcut**, the free default, or its displayed free alternative for each route; **Save shortcut choices** stores the decisions privately and applies only the fixed admitted chords. Existing bindings are never removed or disabled. Native foreign/configuration fingerprints and store revision CAS reject stale choices; a lost outcome retains Unknown until an explicit read, with no automatic retry. Saving is optional; the bar routes and help remain usable.

The bounded native campaign observes a real default conflict, disabled default selection, one explicit save, byte-equivalent customized bindings, help reopening, the chosen alternative and the preserved F12 fixture override. Apps Escape now waits for key release: the current native campaign passes repeated reopening, keyboard traversal, dismissal and taskbar focus restoration. Native configuration reload reinstalls only free selected chords and preserves explicit Keep; its generation retires earlier fingerprints. The original keyboard campaign now opens Apps through its default and submits one actual catalog entry. The separate original-shortcut focus-recipient interval remains failed. Repeated taskbar Home navigation passes after Enter activation moves to its matching key release. Snap now admits both advertised geometry protocols 2 and 3 without bypassing current scope, feasibility or no-replay checks. The preceding source tuple passed the original native keyboard journey across all nine surfaces, including committed right-half placement, Task View and held-Alt switching, with no injected pointer events and normal exit. A later pin/MAX integration regression exposed repeated Home loss. Exact once-only return of an already-admitted GTK key replay to its original live bar engine now clears that boundary; two current native recordings pass all nine surfaces with zero injected pointer events and normal cleanup. See [keyboard replay evidence](qa/evidence/bar-keyboard-replay/README.md). Full restart, native AT/IME consumers and independent acceptance remain unqualified. Stored choice/fresh-store and strict stale/Unknown checks pass in the compiled/transport scope. Native AT, offline rollback and the complete effective Omarchy inventory remain open. See [shortcut choice evidence](qa/evidence/shortcut-choices/README.md), [Apps dismissal evidence](qa/evidence/launcher-dismissal/README.md), and [registration evidence](qa/evidence/shortcut-registration/README.md), and [taskbar Home evidence](qa/evidence/taskbar-home/README.md), and [current snap and keyboard evidence](qa/evidence/current-protocol-snap/README.md).

The native callbacks publish fixed typed navigation events through a bounded
64-event journal, scoped to its admitted live frontend. The broker strictly
decodes the read-only journal; the shared immutable Elm root owns surface
selection. Initial binding adoption skips history, duplicate/old events cannot
reopen a dismissed surface, gaps require a fresh shortcut, and an accumulated
navigation burst opens its latest surface. Locked/exclusive-input sessions
cannot publish routes. Navigation never adds window or application effect
authority.

From Applications, Escape returns keyboard focus to its current taskbar control.
Arrow keys/Home/End reach the other taskbar controls; Enter/Space, Tab, Escape
and Menu/Shift-F10 operate the existing migrated surfaces. Focused verification
uses `--keyboard-shell` with the protected component and native runners. The
compiled reducer/model checks establish event admission and no-replay behavior;
physical surface journeys and independent ELM-UX-023 acceptance are separately
recorded in `qa/evidence/keyboard-shell/manifest.json`. Omarchy's remaining
commands/keybindings and applicable native accessibility gates stay open.

Native move and resize ownership is now observed from the owning core's drag
controller through a strict, binding-correlated `pointer-ownership` snapshot.
Elm retires shell surfaces without requesting focus, preserves existing native
transactions and launch state, and suppresses surface entry while a current
move/resize observation is active. Older or duplicate observations cannot release
ownership. A grouped target without a root identity remains input-blocking.
The native authority independently checks the actual controller before window
activation/minimize/restore and shell shortcut or Alt-Tab admission. Existing
geometry guards continue to refuse competing placement changes.

The source bindings include Omarchy's Super+left/right-button move/resize and
the adopted Alt additions; they invoke native dispatchers. This does not modify
the running desktop. `--drag-ownership` selects the focused protected component
and native checks. The component checks pass, but the original two-output drag
journey did not begin: the private outputs reported 1600×1000 instead of the
fixture's expected 800×600, and did not reach that geometry within six seconds.
Both failed setup reports and the passing current taskbar regression are retained
in `qa/evidence/drag-ownership/manifest.json`. Caption/edge, cancellation,
AT/device coverage and independent original acceptance remain open.

Settings now offers **High contrast theme** alongside Night and Dawn. Its saved
value uses the same typed, revision-correlated appearance protocol and private
atomic store. The native host admits only these three named themes; an unknown
palette or path cannot become a settings request. Unsaved edits do not alter
appearance, and restart restores the committed theme and text scale.

High contrast uses white text and borders on black, inset yellow keyboard focus,
and distinct cyan active/amber attention bands. Disabled controls keep readable
labels. System forced colors take precedence. The shared palette applies to bar,
popup, text-field and snap controls without changing their action identities.

Focused `--high-contrast` checks measure the actual compiled Settings controls
in all 12 theme/text-scale combinations and forced colors. The physical native
journey saves at 150%, traverses keyboard focus, records white glyph/yellow
outline pixels and restarts the host; the existing Dawn journey is checked
separately. Evidence is in `qa/evidence/high-contrast/manifest.json`.
ELM-UX-027 remains partial: all-surface native theme/scale coverage, applicable
accessibility consumers and independent original acceptance remain open.

The taskbar now projects a named toolbar with an explicit active toggle state,
and the window switcher projects a named listbox with exactly one selected
window option. These remain views of the authoritative Elm state. Current
compiled/browser checks cover names, roles, selection changes and retirement;
the actual native switcher still cycles, cancels, activates and restores with
physical keyboard input. Native AT acceptance remains open: two private Orca
qualification attempts failed before observing both shell surfaces. The
read-only inspector's desktop-root traversal bug is corrected but has not been
rerun after the AAR stop threshold. See `qa/evidence/accessibility/manifest.json`
for the exact failed observations and source tuple. `--accessibility` uses
explicitly owned nonactivating session/AT buses and a private Orca home; its
silent speech adapter cannot establish audible or braille acceptance.

Shell text fields now have explicit composition start/end state. Same-field
observations preserve preedit, final input is coalesced with the explicit
commit, cancellation restores the prior text without submitting a query, and
closing or replacing a field retires its local composition. Original mutation
and native admission authority are unchanged. `--ime` component checks cover
the actual popup and the typed lifecycle. Private native Fcitx/GTK/WebKit
recording observes trusted field preedit and one direct Unicode commit with
correct caret and no launch/window effect; the normal launcher filtering and
refusal journey also passes. Candidate-panel traversal/commit and cancellation
remain unverified after the two-attempt stop threshold. See
`qa/evidence/ime/manifest.json`; no complete UX028 or release acceptance is
claimed from the direct-input interval.

Task View now offers **Move …** for a listed window. Its destination chooser
includes ordinary workspaces 1–10 and additional observed workspace identities.
Cancel changes nothing. Selecting a destination closes the chooser, refreshes
current authority and submits one typed transfer through the shared effect
allocator and durable custody. Pending or Unknown transfers retain their source
membership in Task View; only the matching committed receipt releases it to
new native observations. Refusal is visible in the taskbar and never moves the
window optimistically. The native controller reserves the family, refuses pinned
or grouped targets, preserves minimized state and never follows the destination
implicitly. Existing native placement records are retired after transfer.

The original ELM-UX-018 workspace-1 refusal and accepted workspace-2 transfer
were physically observed, including native receipts and actual Task View names.
Compiled reducer/custody/Quint checks pass. A supplementary empty-workspace-3
interval was not reached because the helper expected the excluded source
workspace in the destination chooser; that helper is corrected but unrerun after
the two-attempt limit. Modal/minimized/cross-output coverage, applicable AT and
independent original acceptance remain open. See `qa/evidence/transfer/manifest.json`.

Reduced motion is now a native input to the shared Elm root. The read-only
observer reads the owned session portal `reduced-motion` preference first and
falls back to GTK `gtk-enable-animations`; it never starts the portal or changes
the desktop's settings. Unknown portal uint values mean no preference. Signals,
portal owner replacement and GTK notifications update the current typed input;
stale reads and observations cannot overwrite newer state.

The documented reduced profile is **instant state presentation**: no decorative
position/size/alpha continuation, CSS animation, transition or smooth scrolling.
An acknowledged binding-scoped native profile controls compositor-owned window
and host-surface animation goals. Minimize/restore keeps the original family,
focus, custody, native receipt and Unknown/no-replay semantics. Host surfaces
are identified by actual client credentials and process start identity, never
by an application name. Settings displays the observed system preference.

The actual integrated roots, fourteen motion replay assertions, C observer on a
private portal bus, six named Quint schedules and bounded invariants pass. The
original private native minimize/restore and Task View recording passes with
compositor animations enabled, exact native settled-state traces, physical
pixels, real keyboard recipients and normal cleanup. The unchanged protected
launcher forces in-memory GTK settings, so an explicit QA-only host option sets
the actual GTK property for the fixture; the observer and Elm receive path stay
unchanged. Two earlier native failures are retained, including the production
command-admission refusal corrected before the passing campaign. Native live
preference changes, every overlay/output/device fixture, applicable AT and
independent original/release acceptance remain open. See
`qa/evidence/reduced-motion/manifest.json`.

Motion Settings now offer Follow system, Reduced motion and Full motion with a separate versioned private override record, revision-CAS saves, explicit reset and no automatic retry of an ambiguous save. Confirmed overrides govern the existing typed native profile; reset follows the latest GTK/portal source. A native accepted-family/goal tracker settles valid retained motion at the next pre-render opportunity and discards stale identities/goals without replay. Compiled root/store/model/host checks pass. Actual private native keyboard saves/resets, GTK source changes and saved Full-over-Reduced preference after a whole-host restart are observed; the combined campaign fails at a later off-screen application control. Mid-flight geometry/proxy and separate overlay/AT qualification remain open. See `qa/evidence/live-motion/manifest.json`.

The ordinary window picker now displays authorized native family thumbnails through the existing Elm preview policy. Its dedicated product source retains strict native grant, incarnation, style/crop, privacy, deadline and opaque-URI checks; the older unqualified QA source contracts and controlled curtain remain separate. Closing/reopening preserves the incarnation's native allocator and request floor. A confirmed stale-context refusal permits one changed-context demand after exact terminal acknowledgement; unknown outcomes retain custody without replay. Receiver teardown asks the same Elm reducer to retire all owned jobs before disposing native storage.

Current compiled state/source/refusal/ownership checks and the actual private native picker journey pass. A real colored family paints Live, survives minimize and ordinary reopening as Historical, and becomes Unavailable at the unchanged native expiry; Loading is observed in the actual DOM. All owned clients and helpers exit normally. Physical Loading pixels, actual AT, independent acceptance, broader resource/fairness and simultaneous family raster/export capacity remain open. The native 128MiB/two-allocation budget remains unchanged. See `qa/evidence/preview-states/manifest.json`.

The ordinary picker preview timer now runs only for a current acknowledged picker or outstanding native frame/control cleanup. Once the closed pool is physically empty, its GLib source is removed; retained logical actors keep their request floors. Current presentation acknowledgements and exact native controls can wake it again, without relaxing the source gate or replaying an effect.

The actual private native recording observes a dormant source with unchanged callback/catalog counters over one closed second, then a current reopened gate, increased request floor, fresh authorized pixels and no expired-image borrowing. Historical-frame preservation and native expiry still pass. The extended reopened journey fails normal client exit with outstanding custody, and both native attempts are retained. This is partial UI-017 evidence, not frozen interval, whole-process power/resource soak or independent acceptance. See `qa/evidence/quiescent-picker/manifest.json`.

Pin/unpin of a maximized family now completes through the existing typed window
allocator and menu receipt registry. Post-close observations compare complete
window records by incarnation, preserving actions through list reordering while
rejecting changed facts. Native MAX geometry, displayed pin/MAX state, exact
three intents and visible pixel/GTK pointer recipients pass. The initial
recording retained a picker-custody shutdown failure. Both receiver paths and
the actual WebKit callback now route only owned retirement controls during
shutdown; the unchanged native pin/MAX journey also passes normal client exit,
strict picker closure, plugin unload and private cleanup within the original
drain bound. Independent release-wide retirement evidence remains open. The
shared keyboard Home regression is now repaired; two current native keyboard
journeys pass all nine surfaces. See [pin/MAX evidence](qa/evidence/pin-max-order/README.md)
and [shutdown evidence](qa/evidence/picker-shutdown/README.md).

The primary taskbar activation/minimize/restore journey now has actual keyboard-only native evidence: one committed receipt per action, visible state cues and windows, MRU/desktop focus succession, real application-key recipients, zero injected pointer helpers and normal cleanup. This verifies existing behavior; the fixture addition changes no product policy. Native AT and independent acceptance remain open. See [primary keyboard evidence](qa/evidence/taskbar-primary-keyboard/README.md).

The unchanged original workspace-navigation journey now passes on the current integrated source tuple: Task View and taskbar restores show workspace-2 target pixels, exact native Committed receipts and real GTK keyboard recipients with membership unchanged; stale activation refuses without navigation or focus changes. Earlier failed evidence remains historical. This is current verification of existing behavior, with other-output, partial-refusal, AT and independent acceptance still open. See [workspace restore evidence](qa/evidence/workspace-restore-current/README.md).

The current Task View transfer journey passes cancellation, pinned refusal with retained workspace 1 and visible feedback, exact committed transfer to existing workspace 2 and empty workspace 3, final native membership and normal cleanup. A generic no-transfer footer was corrected only for the explicit transfer journey; all three receipts must match exact submitted identities and only the selected root may change workspace, with its output unchanged. Product policy is unchanged. See [current transfer evidence](qa/evidence/transfer-current/README.md); independent original acceptance and AT remain open.

Settings now offers **Disable soft effects** and **Reduce transparency**. The existing committed preference route saves both across whole-host restart; drafts and unconfirmed saves preserve the applied appearance, legacy files are upgraded only by an explicit changed save, and future versions stay preserved. Solid focus/state edges remain visible when soft shadows are off. Actual keyboard save/restart, isolated invalid-scale refusal, visible native controls and the original nine-surface keyboard regression pass. See [appearance preference evidence](qa/evidence/layer-appearance/README.md). Full layered-window styling, every surface/profile/output, AT and independent acceptance remain open.

### Preview descriptions

Window controls retain their action name and expose preview source state and fidelity through a passive `aria-describedby` relationship. Both the ordinary popup and native visual receiver render the same typed `PreviewVisual` fact; decorative preview content is excluded from the control name. Local capacity/wait/expiry/conflict feedback creates no independent live region. Fallback renders “Preview unavailable” once, preserves real window titles and keeps the existing reserved picker geometry. Hidden previews have no description relationship.

The current compiled component checks cover all eleven states/fallbacks, browser accessibility descriptions, focus/geometry retention, ID collisions and retired/foreign projections. The original native picker journey retains authorized Live/Historical pixels and the original Unavailable expiry. These preview results do not qualify native AT or speech/braille. Single-owner refusal announcements are described below. See [the scoped evidence](qa/evidence/preview-descriptions/README.md). The unchanged picker ownership model is exercised using quint-llm-kit’s implementation workflow; no authority or lifecycle properties were changed.


## Correlated refusal announcements

The integrated Elm root selects one announcement route for matched launch, workspace-transfer and settings-save refusals. The selected output uses its popup while open and its bar otherwise. Other bars retain readable visual status with live delivery disabled. Announcement receivers project typed messages only; they submit no action or focus command. A matched launch refusal preserves its existing launcher/query state and no longer requests focus relocation.

Each new refusal has a monotonic serial and the owning binding/request identity; transfers include the exact effect protocol and intent. Native validates the declared route and forwards each serial once across mirrors. Repeated receipts, repeated publications and owner changes do not replay the message. A new refusal with the same words gets its own serial. Existing refresh/recovery controls remain available.

The additive model follows quint-llm-kit’s modeling and implementation skills. Eight explicitly selected tests and positive witnesses accompany sampled safety checks; existing authority models remain unchanged. Actual compiled roots, twelve typed checks and a three-view browser fixture pass. The protected original native transfer journey also observes one identity-matched refusal in the real WebKit live-region DOM, then passes cancellation and successful existing/empty-workspace transfers with normal cleanup. See [the evidence and abstraction limits](qa/evidence/announcements/README.md).

ELM-UI-010 and WARLOCK-DL-011 remain partial. Native launch/settings announcement delivery, actual stable-focus speech/braille, independent acceptance, native adapter-unavailable delivery across providers and native speech/braille delivery and remaining provider/transport lifecycle coverage remain required. Notification arrival/DND/critical-consent behavior is described below. Unpermitted notification count/history changes do not produce an announcement through this new route. Browser/live-region DOM checks establish no audible or braille delivery.


## Notification announcement permissions

The notification center now includes **Do not disturb for this session** and **Allow critical notification interruptions for this session**, with stable keyed controls, visible On/Off detail and accessible pressed state. Both reset with the Elm shell session. DND suppresses new notification announcements while retaining current history/actions. Turning it off or enabling critical consent never replays previously observed notifications.

New arrivals are polite by default. Explicit critical consent permits assertive delivery for critical arrivals while DND is off; ordinary arrivals remain polite. Native retains the [standard urgency levels](https://specifications.freedesktop.org/notification/latest/urgency-levels.html) from a [BYTE urgency hint](https://specifications.freedesktop.org/notification/latest/hints.html). Missing/legacy or malformed hints cannot elevate urgency. Critical notifications remain live until explicitly closed, dismissed, invoked or disconnected, rather than expiring automatically.

The Elm root correlates an arrival with the current binding, notification service, admitted revision and fresh native incarnation. Initial history, repeated/older snapshots and policy edits create no announcement. Simultaneous arrivals are coalesced into one bounded message retaining every incarnation, concise summaries and a route to details; mixed-urgency batches stay polite. Native still validates the one declared owner and forwards each serial once.

The quint-llm-kit permission model, actual compiled root/view checks and protected native notification journey pass. Native keyboard controls demonstrate DND suppression, no history replay, unopted critical politeness, opted critical assertive delivery and ordinary politeness. Real WebKit reports retain the same focused node/control identity and document focus; current event-stamped DOM IDs are allowed to change. Existing producer action, expiry, reused-ID refusal and normal cleanup observations are preserved. See [scoped evidence](qa/evidence/notification-announcements/README.md).

The selected three ELM-UI-010 scenarios remain partial: actual speech/braille and independent original acceptance are not established by DOM/native transport observations. Relevant notification expiration and expired-action refusal announcements now have scoped native evidence, described below. The adapter-unavailable route is described below. The controls are session policy, not persisted settings or a guarantee of native AT delivery.


## Adapter failure announcements and explicit recovery

Matched failed reads now publish a typed adapter notice through the existing Elm root and single polite announcement owner. Notifications, Files, application actions, system controls, settings, motion and shortcut preferences use their existing request/binding guards; a wholly unavailable system adapter is distinguished from one missing capability. Proven unsent catalog reads and the window connection-loss edge also select typed notices. Text supplies the corresponding refresh or reconnect route. Duplicate receipts do not produce another message, and failed opening reads no longer issue a Focus command. Views still project native facts; this notice is an observed event, not another availability or effect policy.

**Refresh notifications** remains keyboard focusable during a read, with visible “Reading current targets…” detail. The existing Elm pending-request guard rejects extra reads. If another notification service held the bus name at startup, an explicit authenticated refresh can try again after it exits. Warlock never replaces that owner; observations and action requests never trigger a retry. Recovery is limited to a never-owned empty service. Established service loss, producer/action custody and Unknown mutations cannot be restarted or replayed by this route.

The quint-llm-kit model passed eight explicitly selected tests, five positive witnesses and sampled safety before implementation. Actual compiled checks cover matched/foreign/repeated reads, partial capabilities, read-only recovery and no Focus commands. Browser checks retain the same keyed node through pending/failure/recovery. A protected native GUI fixture uses an actual competing bus owner and duplicate real receipts: physical keyboard refresh produces one identity-matched polite message, keeps the same focused node, then recovers after the other owner exits normally without replaying a message or action. The native refresh control has measured text pixels. See [scoped evidence](qa/evidence/adapter-announcements/README.md).

ELM-UI-010 remains partial. Native speech/braille, the native provider matrix, spontaneous service-loss announcements and independent original acceptance remain open. Notification relevance is described below. Native DOM/live-region observations do not prove spoken or braille delivery.


## Relevant notification expiration and rejection

The Elm root now announces expiry only for the exact notification whose action has keyboard focus or whose action the user invoked. An unrelated history expiry stays silent. Matched expired-action refusals carry the request and full native target identity into the same polite announcement owner. DND suppresses both sources; turning it off, refocusing history, refreshing or repeating a receipt never replays a message. These outcomes remain polite even when critical-arrival interruption is enabled.

Popup focus is a passive observation admitted only for the current output owner, notification surface, publication, lease and projected control identity. It grants no action. A focused pending or retired action keeps its existing keyed DOM node with **aria-disabled** and visible unavailable detail. The user can navigate away; departure removes the retired placeholder. The renderer, native gate and Elm resolver all reject action dispatch from that placeholder. Expiry and refusal send no Focus command.

Native retains a bounded set of 64 exact expired incarnation/producer/ID facts and returns a typed reason on matched refusal. This lets Elm report expiry even when a queued action reaches the adapter after its old numeric ID has been replaced and no intermediate expired snapshot was delivered. A substituted producer or changed live target cannot inherit the expired fact. Legacy receipts remain strictly admitted with their existing shape; Unknown actions still cannot replay.

The quint-llm-kit model, nineteen compiled typed checks, twenty-one browser checks, owning native C gate/host checks and the protected original notification journey pass. Native keyboard evidence covers focused expiry with the same node/control/document focus, non-actionable retained control, explicit departure, DND/no replay, unrelated expiry silence and the original queued expiry/ID-replacement refusal. The original nine-surface keyboard journey also passes after the shared presentation change. See [scoped evidence](qa/evidence/notification-relevance/README.md).

The three selected ELM-UI-010 scenarios remain partial. Actual speech/braille, user-invoked expiry with other focus on the native path, broader focus/output/transport lifecycle cases and independent original acceptance remain required. Sampled Quint, browser and native DOM observations qualify only their recorded scopes.

### Observed Always on top checkbox

Window actions keep one **Always on top** label and keyed control identity across observed pin/unpin. The row has a visible checkbox shape and `menuitemcheckbox`/`aria-checked` semantics. The root publishes checked state only from the current provider's captured native geometry observation and exact native/menu binding; a desired toggle or Committed receipt alone cannot change it. Taskbar application Pin/Unpin remains separate. The optional typed presentation flag grants no action authority: disabled controls, stale scope and existing native proof/prepared-read/Unknown gates still apply.

MAX menu selection now exposes `aria-current` when the detail also contains committed MAX/pin state. Passive reveal/resize observations leave the selection change for the selecting observer, so keyboard navigation focuses the selected operation rather than leaving Enter on Close. The existing menu navigation proof route handles Enter; the renderer does not turn checked state into an effect.

[Evidence](qa/evidence/pin-check/README.md) records the unchanged quint-llm-kit menu-read-order model before/after implementation, 28 typed checks, 21 browser checks and the original protected native UX-016 overlap journey. Actual pointer and physical Tab/Home/Down/Enter pin/unpin preserve MAX return geometry, correlate displayed/native state and retain real pixel-to-GTK-hit agreement. Full pin/family/fullscreen/AT and independent acceptance remain open. Failed compiler/browser/native runs are retained; the native keyboard focus failure led to the selection projection fix. Browser fixtures now declare the same UTF-8 encoding as the shipped pages.

## Floating MAX overlap and input regions

A second coherent floating native MAX window now preserves the first MAX placement. Native hit traversal checks each MAX surface's actual input region using the existing XDG-origin/popup/subsurface path; an upper hole can deliver the physical click to the lower eligible MAX without changing upper painting beforehand. Both original return placements and the existing pin/MAX keyboard journey pass on the current tuple. [Evidence and limits](qa/evidence/max-input-region/README.md) retain the real failure and correction. ELM-REN-015 remains partial: one committed render/hit scene revision, transformed/modal cases, native AT and independent acceptance are still required.

## Shared committed MAX window scene

MAX painting and hit traversal now share the native window-order snapshot published after output commit, with exact structural input-region/transform and owner checks before input. The native button owner suppresses a new press on a stale MAX scene while preserving accepted releases and existing layer/grab handling. [Current native scene/press/release evidence](qa/evidence/committed-max-scene/README.md) records matching committed paint/hit revisions, actual upper pixels and lower GTK delivery, both return placements and the pin/MAX regression. The API is a private matched-core authority ABI; it adds no Elm/frontend effect policy. Independent acceptance, broader scene/race/modal/fullscreen/AT/multi-output/resource and release obligations remain open.


## MAX no-activation input

An ordinary MAX press with no eligible window in the committed scene now stops before decoration, raise, focus or cached pointer button delivery. Its matching release is suppressed; an eligible later click works normally. Layer focus, session locks, native grabs and pointer constraints retain their existing branches. The protected native recording preserves the original upper-pixels/lower-recipient journey, observes both-excluded pixels with no GTK press/release or click activation, then restores an eligible region and verifies real press/release ownership and both return placements. Pin/MAX pointer and keyboard regression also passes.

The [scoped evidence](qa/evidence/max-no-activation/README.md) maps the added quint-llm-kit model to native admission/release handling. ELM-REN-015 remains partial: retained cached focus at the shape-commit boundary, actual stale/failed-frame and button races, transformed/modal/grab/layer schedules, native AT and independent acceptance remain open.


## MAX modal activation

Ordinary MAX pointer traversal still excludes a modal-blocked parent. A qualifying button press performs an activation-only traversal of the committed scene, applies the shared native family recipient selector, revalidates the same scene, and suppresses the press/release before changing focus. It raises only the accepted focused modal; parent coordinates never become a modal click. Ambiguous, stale or ineligible selection cannot fall through to a lower root. Native layers, locks, grabs, constraints and full-loose focus retain their existing handling.

The [native evidence](qa/evidence/max-modal-focus/README.md) retains the actual pre-fix focus deadline failure. The fixed journey verifies committed owner-hit identity, real modal focus and keyboard recipient, unchanged MAX root order/geometry, visible modal pixels, taskbar family activation without a synthesized click, modal retirement and restored parent press/release. Original two-MAX/no-activation and pin/MAX regressions pass. The added quint-llm-kit model remains separate from native graph, timing, transform and AT acceptance.

The direct visible-owner modal recordings complete the focus, pixels, keyboard, no-click and restoration checks, then fail normal host exit with outstanding native picker custody/journal. Both failures are retained in the modal evidence. Native campaign acceptance stays partial until actual custody retirement is fixed; the exit check and original deadlines remain.


## Picker capture retirement before offer

The two retained visible-owner modal shutdown failures are now fixed by actual resource retirement. A source change after capture retains the unoffered buffer until its mapping/FD, exact export and native producer have retired; only then can the broker publish Refused, and its reservation/journal still needs the exact Elm acknowledgement. Unknown transport failures retain custody, and lock-delayed retirement stays pending. The strict close and original shutdown drain remain unchanged. [Current evidence](qa/evidence/picker-preoffer-retirement/README.md) includes the unchanged direct-owner modal journey passing normal host exit, actual unoffered retirement receipts, no-activation regression and quint-llm-kit sampled/model checks. Independent and release-wide resource/AT/native acceptance remain open; continue original REN-017 fullscreen policy next.

## True fullscreen and the owned menu

True fullscreen fills the output independently of floating MAX. The owned bar uses the overlay layer, keeps keyboard interactivity NONE outside its existing popup lease, and leaves pinned windows governed by native fullscreen paint/hit/focus priority. Opening the window menu is read-only. A negotiated **Exit fullscreen** item sends one typed desired-state command through the existing journal and native barriers; native readback determines Committed, Refused or Unknown. Unknown is never replayed.

The [bounded native evidence](qa/evidence/fullscreen-pin-menu/README.md) records actual fullscreen/pinned pixels, GTK press/release and focus, a reachable menu, exactly one committed exit with geometry restored and peer pin retained, original MAX/pin behavior, and unchanged direct-owner modal regression with normal shutdown. quint-llm-kit models and compiled Elm checks cover negotiation, eligibility, stale/blocked and Unknown cases separately. ELM-REN-017/ren-017 stays partial pending wider families/policy cells, protected-input races, transforms, native AT/IME and independent acceptance.

## Modal constraints and eligible recipients

The shared private native selector resolves current mapped modal topology first, then evaluates the unique deepest recipient. A live input-blocked modal is still a constraint; it cannot disappear from the tree and permit ancestor fallback. No-focus, blocked or ambiguous recipients refuse. Retired modals release the constraint; minimized families retain the existing restore path. The shell and committed MAX activation use this same selector.

[Current evidence](qa/evidence/modal-recipient-eligibility/README.md) records real unrelated GTK click/key delivery while preserving the modal incarnation, geometry and unsaved typed draft, plus exclusion of a painted native no-focus modal. The original modal/MAX and unchanged fullscreen regressions pass normal shutdown. REN-018 remains partial: actual blocked-modal schedules and wider toolkit/family/AT observations remain open. The retained original taskbar Escape keyboard-return failure is now repaired by the captured entry policy below.

Popup entry now records pointer or keyboard origin in the single Elm policy and preserves it through the stamped action relay and projection-only renderer. Pointer dismissal yields the bar keyboard lease before native grab teardown; keyboard dismissal retains its eligible bar parent. The unchanged native taskbar Escape assertion now observes actual GTK key receipt, and the unchanged nine-surface keyboard, modal/draft and fullscreen journeys pass normal shutdown. Origin is a UI return policy, not native authority. UI-011/UX-024 remain partial pending wider native lifecycle, AT and independent review. See [entry/return evidence](qa/evidence/popup-entry-keyboard-return/README.md).

Native gesture ownership now waits for a current-binding idle observation before shell input, and the owning key handler preserves active move/resize across ordinary keys and shortcuts until pointer release or explicit Escape. Current two-output input checks pass both crossings, native refusal and exactly-one end; Escape cancellation also ends once. That revision retained a failed final screenshot, so UX-021 remains partial. Keyboard-only and taskbar Escape regressions pass. Caption/edge initiation, broader lifecycle/device/AT and independent acceptance remain open. See [gesture readiness evidence](qa/evidence/pointer-ownership-readiness/README.md).


Native caption moves and edge resizes preserve their original owner, finish once on release and keep the unsaved GTK draft. Admission now rechecks the current shared family recipient and protected-input policy after the actual XDG press grant is consumed. Held presses refused after no-focus or a mapped modal cannot replay when eligibility returns. The one-output native addition, matched core/plugin rebuild, Quint checks and unchanged modal/draft regression pass. That revision retained a failed two-output capture; UX-021 and the release remain partial. See [caption admission evidence](qa/evidence/caption-gesture-admission/README.md).

## Native gesture cancellation and retirement — October 10

Escape now restores captured floating move/resize geometry without committing a drop. Cancellation after crossing outputs also restores the live source workspace. Closing the captured owner retires the gesture before button release; a same-title replacement cannot inherit the old press. A new eligible edge press at the same pixel recovers its actual pointer recipient. The current native caption/lifecycle and modal/draft regressions pass. All original two-output input assertions and the new cross-output rollback assertion pass, with a combined-capture timeout retained from that revision. UX-021 and the release remain partial. See [native gesture evidence](qa/evidence/native-gesture-terminal-reasons/README.md).

Maximized, fullscreen, tiled and snapped restoration, wider device/lifecycle schedules, AT and independent scenario acceptance remain open. Cancellation keeps the original owner and never uses release-time grouping or focus redirection.

## Native caption placement restoration — October 10

Native maximized and committed left-half snapped captions now retain placement on a click without movement, restore ordinary size at the original horizontal press fraction, and restore the captured box/modes/source workspace on Escape. Actual quarter- and three-quarter-width drags, one-output pixels, committed release, unsaved drafts and captured-owner retirement/replacement pass. A released MAX caption retires its exact old ordinary placement so the next maximize/restore captures the new box. The admitted restore effect now applies its saved prospective ordinary box after validating live identity/mode/scope. The final caption/lifecycle and original modal/draft regressions pass. Original two-output input and cross-output rollback assertions pass again after separating caption phase from the shared keybind threshold flag; that revision retained a combined-capture failure at the original five-second limit. UX-021 and the release remain partial. See [caption restoration evidence](qa/evidence/native-caption-placement-restoration/README.md).

Native fullscreen/tiled/grouped restoration, the other snap regions/repeated snaps, nondefault thresholds/key traffic, constraints/scale/rotation and resize-mode placement transitions remain unqualified.

## Nested output capture demand — October 10

The unchanged original two-output move/resize journey now passes native owner retention across taskbar/output, blocked shortcut/effect, exactly-one end, Escape and source-workspace rollback, original five-second combined 1600×600 capture and cleanup. An initial live nested capture requests one real render/commit without waiting for an occluded parent callback. The same pair passes MAX/snap caption placement/lifecycle/draft regression. No parent presentation is fabricated; external hardware/AT and independent acceptance remain open. See [current recording](qa/evidence/native-output-capture-demand/README.md).

The next GUI gap is launcher popup placement and control paint across outputs. Its blank control area in this combined image is not accepted as complete launcher presentation.


Native Apps shortcuts now open on the output of the actual keyboard recipient after a cancelled cross-output drag. The shared Elm controller resolves the press-time live output against current issued view geometry; duplicate, missing, moved, retired, ambiguous and pointer-blocked destinations cannot relocate or replay. A fresh valid shortcut clears only obsolete shortcut-refusal feedback. The original two-output drag/cancel/capture journey passes, followed by actual popup bounds, painted control pixels, physical-keyboard no-match/query/focus retention and Escape without launch or window mutation. The unchanged all-nine-surface keyboard journey passes on the same core/plugin/host tuple with normal cleanup. See [current-output shortcut evidence](qa/evidence/shortcut-current-output/README.md). Native AT and independent acceptance remain open.


Keyboard shortcuts now resolve the actual native keyboard window, mapped shell layer or live popup before choosing an output; an unrecognized focused surface is refused. The real nested output-removal journey dismisses the displaced launcher, preserves workspace identity, keeps the typed query and keyboard recovery on a declared survivor, and operates Refresh with one observed catalog read. Reconnection at identical old bounds receives a new view identity while the retired native shortcut destination stays null. No launch/window-effect replay occurs, and original drag/capture plus all-nine-surface keyboard regressions pass with normal cleanup. See [live output retirement evidence](qa/evidence/live-output-retirement/README.md). UI-019 remains partial pending its wider native/hardware/AT and independent obligations.


## Zero-output shell recovery — October 10

Warlock now suspends shell presentation when every real output disappears: the compositor's internal FALLBACK receives no bar, popup, reserved shell band or Apps shortcut event. A returning nested output flushes its parent initialization immediately, receives a fresh issued view after configure acknowledgement, and restores actual launcher focus, typed query and keyboard Refresh without replaying a launch/window effect. Workspace identity remains unchanged. The original two-output drag/capture journey and nine-surface keyboard regression pass on one mapped core/plugin/Aquamarine/host tuple with normal cleanup. See [zero-output return evidence](qa/evidence/zero-output-return/README.md).

That revision retained an offscreen application placement gap. The placement recovery described below repairs the observed floating-window case. UI-019 remains partial; physical hotplug/AT, delayed fresh old shortcut/native topology ordering, pending custody/Unknown and independent acceptance remain open. Quint retirement and parent-transport models retain named scenarios, positive witnesses and sampled safety checks; neither establishes every cross-channel order or write-backpressure schedule.


## Native application placement recovery — October 10

Orphaned workspace placement now includes the destination output origin and wraps negative logical coordinates without changing window size. After the original zero-output shell journey, the returning floating application is at its original reachable x=40/y=230, retains workspace 2 and its unsaved GTK draft, activates through the actual taskbar exactly once, receives client pointer press/release and physical keyboard input, and paints onscreen. Original move/resize/cancel/capture and MAX/snap caption/lifecycle regressions pass on the same core/plugin/Aquamarine/host tuple with normal cleanup. See [placement recovery evidence](qa/evidence/output-placement-recovery/README.md).

The original partially clipped vertical size remains unchanged; this fix restores reachable application origin and input. Smaller/rotated/scaled outputs and minimized/pinned/fullscreen/modal recovery remain unqualified. The delayed fresh old shortcut schedule described below is now observed; wider cross-channel ordering, pending custody/Unknown, physical hotplug/AT/IME and independent original acceptance remain open. The Quint model abstracts integer coordinates and atomic placement; native authority and presentation stay separately observed.


## Delayed shortcut recovery — October 10

A native shortcut reply read before output removal can arrive after a replacement view appears at identical bounds. Shortcut protocol 3 now carries the press-time native output generation. The shared Elm output controller consumes that reply without moving focus or opening a popup unless the generation matches current reconciled observations. Native add/remove signals retire a generation even when names, IDs and geometry match between reads. Unstamped legacy replies can establish/advance the serial watermark but cannot authorize root output routing.

The real nested test holds an actual validated shortcut reply, removes its output, returns a fresh view at the same 800×600 bounds, then delivers the unchanged reply through the original bounded writer. The old reply produces visible refusal without popup or window-effect replay; the next physical shortcut opens the focused launcher normally. Workspace, size and unsaved application draft survive. The existing output/drag/capture journey and nine-surface keyboard regression pass the same core/plugin/host/transport tuple. See [delayed shortcut evidence](qa/evidence/shortcut-generation-recovery/README.md).

UI-019 remains partial. This establishes delivery after host retirement/reconciliation for the observed nested schedule. Native/host observation-before-retirement ordering, other asynchronous schedules, transformed or multiple outputs, minimized/fullscreen/modal recovery, pending custody/Unknown, physical hotplug/AT/IME and independent acceptance remain open. The Quint model separates press, retirement, topology, observation and delivery; sampled safety and compiled root results remain distinct from native acceptance.


## Reachable application area — October 10

Changing a returned output to 400×200 at a negative origin previously left the floating application's input region below the screen. Native workspace transfer and changed usable-area updates now recover the first up-to-32 logical pixels of an ordinary floating window inside the area available after shell reservations and floating gaps. Size, workspace and already reachable placement are preserved. An unchanged-area recalculation leaves deliberate manual placement alone; pinned, fullscreen and grouped targets retain their existing paths.

The observed application is reachable at (-360, -32) after the smaller-output change, with its original 108×440 size and workspace 2. Actual taskbar Minimize/Restore, client pointer press/release, physical keyboard editing and native pixels pass with the unsaved draft preserved. The original output/drag/capture journey, unchanged caption/MAX/snap/lifecycle regression and delayed-shortcut recovery pass on the same core/plugin/host/transport tuple with normal cleanup. See [usable-area evidence](qa/evidence/reachable-output-area/README.md).

UI-019 remains partial. The recovery preserves a reachable input region; it does not fit an oversized client entirely into a smaller screen. Minimized-before-output-change, pinned/fullscreen/grouped/modal families, wider transforms/output combinations, concurrent gestures/custody/Unknown, physical hotplug/AT/IME, independent acceptance and original release/package/rollback gates remain open. Quint and compiled-helper results are separate from native acceptance.


## Minimized application recovery — October 10

A real taskbar Minimize committed before the returned output changed to 400x200 at (-400,-200). The application remained minimized across reconciliation, then a real taskbar Restore committed exactly once at reachable position (-360,-32), preserving size108x440/workspace2 and its unsaved draft. Actual client pointer press/release, physical keyboard editing and painted pixels pass normal cleanup. Existing production placement already covers this ordinary minimized case; no new production behavior is claimed. See [native restore evidence](qa/evidence/minimized-output-area/README.md).

UI-019 remains partial. Pinned/fullscreen/grouped/modal recovery, actual retirement while minimized, wider transforms, hardware/AT/IME, independent acceptance and release/package/rollback gates remain open. This is qualification of existing behavior, not an additional feature.


## Pinned application recovery — October 10

A pinned floating application previously remained at (-360,30), below the real 400x200 output at (-400,-200). The owning changed-area placement now recovers it at (-360,-32) without unpinning or changing its size108x440/workspace2/draft. Real taskbar Minimize/Restore each submit once; actual client pointer press/release, physical keyboard editing and native painted pixels pass. The unchanged minimized-before-reconfigure and caption/MAX/snap/lifecycle regressions pass the exact tuple with normal cleanup. This advances UI-019 reachable application recovery; independent original acceptance and full release remain open. See [pinned usable-area evidence](qa/evidence/pinned-output-area/README.md).

Pinning a native floating window keeps it visible across workspaces. That state now survives the same-monitor usable-area recovery; it does not exclude the window from recovery. This differs from a persistent catalog launcher pin. Recovery preserves size and a reachable input region; fullscreen, hidden/grouped targets, other-monitor transfers and unchanged-area manual placement retain their existing paths. Quint named/positive/sampled checks remain separate from native GUI and hardware/AT acceptance.

UI-019 remains partial. Actual pin/minimized output retirement, wider transforms/fullscreen/group/modal recovery, custody/Unknown/concurrency, hardware/AT/IME, independent acceptance and release/package/rollback gates remain open.


## Pinned output retirement — October 10

Pinned applications now preserve workspace2, size108x440, pin state and the unsaved draft through the original first output removal, replacement, all-output disappearance and fresh return. Owning workspace migration avoids retired-owner gap callbacks and pinned stay-behind paths; the existing native authority permits explicit same-output navigation to the preserved workspace before pin focus. Actual taskbar Activate/Restore and native pointer/keyboard/draft/pixels pass for pinned and previously minimized applications. Real cross-output pin activation remains Refused without transfer; a live-monitor workspace move retains the pin on its old output. The prior pinned smaller/negative-origin journey passes the exact tuple with normal cleanup. See [native retirement evidence](qa/evidence/pinned-output-retirement/README.md).

A native floating pin follows its preserved workspace when its output retires; moving a workspace from a live output keeps the existing pin behavior. Recovering the pin through the taskbar may explicitly select its preserved workspace on the same output before focus. Another focus output still refuses to avoid implicit membership transfer. Existing membership, recipient, output-generation and Unknown/no-replay guards remain in the admitted effect path.

UI-019 remains partial. Hardware/AT/IME and independent acceptance, fuller transformed/fullscreen/group/modal/custody journeys, the separately observed taskbar activity-cue issue and release/package/rollback gates remain open. Sampled/named models and native evidence are distinct.

## Taskbar activity after output retirement — October 10

After real output removal/replacement, an invisible workspace member now offers Activate/Open rather than Minimize/Active. Actual taskbar Activate, Minimize and Restore each commit once, with native frames showing 27,048 red application pixels after activation/restoration and zero after minimize. Workspace2, size108x440 and the unsaved draft survive; actual client pointer and physical keyboard editing pass. The unchanged keyboard primary journey passes MRU/desktop succession, and pinned retirement/return plus cross-output/live-owner guards pass the same tuple. See [the exact observation packet](qa/evidence/taskbar-output-focus/README.md).

The Active cue refers to an eligible visible desktop family. A bar or popup holding keyboard custody keeps that family active; an invisible member remains available for explicit activation. The existing adapter filters only the action projection's focus from coherent native facts. It does not change raw native focus, window membership, effect admission or replay policy.

UI-004 remains partial: applicable native AT and independent acceptance are still required. Sampled Quint/model results remain separate from actual native observations and release acceptance.

## Single-family taskbar native accessibility — October 10

Actual private GTK/WebKit AT-SPI and Orca now qualify the focused single-family Activate/Minimize/Restore fixture. Five real AT-SPI press actions each commit once, with native focus, MRU/desktop succession, client keyboard recipients and painted/absent application frames preserved. A separate physical-Enter journey passes under actual AT observation. All current taskbar names, native active toggle states and focused controls agree with Orca; the real reader emits Activate/Minimize/Restore names. This verifies existing product behavior; no production code or ABI was changed. See [the exact AT observation packet](qa/evidence/taskbar-primary-at/README.md).

Original UI-004 inactive/active/minimized scenarios remain partial pending independent acceptance. The fixture observes the actual current AT tree before the unchanged physical frame assertion; AT-SPI action acknowledgement alone is not a paint acknowledgement. Original waits and policy remain unchanged. This does not qualify grouped/zero/refusal taskbar AT, audible speech/braille or the whole release.


## Visible taskbar refusal recovery — October 10

The taskbar now puts its existing read-only recovery control first when recovery is needed. The actual Refused frame moved it from x803 outside a 540px action region to x1, width120. Real other-output activation receives one native implicit-transfer-required Refused receipt; pin/workspace/geometry/draft and peer focus remain authoritative. Actual peer keyboard input is preserved before recovery. Clicking the visible recovery issues observations without retry or launch. Current browser and native Pending/Refused/Unknown regressions pass with normal cleanup. See [the exact refusal and recovery evidence](qa/evidence/taskbar-native-refusal/README.md).

Recovery keeps the same identity, accessible label and typed observation-only action. Pending recovery remains disabled; Refused and Unknown retain their native outcome and no-replay policy. Visual feedback stays readable with aria-live off while the existing scoped single announcer owns live reporting. This layout change adds no effect authority or new Quint model; unchanged applicable models ran in the compiled build.

Original UI-004 taskbar-refusal is partial. Primary keyboard/AT refusal, independent acceptance, already-scrolled dense arrangements and release-wide hardware/resource/package/rollback gates remain open. Next: the original zero-window pin primary keyboard journey.


## Stable launcher typing and zero-window keyboard launch — October 10

Typing in the launcher now survives the gap between an accepted Elm publication and its preceding DOM frame. Popup-owned field callbacks preserve bounded text within the same lease and rebase only read-only query messages; external edits/buttons remain publication-strict, and replacement leases retire drafts. The original native pin/reorder/restart journey passes. Physical Enter and real AT-SPI press each launch the zero-window Editor pin once through GIO. Its observed running family then minimizes/restores without another launch, receives actual client keyboard input and paints 268,432 green pixels inside its native window region. Both private native campaigns exit normally. See [the exact native and model evidence](qa/evidence/taskbar-zero-keyboard/README.md).

Input text belongs to its current field lease. The popup distinguishes its own Html callbacks from the external action port; this preserves local typing while ordinary captured actions retain exact-publication checks. The repair uses quint-llm-kit, with executable initialization, seven named positive/negative scenarios, sampled safety runs, fifteen compiled field assertions and the unchanged IME/browser regression. No native ABI, effect admission or Unknown/no-replay policy changed.

Original UI-004 taskbar-zero remains partial pending independent acceptance. The fixture does not qualify every application/AT mode or pin/reorder popup paint. Next: original UI-005 search-race with a genuinely delayed old catalog refresh, current query/selection, native pixels and applicable AT observations.


## Current launcher query across delayed refresh — October 10

Launcher typing during a refresh now reaches the authoritative Elm model. The popup adapter retains one current observational query until it posts the native presentation-applied acknowledgement, then forwards that query in FIFO order. Duplicate presentations preserve the slot; a replacement publication or lease retires it. Button/effect admission remains unchanged. See [the native search-race and model evidence](qa/evidence/launcher-search-race/README.md).

A genuine older catalog reply is held while the user changes files to editor. A newer request observes catalog generation 2; releasing the exact generation-1 reply preserves the current query, results and focused selection. Physical Enter and an actual AT-SPI press each submit one identity-bound GIO launch with current generation and recorded CURRENT_EDITOR argv. The current result paints, and the real Orca reader agrees with focus before and after the old reply. Both campaigns exit normally. The quint-llm-kit workflow verifies initialization, six named tests, sampled safety with positive witnesses and the actual adapter's ordering/retirement regression; compiled Elm and browser IME checks pass.

Original UI-005 search-race remains partial pending independent review. The unchanged native IME journey passes direct preedit and commit/caret, then fails at the previously retained candidate-popup observation deadline. Candidate commit/cancel and release-wide hardware/resource/package/rollback obligations remain open. Next: original UI-005 search-unavailable, with native query-preserving keyboard retry and accessible failure.


## Query-preserving launcher failure and retry — October 10

A matched catalog failure now enters the existing typed adapter-error channel: one request-correlated polite announcement, without a receipt-triggered focus command. Refresh has a distinct typed event that uses the same catalog-request authority while retaining the current control; opening Apps still owns initial search focus. Both failed and successful Refresh receipts preserve focus and query. No launch or window action is replayed. See [the exact native failure/retry evidence](qa/evidence/launcher-unavailable/README.md).

An owned desktop name exceeding the unchanged 512-unit bound makes the real authority return an unavailable catalog. Physical keyboard retry and actual AT-SPI press both recover matching Files results after metadata repair, with the query retained, actual AT/Orca status/focus and painted controls. Two deliveries of each genuine failed receipt produce one announcement; a fresh explicit failed read has its own correlation. Enter in the unavailable field, recovery and Escape issue no launch/window effect. The updated delayed-catalog search race still launches only its current generation through physical Enter. All native campaigns clean up normally.

The repair implements the existing quint-llm-kit adapter-announcement specification, including matched/repeated/foreign reads, successful recovery and unchanged focus. The executable model, 34 compiled adapter assertions, shared announcement ownership, local-field/query-delivery/IME/pin checks and announcement/IME browser regressions pass. Two old compiled announcement arrangements gained only their missing native idle fact; original assertions and production input gates remain intact.

Original UI-005 search-unavailable and UI-010 adapter-unavailable acceptance remain partial pending independent review. Audible/braille consumers, wider failure causes and the previously retained native IME candidate gate remain open. Next product work: ordinary visible authorized preview states and identity-correct title/icon fallback, preserving the native grant/custody and current-renderer conditions.

### Application icon and title fallback — October 10

Expired retained previews now resolve a uniquely declared `StartupWMClass` application icon even when the desktop filename differs from the native window class. Exact desktop filenames keep priority; ambiguous matches use the existing generic icon. Picker titles occupy the text column and icons retain their 48px size without moving the family target.

The [current evidence](qa/evidence/preview-application-fallback/README.md) records actual GTK/GIO positives and ambiguity negatives, compiled preview and browser geometry/focus checks, and the original native expiry scenario with correct icon/title pixels, current AT names and normal cleanup. Full preview-state attempts retain their live-paint/Loading failures; Loading and independent acceptance remain open. The unchanged metadata/privacy model runs through quint-llm-kit; its sampled pass does not certify native rendering or desktop-entry discovery.

### Task View refusal recovery — October 10

A refused window choice now restores Task View's workspace filter after fresh native observations are ready. The exact issued intent identifies the return context; the original family receives current DOM focus if still eligible, otherwise the current workspace or All windows control does. Unknown, committed, foreign and duplicate outcomes cannot trigger this return, and opening another interface or replacing native authority cancels it. Recovery emits no native window action.

The [model and native evidence](qa/evidence/taskview-refusal-recovery/README.md) follows quint-llm-kit: executable initialization, eight named tests, sampled safety and eight positive witnesses precede implementation. The compiled root replay preserves the original Task View checks and adds refusal/lifecycle cases. A genuine pinned cross-output refusal restores the actual filtered popup through physical keyboard selection, with focused controls, native pixels and feedback. Read-only Refresh preserves the filter without replay, Escape restores the peer keyboard recipient, and drafts and the main desktop survive normal cleanup.

Original ELM-UI-006 overview-refusal remains partial pending applicable AT and independent review. Empty-workspace navigation, the broader original overview journeys and release acceptance remain open. The Quint abstraction covers one issued choice and UI context; native transport, grants, timing, custody and presentation retain their separate acceptance obligations.

### Native empty-workspace inventory — October 10

Task View now lists ordinary native workspaces that have no windows. Its active marker comes from the focused native output's workspace, so it remains available with no application focus. Keyboard browsing an empty row displays an explicit empty notice with other workspace markers, All windows and Close Task View still reachable. The [current source and native evidence](qa/evidence/taskview-empty-inventory/README.md) separates this visible browsing behavior from the still-required native workspace activation.

The existing authenticated geometry observation carries workspace IDs, native workspace/output owner generations and the active workspace. Strict Python and Elm decoders reject malformed, duplicate, foreign or unsupported metadata. The integration root admits inventory only with its accepted geometry receipt; the Task View projection joins matching request, sequence, revision, output and binding. Pending/Unknown window transfers retain their old display membership even if the source workspace retires; inventory never grants window action authority.

The quint-llm-kit model executes before implementation, with six named scenarios and sampled safety/positive witnesses. Current roots compile and all original Task View/refusal assertions plus empty-inventory checks pass. A real native empty workspace has a keyboard-focused active marker, painted controls, an explicit selected empty view, observation-only browse/close and preserved desktop/no-application focus. The original populated-workspace membership, pointer browsing and Escape recipient assertions remain intact. All owned processes clean up normally; failures in earlier fixture setup are retained.

ELM-UI-006 overview-empty remains partial: actual GUI activation of an empty workspace still needs a separately correlated native navigation effect. Applicable AT and independent review, the remaining overview scenarios and release acceptance remain open.

### Native navigation to an empty workspace — October 10

Task View now offers **Go to workspace** for an existing inactive ordinary empty workspace, separately from browsing its window list. Keyboard and pointer activation use workspace owner identities, source/destination output owners and the exact geometry context. The host admits the intent durably before forwarding; the broker records Unknown before native dispatch. The existing native authority changes the active workspace, clears application keyboard focus and checks that window membership remains unchanged before returning Committed.

Pending, Refused and Unknown have distinct feedback. Refusal restores the selected workspace context after fresh observations. Unknown blocks further mutations while keeping Task View dismissal and read-only workspace recovery available. Recovery queries the exact historical intent; it never resubmits an effect or infers success from a changed desktop. Completed workspace feedback yields to a subsequent window action and does not hide the empty-state message.

The [scoped evidence](qa/evidence/taskview-workspace-navigation/README.md) includes quint-llm-kit initialization, ten named tests and sampled safety with four positive witnesses, strict C/Python durable-journal checks, compiled Elm integration, and real keyboard/pointer navigation, painted Go controls, exact durable receipts and normal helper cleanup. The original window navigation model and original Task View assertions remain unchanged. Full native lost-ack/restart coverage, applicable AT and independent ELM-UI-006 acceptance remain open. This effect creates no workspace and transfers no window; populated destinations continue through the existing family selection path.
### Workspace status recovery from the taskbar

When a workspace switch cannot be confirmed, the taskbar now offers **Refresh workspace status**. It reads the exact recorded outcome and never submits the switch again. A refused switch restores Task View's destination selection and dismissal; reconnect can recover a real native outcome lost before durable settlement. The [native recovery evidence](qa/evidence/taskview-workspace-recovery/README.md) also covers a settled receipt lost before frontend delivery and physical pointer use of the painted taskbar recovery control. Applicable assistive technology and independent original ELM-UI-006 acceptance remain open.

### Accessible Task View filter selection — October 10

Task View's selected workspace filter now exposes pressed toggle-button state to native assistive technology, using the existing immutable Elm selection. Strict native admission requires exactly one selected filter and rejects incomplete, conflicting or foreign checked state. Browsing still submits no window or workspace mutation.

The [scoped evidence](qa/evidence/taskview-filter-accessibility/README.md) retains the passing compiled/model/native-admission checks and actual AT-SPI selected-state observation. The full keyboard/Orca journey fails when WebKit crashes while tabbing to workspace 2; its original deadline and normal-client-exit failure remain intact. Native restore, dismissal focus return and independent original ELM-UI-006 acceptance on this updated tuple remain open.

### Transfer member retirement — October 10

If the selected transfer window closes while its workspace remains, Task View now returns to that workspace's browse view with current keyboard focus. If the workspace also disappears, it returns to All windows. Incomplete observations keep the choice intact; another incarnation cannot replace it, and retirement emits no native action.

The [native before/after evidence](qa/evidence/taskview-transfer-retirement/README.md) records the stranded-chooser failure and the corrected filtered view, painted controls, no replacement activation and physical keyboard return after Escape. The new quint-llm-kit model precedes implementation and the original Task View assertions remain passing. Applicable AT and independent original overview-retire acceptance remain open.

### Transfer chooser cancellation — October 10

Escape now returns from the transfer chooser to its same eligible Move control; Enter reopens it, and Cancel returns focus again. A second Escape closes Task View and returns keyboard input to the original native window. If the opener is unavailable, reserved or no longer in the current view, cancellation focuses the current workspace or All control instead. It emits no native mutation and cannot choose another incarnation.

The [native before/after evidence](qa/evidence/taskview-transfer-cancel/README.md) records the original whole-overview dismissal failure, the premature input-retirement failure and the corrected keyboard/pixels/no-mutation journey. Quint modeling preceded the code. Applicable AT and independent original overview-cancel acceptance remain open.

### Preview Loading paint — October 10

The picker now gives its Loading view a browser paint opportunity before forwarding an already issued native Acquire. Elm retains the exact original job and deadline behind a single-use ticket; cancellation drops only the matching unsent job immediately. Release and acknowledgement commands remain immediate. The ticket creates no native permission or capture policy.

The [before/after evidence](qa/evidence/preview-loading-paint/README.md) includes the previously missing Loading observation, a current native screenshot showing both Loading cards without either fixture's window pixels, and the unchanged authorized Live/Historical/Unavailable journey. quint-llm-kit modeling preceded implementation. Native assistive-technology descriptions, broader capacity/fairness and independent original ELM-UI-016 acceptance remain open.

### Two live previews within the native storage budget

The ordinary window picker can now show two authorized live window-family previews together. Each family owns a separate immutable sealed backing; export duplicates its descriptor instead of copying the encoded image into a second allocation. The original two-slot/128 MiB budget remains in force, including the temporary vector-to-backing handoff. Export release retains the producer charge until exact retirement closes its native mapping and backing.

The [scoped evidence](qa/evidence/picker-shared-storage/README.md) links quint-llm-kit initialization, named custody/capacity tests and reachable safety witnesses to the implementation. Direct C++ checks cover immutable shared backing, separate families, capacity refusal and legacy export behavior. The real native picker journey displays each family's own live pixels, retains its authorized historical frame on minimize, expires to unavailable at the original deadline, and drains both storage slots on dismissal. Full assistive-technology observation, broader capacity/fairness, hardware memory measurements and independent ELM-UI-016 acceptance remain open.

### Reopening a quiescent picker

The current host now passes the [original quiescence/reopen journey](qa/evidence/picker-reopen-cleanup/README.md), including normal client exit. Reopening observes the current native identity and advances its retained request floor, presents fresh owned pixels or an explicit unavailable state, and submits no repeated window effect. The closed interval has unchanged picker callback/catalog counters; an acknowledged reopen wakes them. The older outstanding-custody failure is preserved. This qualifies existing implementation, rather than delivering another GUI feature. Dormancy with authorized retained storage, frozen whole-process power/wakeup/resource budgets, native AT and independent acceptance remain open.

### Switcher reselection and keyboard focus

When the selected switcher member disappears, local and global switchers now focus the next eligible member of the frozen chord once. Metadata refreshes and title changes retain selection without repeating focus; physical Alt+Tab steps still move it. An empty chord dismisses without choosing a newly arrived incarnation. Global chords retain the application's keyboard return policy, so Escape returns physical input to the application instead of leaving it on the bar.

The [before/after evidence](qa/evidence/switcher-reselection-focus/README.md) includes quint-llm-kit initialization, named tests and reachable safety witnesses, compiled production replays, and the original local/global native keyboard journeys. The global chord uses the existing application-return branch of `popupOrigin`; local bar entry retains its captured return policy. Actual allocator address reuse, speech/braille and independent ELM-UX-014/026 acceptance remain open. The separate accessibility campaign missed its original bar-tree deadline; that failure is retained.

### Active groups with multiple windows

A grouped taskbar item now keeps its window count and shows Active when either member is foreground. The same detail drives its existing active styling and native toggle state. Clicking the group still opens its window picker; inactive and fully minimized groups retain their count without Active.

The [before/after evidence](qa/evidence/taskbar-group-active-state/README.md) records five compiled production cases, the original browser accessibility checks, and actual native names/toggle-state agreement. Pointer dismissal returns to the application, while keyboard entry uses the toolbar's Home/arrow navigation. The native AT journey then encountered a WebKit termination while reopening the picker. The failed run, kernel observation and recovery route are retained; full native action, speech/braille and independent ELM-UI-009 acceptance remain open.

### Active picker and menu resize — October 10

An ordinary ready popup now keeps its accepted Elm policy when native output
locations change and every view identity/generation remains exactly unchanged.
The routing table updates without withdrawing registration or reissuing reads.
Changed capabilities and unready/refused/exhausted registration retain their
existing reconciliation path. Native resize still seals the old input before
reflow mints a fresh presentation lease; this grants no new window authority.

At 200% text, picker cards adapt to the available popup height without reducing
the font. Fresh-lease presentation reveals the actual retained focused control
after layout/focus settles; ordinary publications preserve deliberate scrolling,
and an old remembered selection cannot restore focus without a current control.
The [current evidence](qa/evidence/popup-reflow-current/README.md) records the
complete 18-pin/ten-member native picker and menu growth/shrink journey, exact
selection/order, readable pixels, native input retirement, Menu/Shift-F10/Tab and
Escape, one final activation and actual GTK keyboard delivery with normal cleanup.

quint-llm-kit modeling preceded the routing change. Eight named model checks,
sampled safety with four positive witnesses, 21 compiled reducer/integration
checks and 50 browser checks pass; original focus and reflow assertions remain.
Earlier small-card, registration, late-reveal and fixture failures remain frozen.
Original ELM-UI-008 overflow-resize acceptance remains partial pending applicable
native AT and independent review, with broader providers/output profiles and
release-wide hardware/resource/package obligations separate.


## Explicit New instance

A uniquely catalog-matched window menu now offers **New instance**, with an
accessible name identifying the application. The current application actions
menu offers the same control even when the desktop entry declares no extra
actions. It remains separate from declared desktop actions and recent files.

The single Elm reducer rechecks the current view, menu origin and catalog
identity, retires the popup, then requests the existing identity-bound native
application launch. Ordinary taskbar activation, minimize and restore keep their
window-action behavior. Pending and Unknown launches disable New instance;
stale views, removed identities and ambiguous window-to-catalog matches cannot
submit through this route. Refusal never becomes an inferred duplicate launch.

The quint-llm-kit model and actual compiled reducer/view checks cover these
rules. Native pointer, Menu/Shift-F10 and application-action-menu observations,
exact GIO arguments, receipts and normal cleanup are recorded in
[New instance evidence](qa/evidence/explicit-new-instance/README.md).
A Submitted receipt establishes native launch submission. Applicable native AT,
enlarged/dense menu coverage and independent original UI-004/UI-008 acceptance
remain separate release obligations.
