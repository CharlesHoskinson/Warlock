# Additive context-menu requirements

Candidate amendment; no baseline ledger mutation or implementation acceptance.
The 24 EARS requirements below refine the frozen obligations described in
[RIGHT-CLICK.md](../../../../../docs/elm-roadmap/RIGHT-CLICK.md). That document's
ownership table, state table and typed authority contract are part of this
candidate. Scenario identities are stable within this amendment.

## ADDED Requirements

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
