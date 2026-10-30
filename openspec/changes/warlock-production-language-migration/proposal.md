# Warlock production language migration

## Why

Charles's latest October 30 decision selects Elm and Haskell only for authored production, with all GUI elements in Elm. The original 242 requirements / 417 scenarios and additive contracts remain unchanged.

## What Changes

- Haskell native/runtime capabilities, Haskell pure policy where selected, Elm for every GUI element; one authoritative policy owner per domain.
- All authored shipped components use the allowed languages, including implementations behind wrappers.
- Preserve typed Elm ports/validated IPC, pure reducers, exact native authority, receipt ordering and original deadlines.
- Retain original IDs, scenarios, frozen evidence and accepted/failed receipts. No acceptance transfers to replacements.

## Impact

Only design/spec readiness preparation is authorized now. Product implementation remains paused; root coordinates readiness and Muse before any new loop is armed. Development QA/formal tools and inventoried third-party libraries remain separate from authored production.
