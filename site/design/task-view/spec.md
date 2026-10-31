# Task View and workspaces

## Overview

Task View is a single-column inventory of observed workspaces and window families. Filters browse the inventory. A family activates or restores its window. An eligible empty inactive workspace has a separate “Go to workspace N” action. “Move [family]…” enters destination selection. These are separate operations; pressing a filter does not switch desktops.

## Anatomy

`.surface-popup[data-mode="overview"]` contains the Task View heading, a static status paragraph and `.surface-controls`. Controls remain in source order: Close Task View, All windows, each workspace filter followed by its eligible rows, then recovery controls. Each `.overview-workspace` groups its workspace button and only its contiguous family prefix. Move and Go controls can be siblings outside that group. Neutral spacing unifies the list without suggesting a complete card boundary. There are no workspace columns, thumbnails, drag gestures or workspace management controls.

Workspace labels use section-title; details use secondary detail text. Family rows have a 40px leading inset and a minimum 56px height. Single-line controls are at least 36px high and rows with details at least 56px. With a coarse pointer, single-line controls are at least 44px and family rows and other rows with details at least 60px. Rows do not shrink and grow for wrapped content. Move is a subordinate neutral action with a 56px leading inset, one 16px step deeper than its family. A workspace wrapper starts 24px after the preceding sibling, including the shared 6px row gap. This boundary remains neutral and does not enclose sibling Move or Go controls. Destination and Go actions have an essential outline. All labels wrap; the viewport and scrollport preserve a 6px focus gutter. Popup geometry belongs to the host; 960px is a documentation preference, not a native allocation.

## States and behaviour

`overview:all` and `overview:workspace:` use `aria-pressed`. A pressed filter has selected fill, a 3px brand-text leading bar and a visible check drawn with decorative geometry. The control border and padding remain constant across selection states. The check and bar retain visibility for a selected unavailable filter in high contrast and forced colours; the unavailable cue paints in its own reserved inline-end slot on the label, so it never replaces the check or the bar. “Active workspace” is independently sourced detail, not selected state. Family detail identifies workspace and Open, Minimized, Unavailable for activation or Awaiting native confirmation. Disabled controls retain opacity and semantics. Hover and press never erase selection; shared focus styling belongs to the actual focused control.

`overview:transfer:` enters an in-place subflow. Source order becomes Cancel transfer followed by eligible `overview:destination:` actions labelled “Move to workspace N”. Cancel returns to the initiating Move control when it remains available, then the workspace filter or All windows. Transfer membership remains at its admitted source while pending or unknown. A receipt alone does not prove movement. `overview:refresh` and `overview:workspace-refresh` read current facts, without retrying a mutation. The status region uses the source wording and `aria-live="off"`.

An observed empty workspace stays visible. Only an eligible inactive empty workspace gets `overview:go:`; its detail says “Switch desktop”. Navigation closes the overview while its result is observed. Filter, navigation and transfer presentation changes are immediate and do not trigger application portals.

## Keyboard and accessibility

Use the renderer's buttons, names, focus identity and source order. Tab reaches each enabled control and Enter or Space activates it. The controller owns opening focus, cancellation and focus return. The shared 2px focus ring, 2px offset and opaque gap remain visible in the scroll gutter. At 320px and enlarged text, labels wrap and rows grow. Forced colours retain a solid selection bar and a border-drawn check. Shared foundations supply high contrast, focus, motion, coarse target and disabled affordances; this package adds no global recipe.

## Renderer requirements

Keep `data-surface-control` identities `overview:all`, `overview:workspace:`, `overview:family:`, `overview:transfer:`, `overview:destination:`, `overview:go:`, `overview:refresh`, `overview:workspace-refresh`, and `control:close`; retain `aria-pressed`, disabled authority, `data-focus-only`, accessible names and source order. The current `Selected` detail is retained alongside the decorative check. Do not infer active workspace, focus or operation result from text. A complete semantic workspace grouping requires a separately verified renderer change before a card layout can exist. The renderer currently has no visible transfer context naming the selected family; a source-backed projection is required to add it. No CSS-generated label substitutes for that change.

## Evidence and reference

The source authority is commit bc3daf7b80ac7295a1ba1e56639a0e130e520a3c. Native captures from taskview-filter-accessibility, taskview-empty-inventory, taskview-workspace-navigation and transfer-current show the current control order. Their uniform bordered rows flatten filter, family, Move and navigation hierarchy; status and titles compete for vertical space. Catalog v6 supplies the frozen comparison. Fluent layout and Material navigation guidance inform grouping; GNOME keyboard guidance and WCAG focus-not-obscured inform reachability; KDE layout and Apple HIG inform clear hierarchy. Warlock tokens and behaviour override platform styling.

The status gallery isolates source wording and related controls for pending, refused and unknown outcomes. It is an excerpt rather than a complete renderer snapshot. The full specimens retain the renderer hierarchy. The focused selected filter demonstrates that keyboard focus and selection coexist. The specimen links directly to the [Task View scenario](../../test-drive/index.html?scenario=task-view) and [transfer scenario](../../test-drive/index.html?scenario=transfer). The [manifest](manifest.json) records scenario destinations and the four retained images. Its scale links change the root font size once.

## Concept studies

The four images are illustrative and the source-faithful specimen and CSS define the interface. Each image carries the caption **Generated concept study**.

- [Generated concept study](mockups/mockup-1.png): Task View, Night.
- [Generated concept study](mockups/mockup-2.png): Task View, Dawn.
- [Generated concept study](mockups/mockup-3.png): Transfer, Night.
- [Generated concept study](mockups/mockup-4.png): Transfer, Dawn.

The images do not define iconography, grouping, alignment or control emphasis. Task View uses the renderer’s partial wrappers and flat source order. Transfer uses left-aligned destinations and a quiet Cancel transfer control.
