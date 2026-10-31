# Validation

The [Chromium specimen](specimen-chromium.png) loads under `/Warlock/` with no console errors, failed requests or external requests. The screenshot is inspected. The native attention screenshot is inspected; it shows truncated labels and a prominent status stripe. Image files remain generated concept studies, not renderer evidence.

At an 800px browser viewport, Chromium focuses every button in the complete Night toolbar at root sizes 16, 20, 24 and 32px. Every button retains at least 4px between its border box and each scrollport edge, sufficient for the 2px outline and 2px offset. The 6px gutter remains reserved. Enter opens the status disclosure, and Escape closes it and returns focus to the trigger. The status remains `aria-live="off"`; the panel has no live role. These checks exercise the specimen reference script, not the production Elm renderer or native adapter.

The production acceptance remains open. The current adapter has a restoration path that returns before scrolling when the control already has focus. Its actual host and Elm renderer need the focus-scrolling integration and the typed activity, observed window focus and attention projections described in the specification. Elm also needs to own the disclosure and native host allocation. The specimen uses local JavaScript only to demonstrate those requirements; it is not a production state owner. Typed outcome symbols remain a renderer requirement.

High contrast, forced colours, effects-off, reduced motion, reduced transparency, browser zoom, 320px width, long labels, native focus retention and WebKitGTK remain outside these checks. No portal lifecycle or native action is exercised.

## Allocation and text spacing

Chromium measures every bar in [the specimen](specimen.html) and [the 200% document](specimen-scale.html) at 16, 20, 24 and 32px roots. Each bar is exactly `3 × root + 8px` high, matching the native exclusive-zone expression. With the WCAG text-spacing overrides injected (line height 1.5, letter spacing 0.12em, word spacing 0.16em, paragraph spacing 2em), every label and detail stays inside its control's border box and inside the toolbar at all four roots, and no toolbar overflows vertically. These are static specimen measurements; the native bar host is not exercised.

## Revision check

The canonical bootstrap loads before the shared foundations and taskbar sheets. Chromium loads both [the specimen](specimen.html) and [the 200% high-contrast document](specimen-scale.html) under `/Warlock/` with no console errors, failed requests or external requests. Both screenshots were inspected. The 200% document exercises long labels, a long status, effects off and a separate document-focus-loss state. The existing images remain unchanged.

This is a specimen check, not production acceptance. The staged Elm renderer still derives activity from detail strings and does not implement the status disclosure. Its window-focus projection is present. D01 owns the production renderer and native popup allocation, which are outside D02’s assigned paths. Keyboard traversal at 800px for this document and native host behavior remain unverified.
