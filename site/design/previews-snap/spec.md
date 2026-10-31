# Window previews and snap layouts

## Overview

The picker presents window families in stable controls. A preview describes the family or client image; it does not determine whether the control can activate its window. Snap presents six region proposals and a separate action. The popup fills its host allocation and enters and leaves immediately.

## Anatomy

The renderer emits `.surface-popup[data-mode="picker"]`, a heading, a static status and `.surface-controls`. The Close button precedes `button[data-surface-control^="family:"]`. Each family control contains an optional `.preview-content[aria-hidden]`, `.window-preview[data-preview-state]`, image or icon, title, state and fidelity spans, then `.control-label`, `.control-detail` and an optional hidden `.preview-description` referenced by `aria-describedby`. The image is decorative. The action name remains the control's accessible name. `Hidden` has no preview node at all.

A reserved 160 × 100px well and 12px gap hold each preview. Five measured caption slots retain their positions across image, icon and absent-image states. The normal row's height, minimum and maximum are `min(calc(7.5rem + 16px), calc(100vh - 30px))`. Text wraps. Arrival and release never alter a target's rectangle.

The renderer emits `.surface-popup[data-mode="snap"]`, Close, six `snap:region:` buttons in source order and `snap:apply`. The six diagrams depict left and right halves and top left, top right, bottom left and bottom right quarters. Tiles use two columns, 12px gaps, a 112px minimum height and 64 × 40px diagrams. The popup is an inline-size query container. It uses one column below 28rem of available component width and two columns at or above 28rem; root text scaling raises that threshold. Labels and details retain space and wrap. Apply remains a distinct control.

## States and behaviour

Live and historical drawable images use contain, retaining family or client fidelity. Loading, unavailable, capacity, waiting, expired, conflict and exhausted use the source's actual state wording. Capacity and waiting indicate waiting; expired and conflict describe the request; exhausted uses the source's unavailable wording. Image freshness never implies action availability. Passive preview descriptions are not a live announcement. A loading attempt capture is evidence of an attempt, not proof that a loading frame was painted.

Snap selection uses `aria-current="true"`, a selected fill, a leading brand bar and the renderer's `Selected` detail. Keyboard focus uses the shared blue focus ring, independent of selection. Region selection does not apply a snap. Apply is enabled only when the shell is ready, no competing choice exists, the snap capability is present and the proposal exists. Its unavailable label is `Snapping unavailable`. Disabled controls retain semantics and readable text. No tile casts a shadow or glow.

Focus and selected states change immediately. Enabled pointer fills follow shared motion tokens. Neither picker nor snap invokes the application portal. Escape, Close and keyboard traversal follow the existing popup policy. Selection and apply dispatch the renderer's scoped identities, publication and lease; a receipt does not establish placement.

## Geometry and renderer requirements

Before targets become interactive, the host measures the longest admitted label, title, state and detail at the committed scale and text spacing. If the normal fixed row cannot contain them, it publishes a taller stable row or a stacked text-first fixed-slot profile. If even that cannot contain the full content in the available host, it uses a text-first fixed-slot fallback with sufficient height and a scrollport. A change of profile invalidates the publication and lease before renewed input; a held press never transfers. Image arrival alone never causes this negotiation. These profiles require an explicit typed presentation projection and sizing negotiation; the current renderer does not emit one. The specimen measures before it admits its static controls; production admission remains a host requirement. D01 integration must implement and test this gate before enabling targets at those profiles.

The legacy preview lane retains lifecycle, paint and release handshakes, allowlisted handles, keyed nodes and hidden descriptions. No controlled-preview lane is implied. Source supplies only the actual visual variant, so the absence of a preview element must not collapse the reserved well. Screen-reader text remains readable and distinct from the control's own label. Forced colours use system colours and preserve diagram shape, selection wording and focus. Reduced motion and all effects tiers retain static geometry.

## Evidence and references

The native `preview-descriptions/Live.png`, `preview-states/Historical.png`, `picker-shared-storage/native-Loading-attempt.png` and `snap-chooser/native-snap-chooser.png` show current renderer surfaces. The picker presents a focused row and an unavailable fallback; the snap capture presents the region grid. The legacy captions truncate and the snap tiles use decorative gradients and glow, weakening readability and state separation. The catalog v6 component manifest and catalog data are a frozen reference, not current source authority.

Material list guidance supports consistent row alignment; Fluent layout supports predictable grouping; Windows keyboard guidance supports visible focus; GNOME keyboard guidance and KDE layout guidance support keyboard access and consistent placement; Apple motion guidance supports purposeful motion; WCAG focus appearance and focus-not-obscured captures inform the reserved focus gutter. Warlock's tokens and state policy govern the resulting numeric design.

## Try it

