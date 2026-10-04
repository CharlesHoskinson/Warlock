# Windows-style right-click contract

Status: additive amendment candidate requested by the user; specification only.
The frozen 242-requirement/417-scenario baseline and its historical acceptance
remain unchanged. `ELM-RC-*` identifiers are separate until a reviewed amendment
maps them into delivery and UI/UX coverage. No feature is accepted by writing this
document. The normative candidate requirements and Given/When/Then scenarios are
[mirrored in OpenSpec](../../openspec/changes/elm-right-click/specs/elm-context-menus/spec.md).

## Existing obligations

This contract refines `ELM-UI-008 menu-invocation` and overflow, `ELM-UX-010`
catalog/recent-item jump lists, `ELM-UX-023` keyboard routes, `ELM-UX-024` focus
scopes, `ELM-UX-025/026/027` native accessibility/announcements/reflow,
`ELM-UX-028` IME, `ELM-UX-032` system-control adapters and `ELM-UI-007` correlated
outcomes. Identity and authority guards inherit `ELM-ARC-005/006/007`, and modal
eligibility inherits existing native window policy. The existing
[interaction contract](INTERACTION.md) wins where this refinement is silent:
refusal keeps a menu open with feedback; uncertain work is never replayed;
application pinning differs from window always-on-top.

## Reference behavior and deliberate product choices

