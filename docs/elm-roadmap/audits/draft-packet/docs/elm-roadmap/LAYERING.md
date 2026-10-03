# Window layering: native design and acceptance

Correct layering is a mandatory prerequisite for the Elm shell. The visible window, pointer target and native focus outcome must agree for overlapping eligible application surfaces. GUI-language purity and WebGPU acceleration do not fix contradictory native scene/input state.

## Current regression

The user reported that Heroic Games Launcher cannot be minimized or covered by selecting another window. A captured screen visibly shows Heroic while the compositor state sample identifies a terminal as active. Heroic is recorded on `special:win-minimized`, with `hidden=false`, `visible=true`, `acceptsInput=true` and prior over-fullscreen permission; the monitor reports no active special workspace. [Observation](heroic-layering-observation.json).

The metadata sample and screenshot are not an atomic capture. In the inspected core, generic `visible` is based on mapped/hidden/surface/alpha state, and generic `acceptsInput` does not itself encode workspace visibility. Those fields alone cannot prove the final native hit path. The observation establishes a real displayed symptom and an acceptance obligation; it does not isolate the exact offending draw pass, capture actor or runtime source tuple. The staged MAX ordering correction was built for a different bounded scenario and must not be declared a complete correction for this incident.

The current minimizer uses a special workspace. The rebuild instead needs first-class minimized eligibility that preserves normal workspace identity. Independently retained preview pixels are allowed while the live minimized surface is excluded from drawing/input. An application preview or animation actor cannot secretly remain a live clickable duplicate.

## Reference systems

Study source-level architectures, not only screenshots:

- [Mutter study](contributions/gnome-layering.md): visibility/showability, default layers, transient constraints, stack transactions, compositor actors and input ownership.
- [KWin study](contributions/kde-layering.md): constrained stacking, layer recomputation, transient handling, scene publication, input routing, outputs and native rendering.
- [Source/documentation inventories](reference/README.md): complete scoped source snapshots and reachable developer documentation downloaded using Scrapling, pinned revisions and hashes, crawl limitations and retained failures.

These references inform the design; they do not define our Windows product behavior automatically. For example, the inspected Mutter version suppresses its above-state layer for maximized windows. Our pin/MAX acceptance requires an explicit product policy instead of inheriting that behavior accidentally.

## Proposed native authority

Keep a single committed scene revision that includes stable native incarnations, window family relations, output/workspace membership, visibility reasons, presentation geometry, input regions, layer constraints, stack order and active focus. Elm receives a projection and proposes intents against a known revision; the native authority validates and commits them. It does not wait for webview IPC during native pointer dispatch or frame composition.

Apply eligibility before precedence. A stale allowed-over-fullscreen flag, pin permission or high z rank cannot make a minimized, unmapped, destroyed or inactive-workspace live surface eligible. Workspace-independent visibility is an explicit supported state, not an implication of pinning. Animation/preview surfaces have separate identities and lifetimes, remain inert when required, and retire on acknowledged generation changes.

Build layer and family constraints, then produce a deterministic bottom-to-top native order. Preserve stable relative order unless an accepted action changes it. Reject invalid owner cycles and stale requests. Eligible modal/popup children remain above their owner according to their protocol role, while focus redirects according to modal authority; unrelated windows sharing an application identity are not promoted into a modal family.

Native painting traverses the committed order; native hit testing traverses the relevant eligible order in reverse with actual input regions/transforms. Input-transparent surfaces may be painted while deliberately passing hits through. That is an explicit rule, not disagreement between independently computed stacks. Geometry used for animated hit testing follows native presented transforms, not a delayed Elm model or DOM rectangle.

A scene change publishes stack, eligibility and focus as one revision. Render/import completion and physical presentation remain separate evidence events. Generation invalidation prevents an old overlay or retained frame from becoming live input after minimize, restore, output transfer or restart. Any specialized fullscreen/effect pass must preserve the accepted order and eligibility rather than redraw an arbitrary floating window later.

## Layer policy to freeze in P0

| Domain | Product rule / gate |
| --- | --- |
| Ordinary and maximized applications | MAX remains in the ordinary application order; selecting a covered eligible peer raises it without stale peer redraw |
| Pinned applications | Explicit pin priority above ordinary/MAX windows; pin and workspace membership remain separate states |
| True fullscreen | Separate from MAX; output-local fullscreen, pin, transient and shell precedence must match the inherited native pin/fullscreen case matrix |
| Modal/popup families | Eligible children constrained above owner; focus redirects to the accepted modal recipient; protocol grabs/roles remain native |
| Panels/notifications/menus | Explicit shell surface roles and input regions; a fullscreen webview cannot grant itself compositor-wide priority |
| Preview/motion surfaces | Separate inert/interactive policy, frame lease, output generation and retirement; no accidental duplicate application input |
| Lock/security surfaces | Native exclusive security priority; ordinary apps and untrusted shell requests cannot bypass it |
| Minimized/inactive/destroyed | Excluded live surfaces regardless of z rank or old fullscreen permission; retained preview is a separate inert actor |

P0 records the exact inherited fullscreen/pin predicates and resolves any unsupported interactions before qualification. Every released layer relationship then has a concrete scenario and expected draw/hit/focus result. This gate prevents unreviewed precedence changes being smuggled in as language or host migration.

## Required adversarial fixtures

Include Heroic-versus-terminal and maximized Brave-versus-floating-peer, plus minimize/restore while a modal exists, inactive workspaces, pinned MAX/unpin/return, true fullscreen on one output with a pin on another, popup grabs and input-transparent menus. Exercise repeated raises, rapid Alt-tab, release-before-view-ready, pending capture/animation during minimize, source destruction/address reuse, output transfer/hotplug and renderer/service restart.

For each fixture preserve native identities, scene/output generations, committed order, selected window, pixel observation at overlap regions, independent input target, focus receipt and normal lifetime closure. Run the existing protected native campaigns with their original assertions/deadlines and fresh derivatives. Reducer tests, topology/property tests and Quint invariants supplement those campaigns; they do not substitute for actual drawn and clicked outcomes.

The optional replacement compositor must implement the same authority contract and acceptance matrix before taking over the main session. Shell release with Hyprland remains blocked if the active native layer behavior fails those mandatory cases.
