# Warlock integration candidate

This is the active editable product source. It was materialized once from held GUI143; `ANCESTRY.json` records exact inherited bytes and the held build. Historical prototypes and reports are unchanged. Future source revisions are Git commits here.

Follow `docs/warlock-build-loop/v2/INSTRUCTIONS.md`. Generated builds/browser profiles live in ignored `.build/` / `qa/runs/`; commit only minimal reports needed by a bounded claim. Use the held pinned compiler/toolchain by verified reference, not another toolchain copy. Changed Main/Bar/Popup must be rebuilt as one asset package before native qualification.

This candidate is not installed on the user's desktop. Its component results, native scenario acceptance and full release acceptance are separate. Preserve inherited ABI manifests and verify the current recorded core/plugin/Aquamarine pair before loading native code; numbering alone is not ABI proof. Authorized native picker previews have bounded recordings, while full transition, resource and release acceptance remain open.

Current implementation status and remaining behavior are in the [feature-completion checklist](../../docs/warlock-roadmap/FEATURE-COMPLETION.md). Current design guidance and the [contributor plugin section](../../DesignLanguage/catalog/index.html#contributors) distinguish the editable product from frozen browser examples.

The always-on-top/MAX draft adds typed pin/unpin, observed geometry protocol 3 and confirmed state labels through the existing custody/no-replay route. The changed Elm roots, native host, native authority and owning ConfigActions unit compile, with 13 focused replay checks. Its original native interaction remains unfinished. The subsequent picker layout fix reserves source-independent row geometry; native recording now reaches the context menu, exactly one maximize receipt, MAX pixels and the matching real GTK pointer hit. The later Always-on-top action does not satisfy the original completion predicate within six seconds, so pin/unpin and final overlap observations remain open. See [picker stability evidence](qa/evidence/picker-target-stability/README.md). See the [retained draft evidence](qa/evidence/pin-max/README.md). Taskbar application pins are a separate preference feature.

Settings now offers optional keyboard and recovery help. Use **Dismiss help** to hide it and **Show help** to reopen it; the same control retains keyboard focus. Dismissal lasts for the host session, including closing and reopening Settings. Help works while preference writes are pending or unconfirmed and does not send effects, save preferences or discard an unsaved draft. Shortcut-conflict persistence, native AT and offline rollback remain unfinished. See [Settings help evidence](qa/evidence/settings-help/README.md).

The shared surface host accepts `--text-scale 1.5` for enlarged text. Values from
1 to 2 scale the base text and taskbar height together; the default remains 1.
This startup option sets initial scale; the persistent Settings page described below is a separate integrated route.

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

ELM-UI-010 and WARLOCK-DL-011 remain partial. Native launch/settings announcement delivery, actual stable-focus speech/braille, independent acceptance, adapter-unavailable outcomes and the frozen notification relevance/DND/urgency policy remain required. Unpermitted notification count/history changes do not produce an announcement through this new route. Browser/live-region DOM checks establish no audible or braille delivery.
