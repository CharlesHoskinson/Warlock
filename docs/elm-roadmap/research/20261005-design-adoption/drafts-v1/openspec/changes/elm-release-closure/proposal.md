# Make remaining release closure explicit

## Why

Component evidence and changing implementation lanes do not show which original release obligations have been accepted together. The user requested an inventory and EARS/OpenSpec drafts of the remaining work.

## What Changes

Add24 release-evidence closure obligations for S01–S16, conditional C00–C06 and the existing right-click amendment. Preserve all242 requirements/417 scenarios, original deadlines, scope amendment, evidence levels and current component results. These are draft acceptance refinements, not missing-feature counts.

## Capabilities

### New Capabilities

- `elm-verification`: additive requirements under the same capability path as the in-flight elm-desktop-pivot draft. There are no promoted main specs; this change must be merged with the existing draft before archive. It does not introduce a second verifier or overwrite baseline requirements.

### Modified Capabilities

None: no archived main spec is changed.

## Impact

Release ledger, package acceptance and test planning only. No installed desktop, source implementation or baseline registry changes. The full exact mapping is in docs/elm-roadmap/research/20261005-design-adoption/remaining-work.json.