Microsoft documents Alt+Space for the active window menu, Shift+F10 for a selected
item's context menu, and Shift+right-click for taskbar app/group window menus.
Our specification keeps those routes where the shell owns the relevant target,
and preserves customized shortcuts through the existing preference contract.
[Microsoft keyboard shortcuts](https://support.microsoft.com/en-us/accessibility/windows/keyboard-shortcuts-in-windows).

Windows has a system-managed window menu for position, size and close operations.
Our shell provides the equivalent operations only through supported native
capabilities; Linux client decorations and permissions may differ.
[Microsoft About Menus](https://learn.microsoft.com/en-us/windows/win32/menurc/about-menus).

Microsoft's taskbar design supports provider-defined tasks and recent destinations
on application jump lists, including pinned launchers with no running windows.
Our provider contract follows that model without inferring arbitrary commands
from labels or claiming Windows-specific app integration.
[Microsoft Taskbar Extensions](https://learn.microsoft.com/en-us/windows/win32/shell/taskbar-extensions).

Microsoft distinguishes contextual flyouts from menu bars and describes pointer
and keyboard invocation. Menu density, grouping and focus policy below are our
explicit product decisions; they are not assertions about every Windows 11 build.
[Microsoft menu flyouts](https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/menus).

## Ownership and invocation

| Surface | Ordinary secondary click | Additional routes | Owner |
| --- | --- | --- | --- |
| Shell/server titlebar and window icon | Window operations | Alt+Space for current eligible window | Native authority + Elm menu |
| Taskbar application icon | App menu/jump list | Menu key, Shift+F10; Shift+secondary click for window/group operations | Shell |
| Group picker/preview item | Exact family/window menu | Menu key, Shift+F10 | Shell |
| Empty taskbar | Taskbar settings | Menu key/Shift+F10 when background focus is explicit | Shell |
| Shell-owned desktop icon/selection | Item actions from declared icon/file/launcher provider | Menu key, Shift+F10 | Desktop icon provider; Files semantics for file icons |
| Empty desktop | View/sort/refresh, supported new/paste, display and personalization entry points | Menu key/Shift+F10 at desktop focus | Shell desktop provider |
| Shell-owned Files item/selection | Supported file actions | Menu key, Shift+F10 | Files adapter |
| Shell-owned Files empty area | Directory/background actions | Menu key, Shift+F10 at directory focus | Files adapter |
| System controls, launcher/Task View owned items | Declared context actions or no menu | Menu key, Shift+F10 where supported | Relevant shell adapter |
| Application client area, including client titlebars | Original app behavior | Original app keyboard handling | Application; no shell substitution |

Secondary means the configured logical context button, normally physical right
button. Left-handed remapping must work. A titlebar gesture cannot steal a click
from an app-declared client region. Touch/pen long-press is a separately declared
provider gesture; it must use the same context identity if supported, and is not
silently claimed by the mouse-only implementation.

Opening a menu may change shell focus/selection so the user can navigate it, but
must not activate, restore, raise, minimize, launch or commit MRU for its application
target. On a menu's outside click, dismiss then route that same gesture once through
the current native target. That click may legitimately focus another app; opening
or dismissing the menu alone cannot do so.

## Window-menu state table

Standard order is Restore, Move, Size, Minimize, Maximize, separator, Close.
Supported operations unavailable in the current state remain visibly disabled;
unimplemented or unsupported operations are absent, with a labeled unavailable
status for a requested window-menu route. Never show a clickable operation that
cannot be dispatched. All items use current native capabilities and eligibility;
this table does not override lock, exclusive-input, modal or policy restrictions.

| Observed state | Restore | Move | Size | Minimize | Maximize | Close |
| --- | --- | --- | --- | --- | --- | --- |
| Ordinary restored window | Disabled | If native move supported | If native resize supported | If supported | If supported | Graceful close if supported |
| Maximized | Enabled if restore supported | Disabled | Disabled | If supported | Disabled | Graceful close if supported |
| Minimized | Enabled if restore supported | Disabled | Disabled | Disabled | Disabled; restore explicitly first | Graceful close if supported |
| Fixed-size ordinary window | Disabled | If supported | Disabled/absent by capability | If supported | Disabled/absent by capability | Graceful close if supported |
| Pending/unknown operation | No mutation enabled until reconciled | Same | Same | Same | Same | Same |

Fullscreen is distinct from maximized. A fullscreen menu has an explicitly
capability-supported Exit fullscreen action; Move/Size remain disabled until
ordinary geometry is observed. No maximize toggle doubles as fullscreen exit.
Pin to taskbar is persistent application identity; Always on top is an optional,
separately labeled native window operation. Group menus offer only explicit
aggregate actions, never apply a single window geometry command to every member.

## Files and desktop action matrix

This matrix refines RC013/RC014. Capability support is required in every cell:
unsupported operations are absent or labeled unavailable, never enabled. Current
permissions, read-only state, clipboard revision, provider generation and exact
selection identity must also be revalidated at execution. A menu advertised before
a permission change cannot bypass the resulting refusal. Cut marks clipboard
intent and does not move data until a supported Paste commits.

| Action | Single item | Multiple selected items | Empty directory/background |
| --- | --- | --- | --- |
| Open | Declared file/folder/app provider | Only explicit multi-open provider with visible count | Absent |
| Open with | Supported app-choice provider for that item/type | Only declared compatible multi-selection provider | Absent |
| Cut / Copy | Supported exact item selection | Supported frozen selection | Absent; directory itself is not inferred as selected |
| Paste | Selected directory only, if writable and compatible clipboard data exists | Absent; no arbitrary destination inferred | Current writable directory with compatible clipboard revision |
| Copy path | Exact declared representation of selected item | Declared deterministic list of selected paths | Separate Copy directory path, if supported |
| Rename | One writable eligible item | Disabled; batch rename only as a distinct declared action | Absent |
| Move to Trash | Supported recoverable trash operation | Supported frozen selection, with existing confirmation/result behavior | Absent |
| Properties | Supported object metadata provider | Only explicit aggregate provider | Directory properties, if supported |
| New folder / New file | Selected directory context only if declared | Absent | Writable current directory and declared create operation |
| View / Sort / Refresh | Directory-view provider, clearly scoped to current view | Same | Current directory-view provider |
| Open terminal here | Selected directory only and declared launch provider | Absent | Current directory and declared launch provider |

For shell-owned desktop file/folder icons, apply this same selection policy and
the Files adapter. A launcher icon instead exposes catalog-declared Launch,
Properties and supported pin/remove-shortcut actions; removing a shortcut must
not uninstall the app or trash its underlying document. Ordinary secondary click
on an unselected icon selects it without launching; selected icon groups retain
their selection. Empty desktop menus target only the desktop's declared directory
or view/settings provider. They never inherit the last selected icon. If desktop
icons or a desktop directory provider are not implemented, that capability is
explicitly unavailable; no fictitious New/Paste/Trash entries imply support.

Terminal launch, Open with and New file templates require explicit providers, not
string-built commands or invented Windows executables. The current Files adapter
may implement fewer operations than this target matrix; those remain unavailable
until their declared adapters and acceptance cases pass.

## Typed interaction and authority boundary

Model a menu with an opaque MenuId, typed ContextTarget, opener identity, seat,
source gesture, focus return target, output/configuration generation, capability
generation, clipboard revision for paste, selected ActionId and optional pending OperationId. Target variants
include Window/Family, ApplicationCatalogEntry, FrozenGroup, FileSelection,
Directory, Desktop and SystemControl. Window/family keys carry complete binding
and incarnation; catalog/provider/file contexts carry their respective generation
and object identities. Labels and pointers are never authority.

Elm owns pure transitions Closed → Open/Submenu → Pending/Refused/Unknown →
Reconciled/Closed. The host validates input provenance, popup focus and placement.
The native broker validates eligibility and exact identity at execution. A menu
open or selection emits no mutating effect. An explicit command emits one typed
intent; pending suppresses duplicates. Receipt and subsequent correlated native
observation determine outcomes. Closing the view does not cancel committed work
or justify retrying an unknown action.

Close requests are graceful client requests, never process kills. Close all freezes
the displayed eligible family set, submits once per family and reports each result;
late arrivals are excluded and unsaved-document prompts remain app-owned. Move/Size
is an explicit native interactive session: arrows or pointer adjust, Enter finishes,
Escape restores its saved geometry if the target still exists. Retirement aborts
without touching replacements. Files operations retain current no-overwrite/trash
semantics and permission flow; changing `ops.sh` requires its existing Quint-first
process, outside this specification task.

## Acceptance and implementation order

All requirements/scenarios below are in the mirrored OpenSpec file. Qualification
needs compiled Elm reducer/replay cases, an independently selected Quint model,
counterexample replay and source/ABI receipts. Native acceptance additionally
needs real pointer/keyboard/application delivery, pixel/focus/geometry receipts,
normal-exit and protected cleanup, accessibility speech/braille and applicable
multi-output scale fixtures. CPU/model passes cannot substitute for those gates.
Use disposable generic fixtures; do not close real drafts or restart the main
compositor. Preserve original applicable deadlines. Freeze gesture tolerance,
hover/submenu timing, bounds and geometry budgets before measuring candidates.

Implementation slices:

1. Typed lifecycle/target/action model and nonmutating taskbar menu prototype,
   keyboard navigation, refusal and stale-target tests.
2. Native titlebar/system menu with supported minimize/restore/graceful close;
   add Move/Size/Maximize only with their native adapters and postconditions.
3. App/group/preview menus, pin persistence and explicit jump-list providers.
4. Desktop/Files/system adapters, focus scope, mixed-button and modal fixtures.
5. Multi-output/DPI, native accessibility, client delegation and combined recovery.

No implementation or native campaign is performed by this amendment. All task
checkboxes remain open until their mapped evidence passes.

## Candidate requirements and acceptance scenarios

### Requirement: ELM-RC-001 — Menu ownership

WHEN a context gesture targets a shell-owned surface, the desktop SHALL route it
to that surface's declared context provider; WHEN it targets application client
content, the shell SHALL preserve the original application's input route and menu.

#### Scenario: ELM-RC-001 shell-provider

- GIVEN a taskbar icon and a declared app-menu provider
- WHEN the configured secondary button is clicked on that icon
- THEN exactly that provider opens, without synthesizing an app client click

#### Scenario: ELM-RC-001 client-delegation

- GIVEN an application client area or client-decorated titlebar with its own menu
- WHEN secondary click or app-owned Shift+F10 is delivered there
- THEN the app receives its original sequence and no replacement shell menu opens

### Requirement: ELM-RC-002 — Context and selection target

WHEN a menu opens, the shell SHALL freeze the exact typed context target, separately
from application activation; WHERE Files selection is involved, the shell SHALL
retain the selection for a clicked selected item, replace it with an unselected
clicked item, and target the current directory for an empty-area invocation.

#### Scenario: ELM-RC-002 selection-preserved

- GIVEN Files items A and B selected and item A under the pointer
- WHEN secondary click opens A's context
- THEN the menu targets the frozen A,B selection without opening either file

#### Scenario: ELM-RC-002 selection-replaced

- GIVEN Files A,B selected and unselected C under the pointer
- WHEN secondary click opens C's context
- THEN the selected target becomes C alone; an empty-area invocation instead targets its directory

### Requirement: ELM-RC-003 — Secondary-button sequence

WHEN an owned secondary press and matching release occur on the same eligible
context within the frozen gesture tolerance, the shell SHALL open exactly one
menu on release; IF cancellation, target retirement, button chording or a drag
invalidates that gesture, the shell SHALL open none and SHALL NOT turn it into a
primary activation. Logical button remapping SHALL be honored.
The opening release SHALL be consumed by invocation and SHALL NOT select a menu
row that appears under that pointer; a new explicit gesture is required to invoke
an action.

#### Scenario: ELM-RC-003 press-release

- GIVEN right-button context mapping and an eligible shell target
- WHEN one press and release occurs without drag or another held button
- THEN one menu opens; its opening release invokes no newly positioned row, and repeated release and synthetic duplicate events open none

#### Scenario: ELM-RC-003 mixed-buttons

- GIVEN a context press with a primary button already held, or a target retired before release
- WHEN remaining buttons release or focus changes
- THEN no menu command or primary activation is synthesized, and held state clears

### Requirement: ELM-RC-004 — Nonmutating open

WHEN a menu opens or its selection changes, the desktop SHALL preserve the target's
native window state, stack and committed activation history until an explicit
command; popup keyboard focus SHALL remain distinct from application activation.

#### Scenario: ELM-RC-004 inactive-minimized

- GIVEN inactive or minimized app B while app A owns keyboard focus
- WHEN B's taskbar context opens
- THEN B is neither restored nor raised, A's application focus/MRU remains unchanged, and the menu is keyboard reachable

#### Scenario: ELM-RC-004 preview-open

- GIVEN a group picker showing three windows or a currently active taskbar icon
- WHEN the user opens one preview's context and moves menu selection
- THEN no window activates or minimizes and no primary picker/taskbar command runs

### Requirement: ELM-RC-005 — Keyboard invocation

WHEN Menu key or Shift+F10 is invoked on a focused shell item, the shell SHALL
open the same context as secondary click anchored to that item; WHEN the configured
Alt+Space binding is invoked for an eligible active window, the shell SHALL open
that window's operation menu. IME-consumed input SHALL not become shell commands.

#### Scenario: ELM-RC-005 equivalent-context

- GIVEN a focused taskbar, Files or system item
- WHEN Menu key or Shift+F10 opens its context
- THEN target and action capabilities match secondary click and focus stays visible

#### Scenario: ELM-RC-005 active-window-route

- GIVEN an eligible active native window and the default Alt+Space mapping
- WHEN that chord occurs outside consumed IME input
- THEN its window menu opens without dispatching any operation; no active window gives a nonmutating unavailable/no-target result

### Requirement: ELM-RC-006 — Window operations and enablement

WHEN a titlebar/window menu opens, the shell SHALL expose supported Restore, Move,
Size, Minimize, Maximize and Close in the declared order, using current native
state/capabilities and the state table; unsupported operations SHALL never appear
as enabled actions and state-disabled supported actions SHALL be visibly disabled.

#### Scenario: ELM-RC-006 ordinary-maximized

- GIVEN an ordinary resizable window and then its observed maximized state
- WHEN each operation menu opens
- THEN the ordinary state disables Restore, while maximized state enables Restore and disables Move, Size and Maximize

#### Scenario: ELM-RC-006 minimized-fixed-pending

- GIVEN minimized, fixed-size or pending/unknown targets
- WHEN operation menus are projected
- THEN the state table controls enablement, pending/unknown blocks mutations, and no missing adapter is advertised as usable

### Requirement: ELM-RC-007 — Interactive Move and Size

WHEN an enabled Move or Size is selected, the native authority SHALL start an
identity-bound interactive session supporting pointer/arrow adjustment, Enter
commit and Escape rollback to saved geometry; IF the target retires or authority
changes, the session SHALL abort without affecting a replacement incarnation.

#### Scenario: ELM-RC-007 geometry-cancel

- GIVEN an ordinary native window with saved geometry
- WHEN Move or Size adjusts it and Escape is pressed
- THEN original geometry is restored with a native receipt and no extra activation

#### Scenario: ELM-RC-007 retire-session

- GIVEN an active Move/Size session and a subsequently retired window
- WHEN a replacement maps and late pointer/key events arrive
- THEN the session aborts and the replacement geometry remains unchanged

### Requirement: ELM-RC-008 — Graceful Close

WHEN Close is explicitly selected for an eligible target, the broker SHALL request
graceful client closure once and SHALL preserve application-owned save/refusal
dialogs; the menu SHALL NOT kill a process or equate request delivery with window
retirement.

#### Scenario: ELM-RC-008 unsaved-dialog

- GIVEN a disposable app with unsaved content
- WHEN Close is selected
- THEN its save dialog remains reachable and the shell does not force termination

#### Scenario: ELM-RC-008 close-refused

- GIVEN a client that refuses or delays graceful close
- WHEN the request is observed without retirement
- THEN feedback reflects that outcome and no process-kill fallback or blind retry occurs

### Requirement: ELM-RC-009 — Taskbar application menu

WHEN an app icon's ordinary context opens, the shell SHALL provide declared launch,
new-instance, pin/unpin and eligible close actions plus supported jump-list content;
application pinning SHALL persist by catalog identity and SHALL be distinct from
window Always on top.

#### Scenario: ELM-RC-009 pinned-not-running

- GIVEN a pinned application with no running family
- WHEN its context opens
- THEN declared launch actions and Unpin are available, and window-close actions are absent

#### Scenario: ELM-RC-009 pin-distinction

- GIVEN a running unpinned application with native always-on-top support
- WHEN Pin to taskbar is committed
- THEN its launcher persists without changing any window's always-on-top state

### Requirement: ELM-RC-010 — Group and Shift context

WHEN Shift+secondary click targets one taskbar window or a grouped taskbar button,
the shell SHALL open its window or explicit group operations respectively; a group
command SHALL freeze eligible displayed families and SHALL report per-family
outcomes without including late arrivals or applying single-window geometry actions
as an implicit aggregate.

#### Scenario: ELM-RC-010 shift-single-group

- GIVEN single-window and multi-family taskbar entries
- WHEN Shift+secondary click opens each entry
- THEN the single entry has its window operations and the group has labeled group actions, with no implicit app launch

#### Scenario: ELM-RC-010 close-all-membership

- GIVEN group A,B when Close all is selected and C mapping afterward
- WHEN graceful close requests execute
- THEN A and B receive at most one request each, C receives none, and individual refusal/save dialogs remain represented

### Requirement: ELM-RC-011 — Preview context identity

WHEN a live or minimized preview's context opens, the shell SHALL target its exact
family/window identity and SHALL expose state-supported operations without needing
live preview pixels; IF that identity retires, the shell SHALL remove/disable its
commands rather than retargeting a replacement.

#### Scenario: ELM-RC-011 minimized-preview

- GIVEN a minimized identity-bound preview with retained pixels or a placeholder
- WHEN its context opens
- THEN Restore/Close follow capabilities without restoring merely to open the menu

#### Scenario: ELM-RC-011 preview-replacement

- GIVEN an open context for preview A
- WHEN A retires and a new window reuses its position or allocator address
- THEN the new window receives no command from A's menu

### Requirement: ELM-RC-012 — Explicit jump-list providers

WHEN an app jump list opens, the shell SHALL show only catalog-declared tasks and
provider-supported recent destinations tied to application/provider generations;
selection SHALL dispatch a typed declared action, never evaluate labels as commands
or expose another application's recent items.

#### Scenario: ELM-RC-012 declared-only

- GIVEN a provider declaring two tasks and unsupported recent destinations
- WHEN its jump list opens
- THEN exactly supported tasks appear and unsupported/recent cross-app entries do not

#### Scenario: ELM-RC-012 provider-retired

- GIVEN a selected recent destination from provider generation N
- WHEN its provider/catalog changes before selection commits
- THEN stale selection is refused and refreshed content does not auto-launch

### Requirement: ELM-RC-013 — Desktop and taskbar background

WHEN an empty desktop or taskbar context opens, the shell SHALL target that surface
and expose only declared view/sort/refresh/new/paste/display/personalization or
taskbar-settings capabilities; Refresh SHALL refresh observed presentation, not
restart the compositor or mutate unrelated applications.
Desktop icon contexts SHALL follow their declared file/launcher provider and the
Files/desktop action matrix in RIGHT-CLICK.md; an empty desktop context SHALL never
inherit the last selected icon or imply an unimplemented desktop directory.

#### Scenario: ELM-RC-013 desktop-empty

- GIVEN empty desktop with view and settings providers but unavailable paste/new
- WHEN its context opens
- THEN supported desktop entries appear, unavailable entries cannot execute, and no selected file/window command is inherited

#### Scenario: ELM-RC-013 background-refresh

- GIVEN existing apps and an empty desktop/taskbar menu
- WHEN Refresh or taskbar settings is selected
- THEN only the declared presentation/settings action occurs, without compositor restart or closing drafts

### Requirement: ELM-RC-014 — Files adapter semantics

WHEN a Files context action is selected, the shell SHALL dispatch the exact frozen
selection/directory to the supported Files adapter; copy/move/new/rename SHALL
retain existing no-overwrite behavior, deletion SHALL use trash, and permission
failures SHALL use the existing explicit authorization flow rather than bypass it.
Action availability SHALL follow the Files/desktop action matrix in RIGHT-CLICK.md,
including Open/Open with, Cut/Copy/Paste, Copy path, single-item Rename, Move to
Trash, Properties, supported create/view/sort/refresh and declared terminal launch.
Unsupported multi-selection or destination inference SHALL not execute.

#### Scenario: ELM-RC-014 trash-no-overwrite

- GIVEN disposable Files selections and a destination name collision
- WHEN declared copy and deletion actions execute
- THEN collision behavior matches the existing adapter and deletion uses trash, never permanent removal

#### Scenario: ELM-RC-014 files-permission

- GIVEN a supported Files action with a permission-denied result
- WHEN that result is shown
- THEN existing Authorize/cancel is reachable and menu invocation alone does not elevate or retry

### Requirement: ELM-RC-015 — System-control capability accuracy

WHEN system-control, launcher or Task View contexts open, the shell SHALL use their
declared typed adapters and observed state; unavailable operations SHALL be labeled
unavailable or omitted, and no elevated/system mutation SHALL execute on menu open.

#### Scenario: ELM-RC-015 unavailable-control

- GIVEN no supported network-control adapter
- WHEN its menu is invoked
- THEN unavailable state is labeled and no enabled network mutation is offered

#### Scenario: ELM-RC-015 observed-state

- GIVEN a supported settings control with observed state and an explicit action
- WHEN its action is selected and refused
- THEN observed state remains authoritative with correlated feedback

### Requirement: ELM-RC-016 — Dismissal and focus return

WHEN Escape, outside click or explicit cancellation dismisses a menu, the shell
SHALL dismiss the innermost scope first and restore its surviving eligible opener
or the existing committed-MRU/desktop fallback; outside gestures SHALL be routed
once to the independently eligible target without accidental menu-command dispatch.

#### Scenario: ELM-RC-016 nested-escape

- GIVEN a submenu and its surviving parent/opener
- WHEN Escape is pressed twice
- THEN submenu closes before parent and final focus returns to the opener without activation history changes

#### Scenario: ELM-RC-016 outside-and-retired

- GIVEN an open menu whose opener has retired and another eligible app under the pointer
- WHEN outside click dismisses it
- THEN that app receives one original click sequence and no replacement opener is activated

### Requirement: ELM-RC-017 — Menu navigation

WHILE a shell menu is open, it SHALL support arrows, Home/End, Enter/Space,
Escape, labeled mnemonics where declared and bounded overflow; Left/Right SHALL
close/open submenus with locale direction considered, disabled items SHALL not
dispatch, and Tab SHALL not leak a partial popup scope into unrelated applications.
Enabled state SHALL be rechecked for pointer, keyboard and assistive activation;
an all-disabled menu SHALL expose no invokable selection while retaining dismissal.

#### Scenario: ELM-RC-017 navigation-and-disabled

- GIVEN mixed enabled/disabled commands, an all-disabled variant and a submenu
- WHEN arrows, Home/End and Enter/Space navigate/activate
- THEN focus is visible, only currently enabled commands dispatch, the all-disabled variant cannot dispatch and retains Escape, and Left/Right follows declared submenu direction

#### Scenario: ELM-RC-017 overflow-focus

- GIVEN enlarged labels and more commands than fit
- WHEN the last enabled action is reached by keyboard or scrolling
- THEN it remains visible/reachable and Tab follows the documented popup focus scope

### Requirement: ELM-RC-018 — Native accessibility

WHILE menus are visible, the native accessibility bridge SHALL expose menu/item
roles, names, enabled/checked/expanded state, shortcuts, relationships and supported
actions; speech/braille announcements SHALL identify context and changes once,
without moving focus or using color alone.

#### Scenario: ELM-RC-018 semantic-tree

- GIVEN a menu with a disabled operation, checked setting and submenu
- WHEN an assistive client inspects and navigates it
- THEN all roles/states/relationships and available actions match the actual menu

#### Scenario: ELM-RC-018 announcement-dedup

- GIVEN speech and braille consumers and duplicate broker receipts
- WHEN menu selection/status changes
- THEN each relevant change is announced once and keyboard focus is preserved

### Requirement: ELM-RC-019 — Output placement and DPI

WHEN a menu is positioned, the host SHALL map the anchor through the current
output transform/scale and keep all commands reachable within its declared work
area; IF the output disappears or its generation changes, the menu SHALL rehost
or dismiss under the existing output-removal contract and reject stale coordinates.

#### Scenario: ELM-RC-019 mixed-scale-edge

- GIVEN outputs at different scales/transforms and an anchor near each edge
- WHEN a menu/submenu opens with enlarged text
- THEN placement and pointer hitboxes agree, flip/scroll keeps actions reachable and no command crosses into an unintended target

#### Scenario: ELM-RC-019 output-removed

- GIVEN a menu anchored on an output that is removed
- WHEN a late release arrives using its previous generation
- THEN no action dispatches and surviving-output focus/rehost follows the declared policy

### Requirement: ELM-RC-020 — Modal, fullscreen and exclusive policy

WHEN native policy constrains a target through modal ancestry, fullscreen,
exclusive input, lock or a popup grab, the menu SHALL preserve that policy and
display only eligible actions; background commands SHALL never silently operate
on a modal descendant or bypass an exclusive/security boundary.

#### Scenario: ELM-RC-020 blocked-owner

- GIVEN owner A blocked by modal B and an independent peer C
- WHEN A's window menu and C's context are invoked
- THEN A's eligible family operations are explicit or refused, C remains independent, and no unsafe owner activation occurs

#### Scenario: ELM-RC-020 fullscreen-grab-lock

- GIVEN fullscreen, live app popup grab or locked session
- WHEN a context route or command is requested
- THEN fullscreen exit is capability-explicit, blocked commands are refused and protected-session input is not intercepted

### Requirement: ELM-RC-021 — Exact authority at execution

WHEN a context action executes, the broker SHALL revalidate the full target binding,
incarnation, provider/catalog/file identity and relevant output/capability revision;
paste SHALL also validate its declared clipboard revision without logging content;
IF the target or authority becomes stale, the action SHALL refuse/reconcile without
retargeting or affecting a new object with the same label, position or address.

#### Scenario: ELM-RC-021 stale-window

- GIVEN an open window menu and an authority reload or remapped replacement
- WHEN an old action is selected
- THEN the old tuple is refused and the replacement state stays unchanged

#### Scenario: ELM-RC-021 stale-files-catalog

- GIVEN a frozen file selection, clipboard paste revision or app catalog action
- WHEN its object/provider generation changes before dispatch
- THEN no path/label-based replacement executes and refreshed selection requires a new explicit command

### Requirement: ELM-RC-022 — Receipts, cancellation and uncertainty

WHEN an explicit menu command dispatches, the shell SHALL issue one correlated
intent, expose Pending/Committed/Refused/Cancelled/Unknown states and reconcile
with native observation; repeated input SHALL not duplicate dispatch, dismissal
SHALL not undo committed work, and Unknown SHALL never trigger blind replay.

#### Scenario: ELM-RC-022 duplicate-pending

- GIVEN a pending command and repeated click/Enter input
- WHEN duplicate input and an eventual correlated receipt arrive
- THEN exactly one intent executes and final presentation follows fresh observation

#### Scenario: ELM-RC-022 disconnect-dismiss

- GIVEN a dispatched command whose broker disconnects before a definitive outcome
- WHEN the menu is dismissed/reopened and authority reconnects
- THEN state remains Unknown until reconciliation, with no automatic retry or false cancellation/commit

### Requirement: ELM-RC-023 — Bounded provider data and input isolation

WHEN menu/provider data arrives, the shell SHALL enforce frozen counts, label,
nesting and transport bounds, reject malformed/cyclic payloads and render labels
as text; context-button events SHALL not leak into primary shell activation or
arbitrary command execution.

#### Scenario: ELM-RC-023 malformed-provider

- GIVEN oversized/cyclic provider menus or labels containing markup/command syntax
- WHEN the payload is decoded
- THEN invalid data is refused or bounded by declared policy and labels cannot execute code

#### Scenario: ELM-RC-023 scope-isolation

- GIVEN nested menus and rapid secondary/primary input across targets
- WHEN context routing is replayed
- THEN one declared scope owns each gesture and no stale press invokes a different action

### Requirement: ELM-RC-024 — Persistence and privacy

WHEN pins, shortcuts or context preferences persist, the shell SHALL bind them to
versioned identities/preferences and preserve customized bindings; menu diagnostics
SHALL retain only required metadata, SHALL NOT record clipboard/document/secret
content, and recent-item visibility SHALL honor the declared user privacy setting.

#### Scenario: ELM-RC-024 persisted-pins-shortcuts

- GIVEN a pinned app and customized context shortcut followed by restart
- WHEN settings reload or a default shortcut conflicts
- THEN identity-bound pins return and conflicts require explicit choice rather than overwriting customization

#### Scenario: ELM-RC-024 recent-privacy

- GIVEN recent-item display disabled and private clipboard/document content
- WHEN menus open and diagnostics are recorded
- THEN recent items are absent and sensitive content is excluded from logs and replay artifacts
