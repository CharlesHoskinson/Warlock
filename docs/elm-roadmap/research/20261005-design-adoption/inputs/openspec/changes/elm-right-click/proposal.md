# Add Windows-style contextual interactions

## Why

The existing Elm desktop roadmap requires context menus and jump lists but does
not specify enough right-click targeting, gesture, window-state and authority
details for consistent implementation. The user explicitly requested those specs.

## What changes

Add a separate `ELM-RC-001`–`ELM-RC-024` amendment candidate for titlebar/window,
taskbar app/group/preview, desktop, Files and system-control menus; preserve native
application client-area menus. Define keyboard equivalence, supported action
states, identity-safe receipts, focus/dismissal, output placement, accessibility
and negative acceptance cases. Reference Microsoft primary documentation while
making Linux-specific product policies explicit.

## Scope and compatibility

This change refines the existing `ELM-UI-007/008`, `ELM-UX-010/023/024/025/026/027/
028/032` obligations and native authority policy. It does not mutate the frozen
242 requirements, 417 scenarios, historical acceptance, installed desktop or
application menus. IDs remain outside baseline counts until a reviewed amendment
records traceability, ownership and acceptance mappings. No completed requirement
or implemented feature is claimed. No destructive action is run.

The context contract and native/CPU/model gates are documented in
[RIGHT-CLICK.md](../../../docs/elm-roadmap/RIGHT-CLICK.md). Existing refusal,
uncertain-outcome recovery, preferences and Files semantics remain authoritative.
