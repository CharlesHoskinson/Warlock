# Warlock production language migration

## Why

Charles's latest October 30 decision selects Elm and Haskell only for authored production, with all GUI elements in Elm. The original 242 requirements / 417 scenarios and additive contracts remain unchanged.

## What Changes

- Elm for every GUI element and existing GUI interaction policy; one host-side Haskell native admission/custody authority with reviewed runtime integration.
- All authored shipped components use the allowed languages, including implementations behind wrappers.
- Preserve typed Elm ports/validated IPC, pure reducers, exact native authority, receipt ordering and original deadlines.
- Retain original IDs, scenarios, frozen evidence and accepted/failed receipts. No acceptance transfers to replacements.

## Impact

Preparation mode is armed for authorized interface/source/tool/plugin/model/fuzz readiness development. Root has adopted intended private-network UI/local HTTP and host-side native-authority placement, with ordinary apps retaining host launch/network context and native operations empty. Final implementation-mode promotion requires independently reviewed design readiness under existing authorization; full release acceptance remains later. No runtime admission, stopped-host retry or existing acceptance transfer follows. Development QA/formal tools and inventoried third-party libraries remain separate from authored production.