[Open picker](../../test-drive/?scenario=picker), [preview states](../../test-drive/?scenario=preview-states), or [snap](../../test-drive/?scenario=snap) in the test drive. The [scenario manifest](scenario.json) records the fixtures. Open a taskbar group with multiple families to choose a window. Open Window actions and choose Snap window to select a region and apply it. Test-drive host operations are simulated observations and do not operate the visitor's native windows.

## Profile admission contract

The source renderer does not emit `data-picker-profile`. The proposed host projection admits `expanded` or `stacked` only after it measures every visible caption with the active font, scale, width and text-spacing overrides. The host chooses one common `--wl-picker-row-height` that contains every state and content variant, including the image-absent variant. It invalidates the current publication and lease before changing profile or row height, waits for held input to end, then publishes the new geometry. The normal fixed profile is admitted only when every caption fits. A width or text change is a geometry change, while frame delivery and release are not. The stacked specimen illustrates this proposed projection; it does not claim the existing Elm renderer supplies it.

The host keeps targets unavailable until measurement and publication complete. If a 160 × 100 well leaves inadequate text space, the stacked profile places that well above the text. When the allocation cannot contain both, the host negotiates a text-first fixed-slot fallback with a scrollport. Full labels, details and fidelity remain visible. These admission and fallback rules require renderer and host work outside this package.

### Admission and lease sequence

Admission is a prerequisite, not a CSS breakpoint. D01 owns the integration and D06 owns this geometry contract. The current source has no measurement projection or gate, so picker controls must not be treated as admitted for unmeasured content. A compliant integration performs this sequence:

1. Render a noninteractive, offscreen measurement copy using the same width, fonts, scale, text-spacing, wrapping and control styles as the committed surface. Include every current title, action label and detail, all possible lifecycle and local-state labels, both fidelity strings, and the empty visual. Measure after fonts settle. Never announce or expose the measurement copy as an interactive control.
2. Admit the normal fixed row only if all content fits inside its bounds. Otherwise measure a common expanded row, then a stacked row. When the well and full text cannot fit together, negotiate a text-first fixed-slot row that retains full names, state and fidelity and uses a scrollport. The well remains reserved for the lifetime of that admitted profile. No label is clipped or hidden to make a profile fit.
3. Bind the profile and rounded-up common row height to the exact publication, lease, width, typography and content revision. Keep family targets unavailable until that geometry is committed and acknowledged. During a held input, retain the admitted rectangles; invalidate authority before a geometry change and never retarget the press. Re-measure, issue a new publication and lease, then enable input only after the new presentation is acknowledged.
4. A frame, icon, image removal or paint/release event changes only the content of the reserved well. It never changes row size or publication. A change to any measured text, font, available width, scale or spacing invalidates admission. The source-defined preview lifecycle and native release handshake continue independently.

The specimen demonstrates local measurement and admission for its static fixtures. It does not implement the production publication and lease protocol. Real-renderer verification covers 320px effective width, 200% scale and zoom, long titles, all state and fidelity labels, WCAG text spacing, frame delivery and removal while a pointer is held, and stale publication/lease rejection. These checks remain integration work until performed in the host.

## Measured slot projection

The host projects the common measured state, title, fidelity, action-label and action-detail slot heights through `--wl-picker-state-slot`, `--wl-picker-title-slot`, `--wl-picker-fidelity-slot`, `--wl-picker-label-slot` and `--wl-picker-detail-slot`, as well as `--wl-picker-row-height` for expanded, stacked and text-first profiles. Each value covers the greatest wrapped height in that slot across every family and every possible lifecycle visual for the admitted content revision. The normal and expanded profiles use these tracks alongside the 160 × 100px well. The stacked profile puts the well above the text. The text-first profile puts the full text first and retains a 64 × 40px visual slot after it. All profiles use one common measured row height. Every admitted profile uses these explicit tracks, including stacked and text-first. The static specimen measures its fixtures and lifecycle wording before admitting them; the source does not currently project these values.

Snap reserves a 3px leading border in every state, so selection changes its colour without moving the diagram or captions. The source's Selected detail is the non-colour cue. A focus ring is independent. Changes to snap column count are also geometry changes and use the host's publication and lease invalidation before renewed input.

## Generated concept studies

The four files in [mockups](mockups/README.md) are each captioned **Generated concept study**. Their controls and colours are illustrative; the renderer-shaped specimen and this specification define the interface.

## Specimen admission

The specimen loads the canonical bootstrap and starts picker surfaces inert. Its local measurement includes all displayed text and lifecycle wording, chooses a common profile and slot heights, and admits the static targets only after projection. A resize or font change retires the specimen targets before measurement. A held pointer defers re-admission until release. The fixed normal well is 160 × 100px even when the image is absent. The specimen does not implement a native lease, and its admission demonstration does not replace the renderer and host integration.
